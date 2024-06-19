# Stevan Adžić 2019/0477
# Pozivanje funkcije za popunjavanje baze:
# >>>from db_init import init #db_init je u istoj putanji kao i manage.py
# >>>init()
# >>>exit()
from datetime import datetime

from django.contrib.auth.models import Permission

from osmeh.models import *
import random
from django.utils.crypto import get_random_string

def init():
    imena = {'Ana': 'F', 'Miloš': 'M', 'Jovana': 'F', 'Marko': 'M', 'Jelena': 'F', 'Nikola': 'M',
             'Aleka': 'M', 'Dragan': 'M', 'Mirko': 'M', 'Snežana': 'F', 'Ljijana' : 'F'}
    prezimena = {'Ana': 'Anić', 'Miloš': 'Mikić', 'Jovana': 'Petrović', 'Marko': 'Marić', 'Jelena': 'Filipović', 'Nikola': 'Mišić',
                 'Aleka': 'Popović', 'Dragan': 'Jocić', 'Mirko': 'Radović', 'Snežana': 'Pavlović', 'Ljijana' : 'Mitić', 'Ljubica': 'Cvetić'}
    lista_imena = list(imena.keys())
    mesta = ["Beograd", "Novi Sad", "Kragujevac"]
    adr = ["Narodnog fronta 11", "Bulevar kralja Aleksandra 12", "Francuska 66", "Bulevar umetnosti 1", ]
    usluge = [
        {
            'naziv': 'Preventivni pregled',
            'opis': 'Kompletna procena oralnog zdravlja i saveti za održavanje oralne higijene.',
            'cena': 2000
        },
        {
            'naziv': 'Plomba',
            'opis': 'Popunjavanje zuba kompozitnim materijalom za obnovu oštećenog zuba.',
            'cena': 5000
        },
        {
            'naziv': 'Oralna hirurgija',
            'opis': 'Hirurške intervencije kao što su vađenje umnjaka ili implantacija zuba.',
            'cena': 10000
        },
        {
            'naziv': 'Izbeljivanje zuba',
            'opis': 'Postupak kojim se posvetljuju prirodni zubi radi poboljšanja izgleda osmeha.',
            'cena': 8000
        },
        {
            'naziv': 'Parcijalna proteza',
            'opis': 'Protetički nadomestak za izgubljene zube koji se pričvršćuje na preostale zube.',
            'cena': 15000
        },
        {
            'naziv': 'Krunica',
            'opis': 'Protetički nadomestak koji se postavlja na oštećeni zub kako bi se obnovila njegova funkcija i izgled.',
            'cena': 12000
        },
        {
            'naziv': 'Ortodoncija',
            'opis': 'Korekcija nepravilnosti zuba i vilica pomoću fiksnih ili mobilnih aparatića.',
            'cena': 25000
        }
    ]
    admin = Korisnik.objects.create_superuser(username='admin', email='admin@osmeh.rs', password='123')
    admin.first_name = 'Administrator'
    admin.save()
    adminBaza = Admninistrator(idadmin=admin)
    adminBaza.save()

    # kreiranje korisnika
    for i in range(len(lista_imena)):
        email = f'{lista_imena[i].lower()}@osmeh.rs'
        username = email
        password = "123"
        jmbg = get_random_string(length=13, allowed_chars='1234567890')
        pol = imena[lista_imena[i]]
        brtelefona = "06" + get_random_string(length=8, allowed_chars='1234567890')
        korisnik = Korisnik.objects.create_user(username=username, email=email, password=password, jmbg=jmbg,
                                                pol=pol, brtelefona=brtelefona)
        korisnik.first_name = lista_imena[i]
        korisnik.last_name = prezimena[lista_imena[i]]
        korisnik.save()

    # kreiranje ordinacija
    for i in range(5):
        if i == 0:
            naziv = "Osmeh++ Centrala"
            centrala = 1
        else:
            naziv = "Osmeh++ " + str(i)
            centrala = 0
        mesto = random.choice(mesta)
        adresa = random.choice(adr)
        brtelefona = "06" + get_random_string(length=7, allowed_chars='1234567890')

        ordinacija = Ordinacija(naziv=naziv, mesto=mesto, adresa=adresa, brtelefona=brtelefona, centrala=centrala)
        ordinacija.save()

    # kreiranje pacijenata
    korisnici = Korisnik.objects.all()[1:7]
    for korisnik in korisnici:
        pacijent = Pacijent(idpac=korisnik)
        pacijent.save()

    # kreiranje stomatologa
    korisnici = Korisnik.objects.all().order_by('-id')[:5]
    ordinacije = Ordinacija.objects.all()[:5]
    for korisnik, ordinacija in zip(korisnici, ordinacije):
        # biografija = get_random_string(length=100)
        ime = korisnik.first_name + " " +  korisnik.last_name
        biografija = f"{ime} je stručnjak stomatologije sa bogatim iskustvom i širokim spektrom znanja u svim oblastima oralnog zdravlja. Sa svojom ljubaznošću i pažljivim pristupom, Dr. {ime} stvara prijateljsku i udobnu atmosferu za svoje pacijente. Njegova posvećenost kvalitetnoj stomatološkoj nezi i kontinuiranom usavršavanju čini ga pouzdanim izborom za sve dentalne potrebe."
        stomatolog = Stomatolog(idsto=korisnik, biografija=biografija, ordinacija=ordinacija)
        stomatolog.save()

    # Kreiranje usluga
    for usluga in usluge:
        naziv = usluga['naziv']
        opis = usluga['opis']
        cena = usluga['cena']

        novaUsluga = Usluga(naziv=naziv, cena=cena, opis=opis)
        novaUsluga.save()

    # kreiranje rezervacija
    stomatolozi = Stomatolog.objects.all()[:5]
    pacijenti = Pacijent.objects.all()[1:7] # bez admina
    ordinacije = Ordinacija.objects.all()[:5]
    usluge = Usluga.objects.all()[:7]

    # for stomatolog, pacijent, ordinacija, usluga in zip(stomatolozi, pacijenti, ordinacije, usluge):
    #     datum = datetime.now()
    #     vreme = random.randint(1, 10)
    #     status = random.choice(['Zakazano', 'Otkazano'])
    #
    #     rezervacija = Rezervacija(
    #         stomatolog=stomatolog,
    #         pacijent=pacijent,
    #         ordinacijarez=ordinacija,
    #         usluga=usluga,
    #         datum=datum,
    #         vreme=vreme,
    #         status=status
    #     )
    #     rezervacija.save()

    for x in range(10):
        datum = datetime.now()
        vreme = random.randint(1, 10)
        status = random.choice(['Zakazano', 'Otkazano'])
        stom = random.choice(stomatolozi)
        pac = random.choice(pacijenti)
        ord = random.choice(ordinacije)
        usl = random.choice(usluge)
        rezervacija = Rezervacija(
            stomatolog=stom,
            pacijent=pac,
            ordinacijarez=ord,
            usluga=usl,
            datum=datum,
            vreme=vreme,
            status=status
        )
        rezervacija.save()