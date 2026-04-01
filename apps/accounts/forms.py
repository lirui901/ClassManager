from django import forms
from django.contrib.auth.forms import AuthenticationForm, UserCreationForm
from .models import User

class LoginForm(AuthenticationForm):
    username = forms.CharField(
        label='用户名',
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': '请输入用户名'})
    )
    password = forms.CharField(
        label='密码',
        widget=forms.PasswordInput(attrs={'class': 'form-control', 'placeholder': '请输入密码'})
    )

class RegisterForm(UserCreationForm):
    username = forms.CharField(
        label='用户名',
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': '请输入用户名'})
    )
    password1 = forms.CharField(
        label='密码',
        widget=forms.PasswordInput(attrs={'class': 'form-control', 'placeholder': '请输入密码'})
    )
    password2 = forms.CharField(
        label='确认密码',
        widget=forms.PasswordInput(attrs={'class': 'form-control', 'placeholder': '请再次输入密码'})
    )
    phone = forms.CharField(
        label='手机号',
        required=False,
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': '请输入手机号'})
    )
    
    class Meta:
        model = User
        fields = ('username', 'password1', 'password2', 'phone')
    
    def save(self, commit=True):
        user = super().save(commit=False)
        user.phone = self.cleaned_data['phone']
        if commit:
            user.save()
        return user