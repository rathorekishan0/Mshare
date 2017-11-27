from django.contrib.auth.models import User
from django import forms
from .models import userprofile,music

# class UserForm(forms.ModelForm):
#     password=forms.CharField(widget=forms.PasswordInput)
#     class Meta:
#         model=User
#         fields=['username','email','password']


class profileform(forms.ModelForm):
    class Meta:
        model=userprofile
        fields=['name','userphoto','prefferedgenre','description']


class musicform(forms.ModelForm):
    class Meta:
        model=music
        fields=[
        'songname','description','genre','songphoto','songupload','public'
        ]
    # def __init__(self,user=None,*args,**kwargs):
    #     super(musicform,self).__init__(*args,**kwargs)
    #     self.fields['artist'].queryset=music.objects.filter(artist=user)

class UserRegisterForm(forms.ModelForm):
    """A form for creating new users. Includes all the required
    fields, plus a repeated password."""
    password1 = forms.CharField(label='Password', widget=forms.PasswordInput)
    password2 = forms.CharField(label='Password confirmation', widget=forms.PasswordInput)

    class Meta:
        model = User
        fields = ('username', 'email',)
    def clean_email(self):
        email=self.cleaned_data.get('email')
        qs=User.objects.filter(email__iexact=email)
        if qs.exists():
            raise forms.ValidationError("email already has a account")
        return email
    def clean_password2(self):
        # Check that the two password entries match
        password1 = self.cleaned_data.get("password1")
        password2 = self.cleaned_data.get("password2")
        if password1 and password2 and password1 != password2:
            raise forms.ValidationError("Passwords don't match")
        return password2

    def save(self, commit=True):
        # Save the provided password in hashed format
        user = super(UserRegisterForm, self).save(commit=False)
        user.set_password(self.cleaned_data["password1"])
        user.is_active = False
        # create a new user hash for activating email.

        if commit:
            user.save()
            user.userprofile.send_activation_email()
        return user