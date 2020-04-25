from django import forms
from captcha.fields import CaptchaField

class CaptchaForms(forms.Form):
    captcha = CaptchaField(label="")