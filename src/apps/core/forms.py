from django import forms
from .models import Audiobook

class AudiobookForm(forms.ModelForm):
    class Meta:
        model = Audiobook
        fields = ['title', 'author', 'series', 'narrator', 'status']
        widgets = {
            'title': forms.TextInput(attrs={'class': 'form-control'}),
            'author': forms.TextInput(attrs={'class': 'form-control'}),
            'series': forms.TextInput(attrs={'class': 'form-control'}),
            'narrator': forms.TextInput(attrs={'class': 'form-control'}),
            'status': forms.Select(attrs={'class': 'form-control'}),
        }