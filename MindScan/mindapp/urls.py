from django.urls import path
from . import views

urlpatterns = [
    path('assessment/', views.assessment_view, name='assessment'),
    path('poremecaj/anksioznost/', views.anksioznost_view, name='anksioznost'),
    path('poremecaj/depresija/', views.depresija_view, name='depresija'),
    path('poremecaj/stres/', views.stres_view, name='stres'),
    path('poremecaj/adhd/', views.adhd_view, name='adhd'),
    path('poremecaj/kvaliteta/', views.kvaliteta_view, name='kvaliteta'),
    path('testovi/', views.testovi, name='testovi'),
    path('pronadi-klijente/', views.pronadi_klijente, name='pronadi_klijente'),
    path('profil/', views.profil_view, name='profil'),
    path('uredi-profil/', views.uredi_profil_view, name='uredi_profil'),
    path('rezultati/', views.rezultati_testa, name='rezultati_testa'),
    path('rezultati/<int:test_id>/', views.pregled_upitnika, name='pregled_upitnika'),
    path('pronadi-klijente/', views.pronadi_klijente, name='pronadi_klijente'),
    path('kontaktiraj/<int:user_id>/', views.kontaktiraj_klijenta, name='kontaktiraj_klijenta'),
    path('notifikacije/', views.notifikacije_view, name='notifikacije'),
    path('chat/<int:lijecnik_id>/', views.chat_s_lijecnikom, name='chat_s_lijecnikom'),
    path('chat/klijent/<int:klijent_id>/', views.chat_s_klijentom, name='chat_s_klijentom'),

]
