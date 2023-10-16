from django import forms
from django.forms import ModelForm

from .models import Listing

class CreateListingForm(ModelForm):
    class Meta:
        model = Listing
        fields = ['category', 'title', 'description', 'starting_bid', 'image_data']
        widgets = {
            'category': forms.Select(attrs={'class': 'form-select fs-4 p-3', 'id': 'category', "required": "required",}),
            'title': forms.TextInput(attrs={'class': 'form-control fs-4 p-3', 'id': 'title', 'placeholder': '', "required": "required",}),
            'description': forms.Textarea(attrs={'class': 'form-control fs-4 p-3', 'id': 'description', "required": "required",}),
            'starting_bid': forms.NumberInput(attrs={'class': 'form-control fs-4 p-3', 'id': 'starting_bid', "required": "required",}),
            'image_data': forms.URLInput(attrs={'class': 'form-control fs-4 p-3', 'id': 'image_data'}),
        }
        
        
    