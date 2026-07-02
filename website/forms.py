from django import forms


class ContactForm(forms.Form):
    name = forms.CharField(max_length=120)
    email = forms.EmailField(max_length=254)
    phone = forms.CharField(max_length=40, required=False)
    message = forms.CharField(widget=forms.Textarea, max_length=2000)
