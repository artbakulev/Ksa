from django import forms


class AnswerForm(forms.Form):
    text = forms.CharField(label='Your answer', max_length=100, widget=forms.Textarea(attrs={'rows': '3'}))


class EditProfileForm(forms.Form):
    login = forms.CharField(label='Login', required=False)
    email = forms.CharField(label='Email', required=False)
    first_name = forms.CharField(label='First name', required=False)
    last_name = forms.CharField(label='Last name', required=False)
    bio = forms.CharField(label='Bio', max_length=100, widget=forms.Textarea(attrs={'rows': '3'}), required=False)
    avatar = forms.ImageField(required=False)
