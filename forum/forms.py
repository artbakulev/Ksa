from django import forms


class AnswerForm(forms.Form):
    text = forms.CharField(label='Your answer', max_length=100, widget=forms.Textarea(attrs={'rows': '3'}))


class RegistrationForm(forms.Form):
    first_name = forms.CharField(label='Enter first name', max_length=50)
    last_name = forms.CharField(label='Enter last name', max_length=50)
    email = forms.EmailField(label='Enter email', max_length=50)
    username = forms.CharField(label='Enter username', max_length=50)
    password = forms.CharField(label='Enter password', widget=forms.PasswordInput, max_length=50)
    repeated_password = forms.CharField(label='Repeat password', widget=forms.PasswordInput, max_length=50)


class EditProfileForm(forms.Form):
    username = forms.CharField(label='Username', required=False)
    email = forms.CharField(label='Email', required=False)
    first_name = forms.CharField(label='First name', required=False)
    last_name = forms.CharField(label='Last name', required=False)
    bio = forms.CharField(label='Bio', max_length=100, widget=forms.Textarea(attrs={'rows': '3'}), required=False)
    avatar = forms.ImageField(required=False)
