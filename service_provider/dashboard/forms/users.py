# pylint: disable=missing-class-docstring
from unicodedata import name
from django import forms
from authorization.models.user import User

GENDER_CHOICES = [
    ('0', 'None.'),
    ('1', 'Male.'),
    ('2', 'Female.'),
    ('3', 'Not Specify.'),
]
TYPE_CHOICES = [
    ('0', 'None.'),
    ('1', 'Vendor.'),
    ('2', 'Client.'),
    ('3', 'Admin.'),
]
STATUS_CHOICES = [
    ('0', 'None.'),
    ('1', 'Inactive.'),
    ('2', 'Active.'),
    ('3', 'Pending.'),
]


class RegisterForm(forms.ModelForm):
    status = forms.CharField(
        required=False,
        widget=forms.Select(
            attrs={
                "placeholder": "status",
                "class": "form-control"
            }, choices=STATUS_CHOICES
        )
    )

    type = forms.CharField(
        widget=forms.Select(
            attrs={
                "placeholder": "type",
                "class": "form-control"
            }, choices=TYPE_CHOICES
        )
    )
    gender = forms.CharField(
        widget=forms.Select(
            attrs={
                "placeholder": "gender",
                "class": "form-control"
            }, choices=GENDER_CHOICES
        )
    )
    first_name = forms.CharField(
        widget=forms.TextInput(
            attrs={
                "placeholder": "First Name",
                "class": "form-control"
            }
        ))
    home_address = forms.CharField(
        required=False,
        widget=forms.TextInput(
            attrs={
                "placeholder": "home_address",
                "class": "form-control"
            }
        ))
    street_address = forms.CharField(
        required=False,
        widget=forms.TextInput(
            attrs={
                "placeholder": "street_address",
                "class": "form-control"
            }
        ))
    apartment = forms.CharField(
        required=False,
        widget=forms.TextInput(
            attrs={
                "placeholder": "home_address",
                "class": "form-control"
            }
        ))
    zipcode = forms.CharField(
        required=False,
        widget=forms.NumberInput(
            attrs={
                "placeholder": "Zip Code",
                "class": "form-control"
            }
        ))
    last_name = forms.CharField(
        widget=forms.TextInput(
            attrs={
                "placeholder": "Last Name",
                "class": "form-control"
            }
        ))
    email = forms.EmailField(
        widget=forms.EmailInput(
            attrs={
                "placeholder": "Email",
                "class": "form-control"
            }
        ))
    password = forms.CharField(
        widget=forms.PasswordInput(
            attrs={
                "placeholder": "Password",
                "class": "form-control"

            }
        ))
    # date_of_birth = forms.DateTimeField(
    #     widget=forms.DateTimeInput(
    #         attrs={
    #             "placeholder": "Date of Birth",
    #             "class": "form-control"
    #         }
    #     ))
    phone_number = forms.CharField(
        widget=forms.TextInput(
            attrs={
                "placeholder": "Phone Number",
                "class": "form-control",
                'name': "phone_number",
                "id": "phone",
            }
        ))

    def clean_email(self):
        try:
            User.objects.get(email__iexact=self.cleaned_data['email'])
        except User.DoesNotExist:
            return self.cleaned_data['email']
        raise forms.ValidationError(
            ("The email already exists. Please try another one."))

    def clean_phone_number(self):
        try:
            User.objects.get(
                phone_number__iexact=self.cleaned_data['phone_number'])
        except User.DoesNotExist:
            return self.cleaned_data['phone_number']
        raise forms.ValidationError(
            ("The Phone Number already exists. Please try another one."))

    class Meta:
        model = User
        fields = ('email', 'password', 'first_name', 'last_name',  'status', 'phone_number',  'gender', "type",
                  'zipcode', 'apartment', 'street_address', 'home_address')


# class UserEdit(forms.ModelForm):
#     first_name = forms.CharField(
#         widget=forms.TextInput(
#             attrs={
#                 "placeholder": "FirstName",
#                 "class": "form-control"
#             }
#         ))
#     last_name = forms.CharField(
#         widget=forms.TextInput(
#             attrs={
#                 "placeholder": "LastName",
#                 "class": "form-control"
#             }
#         ))
#     username = forms.CharField(
#         widget=forms.TextInput(
#             attrs={
#                 "placeholder": "Username",
#                 "class": "form-control"
#             }
#         ))

#     class Meta:
#         model = User
#         fields = ('username', 'first_name', 'last_name')


class LoginForm(forms.Form):
    email = forms.CharField(
        widget=forms.TextInput(
            attrs={
                "placeholder": "Email",
                "class": "form-control"
            }
        ))
    password = forms.CharField(
        widget=forms.PasswordInput(
            attrs={
                "placeholder": "Password",
                "class": "form-control"
            }
        ))


# class SignUpForm(Model):
#     username = forms.CharField(
#         widget=forms.TextInput(
#             attrs={
#                 "placeholder": "Username",
#                 "class": "form-control"
#             }
#         ))
#     email = forms.EmailField(
#         widget=forms.EmailInput(
#             attrs={
#                 "placeholder": "Email",
#                 "class": "form-control"
#             }
#         ))
#     password1 = forms.CharField(
#         widget=forms.PasswordInput(
#             attrs={
#                 "placeholder": "Password",
#                 "class": "form-control"
#             }
#         ))
#     password2 = forms.CharField(
#         widget=forms.PasswordInput(
#             attrs={
#                 "placeholder": "Password check",
#                 "class": "form-control"
#             }
#         ))

#     class Meta:
#         model = User
#         fields = ('username', 'email', 'password', 'password2')
