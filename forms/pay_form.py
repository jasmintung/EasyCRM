from django.forms import ModelForm
from django import forms
from repository import models


class PaymentRecordForm(ModelForm):
    class Meta:
        model = models.PaymentRecord
        fields = '__all__'
