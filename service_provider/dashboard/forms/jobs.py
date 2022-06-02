from unicodedata import name
from django import forms
from leads.models.job import Job
from .widgets import DatePickerInput, TimePickerInput, DateTimePickerInput

STATE_CHOICES = [
    ('1', 'PENDING'),
    ('2', 'COMPLETE'),
    ('3', 'INCOMPLETE'),
    ('4', 'CANCELED'),
]


class RegisterJobs(forms.ModelForm):

    state = forms.CharField(
        required=True,
        widget=forms.Select(
            attrs={
                "placeholder": "state",
                "class": "form-control"
            }, choices=STATE_CHOICES
        )
    )
    start_datetime = forms.DateTimeField(
        required=True,
        input_formats=["%Y-%m-%dT%H:%M", ],
        widget=DateTimePickerInput(
            attrs={
                "placeholder": "Enter Start Date and time",
                "class": "form-control datetimepicker-input"
            }
        ))
    end_datetime = forms.DateTimeField(
        required=True,
        input_formats=["%Y-%m-%dT%H:%M"],
        widget=DateTimePickerInput(
            attrs={
                "placeholder": "Enter End Date and time",
                "class": "form-control datetimepicker-input"
            }
        ))

    class Meta:
        model = Job
        fields = ('start_datetime', 'end_datetime', 'state')
