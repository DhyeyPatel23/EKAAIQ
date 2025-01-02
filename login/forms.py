from django import forms
from django.contrib.auth.forms import UserCreationForm
from .models import User
from django.contrib.auth.forms import AuthenticationForm
from django.core.exceptions import ValidationError
from django.contrib.auth import get_user_model
import re
from django.contrib.auth.hashers import check_password

User = get_user_model()

# class StudentSignUpForm(UserCreationForm):
#     prn = forms.CharField(max_length=12, help_text='Enter your unique PRN')
#     email = forms.EmailField(
#         label="Email",
#         widget=forms.EmailInput(attrs={"class": "form-control", "placeholder": "Email"})
#     )

#     class Meta:
#         model = User
#         fields = ['username', 'email', 'prn', 'password1', 'password2']

#     def clean_prn(self):
#         prn = self.cleaned_data.get('prn')
#         if User.objects.filter(prn=prn).exists():
#             raise forms.ValidationError("PRN already exists")
#         return prn

#     def clean_username(self):
#         username = self.cleaned_data.get('username')
#         if any(char.isdigit() for char in username):
#             raise forms.ValidationError('Username should not contain numbers.')
#         if User.objects.filter(username=username).exists():
#             raise ValidationError("This username is already taken. Please choose a different one.")
#         return username

#     def clean_email(self):
#         email = self.cleaned_data.get('email')
#         if User.objects.filter(email=email).exists():
#             raise ValidationError("This email is already registered. Please use a different one.")
#         return email

#     def clean_password2(self):
#         password1 = self.cleaned_data.get('password1')
#         password2 = self.cleaned_data.get('password2')
        
#         if password1 and password2 and password1 != password2:
#             raise ValidationError("Passwords do not match.")
        
#         if len(password1) < 8:
#             raise ValidationError("Password must be at least 8 characters long.")
        
#         if not re.search(r'[A-Z]', password1):
#             raise ValidationError("Password must contain at least one uppercase letter.")
        
#         if not re.search(r'[a-z]', password1):
#             raise ValidationError("Password must contain at least one lowercase letter.")
        
#         if not re.search(r'\d', password1):
#             raise ValidationError("Password must contain at least one digit.")
        
#         if not re.search(r'[!@#$%^&*(),.?":{}|<>]', password1):
#             raise ValidationError("Password must contain at least one special character.")
        
#         return password2

#     def save(self, commit=True):
#         user = super().save(commit=False)
#         user.is_student = True
#         if commit:
#             user.save()
#         return user
###########################################################################################################
class StudentSignUpForm(UserCreationForm):
    prn = forms.CharField(max_length=12, help_text='Enter your unique PRN')
    first_name = forms.CharField(max_length=30, required=True, help_text='Enter your first name')
    last_name = forms.CharField(max_length=30, required=True, help_text='Enter your last name')
    email = forms.EmailField(
        label="Email",
        widget=forms.EmailInput(attrs={"class": "form-control", "placeholder": "Email"})
    )

    class Meta:
        model = User
        fields = ['first_name', 'last_name', 'email', 'prn', 'password1', 'password2', 'gender']

    def clean_prn(self):
        prn = self.cleaned_data.get('prn')
        if User.objects.filter(prn=prn).exists():
            raise forms.ValidationError("PRN already exists")
        return prn

    def clean_email(self):
        email = self.cleaned_data.get('email')

        # Allowed email domains
        allowed_domains = ['gmail.com', 'outlook.com', 'yahoo.com']
        domain_regex = r'@([a-zA-Z0-9.-]+)$'

        # Extract domain from the email
        domain_match = re.search(domain_regex, email)
        if not domain_match:
            raise ValidationError("Enter a valid email address.")

        domain = domain_match.group(1)

        # Check if the domain is in the allowed list
        if domain not in allowed_domains:
            raise ValidationError(f"Email domain '{domain}' is not allowed. Please use Gmail, Outlook, or Yahoo.")

        # Check if the email is already registered
        if User.objects.filter(email=email).exists():
            raise ValidationError("This email is already registered. Please use a different one.")

        return email

    def clean_password2(self):
        password1 = self.cleaned_data.get('password1')
        password2 = self.cleaned_data.get('password2')
        
        if password1 and password2 and password1 != password2:
            raise ValidationError("Passwords do not match.")
        
        if len(password1) < 8:
            raise ValidationError("Password must be at least 8 characters long.")
        
        if not re.search(r'[A-Z]', password1):
            raise ValidationError("Password must contain at least one uppercase letter.")
        
        if not re.search(r'[a-z]', password1):
            raise ValidationError("Password must contain at least one lowercase letter.")
        
        if not re.search(r'\d', password1):
            raise ValidationError("Password must contain at least one digit.")
        
        if not re.search(r'[!@#$%^&*(),.?":{}|<>]', password1):
            raise ValidationError("Password must contain at least one special character.")
        
        return password2

    def save(self, commit=True):
        user = super().save(commit=False)
        user.is_student = True
        user.first_name = self.cleaned_data.get('first_name')
        user.last_name = self.cleaned_data.get('last_name')
        if commit:
            user.save()
        return user

class TeacherSignUpForm(UserCreationForm):
    first_name = forms.CharField(max_length=30, required=True, help_text='Enter your first name')
    last_name = forms.CharField(max_length=30, required=True, help_text='Enter your last name')
    email = forms.EmailField(
        label="Email",
        widget=forms.EmailInput(attrs={"class": "form-control", "placeholder": "Email"})
    )

    class Meta:
        model = User
        fields = ['first_name', 'last_name', 'email', 'password1', 'password2', 'gender']

    def clean_email(self):
        email = self.cleaned_data.get('email')

        # Allowed email domains
        allowed_domains = ['gmail.com', 'outlook.com', 'yahoo.com']
        domain_regex = r'@([a-zA-Z0-9.-]+)$'

        # Extract domain from the email
        domain_match = re.search(domain_regex, email)
        if not domain_match:
            raise ValidationError("Enter a valid email address.")

        domain = domain_match.group(1)

        # Check if the domain is in the allowed list
        if domain not in allowed_domains:
            raise ValidationError(f"Email domain '{domain}' is not allowed. Please use Gmail, Outlook, or Yahoo.")

        # Check if the email is already registered
        if User.objects.filter(email=email).exists():
            raise ValidationError("This email is already registered. Please use a different one.")

        return email

    def clean_password2(self):
        password1 = self.cleaned_data.get('password1')
        password2 = self.cleaned_data.get('password2')
        
        if password1 and password2 and password1 != password2:
            raise ValidationError("Passwords do not match.")
        
        if len(password1) < 8:
            raise ValidationError("Password must be at least 8 characters long.")
        
        if not re.search(r'[A-Z]', password1):
            raise ValidationError("Password must contain at least one uppercase letter.")
        
        if not re.search(r'[a-z]', password1):
            raise ValidationError("Password must contain at least one lowercase letter.")
        
        if not re.search(r'\d', password1):
            raise ValidationError("Password must contain at least one digit.")
        
        if not re.search(r'[!@#$%^&*(),.?":{}|<>]', password1):
            raise ValidationError("Password must contain at least one special character.")
        
        return password2

    def save(self, commit=True):
        user = super().save(commit=False)
        user.is_teacher = True
        user.first_name = self.cleaned_data.get('first_name')
        user.last_name = self.cleaned_data.get('last_name')
        if commit:
            user.save()
        return user







# class TeacherSignUpForm(UserCreationForm):
#     email = forms.EmailField(
#         label="Email",
#         widget=forms.EmailInput(attrs={"class": "form-control", "placeholder": "Email"})
#     )

#     class Meta:
#         model = User
#         fields = ['username', 'email', 'password1', 'password2']

#     def clean_username(self):
#         username = self.cleaned_data.get('username')
#         if User.objects.filter(username=username).exists():
#             raise ValidationError("This username is already taken. Please choose a different one.")
#         return username

#     def clean_email(self):
#         email = self.cleaned_data.get('email')
#         if User.objects.filter(email=email).exists():
#             raise ValidationError("This email is already registered. Please use a different one.")
#         return email

#     def clean_password2(self):
#         password1 = self.cleaned_data.get('password1')
#         password2 = self.cleaned_data.get('password2')
        
#         if password1 and password2 and password1 != password2:
#             raise ValidationError("Passwords do not match.")
        
#         if len(password1) < 8:
#             raise ValidationError("Password must be at least 8 characters long.")
        
#         if not re.search(r'[A-Z]', password1):
#             raise ValidationError("Password must contain at least one uppercase letter.")
        
#         if not re.search(r'[a-z]', password1):
#             raise ValidationError("Password must contain at least one lowercase letter.")
        
#         if not re.search(r'\d', password1):
#             raise ValidationError("Password must contain at least one digit.")
        
#         if not re.search(r'[!@#$%^&*(),.?":{}|<>]', password1):
#             raise ValidationError("Password must contain at least one special character.")
        
#         return password2

#     def save(self, commit=True):
#         user = super().save(commit=False)
#         user.is_teacher = True
#         if commit:
#             user.save()
#         return user
   
class CustomLoginForm(forms.Form):
    email = forms.EmailField(label="Email", max_length=254, required=True)
    password = forms.CharField(widget=forms.PasswordInput)

    def clean(self):
        cleaned_data = super().clean()
        email = cleaned_data.get('email')
        password = cleaned_data.get('password')

        # Add any additional validation if needed
        return cleaned_data


class ProfileForm(forms.ModelForm):
    password = forms.CharField(widget=forms.PasswordInput, required=False, label='New Password')

    class Meta:
        model = User
        fields = ['profile_picture', 'gender', 'location', 'password', 'email', 'first_name', 'last_name']

    def clean_password(self):
        password = self.cleaned_data.get('password')
        if password and len(password) < 8:
            raise forms.ValidationError("Password must be at least 8 characters long.")
        return password

class UserProfileUpdateForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ['location', 'profile_picture']



class ChangePasswordForm(forms.Form):
    new_password = forms.CharField(label="New Password", widget=forms.PasswordInput(), required=True)
    confirm_password = forms.CharField(label="Confirm Password", widget=forms.PasswordInput(), required=True)

    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop('user', None)  # Pass user from view
        super(ChangePasswordForm, self).__init__(*args, **kwargs)

    def clean_new_password(self):
        new_password = self.cleaned_data.get('new_password')

        # Check if new password matches current password
        if self.user and check_password(new_password, self.user.password):
            raise forms.ValidationError('Do not enter your current password as the new password.')

        # Additional password validations
        if len(new_password) < 8:
            raise forms.ValidationError("Password must be at least 8 characters long.")
        if not re.search(r'[A-Z]', new_password):
            raise forms.ValidationError("Password must contain at least one uppercase letter.")
        if not re.search(r'[a-z]', new_password):
            raise forms.ValidationError("Password must contain at least one lowercase letter.")
        if not re.search(r'\d', new_password):
            raise forms.ValidationError("Password must contain at least one digit.")
        if not re.search(r'[!@#$%^&*(),.?":{}|<>]', new_password):
            raise forms.ValidationError("Password must contain at least one special character.")

        return new_password

    def clean(self):
        cleaned_data = super().clean()
        new_password = cleaned_data.get('new_password')
        confirm_password = cleaned_data.get('confirm_password')

        if new_password and confirm_password and new_password != confirm_password:
            raise forms.ValidationError("Passwords do not match.")

        return cleaned_data

class ForgotPasswordForm(forms.Form):
    email = forms.EmailField(label="Email", required=True)

    def clean_email(self):
        email = self.cleaned_data.get('email')

        # Check if the email is valid
        if not email:
            raise forms.ValidationError("Please enter a valid email address.")

        # Check if the email exists in the User model
        if not User.objects.filter(email=email).exists():
            raise forms.ValidationError("There is no account associated with this email.")

        return email
