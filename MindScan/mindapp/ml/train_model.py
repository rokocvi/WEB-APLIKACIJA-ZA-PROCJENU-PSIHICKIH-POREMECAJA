import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import cloudpickle

from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split, GridSearchCV
from sklearn.metrics import accuracy_score, classification_report
from sklearn.impute import SimpleImputer
from sklearn.preprocessing import LabelEncoder

from imblearn.over_sampling import SMOTE


data = pd.read_csv("C:/Users/cvitk/OneDrive/Radna površina/zavrsni/MindScan/mindapp/ml/mentalni_upitnik_bipolarni.csv")


counts = data["dijagnoza"].value_counts()
valid_classes = counts[counts >= 2].index
data_filtered = data[data["dijagnoza"].isin(valid_classes)].copy()


X = data_filtered.drop("dijagnoza", axis=1)
y = data_filtered["dijagnoza"]


imputer = SimpleImputer(strategy="mean")
X_imputed = pd.DataFrame(imputer.fit_transform(X), columns=X.columns)


le = LabelEncoder()
y_encoded = le.fit_transform(y)


class_mapping = dict(zip(le.classes_, le.transform(le.classes_)))


original_counts = pd.Series(y_encoded).value_counts()


desired_counts = {
    'anksioznost': 20,
    'bipolarni_poremecaj': 20
}


custom_sampling = {
    class_mapping[label]: count
    for label, count in desired_counts.items()
    if count > original_counts[class_mapping[label]]
}


if custom_sampling:
    smote = SMOTE(sampling_strategy=custom_sampling, random_state=42)
    X_resampled, y_resampled = smote.fit_resample(X_imputed, y_encoded)
else:
    X_resampled, y_resampled = X_imputed, y_encoded


X_train, X_test, y_train, y_test = train_test_split(
    X_resampled, y_resampled, test_size=0.2, random_state=42, stratify=y_resampled
)


param_grid = {
    "n_estimators": [100, 300],
    "max_depth": [5, 10, None],
    "min_samples_split": [2, 5],
    "class_weight": ['balanced']
}

grid = GridSearchCV(
    RandomForestClassifier(random_state=42),
    param_grid,
    cv=3,
    scoring="precision_weighted",
    n_jobs=-1
)

grid.fit(X_train, y_train)
model = grid.best_estimator_


y_pred = model.predict(X_test)
accuracy = accuracy_score(y_test, y_pred)
print(f"Točnost modela: {accuracy:.4f}")
print("\nKlasifikacijski izvještaj:\n")
print(classification_report(y_test, y_pred, target_names=le.classes_))


feat_importances = pd.Series(model.feature_importances_, index=X.columns)
plt.figure(figsize=(10, 6))
sns.barplot(
    x=feat_importances.sort_values(ascending=False).head(15),
    y=feat_importances.sort_values(ascending=False).head(15).index
)
plt.title("Top 15 najvažnijih pitanja za klasifikaciju")
plt.xlabel("Važnost")
plt.ylabel("Pitanje")
plt.tight_layout()
plt.show()


with open("model.pkl", "wb") as f:
    cloudpickle.dump(model, f)

with open("label_encoder.pkl", "wb") as f:
    cloudpickle.dump(le, f)

print("✅ Model i LabelEncoder su uspješno spremljeni.")
