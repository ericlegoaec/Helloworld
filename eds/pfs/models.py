from django.db import models

# Create your models here.
class Portfolio(models.Model):
    pf_id = models.CharField(max_length=50)
    stock_id = models.CharField(max_length=50)
    quantity = models.IntegerField()
    date = models.DateField()
    price = models.DecimalField(max_digits=18, decimal_places=6)
    stock_sum = models.DecimalField(max_digits=18, decimal_places=6)
    app_fee = models.DecimalField(max_digits=18, decimal_places=6)
    
    def __unicode__(self):
        return unicode(self.pf_id)

class Trade(models.Model):
    pf_id = models.CharField(max_length=50)
    stock_id = models.CharField(max_length=50)
    quantity = models.IntegerField()
    date = models.DateField()
    price = models.DecimalField(max_digits=18, decimal_places=6)

    def __unicode__(self):
        return unicode(self.pf_id)

class Price(models.Model):
    stock_id = models.CharField(max_length=50)
    price = models.DecimalField(max_digits=18, decimal_places=6)
    date = models.DateField()

class Relatename(models.Model):
    stock_id = models.CharField(max_length=50)
    companyname = models.CharField(max_length=150)
    sector = models.CharField(max_length=150)
    industry = models.CharField(max_length=150)