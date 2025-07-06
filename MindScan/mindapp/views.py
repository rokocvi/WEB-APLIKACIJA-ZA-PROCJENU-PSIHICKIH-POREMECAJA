from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from accounts.forms import UserUpdateForm, LijecnikUpdateForm
from .models import PsiholoskiTest, Notifikacija, ChatPoruka,User, Lijecnik
import numpy as np
import joblib
import os
from django.conf import settings
from .ml.model_utils import load_model
from django.contrib.auth.models import User
from django.contrib import messages
from django.views.decorators.http import require_POST
from django.db.models import Max, Q
from django.http import HttpResponseForbidden
# Create your views here.
def home(request):
    je_li_lijecnik = False
    if request.user.is_authenticated:
        try:
            _ = request.user.lijecnik  # pokušava dohvatiti povezani Lijecnik
            je_li_lijecnik = True
        except:
            je_li_lijecnik = False

    return render(request, 'home.html', {'je_li_lijecnik': je_li_lijecnik})




def assessment_view(request):
    return render(request, 'assessment.html')


def anksioznost_view(request):
    return render(request, 'anksioznost.html')

def depresija_view(request):
    return render(request, 'depresija.html')

def stres_view(request):
    return render(request, 'stres.html')

def adhd_view(request):
    return render(request, 'adhd.html')

def kvaliteta_view(request):
    return render(request, 'kvaliteta.html')



@login_required
def pronadi_klijente(request):
    klijenti = []

    # Uzmi sve korisnike (ili samo one relevantne, npr. svi koji imaju testove)
    users = User.objects.all()

    for user in users:
        # Uzmi zadnji test tog usera koji ima predikciju
        test = PsiholoskiTest.objects.filter(user=user).exclude(predikcija__isnull=True).exclude(predikcija='').order_by('-datum').first()
        if test:
            klijenti.append(test)

    return render(request, 'pronadi_klijente.html', {'klijenti': klijenti})

@login_required
def profil_view(request):
    user = request.user

    # Ako korisnik ima povezan objekt Lijecnik — vodi ga na liječnički profil
    if hasattr(user, 'lijecnik'):
        return render(request, 'profil_lijecnik.html', {
            'user': user,
            'lijecnik': user.lijecnik
        })
    
    # Inače, vodi ga na profil običnog korisnika
    return render(request, 'profil_korisnik.html', {
        'user': user
    })

def uredi_profil_view(request):
    if hasattr(request.user, 'lijecnik'):
        # Ako je liječnik
        user_form = UserUpdateForm(request.POST or None, instance=request.user)
        lijecnik_form = LijecnikUpdateForm(request.POST or None, instance=request.user.lijecnik)

        if request.method == 'POST':
            if user_form.is_valid() and lijecnik_form.is_valid():
                user_form.save()
                lijecnik_form.save()
                return redirect('profil')

        return render(request, 'uredi_profil_lijecnik.html', {
            'user_form': user_form,
            'lijecnik_form': lijecnik_form,
        })

    else:
        # Obični korisnik
        user_form = UserUpdateForm(request.POST or None, instance=request.user)

        if request.method == 'POST':
            if user_form.is_valid():
                user_form.save()
                return redirect('profil')

        return render(request, 'uredi_profil_korisnik.html', {
            'user_form': user_form,
        })


@login_required
def testovi(request):
    questions = {
        1: "Imate li problema s koncentracijom?",
        2: "Osjećate li se često bezvoljno?",
        3: "Imate li poteškoća sa spavanjem?",
        4: "Osjećate li se tjeskobno bez jasnog razloga?",
        5: "Teško vam je donijeti odluke?",
        6: "Osjećate li se iscrpljeno većinu dana?",
        7: "Imate li osjećaj da ništa nema smisla?",
        8: "Često se osjećate napeto ili pod stresom?",
        9: "Zaboravljate važne stvari češće nego prije?",
        10: "Imate li potrebu često provjeravati jeste li nešto napravili (npr. zaključali vrata)?",
        11: "Osjećate li ubrzan rad srca bez fizičkog napora?",
        12: "Često odgađate zadatke koje trebate obaviti?",
        13: "Imate li problema s organizacijom vremena?",
        14: "Osjećate se nesigurno u svakodnevnim situacijama?",
        15: "Imate li česte promjene raspoloženja?",
        16: "Imate osjećaj da drugi ne razumiju kroz što prolazite?",
        17: "Izbjegavate društvene situacije?",
        18: "Imate li napade panike?",
        19: "Imate li osjećaj da gubite kontrolu nad svojim mislima?",
        20: "Osjećate se emocionalno iscrpljeno?",
        21: "Imate problema s motivacijom?",
        22: "Često kritizirate sami sebe?",
        23: "Imate osjećaj da se ne možete opustiti?",
        24: "Imate li poteškoća s praćenjem razgovora ili predavanja?",
        25: "Osjećate li se izolirano od drugih ljudi?",
        26: "Imate probleme s pamćenjem novijih informacija?",
        27: "Imate li osjećaj unutarnjeg nemira?",
        28: "Imate smanjen interes za aktivnosti koje ste nekad voljeli?",
        29: "Imate poteškoća s izražavanjem emocija?",
        30: "Imate osjećaj da vaš život nema smisla?"
    }

    if request.method == "POST":
        answers = {}
        for i in range(1, 31):
            answers[f'q{i}'] = int(request.POST.get(f'q{i}', 0))
        PsiholoskiTest.objects.create(user=request.user, **answers)
        return redirect('rezultati_testa')  

    return render(request, "testovi.html", {
        "questions": questions,
        "range_30": range(1, 31)
    })


model_path = os.path.join(settings.BASE_DIR, 'mindapp', 'ml', 'model.pkl')
ml_model = joblib.load(model_path)

def preporuka_za_poremecaj(poremecaj):
     preporuke = {
    "anksioznost": (
        "Preporučujemo svakodnevno izvođenje tehnika dubokog disanja i progresivne mišićne relaksacije kako biste smanjili napetost. "
        "Vođenje dnevnika briga može pomoći u prepoznavanju i racionalizaciji iracionalnih misli. "
        "Preporučuje se i redoviti san, umjerena tjelovježba te ograničavanje unosa kofeina. "
        "Razgovor sa stručnjakom, poput psihologa ili psihoterapeuta, može značajno doprinijeti boljoj kontroli simptoma anksioznosti."
    ),

    "depresija": (
        "Važno je uspostaviti strukturu dana i izbjegavati izolaciju. Pokušajte se svakodnevno uključiti u aktivnosti koje su vam nekad bile ugodne, čak i ako trenutno ne osjećate motivaciju. "
        "Redovita tjelovježba i boravak na svježem zraku mogu poboljšati raspoloženje. "
        "Vođenje dnevnika emocija pomaže u prepoznavanju negativnih obrazaca mišljenja. "
        "Potražite pomoć stručnjaka – kognitivno-bihevioralna terapija i/ili farmakološko liječenje može biti vrlo učinkovito."
    ),

    "ADHD": (
        "Za upravljanje simptomima ADHD-a preporučuje se uspostavljanje jasne dnevne rutine s vremenskim blokovima i podsjetnicima. "
        "Korištenje vizualnih planera i razbijanje zadataka u manje cjeline olakšava organizaciju. "
        "Tehnike samoregulacije, poput mindfulness meditacije, mogu pomoći kod impulzivnosti. "
        "Savjetovanje sa stručnjakom za mentalno zdravlje, a po potrebi i farmakološka terapija, važan su dio potpore osobama s ADHD-om."
    ),

    "stres": (
        "Ako osjećate visoku razinu stresa, važno je naučiti tehnike upravljanja, poput svjesnog disanja, meditacije i tehnika opuštanja. "
        "Redovita tjelesna aktivnost i zdrav stil života (san, prehrana) izravno utječu na otpornost prema stresu. "
        "Identificirajte izvore stresa i razmislite o mogućnostima delegiranja obaveza. "
        "Razgovor s terapeutom može vam pomoći u boljem razumijevanju vlastitih emocionalnih reakcija i strategija suočavanja."
    ),

    "bipolarni_poremecaj": (
    "Upravljanje bipolarni poremećaj zahtijeva kombinaciju farmakološkog liječenja i psihoterapije. "
    "Važno je redovito uzimati propisane lijekove i pratiti promjene raspoloženja kako bi se spriječile epizode manije i depresije. "
    "Vođenje dnevnika raspoloženja može pomoći u prepoznavanju okidača i ranih znakova promjena. "
    "Održavanje stabilne dnevne rutine, uključujući redoviti san i uravnoteženu prehranu, ključni su za stabilnost. "
    "Psihoterapijske metode poput kognitivno-bihevioralne terapije, psihoedukacije i podrške obitelji značajno doprinose kvaliteti života. "
    "Važno je održavati blisku suradnju sa stručnjacima mentalnog zdravlja te uključiti obitelj u podršku i edukaciju."
),

    "nema_poremecaja": (
        "Prema rezultatima, trenutno nema znakova značajnog psihičkog poremećaja. "
        "Ipak, važno je i dalje njegovati mentalno zdravlje. Preporučujemo održavanje uravnoteženog načina života: dovoljno sna, zdrava prehrana, fizička aktivnost i njegovanje društvenih odnosa. "
        "Povremena introspekcija i otvoren razgovor o osjećajima pomažu u prevenciji stresa i očuvanju dobrobiti."
    )
}
     return preporuke.get(poremecaj, "Trenutno nemamo specifične preporuke za ovaj poremećaj.")

@login_required
def rezultati_testa(request):
    try:
        test = PsiholoskiTest.objects.filter(user=request.user).latest('datum')
    except PsiholoskiTest.DoesNotExist:
        return redirect('testovi')

    rezultat = test.ukupni_rezultat()
    threshold = 10

    if rezultat < threshold:
        stanje = "Nema znakova psihičkog poremećaja."
        test.predikcija = "nema_poremecaja"
        preporuka = preporuka_za_poremecaj(test.predikcija)
        postotak = None
        test.save()
    else:
        # Priprema podataka za model
        X = np.array([[getattr(test, f'q{i}') for i in range(1, 31)]])
        model, label_encoder = load_model()

        # Dobivanje predikcije
        predikcija_raw = model.predict(X)[0]
        predikcija = label_encoder.inverse_transform([predikcija_raw])[0]

        # Računanje postotka sigurnosti
        if hasattr(model, 'predict_proba'):
            proba = model.predict_proba(X)[0]
            try:
                index = list(model.classes_).index(predikcija_raw)
                postotak = round(proba[index] * 100, 2)
            except ValueError:
                postotak = None
        else:
            postotak = None

        test.predikcija = predikcija
        preporuka = preporuka_za_poremecaj(predikcija)

        stanje = f"Model je procijenio da se najvjerojatnije radi o: {predikcija.replace('_', ' ')}."
        test.save()

    return render(request, "rezultati.html", {
        "rezultat": rezultat,
        "stanje": stanje,
        "test": test,
        "preporuka": preporuka,
        "postotak": postotak,
    })


@login_required
def pregled_upitnika(request, test_id):
    pitanja = {
        1: "Imate li problema s koncentracijom?",
        2: "Osjećate li se često bezvoljno?",
        3: "Imate li poteškoća sa spavanjem?",
        4: "Osjećate li se tjeskobno bez jasnog razloga?",
        5: "Teško vam je donijeti odluke?",
        6: "Osjećate li se iscrpljeno većinu dana?",
        7: "Imate li osjećaj da ništa nema smisla?",
        8: "Često se osjećate napeto ili pod stresom?",
        9: "Zaboravljate važne stvari češće nego prije?",
        10: "Imate li potrebu često provjeravati jeste li nešto napravili (npr. zaključali vrata)?",
        11: "Osjećate li ubrzan rad srca bez fizičkog napora?",
        12: "Često odgađate zadatke koje trebate obaviti?",
        13: "Imate li problema s organizacijom vremena?",
        14: "Osjećate se nesigurno u svakodnevnim situacijama?",
        15: "Imate li česte promjene raspoloženja?",
        16: "Imate osjećaj da drugi ne razumiju kroz što prolazite?",
        17: "Izbjegavate društvene situacije?",
        18: "Imate li napade panike?",
        19: "Imate li osjećaj da gubite kontrolu nad svojim mislima?",
        20: "Osjećate se emocionalno iscrpljeno?",
        21: "Imate problema s motivacijom?",
        22: "Često kritizirate sami sebe?",
        23: "Imate osjećaj da se ne možete opustiti?",
        24: "Imate li poteškoća s praćenjem razgovora ili predavanja?",
        25: "Osjećate li se izolirano od drugih ljudi?",
        26: "Imate probleme s pamćenjem novijih informacija?",
        27: "Imate li osjećaj unutarnjeg nemira?",
        28: "Imate smanjen interes za aktivnosti koje ste nekad voljeli?",
        29: "Imate poteškoća s izražavanjem emocija?",
        30: "Imate osjećaj da vaš život nema smisla?"
    }

    odgovori_tekst = {
        0: "Nikada",
        1: "Rijetko",
        2: "Često",
        3: "Gotovo stalno"
    }

    test = get_object_or_404(PsiholoskiTest, id=test_id)

    # Pripremi listu pitanja i odgovora za template
    pitanja_i_odgovori = []
    for i in range(1, 31):
        pitanje = pitanja[i]
        odgovor_kod = getattr(test, f'q{i}')
        odgovor_tekst = odgovori_tekst.get(odgovor_kod, "Nepoznat odgovor")
        pitanja_i_odgovori.append((pitanje, odgovor_tekst))

    context = {
        'test': test,
        'pitanja_i_odgovori': pitanja_i_odgovori,
    }

    return render(request, 'pregled_upitnika.html', context)


def is_lijecnik(self):
    return Lijecnik.objects.filter(user=self).exists()

User.add_to_class("is_lijecnik", property(is_lijecnik))


@require_POST
@login_required
def kontaktiraj_klijenta(request, user_id):
    if not Lijecnik.objects.filter(user=request.user).exists():
        return HttpResponseForbidden("Samo liječnici mogu kontaktirati korisnike.")
    
    klijent = get_object_or_404(User, pk=user_id)
    poruka = f"Liječnik {request.user.username} želi stupiti u kontakt s Vama u vezi mentalnog zdravlja."
    Notifikacija.objects.create(korisnik=klijent, poruka=poruka, lijecnik=request.user)
    messages.success(request, f"Notifikacija je poslana korisniku {klijent.username}.")
    return redirect('pronadi_klijente')




def notifikacije_view(request):
    korisnik = request.user

    if hasattr(korisnik, 'lijecnik'):
        notifikacije_qs = Notifikacija.objects.filter(korisnik=korisnik)
    else:
        notifikacije_qs = Notifikacija.objects.filter(korisnik=korisnik)

    latest_dates = (
        notifikacije_qs
        .values('lijecnik')
        .annotate(latest_datum=Max('datum'))
    )

    notifikacije = []
    for entry in latest_dates:
        najnovija = notifikacije_qs.filter(
            korisnik=korisnik,
            lijecnik=entry['lijecnik'],
            datum=entry['latest_datum']
        ).first()
        if najnovija:
            notifikacije.append(najnovija)

    return render(request, 'notifikacije.html', {'notifikacije': notifikacije})


@login_required
def chat_s_lijecnikom(request, lijecnik_id):
    korisnik = request.user
    lijecnik = get_object_or_404(User, id=lijecnik_id)

    if request.method == 'POST':
        poruka = request.POST.get('poruka')
        if poruka:
            ChatPoruka.objects.create(
                posiljalac=korisnik,
                primalac=lijecnik,
                tekst=poruka
            )
            
            if not Lijecnik.objects.filter(user=korisnik).exists():
                notifikacija_poruka = f"Korisnik {korisnik.username} Vam je poslao novu poruku."
                Notifikacija.objects.create(
                    korisnik=lijecnik,
                    poruka=notifikacija_poruka,
                    lijecnik=korisnik 
                )
            return redirect('chat_s_lijecnikom', lijecnik_id=lijecnik_id)

    poruke = ChatPoruka.objects.filter(
        (Q(posiljalac=korisnik) & Q(primalac=lijecnik)) |
        (Q(posiljalac=lijecnik) & Q(primalac=korisnik))
    ).order_by('vreme')

    return render(request, 'chat.html', {
        'poruke': poruke,
        'lijecnik': lijecnik
    })


@login_required
def chat_s_klijentom(request, klijent_id):
    lijecnik = request.user
    klijent = get_object_or_404(User, id=klijent_id)

    if not Lijecnik.objects.filter(user=lijecnik).exists():
        return HttpResponseForbidden("Nemate pristup ovom chatu.")

    if request.method == 'POST':
        poruka = request.POST.get('poruka')
        if poruka:
            ChatPoruka.objects.create(
                posiljalac=lijecnik,
                primalac=klijent,
                tekst=poruka
            )
            Notifikacija.objects.create(
                korisnik=klijent,
                poruka=f"Liječnik {lijecnik.username} vam je poslao novu poruku.",
                lijecnik=lijecnik
            )
            return redirect('chat_s_klijentom', klijent_id=klijent_id)

    poruke = ChatPoruka.objects.filter(
        (Q(posiljalac=lijecnik) & Q(primalac=klijent)) |
        (Q(posiljalac=klijent) & Q(primalac=lijecnik))
    ).order_by('vreme')

    return render(request, 'chat.html', {
        'poruke': poruke,
        'korisnik': klijent,
        'lijecnik': lijecnik,
    })
