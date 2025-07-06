from django.db import models
from django.contrib.auth.models import User


class Lijecnik(models.Model):
    IMENA_STRUCNOSTI = [
        ('psihijatar', 'Psihijatar'),
        ('psiholog', 'Psiholog'),
        ('psihoterapeut', 'Psihoterapeut'),
    ]
    user = models.OneToOneField(User, on_delete=models.CASCADE, null=True, blank=True)
    ime = models.CharField(max_length=100)
    prezime = models.CharField(max_length=100)
    email = models.EmailField(unique=False, blank=True, null=True)
    telefon = models.CharField(max_length=20, blank=True)
    strucnost = models.CharField(max_length=20, choices=IMENA_STRUCNOSTI)
    lokacija = models.CharField(max_length=100, blank=True)
    opis = models.TextField(blank=True, help_text="Kratki opis iskustva ili pristupa liječenju.")
    dostupnost = models.BooleanField(default=True)
    odobren = models.BooleanField(default=False, help_text="Označava je li liječnik verificiran od strane administratora.")
    verifikacijski_dokument = models.FileField(upload_to='verifikacijski_dokumenti/', blank=True, null=True, help_text="Prenesi dokument koji dokazuje kvalifikacije.")

    def __str__(self):
        return f"{self.ime} {self.prezime} ({self.get_strucnost_display()})"


class PsiholoskiTest(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    datum = models.DateTimeField(auto_now_add=True)

    # 30 pitanja – svako jedno polje
    q1 = models.IntegerField()
    q2 = models.IntegerField()
    q3 = models.IntegerField()
    q4 = models.IntegerField()
    q5 = models.IntegerField()
    q6 = models.IntegerField()
    q7 = models.IntegerField()
    q8 = models.IntegerField()
    q9 = models.IntegerField()
    q10 = models.IntegerField()
    q11 = models.IntegerField()
    q12 = models.IntegerField()
    q13 = models.IntegerField()
    q14 = models.IntegerField()
    q15 = models.IntegerField()
    q16 = models.IntegerField()
    q17 = models.IntegerField()
    q18 = models.IntegerField()
    q19 = models.IntegerField()
    q20 = models.IntegerField()
    q21 = models.IntegerField()
    q22 = models.IntegerField()
    q23 = models.IntegerField()
    q24 = models.IntegerField()
    q25 = models.IntegerField()
    q26 = models.IntegerField()
    q27 = models.IntegerField()
    q28 = models.IntegerField()
    q29 = models.IntegerField()
    q30 = models.IntegerField()

    predikcija = models.CharField(max_length=50, default="Nema poremećaja")

    def ukupni_rezultat(self):
        return sum([getattr(self, f'q{i}') for i in range(1, 31)])
    

class Ponuda(models.Model):
    lijecnik = models.ForeignKey(User, on_delete=models.CASCADE, related_name='poslane_ponude')
    klijent = models.ForeignKey(User, on_delete=models.CASCADE, related_name='primljene_ponude')
    datum = models.DateTimeField(auto_now_add=True)
    poruka = models.TextField()

    def __str__(self):
        return f'Ponuda od {self.lijecnik.username} za {self.klijent.username}'
    
class Notifikacija(models.Model):
    korisnik = models.ForeignKey(User, on_delete=models.CASCADE, related_name='notifikacije')
    poruka = models.TextField()
    procitano = models.BooleanField(default=False)
    datum = models.DateTimeField(auto_now_add=True)
    lijecnik = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True) 

    def __str__(self):
        return f"Notifikacija za {self.korisnik.username}"


class ChatPoruka(models.Model):
    posiljalac = models.ForeignKey(User, on_delete=models.CASCADE, related_name='poslane_poruke')
    primalac = models.ForeignKey(User, on_delete=models.CASCADE, related_name='primljene_poruke')
    tekst = models.TextField()
    vreme = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f'{self.posiljalac} ➤ {self.primalac}: {self.tekst[:20]}'


class Pacijent(User):
    class Meta:
        proxy = True
        verbose_name = 'Pacijent'
        verbose_name_plural = 'Pacijenti'

class Profil(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    datum_rodenja = models.DateField(null=True, blank=True)

    def __str__(self):
        return f"{self.user.username} – Profil"