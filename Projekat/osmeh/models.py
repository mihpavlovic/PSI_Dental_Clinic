from django.db import models
from django.db.models import Model
from django.contrib.auth.models import User, AbstractUser


# Create your models here.
class Admninistrator(models.Model):
    idadmin = models.OneToOneField('Korisnik', models.DO_NOTHING, db_column='idAdmin', primary_key=True)

    class Meta:
        db_table = 'admninistrator'


class Korisnik(AbstractUser):
    # idkor = models.IntegerField(db_column='idKor', primary_key=True) IMA VEC ABSTRACT USER
    # ime = models.CharField(db_column='Ime', max_length=20) IMA VEC ABSTRACT USER
    # prezime = models.CharField(db_column='Prezime', max_length=20) IMA VEC ABSTRACT USER
    # email = models.CharField(db_column='Email', max_length=45) IMA VEC ABSTRACT USER
    # lozinka = models.CharField(db_column='Lozinka', max_length=45) IMA VEC ABSTRACT USER
    jmbg = models.CharField(db_column='JMBG', max_length=13)
    pol = models.CharField(db_column='Pol', max_length=1)
    # slika = models.TextField(db_column='Slika', blank=True, null=True)
    brtelefona = models.CharField(db_column='BrTelefona', max_length=45)
    pfp = models.ImageField(upload_to='imgs/', null=True)

    class Meta:
        db_table = 'korisnik'


class Ordinacija(models.Model):
    idordinacija = models.AutoField(db_column='idOrdinacija', primary_key=True)
    naziv = models.CharField(db_column='Naziv', max_length=40)
    mesto = models.CharField(db_column='Mesto', max_length=40)
    adresa = models.CharField(db_column='Adresa', max_length=40)
    brtelefona = models.CharField(db_column='BrTelefona', max_length=20)
    # slika = models.TextField(db_column='Slika', blank=True, null=True)
    pfp = models.ImageField(upload_to='imgs/', null=True)
    centrala = models.BooleanField(db_column='Centrala', default=0)

    class Meta:
        db_table = 'ordinacija'


class Pacijent(models.Model):
    idpac = models.OneToOneField(Korisnik, models.DO_NOTHING, db_column='idPac', primary_key=True)

    class Meta:
        db_table = 'pacijent'

    def get_name(self):
        if self.idpac:
            return self.idpac.first_name + " " + self.idpac.last_name
        return None


class Stomatolog(models.Model):
    idsto = models.OneToOneField(Korisnik, models.DO_NOTHING, db_column='idSto', primary_key=True)
    biografija = models.CharField(db_column='Biografija', max_length=1000)
    ordinacija = models.ForeignKey(Ordinacija, models.SET_NULL, null=True, db_column='Ordinacija')

    class Meta:
        db_table = 'stomatolog'

    def get_name(self):
        if self.idsto:
            return self.idsto.first_name + " " + self.idsto.last_name
        return None

class Usluga(models.Model):
    idusl = models.AutoField(db_column='idUsl', primary_key=True)
    naziv = models.CharField(db_column='Naziv', max_length=20)
    cena = models.IntegerField(db_column='Cena')
    opis = models.CharField(db_column='Opis', max_length=300)

    class Meta:
        db_table = 'usluga'


class Rezervacija(models.Model):
    idrez = models.AutoField(db_column='idRez', primary_key=True)
    stomatolog = models.ForeignKey(Stomatolog, models.SET_NULL, null=True, db_column='Stomatolog')
    pacijent = models.ForeignKey(Pacijent, models.SET_NULL, null=True, db_column='Pacijent')
    ordinacijarez = models.ForeignKey(Ordinacija, models.SET_NULL, null=True, db_column='OrdinacijaRez')
    usluga = models.ForeignKey(Usluga, models.SET_NULL, null=True, db_column='Usluga')
    datum = models.DateTimeField(db_column='Datum')
    vreme = models.IntegerField(db_column='Vreme')
    status = models.CharField(db_column='Status', max_length=10)

    stomatolog_ime = models.CharField(db_column='StomatologIme', max_length=50, default='')
    pacijent_ime = models.CharField(db_column='PacijentIme', max_length=50, default='')
    ordinacija_adresa = models.CharField(db_column='OrdinacijaIme', max_length=50, default='')

    class Meta:
        db_table = 'rezervacija'

    def save(self, *args, **kwargs):
        if self.stomatolog:
            self.stomatolog_ime = self.stomatolog.get_name()
        if self.pacijent:
            self.pacijent_ime = self.pacijent.get_name()
        if self.ordinacijarez:
            self.ordinacija_adresa = self.ordinacijarez.adresa

        super(Rezervacija, self).save(*args, **kwargs)
