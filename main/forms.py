from django import forms
from phonenumber_field.formfields import PhoneNumberField
from .models import Advertisement, Comment

class AdvertisementForm(forms.ModelForm):
    phone_number = PhoneNumberField(help_text="Telefon numaranızı uluslararası formatta yazın.")
    
    class Meta:
        model = Advertisement
        fields = ['title', 'description', 'price', 'image', 'phone_number']

class CommentForm(forms.ModelForm):
    class Meta:
        model = Comment
        fields = ['content']