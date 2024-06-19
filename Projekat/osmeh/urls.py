from django.contrib import admin
from django.urls import path
from .views import *

urlpatterns = [

    # ====================Pavlovic===================
    path('doktorTermini/', aktivniTerminiDoktor, name='doctorsTerms'),
    path('doktorZavrsavanjeTermina/', statusZavrsen, name='endStatus'),
    path('doktorOtkazivanjeTermina/', statusOtkazan, name='cancelStatus'),
    path('doktorIstorija/', doktorIstorijaRezervacija, name='doctorHistory'),
    path('registrujNovogDoktora/', registracijaDoktora, name='registracijaDoktora'),
    path('sviDoktori/', pregledSvihDoktora, name='pregledSvihDok'),

    # ====================Pantovic======================
    path('pacijentiRezervacije/', rezervacijePacijent, name='pacijentiRezervacije'),
    path('istorijaPacijent/', istorijaPacijent, name='istorijaPacijent'),
    path('profilKorisnika/', profilKorisnika,
         name='profilKorisnika'),
    path('izmenaNalogaPacijentDoktor/', izmenaNalogaPacijentDoktor,
         name='izmenaNalogaPacijentDoktor'),
    path('izmenaSifrePacijentDoktor/', izmenaSifrePacijentDoktor,
         name='izmenaSifrePacijentDoktor'),
    path('izmenaSlikePacijentDoktor/', izmenaSlikePacijentDoktor,
         name='izmenaSlikePacijentDoktor'),
    path('izmena/', izmena,
         name='izmena'),
    path('otkazivanjeTerminaPacijent/<int:id_termina>', otkazivanjeTerminaPacijent,
         name='otkazivanjeTerminaPacijent'),
    path('deaktivacijaNalogaPacijentDoktor/', deaktivacijaNalogaPacijentDoktor,
         name='deaktivacijaNalogaPacijentDoktor'),
    path('lekarBiografija/<int:id_lekara>', lekarBiografija, name='lekarBiografija'),
    path('izmenaAdmin/', izmenaAdmin, name='izmenaAdmin'),
    path('izmenaNalogaAdmin/', izmenaNalogaAdmin, name='izmenaNalogaAdmin'),
    # ====================Adzic======================
    path('pregledOrdinacija/', pregledOrdinacija, name='pregledOrdinacija'),
    path('uredjivanjeOrdinacija/<int:ordinacija_id>', uredjivanjeOrdinacija, name='uredjivanjeOrdinacija'),
    path('dodavanjeOrdinacije/', dodavanjeOrdinacije, name='dodavanjeOrdinacije'),
    path('uslugeIcene/', uslugeIcene, name='uslugeIcene'),
    path('dodavanjeUslugeIcene/', dodavanjeUsluge, name='dodavanjeUsluge'),
    path('izmenaUsluge/<int:usluga_id>', izmenaUsluge, name='izmenaUsluge'),
    path('pregledKorisnika/', pregledKorisnika, name='pregledKorisnika'),
    path('brisanjeKorisnika/<int:korisnik_id>', brisanjeKorisnika, name='brisanjeKorisnika'),
    # ====================Glisic=======================
    path('', index, name='index'),
    path('login/', login_req, name="login"),
    path('logout/', logout_req, name='logout'),
    path('register/', register_req, name='register'),
    path('registerMethod/', register_user, name='registerMethod'),
    path('termin/', zakazi_termin, name='termin'),
    path('terminZakazivanje/', zakazivanje, name='terminZakazivanje'),
    path('kontakt/', kontakt, name='kontakt')

]

# ovde dodajemo urls za apliakicju
# svako pise ispod svog imena
