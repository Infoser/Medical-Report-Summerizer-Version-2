from django import forms

class UploadForm(forms.Form):
    file = forms.FileField(required=True)
    age = forms.IntegerField(required=False)
    gender = forms.ChoiceField(choices=[('', '---'), ('M','Male'),('F','Female'),('O','Other')], required=False)
