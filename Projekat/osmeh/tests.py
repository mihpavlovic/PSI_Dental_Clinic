import datetime
from django.utils import timezone

import django.utils.dateparse
from django import setup
from django.contrib.messages import get_messages
from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth import get_user_model
from django.utils import timezone

from .views import *
from .models import *


# Create your tests here.
# ====================Pavlovic===================
class PregledNalogaTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.s = Korisnik(id=1, username="nenad@osmeh.rs", first_name="Nenad", last_name="Nenadovic", email="nenad@osmeh.rs")
        cls.s.set_password("123")
        cls.s.save()

    def test_pregled_svog_profila(self):
        self.client.login(username="nenad@osmeh.rs", password="123")
        response = self.client.get("/profilKorisnika/")
        self.assertContains(response, " Ime: Nenad ", html=True)

class PregledIstorijeTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        #pravljenje pacijenta
        cls.kor = Korisnik(id=1, username="nenad@osmeh.rs", first_name="Nenad", last_name="Nenadovic")
        cls.kor.set_password("123")
        cls.kor.save()
        cls.pac = Pacijent(idpac=cls.kor)
        cls.pac.save()
        #pravljenje doktora
        cls.dok = Korisnik(id=2, username="doc@osmeh.rs", first_name="Dok", last_name="Dokic")
        cls.dok.save()
        cls.stomatolog = Stomatolog(idsto=cls.dok)
        cls.stomatolog.save()
        #pravljenje termina
        cls.ter = Rezervacija(idrez=3, pacijent=cls.pac, stomatolog=cls.stomatolog, status="Otkazano",
                              datum=timezone.now(), vreme="1")
        cls.ter.save()

    def test_pregled_svoje_istorije(self):
        self.client.login(username="nenad@osmeh.rs", password="123")
        response = self.client.get("/istorijaPacijent/")
        self.assertContains(response, "Datum", html=True)


class PregledAktivnihRezTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        #pravljenje pacijenta
        cls.kor = Korisnik(id=1, username="nenad@osmeh.rs", first_name="Nenad", last_name="Nenadovic")
        cls.kor.set_password("123")
        cls.kor.save()
        cls.pac = Pacijent(idpac=cls.kor)
        cls.pac.save()
        #pravljenje doktora
        cls.dok = Korisnik(id=2, username="doc@osmeh.rs", first_name="Dok", last_name="Dokic")
        cls.dok.save()
        cls.stomatolog = Stomatolog(idsto=cls.dok)
        cls.stomatolog.save()
        #pravljenje termina
        cls.ter = Rezervacija(idrez=3, pacijent=cls.pac, stomatolog=cls.stomatolog, status="Zakazano",
                              datum=timezone.now(), vreme="1")
        cls.ter.save()

    def test_pregled_aktivnih_termina(self):
        self.client.login(username="nenad@osmeh.rs", password="123")
        response = self.client.get("/pacijentiRezervacije/")
        self.assertContains(response, "Status: Zakazano", html=True)


class OtkazivanjeTerminaTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        #pravljenje pacijenta
        cls.kor = Korisnik(id=1, username="nenad@osmeh.rs", first_name="Nenad", last_name="Nenadovic")
        cls.kor.set_password("123")
        cls.kor.save()
        cls.pac = Pacijent(idpac=cls.kor)
        cls.pac.save()
        #pravljenje doktora
        cls.dok = Korisnik(id=2, username="doc@osmeh.rs", first_name="Dok", last_name="Dokic")
        cls.dok.save()
        cls.stomatolog = Stomatolog(idsto=cls.dok)
        cls.stomatolog.save()
        #pravljenje termina
        cls.ter = Rezervacija(idrez=3, pacijent=cls.pac, stomatolog=cls.stomatolog, status="Zakazano",
                              datum=timezone.now(), vreme="1")
        cls.ter.save()

    def test_pregled_aktivnih_termina(self):
        self.client.login(username="nenad@osmeh.rs", password="123")
        response = self.client.get("/pacijentiRezervacije/")
        self.assertContains(response, "Status: Zakazano", html=True)


class PacijentOtkazivanje(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.s = Korisnik(username="doktor@osmeh.rs", first_name="Mihailo", last_name="Pantovic")
        cls.s.set_password("123")
        cls.s.save()
        cls.stomatolog = Stomatolog(idsto=cls.s)
        cls.stomatolog.save()

        cls.p = Korisnik(username="marko@osmeh.rs", first_name="Marko", last_name="Markovic")
        cls.p.set_password("123")
        cls.p.save()
        cls.pacijent = Pacijent(idpac=cls.p)
        cls.pacijent.save()

        cls.termin = Rezervacija(idrez=1, pacijent=cls.pacijent, stomatolog=cls.stomatolog, vreme=8,
                                 status="Zakazano",
                                 datum=timezone.now())
        cls.termin.save()

    def test_otkazivanje_pacijent(self):
        self.client.login(username="marko@osmeh.rs", password="123")
        response = self.client.post('/otkazivanjeTerminaPacijent/1')
        self.assertEqual(response.status_code, 302)
        response = self.client.get("/istorijaPacijent/")
        self.assertContains(response, "Otkazano", html=True)

class IzmenaNaloga(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.korisnik = Korisnik(username="kor@osmeh.rs", email="kor@osmeh.rs", first_name="Kor",
                                last_name="Koric", brtelefona="0601234567")
        cls.korisnik.set_password("123")
        cls.korisnik.save()

    def test_uspesna_zamena(self):
        self.client.login(username="kor@osmeh.rs", password="123")
        response = self.client.post("/izmena/", data={
            "name": "Kor",
            "surname": "Pantovic",
            "email": "kor@osmeh.rs",
            "phoneNumber": "0601234567",
            "password": "123",
            "confirm-password": "123"

        })
        self.assertEqual(response.status_code, 200)
        #response = self.client.get("/profilKorisnika/")
        self.assertContains(response, "Ime:", html=True)


# ====================Pantovic======================

def napraviTermin(id, stomatolog, pacijent, status, v):
    termin = Rezervacija(idrez=id, pacijent=pacijent, stomatolog=stomatolog, vreme=v, status=status,
                         datum=timezone.now())
    termin.save()
    return termin


def napraviPacijenta(ki, fn, ln):
    p = Korisnik(username=ki, first_name=fn, last_name=ln)
    p.set_password("123")
    p.save()
    pacijent = Pacijent(idpac=p)
    pacijent.save()
    return pacijent


def napraviStomatologa(ki, fn, ln):
    s = Korisnik(username=ki, first_name=fn, last_name=ln)
    s.set_password("123")
    s.save()
    stomatolog = Stomatolog(idsto=s)
    stomatolog.save()
    return stomatolog


class DoktorPregledTermina(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.stomatolog1 = napraviStomatologa(ki="doktor@osmeh.rs", fn="Mihailo", ln="Pantovic")
        cls.stomatolog1.save()

        cls.stomatolog2 = napraviStomatologa(ki="doktor2@osmeh.rs", fn="Mihailo2", ln="Pantovic2")
        cls.stomatolog2.save()

        cls.pacijent1 = napraviPacijenta(ki="marko@osmeh.rs", fn="Marko", ln="Markovic")
        cls.pacijent1.save()

        cls.pacijent2 = napraviPacijenta(ki="mihailo@osmeh.rs", fn="Miha", ln="Mihailovic")
        cls.pacijent2.save()

        cls.terminOtkazan1 = napraviTermin(1, cls.stomatolog1, cls.pacijent1, "Otkazano", 8)
        cls.terminOtkazan1.save()

        cls.terminZakazan1 = napraviTermin(2, cls.stomatolog1, cls.pacijent1, "Zakazano", 1)
        cls.terminZakazan1.save()

        cls.terminZavrsen1 = napraviTermin(3, cls.stomatolog1, cls.pacijent1, "Zavrseno", 5)
        cls.terminZavrsen1.save()

        cls.terminZakazan2 = napraviTermin(4, cls.stomatolog2, cls.pacijent1, "Zakazano", 1)
        cls.terminZakazan2.save()

    def test_pregled_rasporeda(self):
        self.client.login(username="doktor@osmeh.rs", password="123")
        response = self.client.get("/doktorTermini/")
        self.assertContains(response, "Pacijent: Marko", html=True)

    def test_pregled_istorije(self):
        self.client.login(username="doktor@osmeh.rs", password="123")
        response = self.client.get("/doktorIstorija/")
        self.assertContains(response, "Marko Markovic", html=True)

    def test_otkazivanje_termina(self):
        self.client.login(username="doktor2@osmeh.rs", password="123")
        response = self.client.post('/doktorOtkazivanjeTermina/', data={
            "rezervacija": 4
        })
        self.assertEqual(response.status_code, 302)
        response = self.client.get("/doktorIstorija/")
        self.assertContains(response, "Otkazano", html=True)

    def test_zavrsavanje_termina(self):
        self.client.login(username="doktor2@osmeh.rs", password="123")
        response = self.client.post('/doktorZavrsavanjeTermina/', data={
            "rezervacija": 4
        })
        self.assertEqual(response.status_code, 302)
        response = self.client.get("/doktorIstorija/")
        self.assertContains(response, "Zavrseno", html=True)


class PredledDoktora(TestCase):

    @classmethod
    def setUpTestData(cls):
        cls.s = Korisnik(id=1, username="doc@osmeh.rs", first_name="Dok", last_name="Dokic")
        cls.s.save()
        cls.stomatolog = Stomatolog(idsto=cls.s)
        cls.stomatolog.save()

    def test_pregled_doktora(self):
        response = self.client.get("/sviDoktori/")
        self.assertContains(response, "dr Dok Dokic", html=True)

    def test_pregled_doktora_detaljno(self):
        response = self.client.get("/sviDoktori/")
        self.assertContains(response, "dr Dok Dokic", html=True)
        response = self.client.get(f"/lekarBiografija/{self.stomatolog.idsto_id}")
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Ime: Dok", html=True)


class RegistracijaStomatologa(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.admin = Korisnik(username="admin", is_superuser=1, is_staff=1)
        cls.admin.set_password("123")
        cls.admin.save()

        cls.korisnik = Korisnik(username="proba@osmeh.rs", email="proba@osmeh.rs", first_name="Proba",
                                last_name="Probic")
        cls.korisnik.save()

        cls.ordinacija1 = Ordinacija(idordinacija=1, naziv="ordinacija1", brtelefona="060123123", centrala=1,
                                     adresa="adresa1", mesto="mesto1")
        cls.ordinacija1.save()

    def test_uspesno_registrovanje(self):
        self.client.login(username="admin", password="123")
        response = self.client.post('/registrujNovogDoktora/', data={
            "name": "Korisnik",
            "surname": "Korisnik",
            "email": "korisnik@osmeh.rs",
            "password": "123",
            "confirm-password": "123",
            "phoneNumber": "0654324134",
            "sex": "M",
            "lokacija": "ordinacija1",
            "biografija": "Biografija"
        })
        self.assertEqual(response.status_code, 302)
        response = self.client.get("/pregledKorisnika/")
        self.assertContains(response, "Korisnik", html=True)

    def test_prazno_ime(self):
        self.client.login(username="admin", password="123")
        response = self.client.post('/registrujNovogDoktora/', data={
            "name": "",
            "surname": "Korisnik1",
            "email": "k@osmeh.rs",
            "password": "123",
            "confirm-password": "123",
            "phoneNumber": "0654324134",
            "sex": "M",
            "lokacija": "ordinacija1",
            "biografija": "Biografija"
        })
        self.assertEqual(response.status_code, 302)
        response = self.client.get("/registrujNovogDoktora/")
        self.assertContains(response, "Ime nije uneto", html=True)

    def test_prazno_prezime(self):
        self.client.login(username="admin", password="123")
        response = self.client.post('/registrujNovogDoktora/', data={
            "name": "Korisnik1",
            "surname": "",
            "email": "k@osmeh.rs",
            "password": "123",
            "confirm-password": "123",
            "phoneNumber": "0654324134",
            "sex": "M",
            "lokacija": "ordinacija1",
            "biografija": "Biografija"
        })
        self.assertEqual(response.status_code, 302)
        response = self.client.get("/registrujNovogDoktora/")
        self.assertContains(response, "Prezime nije uneto", html=True)

    def test_prazno_email(self):
        self.client.login(username="admin", password="123")
        response = self.client.post('/registrujNovogDoktora/', data={
            "name": "Korisnik1",
            "surname": "Korisnik1",
            "email": "",
            "password": "123",
            "confirm-password": "123",
            "phoneNumber": "0654324134",
            "sex": "M",
            "lokacija": "ordinacija1",
            "biografija": "Biografija"
        })
        self.assertEqual(response.status_code, 302)
        response = self.client.get("/registrujNovogDoktora/")
        self.assertContains(response, "Email nije unet", html=True)

    def test_prazno_lozinka(self):
        self.client.login(username="admin", password="123")
        response = self.client.post('/registrujNovogDoktora/', data={
            "name": "Korisnik1",
            "surname": "Korisnik1",
            "email": "k@osmeh.rs",
            "password": "",
            "confirm-password": "123",
            "phoneNumber": "0654324134",
            "sex": "M",
            "lokacija": "ordinacija1",
            "biografija": "Biografija"
        })
        self.assertEqual(response.status_code, 302)
        response = self.client.get("/registrujNovogDoktora/")
        self.assertContains(response, "Lozinka nije uneta", html=True)

    def test_prazno_potvrda(self):
        self.client.login(username="admin", password="123")
        response = self.client.post('/registrujNovogDoktora/', data={
            "name": "Korisnik1",
            "surname": "Korisnik1",
            "email": "k@osmeh.rs",
            "password": "123",
            "confirm-password": "",
            "phoneNumber": "0654324134",
            "sex": "M",
            "lokacija": "ordinacija1",
            "biografija": "Biografija"
        })
        self.assertEqual(response.status_code, 302)
        response = self.client.get("/registrujNovogDoktora/")
        self.assertContains(response, "Potvrda lozinke nije uneta", html=True)

    def test_prazno_broj(self):
        self.client.login(username="admin", password="123")
        response = self.client.post('/registrujNovogDoktora/', data={
            "name": "Korisnik1",
            "surname": "Korisnik1",
            "email": "k@osmeh.rs",
            "password": "123",
            "confirm-password": "123",
            "phoneNumber": "",
            "sex": "M",
            "lokacija": "ordinacija1",
            "biografija": "Biografija"
        })
        self.assertEqual(response.status_code, 302)
        response = self.client.get("/registrujNovogDoktora/")
        self.assertContains(response, "Telefon mora biti najmanje 9 a najvise 10 cifara. Primer: 060 321321",
                            html=True)

    def test_zauzet_email(self):
        self.client.login(username="admin", password="123")
        response = self.client.post('/registrujNovogDoktora/', data={
            "name": "Korisnik1",
            "surname": "Korisnik1",
            "email": "proba@osmeh.rs",
            "password": "123",
            "confirm-password": "123",
            "phoneNumber": "0654324134",
            "sex": "M",
            "lokacija": "ordinacija1",
            "biografija": "Biografija"
        })
        self.assertEqual(response.status_code, 302)
        response = self.client.get("/registrujNovogDoktora/")
        self.assertContains(response, "Mejl adresa je vec u upotrebi", html=True)

    def test_los_format_email(self):
        self.client.login(username="admin", password="123")
        response = self.client.post('/registrujNovogDoktora/', data={
            "name": "",
            "surname": "Korisnik3",
            "email": "kor@osmeh.rs",
            "password": "123",
            "confirm-password": "123",
            "phoneNumber": "0654324134",
            "sex": "M",
            "lokacija": "ordinacija1",
            "biografija": "Biografija"
        })
        self.assertEqual(response.status_code, 302)
        response = self.client.get("/registrujNovogDoktora/")
        self.assertContains(response,
                            "Registracija novog doktora",
                            html=True)

    def test_lozinke_nepoklapanje(self):
        self.client.login(username="admin", password="123")
        response = self.client.post('/registrujNovogDoktora/', data={
            "name": "Korisnik1",
            "surname": "Korisnik1",
            "email": "kor@osmeh.rs",
            "password": "1234",
            "confirm-password": "123",
            "phoneNumber": "0654324134",
            "sex": "M",
            "lokacija": "ordinacija1",
            "biografija": "Biografija"
        })
        self.assertEqual(response.status_code, 302)
        response = self.client.get("/registrujNovogDoktora/")
        self.assertContains(response, "Lozinke se ne podudaraju", html=True)

    def test_los_format_broj(self):
        self.client.login(username="admin", password="123")
        response = self.client.post('/registrujNovogDoktora/', data={
            "name": "Korisnik1",
            "surname": "Korisnik1",
            "email": "kor@osmeh.rs",
            "password": "123",
            "confirm-password": "123",
            "phoneNumber": "+381654324134",
            "sex": "M",
            "lokacija": "ordinacija1",
            "biografija": "Biografija"
        })
        self.assertEqual(response.status_code, 302)
        response = self.client.get("/registrujNovogDoktora/")
        self.assertContains(response, "Telefon mora biti najmanje 9 a najvise 10 cifara. Primer: 060 321321", html=True)


# ====================Adzic=========================
#Testiranje odjavljivanja sa sistema
class LogoutViewTest(TestCase):
    def setUp(self):
        User = get_user_model()
        self.user = User.objects.create_user(username='user', password='123')
        self.client.login(username='user', password='123')

    def test_logout_view(self):
        response = self.client.get(reverse('logout'))
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, reverse('index'))

#Testiranje registracije na sistem
class RegisterView(TestCase):

    def test_register_view(self):
        url = reverse('register')
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'stranice/registracija.html')

    def test_register_user_uspesan(self):
        url = reverse('registerMethod')
        data = {
            'name': 'Maki',
            'surname': 'Marinkovic',
            'email': 'makimarinkovic23@mejl.com',
            'password': 'password123',
            'confirm-password': 'password123',
            'phoneNumber': '0649877894',
            'JMBG': '1234567890123',
            'sex': 'M'
        }
        response = self.client.post(url, data)
        self.assertRedirects(response, reverse('index'))

        user = get_user_model().objects.get(email=data['email'])
        self.assertEqual(user.first_name, data['name'])
        self.assertEqual(user.last_name, data['surname'])
        self.assertEqual(user.brtelefona, data['phoneNumber'])
        self.assertEqual(user.jmbg, data['JMBG'])
        self.assertEqual(user.pol, data['sex'])

        self.assertTrue(user.is_authenticated)

    def test_register_user_neuspesan_neispravn_format_mejla(self):
        url = reverse('registerMethod')
        data = {
            'name': 'Maki',
            'surname': 'Marinkovic',
            'email': 'makimarinkovic23mejl.com',
            'password': 'password123',
            'confirm-password': 'password123',
            'phoneNumber': '0649877894',
            'JMBG': '1234567890123',
            'sex': 'M'
        }
        response = self.client.post(url, data)
        self.assertTemplateNotUsed(response, reverse('index'))

        with self.assertRaises(Korisnik.DoesNotExist):
            get_user_model().objects.get(email=data['email'])

    def test_register_user_neuspesan_neispravn_format_telefona(self):
        url = reverse('registerMethod')
        data = {
            'name': 'Maki',
            'surname': 'Marinkovic',
            'email': 'makimarinkovic23@mejl.com',
            'password': 'password123',
            'confirm-password': 'password123',
            'phoneNumber': '064',
            'JMBG': '1234567890123',
            'sex': 'M'
        }
        response = self.client.post(url, data)
        self.assertTemplateNotUsed(response, reverse('index'))
        self.assertContains(response, "Telefon mora biti najmanje 9 a najvise 10 cifara.")

        with self.assertRaises(Korisnik.DoesNotExist):
            get_user_model().objects.get(email=data['email'])

    def test_register_user_neuspesan_neispravn_lozinka(self):
        url = reverse('registerMethod')
        data = {
            'name': 'Maki',
            'surname': 'Marinkovic',
            'email': 'makimarinkovic23@mejl.com',
            'password': 'password123',
            'confirm-password': 'password12345',
            'phoneNumber': '0649877894',
            'JMBG': '1234567890123',
            'sex': 'M'
        }
        response = self.client.post(url, data)
        self.assertTemplateNotUsed(response, reverse('index'))
        self.assertContains(response, "Lozinke se ne podudaraju")

        with self.assertRaises(Korisnik.DoesNotExist):
            get_user_model().objects.get(email=data['email'])

    def test_register_user_neuspesan_neispravn_format_JMBG(self):
        url = reverse('registerMethod')
        data = {
            'name': 'Maki',
            'surname': 'Marinkovic',
            'email': 'makimarinkovic23@mejl.com',
            'password': 'password123',
            'confirm-password': 'password123',
            'phoneNumber': '0649877894',
            'JMBG': '12345',
            'sex': 'M'
        }
        response = self.client.post(url, data)
        self.assertTemplateNotUsed(response, reverse('index'))
        self.assertContains(response, "Pogresno unet JMBG")

        with self.assertRaises(Korisnik.DoesNotExist):
            get_user_model().objects.get(email=data['email'])

    def test_register_user_neuspesan_neispravn_prazno_ime(self):
        url = reverse('registerMethod')
        data = {
            'name': '',
            'surname': 'Marinkovic',
            'email': 'makimarinkovic23@mejl.com',
            'password': 'password123',
            'confirm-password': 'password123',
            'phoneNumber': '0649877894',
            'JMBG': '1234567890123',
            'sex': 'M'
        }
        response = self.client.post(url, data)
        self.assertTemplateNotUsed(response, reverse('index'))
        self.assertContains(response, "Ime nije uneto")

        with self.assertRaises(Korisnik.DoesNotExist):
            get_user_model().objects.get(email=data['email'])

    def test_register_user_neuspesan_neispravn_prazno_prezime(self):
        url = reverse('registerMethod')
        data = {
            'name': 'Maki',
            'surname': '',
            'email': 'makimarinkovic23@mejl.com',
            'password': 'password123',
            'confirm-password': 'password123',
            'phoneNumber': '0649877894',
            'JMBG': '1234567890123',
            'sex': 'M'
        }
        response = self.client.post(url, data)
        self.assertTemplateNotUsed(response, reverse('index'))
        self.assertContains(response, "Prezime nije uneto")

        with self.assertRaises(Korisnik.DoesNotExist):
            get_user_model().objects.get(email=data['email'])

    def test_register_user_neuspesan_neispravn_prazan_email(self):
        url = reverse('registerMethod')
        data = {
            'name': 'Maki',
            'surname': 'Marinkovic',
            'email': '',
            'password': 'password123',
            'confirm-password': 'password123',
            'phoneNumber': '0649877894',
            'JMBG': '1234567890123',
            'sex': 'M'
        }
        response = self.client.post(url, data)
        self.assertTemplateNotUsed(response, reverse('index'))
        self.assertContains(response, "Email nije")

        with self.assertRaises(Korisnik.DoesNotExist):
            get_user_model().objects.get(email=data['email'])

    def unetiPodatke(self):
        self.username = 'testuser'
        self.password = 'testpassword'
        self.user = get_user_model().objects.create_user(username=self.username, password=self.password)
        return self.user

    def test_register_user_neuspesan_neispravn_podaci_postoje(self):
        self.user = self.unetiPodatke()
        url = reverse('registerMethod')
        data = {
            'name': 'testuser',
            'surname': 'testuser',
            'email': 'testuser',
            'password': 'testpassword',
            'confirm-password': 'testpassword',
            'phoneNumber': '0649877894',
            'JMBG': '1234567890123',
            'sex': 'M'
        }
        response = self.client.post(url, data)
        self.assertTemplateNotUsed(response, reverse('index'))

        with self.assertRaises(Korisnik.DoesNotExist):
            get_user_model().objects.get(email=data['email'])

#Testrianje zakazivanje usluge
class ZakaziTerminViewTest(TestCase):
    def setUp(self):
        self.admin = get_user_model().objects.create_superuser(username='admin', password='admin', email='admin@example.com')
        self.user2 = get_user_model().objects.create_user(username='testuserDoktor', password='testpassword')
        self.user = get_user_model().objects.create_user(username='testkorisnik', password='testlozinka')

        self.ordinacija = Ordinacija.objects.create(naziv='Naziv ordinacije', mesto='Mesto ordinacije',
                                                    adresa='Adresa ordinacije', brtelefona='062916722')

        self.stomatolog = Stomatolog.objects.create(idsto=self.user2, biografija='Biografija doktora',
                                                ordinacija=self.ordinacija)
        self.usluga = Usluga.objects.create(naziv='Naziv usluge', cena=100, opis='Opis usluge')
        self.pacijent = Pacijent.objects.create(idpac=self.user)
        self.url = reverse('termin')

    def test_admin_ne_moze_zakazati_termin(self):
        self.client.login(username='admin', password='admin')
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Korisnik nije u mogucnosti da zakaze termin")

    def test_stomatolog_ne_moze_zakazati_termin(self):
        self.client.login(username='testuserDoktor', password='testpassword')
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Korisnik nije u mogucnosti da zakaze termin")

    def test_get_zahtev(self):
        self.client.login(username='testkorisnik', password='testlozinka')

        response = self.client.get(self.url)

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'stranice/zakazivanjeTermina.html')
        self.assertContains(response, '<select name="lokacija"')
        self.assertContains(response, '<select name="doktor"')
        self.assertContains(response, '<select name="usluga"')

    def test_post_zahtev(self):
        self.client.login(username='testkorisnik', password='testlozinka')

        data = {
            'lokacija': self.ordinacija.idordinacija,
            'datum': timezone.datetime(2023, 6, 27, tzinfo=timezone.get_current_timezone()),
            'doktor': self.stomatolog.idsto_id,
            'usluga': self.usluga.idusl,
            'vreme': '11',
            'sifra': '2'
        }
        response = self.client.post(self.url, data)

        self.assertEqual(response.status_code, 200)

#Testiranje zakazivanja usluge - cuvanje u bazi
class ZakazivanjeTests(TestCase):
    def setUp(self):
        self.user = get_user_model().objects.create_user(username='testuser', password='testpassword')
        self.user2 = get_user_model().objects.create_user(username='testuserDoktor', password='testpassword')

        self.usluga = Usluga.objects.create(naziv='Naziv usluge', cena=100, opis='Opis usluge')
        self.ordinacija = Ordinacija.objects.create(naziv='Naziv ordinacije', mesto='Mesto ordinacije',
                                                    adresa='Adresa ordinacije', brtelefona='062916722')
        self.doktor = Stomatolog.objects.create(idsto=self.user2, biografija='Biografija doktora', ordinacija=self.ordinacija)

        self.pacijent = Pacijent.objects.create(idpac=self.user)

    def test_cuvanje_termina(self):
        self.client.login(username='testuser', password='testpassword')

        url = reverse('terminZakazivanje')
        data = {
            'lokacija': self.ordinacija.idordinacija,
            'datum': '2023-06-27',
            'doktor': self.user2.id,
            'usluga': self.usluga.idusl,
            'vreme': '11',
        }
        response = self.client.post(url, data)
        self.assertRedirects(response, reverse('pacijentiRezervacije'))

#Testiranje prijave na sistem
class LoginViewTest(TestCase):
    @classmethod
    def setUp(self):
        self.username = 'testuser'
        self.password = 'testpassword'
        self.user = get_user_model().objects.create_user(username=self.username, password=self.password)

    def test_login_view_uspesan(self):
        url = reverse('login')
        data = {'username': self.username, 'password': self.password}
        response = self.client.post(url, data)
        self.assertRedirects(response, reverse('index'))

    def test_login_view_neuspesan_pogresni_podaci(self):
        url = reverse('login')
        data = {'username': 'invaliduser', 'password': 'invalidpassword'}
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'stranice/prijava.html')
        self.assertContains(response, "Korisnik ne postoji")

    def test_login_view_get_request(self):
        url = reverse('login')
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'stranice/prijava.html')

#Testiranje index view-a
class IndexViewTest(TestCase):
    def test_index_view(self):
        response = self.client.get(reverse('index'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'stranice/index.html')


#Testiranje pregleda kontakata
class KontaktViewTest(TestCase):
    @classmethod
    def setUp(self):
        self.centrala = Ordinacija.objects.create(naziv='Glavna Centrala', mesto='Grad', adresa='Adresa 123',
                                                  brtelefona='123456789', centrala=True)

    def test_kontakt_view(self):
        url = reverse('kontakt')
        request = self.client.get(url)
        response = kontakt(request)

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, self.centrala.adresa, html=True)

# ====================Glisic=======================

class KorisniciTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.admin = Korisnik(username="admin", is_superuser=1, is_staff=1)
        cls.admin.set_password("123")
        cls.admin.save()

        cls.pacijent = Korisnik(username="marko")
        cls.pacijent.set_password("123")
        cls.pacijent.save()

    def test_pregled_korisnika(self):
        self.client.login(username="admin", password="123")
        response = self.client.get("/pregledKorisnika/")

        self.assertContains(response, " <th scope='col'>Tip</th>", html=True)

    def test_brisanje_korisnika(self):
        self.client.login(username="admin", password="123")
        response = self.client.get(f"/brisanjeKorisnika/{self.pacijent.id}")

        self.assertEqual(response.status_code, 302)


class UslugeTest(TestCase):

    @classmethod
    def setUpTestData(cls):
        cls.admin = Korisnik(username="admin", is_superuser=1, is_staff=1)
        cls.admin.set_password("123")
        cls.admin.save()

        cls.usluga1 = Usluga(idusl=1, naziv="usluga1", opis="opis1", cena=1000)
        cls.usluga1.save()

        cls.usluga2 = Usluga(idusl=2, naziv="usluga2", opis="opis2", cena=2000)
        cls.usluga2.save()

    def test_pregled_usluga(self):
        response = self.client.get('/uslugeIcene/')
        self.assertContains(response, "usluga1", html=True)

    def test_izmena_usluge_Get_Los(self):
        self.client.login(username="admin", password="123")
        response = self.client.get("/izmenaUsluge/3")

        self.assertEqual(response.status_code, 302)

    def test_izmena_usluge_Get_Dobar(self):
        self.client.login(username="admin", password="123")
        response = self.client.get("/izmenaUsluge/1")

        self.assertEqual(response.status_code, 200)

    def test_izmena_usluge_Post(self):
        self.client.login(username="admin", password="123")
        response = self.client.post('/izmenaUsluge/1', data={
            "cena": 3000
        })
        self.assertEqual(response.status_code, 302)
        response = self.client.get('/uslugeIcene/')
        self.assertContains(response, "3000", html=True)


class OrdinacijeTest(TestCase):

    @classmethod
    def setUpTestData(cls):
        cls.admin = Korisnik(username="admin", is_superuser=1, is_staff=1)
        cls.admin.set_password("123")
        cls.admin.save()

        cls.ordinacija1 = Ordinacija(idordinacija=1, naziv="ordinacija1", brtelefona="060123123", centrala=1,
                                     adresa="adresa1", mesto="mesto1")
        cls.ordinacija1.save()

        cls.ordinacija2 = Ordinacija(idordinacija=2, naziv="ordinacija2", brtelefona="060321321", centrala=0,
                                     adresa="adresa2", mesto="mesto2")

        cls.ordinacija2.save()

    def test_pregled_ordinacija(self):
        response = self.client.get("/pregledOrdinacija/")
        self.assertEqual(response.status_code, 200)

    def test_dodavanje_ordinacije_nije_superuser(self):
        response = self.client.get("/dodavanjeOrdinacije/")
        self.assertEqual(response.status_code, 302)

    def test_dodavanje_ordinacije_Get(self):
        self.client.login(username="admin", password="123")
        response = self.client.get("/dodavanjeOrdinacije/")
        self.assertEqual(response.status_code, 200)

    def test_dodavanje_ordinacije_Post(self):
        self.client.login(username="admin", password="123")
        response = self.client.post("/dodavanjeOrdinacije/", data={
            "ime": "ordinacija3",
            "adresa": "adresa3",
            "mesto": "mesto3",
            "telefon": "060123321"
        })
        self.assertEqual(response.status_code, 302)

        response = self.client.get("/pregledOrdinacija/")
        self.assertContains(response, "ordinacija3", html=True)

    def test_uredjivanje_ordinacije_nije_superuser(self):
        response = self.client.get("/uredjivanjeOrdinacija/1")
        self.assertEqual(response.status_code, 302)

    def test_uredjivanje_ordinacije_Get(self):
        self.client.login(username="admin", password="123")
        response = self.client.get("/uredjivanjeOrdinacija/1")
        self.assertEqual(response.status_code, 200)

    def test_uredjivanje_ordinacije_Post_izmeni(self):
        self.client.login(username="admin", password="123")
        response = self.client.post("/uredjivanjeOrdinacija/1", data={
            "ime": "Drugo ime",
            "adresa": "Druga adresa",
            "mesto": "Drugo mesto",
            "telefon": "060234234",
            "action": "izmeni"
        })
        self.assertEqual(response.status_code, 302)

        response = self.client.get("/pregledOrdinacija/")
        self.assertContains(response, "Drugo ime", html=True)

    def test_uredjivanje_ordinacije_Post_izbrisiCentralu(self):
        self.client.login(username="admin", password="123")
        response = self.client.post("/uredjivanjeOrdinacija/1", data={
            "action": "izbrisi"
        })
        self.assertEqual(response.status_code, 200)

        response = self.client.get("/pregledOrdinacija/")
        self.assertContains(response, "ordinacija1", html=True)

    def test_uredjivanje_ordinacije_Post_izbrisi(self):
        '''
        Fail je ocekivan jer je ordinacija izbrisana
        :return:
        '''
        self.client.login(username="admin", password="123")
        response = self.client.post("/uredjivanjeOrdinacija/2", data={
            "action": "izbrisi"
        })
        self.assertEqual(response.status_code, 302)

        response = self.client.get("/pregledOrdinacija/")
        self.assertContains(response, "ordinacija2", html=True)
