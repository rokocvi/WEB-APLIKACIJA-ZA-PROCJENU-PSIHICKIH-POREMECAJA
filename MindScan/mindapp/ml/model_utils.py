# mindapp/ml/utils.py
import os
import cloudpickle

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

def load_model():
    with open(os.path.join(BASE_DIR, "model.pkl"), "rb") as f:
        model = cloudpickle.load(f)
    with open(os.path.join(BASE_DIR, "label_encoder.pkl"), "rb") as f:
        label_encoder = cloudpickle.load(f)
    return model, label_encoder
