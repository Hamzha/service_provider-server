from unicodedata import name
from django import forms
from leads.models.service_category import ServiceCategory


class RegisterServiceCategory(forms.ModelForm):
    name = forms.CharField(
        widget=forms.TextInput(
            attrs={
                "placeholder": "Name",
                "class": "form-control"
            }
        ))

    class Meta:
        model = ServiceCategory
        fields = ('parent_id', 'name')
