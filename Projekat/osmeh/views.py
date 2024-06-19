from django.db.models import ProtectedError
from django.shortcuts import render, redirect
from django.http import HttpRequest, HttpResponse
from .models import *

from django.contrib.auth.decorators import login_required, permission_required, user_passes_test
from django.contrib.auth.forms import AuthenticationForm, UserCreationForm

from django.contrib.auth import authenticate
from django.contrib import messages

from templates import *
from django.contrib.auth.models import Group
import re  # Za regularne izraze u pajtonu


# Create your views here.

# Svako pise ispod svog imena
# ====================Pavlovic===================
@login_required(login_url='login')
@user_passes_test(lambda u: u.stomatolog)
def aktivniTerminiDoktor(request: HttpRequest):
    '''
    aktivniTerminiDoktor je funkcija koja sluzi za prikaz aktivnih rezervacija kod doktora
    kada se ucita stranica ispisuje sve rezervacije koje su zakazane sortirane po datumu
    kad se popuni forma za datum izbacuje samo za taj datum
    permisije - da moze da menja stomatologa (da je ili stomatolog ili admin)
    :param request:
    :return:
    '''
    username = request.user.username
    if request.method == 'GET':
        rezervacije = Rezervacija.objects.filter(stomatolog__idsto__username__exact=username,
                                                 status__exact='Zakazano').order_by('datum')
    else:
        datum = request.POST['datum']
        rezervacije = Rezervacija.objects.filter(stomatolog__idsto__username__exact=username, datum__contains=datum,
                                                 status__exact='Zakazano').order_by('vreme')
    context = {
        'rezervacije': rezervacije
    }
    return render(request, 'stranice/aktivniTerminiDoktor.html', context)


@login_required(login_url='login')
# @permission_required('osmeh.change_stomatolog', raise_exception=True)
def statusOtkazan(request: HttpRequest):
    '''
    pomocna funkcija koja prebacuje status rezervacije u Otkazan
    :param request:
    :return:
    '''
    if request.method == 'POST':
        idRez = request.POST.get('rezervacija')
        if idRez:
            rez = Rezervacija.objects.get(pk=idRez)
            rez.status = 'Otkazano'
            rez.save()
    return redirect('doctorsTerms')


@login_required(login_url='login')
# @permission_required('osmeh.change_stomatolog', raise_exception=True)
@user_passes_test(lambda u: u.stomatolog)
def statusZavrsen(request: HttpRequest):
    '''
    pomocna funkcija koja prebacuje status rezervacije u Zavrsen
    :param request:
    :return:
    '''
    if request.method == 'POST':
        idRez = request.POST.get('rezervacija')
        if idRez:
            rez = Rezervacija.objects.get(pk=idRez)
            rez.status = 'Zavrseno'
            rez.save()
    return redirect('doctorsTerms')


@login_required(login_url='login')
@user_passes_test(lambda u: u.stomatolog)
def doktorIstorijaRezervacija(request: HttpRequest):
    '''
    ispisuje sve rezervacije koje imaju status Zavrsen ili Otkazan
    :param request:
    :return:
    '''
    username = request.user.username
    rezervacije = Rezervacija.objects.filter(stomatolog__idsto__username__exact=username,
                                             status__in=['Otkazano', 'Zavrseno']).order_by('-datum')
    context = {
        'rezervacije': rezervacije
    }
    return render(request, 'stranice/istorijaTerminaDoktor.html', context)


@login_required(login_url='login')
@user_passes_test(lambda u: u.is_superuser)
def registracijaDoktora(request: HttpRequest):
    '''
    ova funkcija sluzi za registrovanje doktora
    kada se ucita (GET zahtev) ona ispisuje formu za registrovanje
    formi se prosledjuju objekti svih ordinacija da bi mogla da se izabere gde ce doktor raditi
    kada se submit-uje forma kupe se vrednosti iz forme preko POST zahteva, proveravaju
    se vrednosti da li su validne, dodaju se u korisnika koji se dodaje
    u novog stomatologa, i korisnik(koji je dodat u stomatologa) se
    :param request:
    :return:
    '''
    sve_lokacije = Ordinacija.objects.all()
    if request.method == 'POST':
        # Uzimaje vrednosti polja i proveravanja da li su uneta i da li su validna
        ime = request.POST['name']
        if ime == "":
            messages.error(request, "Ime nije uneto\n")
            return redirect('registracijaDoktora')

        prezime = request.POST['surname']
        if prezime == "":
            messages.error(request, "Prezime nije uneto\n")
            return redirect('registracijaDoktora')

        email = request.POST['email']
        if email == "":
            messages.error(request, "Email nije unet\n")
            return redirect('registracijaDoktora')
        # Ako je mejl vec zauzet
        zauzeto = Korisnik.objects.filter(email=email)
        if zauzeto:
            messages.error(request, "Mejl adresa je vec u upotrebi\n")
            return redirect('registracijaDoktora')
        x = re.search("^[a-z0-9]*[@]\w+[.]\w{2,3}$", email)
        if not x:
            messages.error(request,
                           "Mejl pogresan format. Ocekivan format <rec proizvoljne duzine>@<rec proizvoljne duzine><rec duzine 2 ili 3 slova> \n")
            return redirect('registracijaDoktora')

        lozinka = request.POST['password']
        potvrda = request.POST['confirm-password']
        if lozinka =="":
            messages.error(request, "Lozinka nije uneta")
            return redirect('registracijaDoktora')
        if potvrda == "":
            messages.error(request, "Potvrda lozinke nije uneta")
            return redirect('registracijaDoktora')

        if lozinka != potvrda:
            messages.error(request, "Lozinke se ne podudaraju")
            return redirect('registracijaDoktora')

        telefon = request.POST['phoneNumber']
        x = re.search("^\d{9,10}$", telefon)
        if not x:
            messages.error(request, "Telefon mora biti najmanje 9 a najvise 10 cifara. Primer: 060 321321\n")
            return redirect('registracijaDoktora')

        pol = request.POST['sex']
        ime_ordinacije = request.POST['lokacija']
        lokacija = Ordinacija.objects.get(naziv__exact=ime_ordinacije)
        # lokacija = Ordinacija.objects.get(mesto__exact='Beograd') #request.POST['lokacija']
        biografija = request.POST['biografija']

        # pravljenje samog korisnika
        noviKorisnik = Korisnik()
        noviKorisnik.first_name = ime
        noviKorisnik.last_name = prezime
        noviKorisnik.username = email
        noviKorisnik.email = email
        noviKorisnik.set_password(lozinka)
        # noviKorisnik.password = lozinka
        noviKorisnik.brtelefona = telefon
        noviKorisnik.pol = pol
        # Cuvamo korisnika
        noviKorisnik.save()

        # pravimo doktora i dodajemo ga
        noviStomatolog = Stomatolog()
        noviStomatolog.idsto = noviKorisnik
        noviStomatolog.biografija = biografija
        noviStomatolog.ordinacija = lokacija
        noviStomatolog.save()

        return redirect('index')
    context = {
        'ordinacije': sve_lokacije
    }
    return render(request, 'stranice/registrujDoktora.html', context)


def pregledSvihDoktora(request: HttpRequest):
    '''
    ispisuje sve doktore
    Ako je usao admin, on ima dugme za dodavanje doktora koje se nalazi u formi
    kada se forma submit-uje dobija se POST zahtev koji salje na stranicu za registraciju doktora
    :param request:
    :return:
    '''
    if request.method == 'GET':
        doktori = Stomatolog.objects.all()
        context = {
            'sviDoktori': doktori
        }
        return render(request, 'stranice/pregledDoktora.html', context)
    else:
        return redirect('registracijaDoktora')


# ====================Pantovic======================

@login_required(login_url='login')
@user_passes_test(lambda u: u.pacijent)
def rezervacijePacijent(request: HttpRequest):
    '''
    Funcija salje zahtev za prikazivanje aktivnih rezervacija pacijenta
    Odlazi se na stranicu aktivniTermini.html
    :param request:
    :return:
    '''

    # res = Rezervacija.objects.filter(pacijent__idpac=request.user.id)
    res = Rezervacija.objects.filter(pacijent__idpac=request.user.id,
                                     status__exact='Zakazano').order_by('datum')
    context = {
        "rezervacije": res
    }
    return render(request, 'stranice/aktivniTermini.html', context)


@login_required(login_url='login')
@user_passes_test(lambda u: u.pacijent)
def istorijaPacijent(request: HttpRequest):
    '''
    Funcija salje zahtev za prikazivanje neaktiivnih rezervacija pacijenta
    Odlazi se na stranicu istorijaTermini.html
    :param request:
    :return:
    '''
    # res = Rezervacija.objects.filter(pacijent__idpac=request.user.id)
    res = Rezervacija.objects.filter(pacijent__idpac=request.user.id,
                                     status__in=['Otkazano', 'Zavrseno']).order_by('-datum')
    context = {
        "rezervacije": res
    }
    return render(request, 'stranice/istorijaTermini.html', context)


@login_required(login_url='login')
@user_passes_test(lambda u: not u.is_superuser)
def izmena(request: HttpRequest):
    '''
    Funcija salje zahtev za izmenu naloga
    Odlazi se na stranicu izmenaProfila.html
    :param request:
    :return:
    '''
    context = {

    }
    return render(request, 'stranice/izmenaProfila.html', context)


@login_required(login_url='login')
@user_passes_test(lambda u: u.is_superuser)
def izmenaAdmin(request: HttpRequest):
    '''
    Funcija salje zahtev za izmenu naloga admina
    Odlazi se na stranicu izmenaProfilaAdmin.html
    :param request:
    :return:
    '''
    context = {

    }
    return render(request, 'stranice/izmenaProfilaAdmin.html', context)


@login_required(login_url='login')
@user_passes_test(lambda u: not u.is_superuser)
def izmenaNalogaPacijentDoktor(request: HttpRequest):
    '''
    Funcija za izmenu imena,prezimena,emaila,telefona(Pacijent) i biografije(Stomatolog)
    U slucaju greske se ostaje na istoj stranici, u suprotnom se odlazi na stranicu naloga korisnika
    :param request:
    :return:
    '''
    ime = request.POST['name']
    prezime = request.POST['surname']
    email = request.POST['email']

    korisnik = request.user

    if hasattr(korisnik, 'pacijent'):
        telefon = request.POST['phoneNumber']
    elif hasattr(korisnik, 'stomatolog'):
        biografija = request.POST['information']

    if (korisnik.email == email and korisnik.last_name == prezime and korisnik.first_name == ime and (
            (hasattr(korisnik, 'pacijent') and korisnik.brtelefona == telefon) or (
            hasattr(korisnik, 'stomatolog') and korisnik.stomatolog.biografija == biografija))):
        messages.error(request, 'Niste promenili podatke')
        return redirect('izmena')

    if korisnik.email != email:
        postoji = Korisnik.objects.filter(email=email)
        if postoji:
            messages.error(request, 'Unet email je zauzet')
            return redirect('izmena')
        reg = re.search("^[a-z0-9]*[@]\w+[.]\w{2,3}$", email)
        if not reg:
            messages.error(request,
                           'Mejl pogresan format. Ocekivan format <rec proizvoljne duzine>@<rec proizvoljne duzine>.<rec duzine 2 ili 3 slova>')
            return redirect('izmena')
        korisnik.email = email
        korisnik.username = email
    korisnik.first_name = ime
    korisnik.last_name = prezime
    if hasattr(korisnik, 'pacijent'):
        tel = re.search("^\d{9,10}$", telefon)
        if not tel:
            messages.error(request, "Telefon mora biti najmanje 9 a najvise 10 cifara. Primer: 060321321\n")
            return redirect('izmena')
        korisnik.brtelefona = telefon
    elif hasattr(korisnik, 'stomatolog'):
        korisnik.stomatolog.biografija = biografija
        korisnik.stomatolog.save()

    korisnik.save()
    return redirect('profilKorisnika')


@login_required(login_url='login')
def izmenaSifrePacijentDoktor(request: HttpRequest):
    '''
    Funckija za izmenu lozinke pacijenta ili stomatologa
    U slucaju greske se ostaje na istoj stranici, u suprotnom se odjavljuje i odlazi na index stranicu
    :param request:
    :return:
    '''
    lozinka = request.POST['password']
    potvrda = request.POST['confirm-password']

    if (lozinka != potvrda):
        messages.error(request, 'Lozinka i njena potvrda se ne poklapaju')
        if request.user.is_superuser:
            return redirect('izmenaAdmin')
        return redirect('izmena')
    pass

    user = Korisnik.objects.get(username=request.user.username)
    user.set_password(lozinka)
    user.save()
    return redirect('index')


@login_required(login_url='login')
@user_passes_test(lambda u: not u.is_superuser)
def izmenaSlikePacijentDoktor(request: HttpRequest):
    '''
    Funkcija za izmenu ili postavljanje slike Pacijenta ili Stomatologa
    Korisniku se menja slika i vraca se na Moj profil
    :param request:
    :return:
    '''
    slika = request.FILES['picture']
    user = request.user
    user.pfp = slika
    user.save()
    return redirect('profilKorisnika')


@login_required(login_url='login')
@user_passes_test(lambda u: u.is_superuser)
def izmenaNalogaAdmin(request: HttpRequest):
    '''
    Funkcija za izmenu naloga admina
    Ukoliko je uneta forma validna vraca se na index stranicu, a ako nije ostaje na stranici sa porukom greske
    :param request:
    :return:
    '''
    ime = request.POST['name']
    email = request.POST['email']
    korisnik = request.user

    if (korisnik.email == email and korisnik.first_name == ime):
        messages.error(request, 'Niste promenili podatke')
        return redirect('izmenaAdmin')

    if korisnik.email != email:
        postoji = Korisnik.objects.filter(email=email)
        if postoji:
            messages.error(request, 'Unet email je zauzet')
            return redirect('izmenaAdmin')
        reg = re.search("^[a-z0-9]*[@]\w+[.]\w{2,3}$", email)
        if not reg:
            messages.error(request,
                           'Mejl pogresan format. Ocekivan format <rec proizvoljne duzine>@<rec proizvoljne duzine>.<rec duzine 2 ili 3 slova>')
            return redirect('izmenaAdmin')
        korisnik.email = email
        korisnik.username = email
    korisnik.first_name = ime

    korisnik.save()
    return redirect('index')


def lekarBiografija(request: HttpRequest, id_lekara):
    '''
    Funkcija za dohvatanje Stomatologa da bi se ispisali njegovi podaci u htmlu lekarBiografija.html
    Otvara se stranica lekarBiografija.html
    :param request:
    :param id_lekara:
    :return:
    '''
    doktor = Korisnik.objects.get(pk=id_lekara)
    context = {
        "doc": doktor
    }
    return render(request, 'stranice/lekarBiografija.html', context)


@login_required(login_url='login')
@user_passes_test(lambda u: u.pacijent)
def otkazivanjeTerminaPacijent(request: HttpRequest, id_termina):
    '''
    Funkcija za otkazivanje termina od stane pacijenta
    Ponovo se otvara stranica rezervacija pacijenta
    :param request:
    :param id_termina:
    :return:
    '''
    rezervacija = Rezervacija.objects.get(pk=id_termina)
    rezervacija.status = "Otkazano"
    rezervacija.save()

    return redirect('pacijentiRezervacije')


# Funkcija za brisanje
def deaktivacijaNalogaPacijentDoktor(request: HttpRequest):
    '''
    Funkcija za deaktivaciju naloga pacijenta ili stomatologa
    :param request:
    :return:
    '''
    korisnik = request.user
    # if isinstance(korisnik, Pacijent):
    if hasattr(korisnik, 'pacijent'):
        pacijent = korisnik.pacijent
        pacijent.delete()

    # if isinstance(korisnik, Stomatolog):
    if hasattr(korisnik, 'stomatolog'):
        stomatolog = korisnik.stomatolog
        stomatolog.delete()

    korisnik.delete()
    return redirect('index')


@login_required(login_url='login')
@user_passes_test(lambda u: not u.is_superuser)
def profilKorisnika(request: HttpRequest):
    '''
    Zahtev za ispisivanje informacija o Pacijentu ili Stomatologu
    Otvara se stranica profil.html
    :param request:
    :return:
    '''
    context = {

    }
    return render(request, 'stranice/profil.html', context)


# ====================Adzic======================
@user_passes_test(lambda u: u.is_superuser)
def brisanjeKorisnika(request, korisnik_id):
    '''
    brisanjeKorisnika - funkcija preko kojeg Administrator brise korisnika
                        kome je primarni kljuc = korisnik_id
    :param request:
    :param korisnik_id:
    :return:
    '''
    korisnik = Korisnik.objects.get(pk=korisnik_id)

    if hasattr(korisnik, 'pacijent'):
        pacijent = korisnik.pacijent
        rezervacije = Rezervacija.objects.filter(pacijent=pacijent)
        for res in rezervacije:
            if res.status == "Zakazano":
                res.status = "Otkazano"
                res.save()
        # rezervacije = Rezervacija.objects.filter(pacijent=pacijent)
        # try:
        #     rezervacije.delete()
        # except ProtectedError:
        #     pass
        pacijent.delete()

        # if isinstance(korisnik, Stomatolog):
    if hasattr(korisnik, 'stomatolog'):
        stomatolog = korisnik.stomatolog
        rezervacije = Rezervacija.objects.filter(stomatolog=stomatolog)
        for res in rezervacije:
            if res.status == "Zakazano":
                res.status = "Otkazano"
                res.save()
        # try:
        #     # rezervacije.delete()
        # except ProtectedError:
        #     pass
        stomatolog.delete()

    korisnik.delete()
    return redirect('pregledKorisnika')


@user_passes_test(lambda u: u.is_superuser)
def pregledKorisnika(request):
    '''
    pregledKorisnika - view preko kojeg administrator ima pregled registrovanih korisnika
    :param request:
    :return:
    '''
    korisnici = Korisnik.objects.all()
    context = {
        "korisnici": korisnici
    }
    return render(request, "stranice/pregledKorisnikaAdmin.html", context)


@user_passes_test(lambda u: u.is_superuser)
def izmenaUsluge(request, usluga_id):
    '''
    izmenaUsluge - view funkcija preko koje administrator menja cenu usluge
    :param request:
    :param usluga_id:
    :return:
    '''
    try:
        usluga = Usluga.objects.get(pk=usluga_id)
    except Usluga.DoesNotExist:
        return redirect('uslugeIcene')

    if request.method == 'POST':
        cena = request.POST.get('cena')
        usluga.cena = cena
        usluga.save()
        return redirect('uslugeIcene')

    context = {
        "usluga": usluga
    }
    return render(request, "stranice/izmenaUsluge.html", context)


@user_passes_test(lambda u: u.is_superuser)
def dodavanjeUsluge(request):
    '''
    dodavanjeUsluge - funkcija preko koje administrator dodaje nove usluge
    :param request:
    :return:
    '''
    if request.method == 'POST':
        naziv = request.POST.get('usluga')
        opis = request.POST.get('opis')
        cena = request.POST.get('cena')

        usluga = Usluga(naziv=naziv, opis=opis, cena=cena)

        usluga.save()

        return redirect('uslugeIcene')
    context = {}
    return render(request, "stranice/dodavanjeUsluge.html", context)


def uslugeIcene(request):
    '''
    uslugeIcene - view koji upucuje na stranicu sa tabelom usluga i njihovih
                  cena
    :param request:
    :return:
    '''
    usluge = Usluga.objects.all()
    context = {
        "usluge": usluge
    }
    return render(request, "stranice/uslugeIcene.html", context)


@user_passes_test(lambda u: u.is_superuser)
def dodavanjeOrdinacije(request):
    '''
    dodavanjeOrdinacije - view funkcija koja upucuje administratora na stranicu preko
                          koje moze da doda novu ordinaciju u sistem
    :param request:
    :return:
    '''
    if request.method == 'POST':
        naziv = request.POST.get('ime')
        adresa = request.POST.get('adresa')
        mesto = request.POST.get('mesto')
        telefon = request.POST.get('telefon')

        x = re.search("^\d{9,10}$", telefon)
        if not x:
            messages.error(request, "Telefon mora biti najmanje 9 a najvise 10 cifara. Primer: 060 321321\n")
            return render(request, 'stranice/dodavanjeOrdinacije.html', {})

        ordinacija = Ordinacija(naziv=naziv, adresa=adresa, mesto=mesto, brtelefona=telefon)

        try:
            slika = request.FILES['picture']
            if slika:
                ordinacija.pfp = slika
        except:
            pass

        ordinacija.save()

        return redirect('pregledOrdinacija')

    context = {}
    return render(request, "stranice/dodavanjeOrdinacije.html", context)


@user_passes_test(lambda u: u.is_superuser)
def uredjivanjeOrdinacija(request, ordinacija_id):
    '''
    uredjivanjeOrdinacija - view funkcija koja upucuje administratora na stranicu preko koje
                            uredjuje ordinaciju sa id kljucem = ordinacija_id
    :param request:
    :param ordinacija_id: primarni kljuc
    :return:
    '''
    ordinacija = Ordinacija.objects.get(pk=ordinacija_id)

    if request.method == 'POST':
        action = request.POST.get('action')

        if action == 'izmeni':
            naziv = request.POST.get('ime')
            adresa = request.POST.get('adresa')
            mesto = request.POST.get('mesto')
            telefon = request.POST.get('telefon')

            if naziv:
                ordinacija.naziv = naziv
                ordinacija.adresa = adresa
                ordinacija.mesto = mesto

                x = re.search("^\d{9,10}$", telefon)
                if not x:
                    messages.error(request, "Telefon mora biti najmanje 9 a najvise 10 cifara. Primer: 060 321321\n")
                    return render(request, 'stranice/uredjivanjeOrdinacija.html', {"ordinacija": ordinacija})

                ordinacija.brtelefona = telefon

                try:
                    slika = request.FILES['picture']
                    if slika:
                        ordinacija.pfp = slika
                except:
                    pass

                ordinacija.save()

                return redirect('pregledOrdinacija')

        elif action == 'izbrisi':

            if ordinacija.idordinacija == 1:
                messages.error(request, "Nije moguće obrisati centralu.\n")
                return render(request, 'stranice/uredjivanjeOrdinacija.html', {"ordinacija": ordinacija})

            rezervacije = Rezervacija.objects.filter(ordinacijarez=ordinacija)
            for res in rezervacije:
                if res.status == "Zakazano":
                    res.status = "Otkazano"
                    res.save()
            # try:
            #     rezervacije.delete()
            # except ProtectedError:
            #     pass
            ordinacija.delete()

            return redirect('pregledOrdinacija')

    context = {
        "ordinacija": ordinacija
    }
    return render(request, "stranice/uredjivanjeOrdinacija.html", context)


def pregledOrdinacija(request):
    '''
    pregledOrdinacija - view koji upucuje sve tipove korisnika na stranicu sa pregledom ordinacija
    :param request:
    :return:
    '''
    ordinacije = Ordinacija.objects.all()
    context = {
        "ordinacije": ordinacije
    }
    return render(request, "stranice/pregledOrdinacija.html", context)


# ====================Glisic=======================
from django.contrib.auth import login, logout, authenticate
import json  # Da moze skripti da se posalje JSON fajl


def index(request: HttpRequest):
    '''
    index - view upucuje korisnika na pocetnu stranicu gde bira opciju da se prijavi na sistem ili registruje
    :param request:
    :return redner:
    '''

    context = {

    }
    return render(request, 'stranice/index.html', context)


def login_req(request: HttpRequest):
    '''
    login_req - view koji ce da uloguje korisnika na sistem

    :param HttpRequest:
    :return render:
    '''

    '''
    If koji preko "POST" requesta dohvata informacie iz forme
    '''

    # Proverava ako je bio POST request da uzme informacije iz forme
    if request.method == "POST":
        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(username=username, password=password)
        if user:
            login(request, user)
            return redirect('index')
        else:
            messages.error(request, "Korisnik ne postoji")

    context = {
    }
    return render(request, 'stranice/prijava.html', context)


def register_req(request: HttpRequest):
    '''
    register_req - view koji ce da omoguci korisniku da napravi nalog na sistemu ako ga ne poseduju

    :param HttpRequest:
    :return redner:
    '''

    context = {

    }
    return render(request, 'stranice/registracija.html', context)


def register_user(request: HttpRequest):
    '''
    register_user - view koji regitruje informacije u bazu podataka
    :param request:
    :return redirect:
    '''

    """
    Svakom polju se prover ispravnost vrednosti sa regularnim izrazom
    """
    # Dohvatanje imena
    ime = request.POST['name']
    if ime == "":
        messages.error(request, "Ime nije uneto\n")
        return render(request, 'stranice/registracija.html')

    # Dohvatanje prezimena
    prezime = request.POST['surname']
    if prezime == "":
        messages.error(request, "Prezime nije uneto\n")
        return render(request, 'stranice/registracija.html')

    # Dohvatanje mejla
    email = request.POST['email']
    if email == "":
        messages.error(request, "Email nije unet\n")
        return render(request, 'stranice/registracija.html')

    # Ako je mejl vec zauzet
    zauzeto = Korisnik.objects.filter(email=email)
    if zauzeto:
        messages.error(request, "Mejl adresa je vec u upotrebi\n")
        return render(request, 'stranice/registracija.html')

    x = re.search("^[a-z0-9]*[@]\w+[.]\w{2,3}$", email)
    if not x:
        messages.error(request,
                       "Mejl pogresan format. Ocekivan format <rec proizvoljne duzine>@<rec proizvoljne duzine><rec duzine 2 ili 3 slova> \n")
        return render(request, 'stranice/registracija.html')

    # Dohvatanje lozinke
    lozinka = request.POST['password']

    # REGEX LOZINKE ZAKOMENTARISAN DA BI MOGLA LOZINKA DA BUDE 123
    # x = re.search(".*[A-Z].*.*[0-9].*", lozinka)
    # if not x:
    #     messages.error(request, "Lozinka treba da sadrzi barem jedno veliko slovo i barem jedna broj \n")
    #     return render(request, 'stranice/registracija.html')

    # Dohvatanje potvrde lozinke
    potvrda = request.POST['confirm-password']
    if lozinka != potvrda:
        messages.error(request, "Lozinke se ne podudaraju")
        return render(request, 'stranice/registracija.html')

    # Dohvatanje telefona korisnika
    telefon = request.POST['phoneNumber']
    x = re.search("^\d{9,10}$", telefon)
    if not x:
        messages.error(request, "Telefon mora biti najmanje 9 a najvise 10 cifara. Primer: 060 321321\n")
        return render(request, 'stranice/registracija.html')

    # Dohvatanje JMBG korisnika
    jmbg = request.POST['JMBG']
    x = re.search("^\d{13}$", jmbg)
    if not x:
        messages.error(request, "Pogresno unet JMBG\n")
        return render(request, 'stranice/registracija.html')
    pol = request.POST['sex']

    '''
    Pravljenje novog korisnika i cuvanje u bazi podataka
    '''
    noviKorisnik = Korisnik()
    noviKorisnik.first_name = ime
    noviKorisnik.last_name = prezime
    noviKorisnik.username = email
    noviKorisnik.email = email
    noviKorisnik.set_password(lozinka)
    noviKorisnik.brtelefona = telefon
    noviKorisnik.jmbg = jmbg
    noviKorisnik.pol = pol
    # Cuvamo korisnika
    noviKorisnik.save()

    '''
    Uvezivanje korisnika za pacijenta
    '''
    noviPacijent = Pacijent()
    noviPacijent.idpac = noviKorisnik
    noviPacijent.save()

    login(request, noviKorisnik)

    return redirect('index')


def logout_req(request: HttpRequest):
    '''
    logout_req - view koji ce da odjavi korisnika sa sistema

    :param HttpRequest:
    :return:
    '''

    logout(request)

    return redirect("index")


@login_required(login_url='login')
def zakazi_termin(request: HttpRequest):
    '''
    zakazi_termin - view koji ce da obavlja funkciju zakazivanja termina pacijenta na sistemu i dinamicki menja formu
    pomocu AJAX tehnologije

    :param HttpReauest:
    :return:
    '''

    '''
    Ako doktor ili administrator udje na strau da ih obavesti da ne mogu da zakazu termin
    '''
    if request.user.is_superuser:
        messages.error(request, "Korisnik nije u mogucnosti da zakaze termin.")
        return render(request, 'stranice/zakazivanjeTermina.html')

    if Admninistrator.objects.filter(idadmin_id=request.user.id):
        messages.error(request, "Korisnik nije u mogucnosti da zakaze termin.")
        return render(request, 'stranice/zakazivanjeTermina.html')

    if Stomatolog.objects.filter(idsto_id=request.user.id):
        messages.error(request, "Korisnik nije u mogucnosti da zakaze termin.")
        return render(request, 'stranice/zakazivanjeTermina.html')

    '''
    :var korisnici - lista u kojoj se stavljaju doktori koji rade u odredjenoj ordinaciji
    '''
    korisnici = []

    '''
    :var termini - termini koji mogu da se zakazu na stranici za zakazivanje
    '''
    termini = {
        1: "08:00-09:00",
        2: "09:00-10:00",
        3: "10:00-11:00",
        4: "11:00-12:00",
        5: "12:00-13:00",
        6: "13:00-14:00",
        7: "14:00-15:00",
        8: "15:00-16:00",
        9: "16:00-17:00",
        10: "17:00-18:00",
    }

    '''
    :var lokacije - pormenljiva u kojoj se nalaze sve lokacije iz baze
    :var doktori - promenljiva u kojoj se nalaze svi stomatolozi iz baze
    '''

    lokacije = Ordinacija.objects.all()
    doktori = Stomatolog.objects.all()

    for doktor in doktori:
        korisnici.append(Korisnik.objects.get(id=doktor.idsto_id))

    '''
    :var usluge - promenljiva u kojoj se nalaze sve usluge u bazi
    '''
    usluge = Usluga.objects.all()

    if request.method == "POST":
        if request.POST['sifra'] == '1':
            # Dinamicko ucitavanje stomatologa koji su zaposleni u datoj ordinaciji
            recnik = {}
            # kupi stvari iz forme
            lokacija = Ordinacija.objects.get(idordinacija=request.POST['lokacija'])

            # treba da mi nabavi sve doktore preko lokacije ove
            doktorLista = Stomatolog.objects.filter(ordinacija=lokacija)

            for doktor in doktorLista:
                imePrez = str(doktor.idsto.first_name + " " + doktor.idsto.last_name)
                recnik[doktor.idsto_id] = imePrez

            return HttpResponse(json.dumps(recnik))

        '''
        Informacije iz forme se prikupljaju u promenljive
        '''
        lokacija = request.POST['lokacija']
        doktor = request.POST['doktor']
        usluga = request.POST['usluga']
        datum = request.POST['datum']

        # Treba da uzme da izbaci samo slobodne termine
        stariTermini = Rezervacija.objects.all()
        stariTermini = stariTermini.filter(datum=datum)
        stariTermini = stariTermini.filter(stomatolog=doktor)
        stariTermini = stariTermini.filter(ordinacijarez=lokacija)
        stariTermini = stariTermini.exclude(status="Otkazano")

        '''
        Petlja za izbacivanje zauzetih termina
        '''
        for termin in stariTermini:
            termini.pop(termin.vreme)

        return HttpResponse(json.dumps(termini))
    else:
        context = {
            "lokacije": lokacije,
            "doktori": korisnici,
            "usluge": usluge,
            'termini': termini
        }

    return render(request, 'stranice/zakazivanjeTermina.html', context)


def zakazivanje(request: HttpRequest):
    '''
    zakazivanje - view koji cuva informacije o zakazanom terminu unutar baze podataka

    :param request:
    :return redirect:
    '''

    '''
    If koji gleda da li je request tipa "POST" kako bi mogao da dohvati podatke iz forme i
    sacuvia ih u bazi kao novi termin
    '''

    if request.method == "POST":
        # Uzimamo informacije
        lokacija = request.POST['lokacija']
        doktor = request.POST['doktor']
        usluga = request.POST['usluga']
        datum = request.POST['datum']
        termin = request.POST['vreme']
        pac = Pacijent.objects.get(idpac=request.user.id)

        noviTermin = Rezervacija()
        noviTermin.datum = datum
        noviTermin.vreme = termin
        noviTermin.status = "Zakazano"
        noviTermin.ordinacijarez = Ordinacija.objects.get(idordinacija=lokacija)
        noviTermin.usluga = Usluga.objects.get(idusl=usluga)
        noviTermin.pacijent = pac
        noviTermin.stomatolog = Stomatolog.objects.get(idsto=doktor)

        # Cuvanje termina u bazi
        noviTermin.save()

        return redirect('pacijentiRezervacije')


def kontakt(request: HttpRequest):
    '''
    kontak - view koji renderuje stranicu sa kontaktom glavne centrale

    :param request:
    :return render:
    '''

    '''
    :var centrala - 
    '''
    centrala = Ordinacija.objects.get(centrala=1)

    context = {
        "centrala": centrala
    }

    return render(request, 'stranice/kontakt.html', context)
