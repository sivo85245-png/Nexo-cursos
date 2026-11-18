from django import forms
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm, PasswordResetForm
from django.core.exceptions import ValidationError
from .models import User, Course, Lesson
from urllib.parse import urlparse


class SignupForm(UserCreationForm):
    first_name = forms.CharField(label='Seu nome', max_length=150)
    email = forms.EmailField(label='E-mail')
    class Meta:
        model = User
        fields = ['first_name', 'email', 'password1', 'password2']

    def clean_email(self):
        email = self.cleaned_data['email'].strip().lower()
        if User.objects.filter(email__iexact=email).exists():
            raise ValidationError('Este e-mail já possui uma conta. Entre ou recupere sua senha.')
        return email


class EmailLoginForm(AuthenticationForm):
    username = forms.EmailField(label='E-mail', widget=forms.EmailInput(attrs={'autocomplete': 'email'}))
    def clean_username(self):
        return self.cleaned_data['username'].strip().lower()


class CourseForm(forms.ModelForm):
    class Meta:
        model = Course
        fields = ['title', 'slug', 'description', 'category', 'theme', 'level', 'price', 'published']
        widgets = {'description': forms.Textarea(attrs={'rows': 5})}


class LessonForm(forms.ModelForm):
    class Meta:
        model = Lesson
        fields = ['title', 'module', 'position', 'minutes', 'content', 'video_url', 'material_url', 'published']
        widgets = {'content': forms.Textarea(attrs={'rows': 14})}

    def clean_video_url(self):
        value = self.cleaned_data['video_url']
        if value:
            if urlparse(value).scheme != 'https' or not Lesson(video_url=value).embed_url:
                raise ValidationError('Use um link HTTPS de vídeo do YouTube ou Vimeo com identificador válido.')
        return value

    def clean_material_url(self):
        value = self.cleaned_data['material_url']
        if value and urlparse(value).scheme != 'https':
            raise ValidationError('Use um link HTTPS para o material.')
        return value

    def clean(self):
        data = super().clean()
        if not data.get('content', '').strip() and not data.get('video_url'):
            raise ValidationError('Adicione o texto da aula ou um vídeo.')
        return data


class AccessForm(forms.Form):
    email = forms.EmailField(label='E-mail do aluno já cadastrado')
