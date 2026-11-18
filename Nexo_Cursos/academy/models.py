from decimal import Decimal
import re
from urllib.parse import urlparse, parse_qs
from django.db import models
from django.contrib.auth.models import AbstractUser, BaseUserManager
from django.conf import settings
from django.core.validators import MinValueValidator


class UserManager(BaseUserManager):
    use_in_migrations = True
    def create_user(self, email, password=None, **extra):
        if not email:
            raise ValueError('Informe um e-mail.')
        user = self.model(email=email.strip().lower(), **extra)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password, **extra):
        extra.setdefault('is_staff', True)
        extra.setdefault('is_superuser', True)
        if not extra['is_staff'] or not extra['is_superuser']:
            raise ValueError('Administrador precisa das permissões administrativas.')
        return self.create_user(email, password, **extra)


class User(AbstractUser):
    username = None
    email = models.EmailField('e-mail', unique=True)
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['first_name']
    objects = UserManager()

    def save(self, *args, **kwargs):
        self.email = self.email.strip().lower()
        super().save(*args, **kwargs)


class Course(models.Model):
    CATEGORIES = [('tecnologia', 'Tecnologia'), ('negocios', 'Negócios'), ('criatividade', 'Criatividade'), ('estudos', 'Estudos')]
    THEMES = [('purple', 'Violeta'), ('green', 'Verde'), ('orange', 'Laranja'), ('blue', 'Azul')]
    title = models.CharField('título', max_length=150)
    slug = models.SlugField('endereço', unique=True, max_length=160)
    description = models.TextField('descrição')
    category = models.CharField('categoria', max_length=20, choices=CATEGORIES)
    theme = models.CharField('cor da capa', max_length=10, choices=THEMES, default='purple')
    price = models.DecimalField('preço em R$', max_digits=9, decimal_places=2, default=0, validators=[MinValueValidator(Decimal('0'))])
    published = models.BooleanField('publicado no catálogo', default=False)
    level = models.CharField('nível', max_length=50, default='Iniciante')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']
        constraints = [models.CheckConstraint(condition=models.Q(price__gte=0), name='nonnegative_course_price')]

    def __str__(self):
        return self.title


class Lesson(models.Model):
    course = models.ForeignKey(Course, related_name='lessons', on_delete=models.CASCADE)
    title = models.CharField('título da aula', max_length=180)
    module = models.CharField('módulo', max_length=100, default='Primeiros passos')
    position = models.PositiveIntegerField('ordem', default=1)
    minutes = models.PositiveIntegerField('duração estimada (min)', default=10)
    content = models.TextField('conteúdo da aula', blank=True)
    video_url = models.URLField('vídeo do YouTube ou Vimeo', blank=True)
    material_url = models.URLField('link HTTPS do material complementar', blank=True)
    published = models.BooleanField('aula publicada', default=False)

    class Meta:
        ordering = ['position', 'id']

    @property
    def embed_url(self):
        if not self.video_url:
            return ''
        p = urlparse(self.video_url)
        host = (p.hostname or '').lower()
        if host in ('youtu.be', 'www.youtu.be'):
            ident = p.path.strip('/')
        elif host in ('youtube.com', 'www.youtube.com', 'm.youtube.com'):
            ident = parse_qs(p.query).get('v', [''])[0]
            if p.path.startswith(('/embed/', '/shorts/')):
                ident = p.path.split('/')[2]
        elif host in ('vimeo.com', 'www.vimeo.com'):
            ident = p.path.strip('/')
            return 'https://player.vimeo.com/video/' + ident if ident.isdigit() else ''
        else:
            return ''
        return 'https://www.youtube-nocookie.com/embed/' + ident if re.fullmatch(r'[A-Za-z0-9_-]{11}', ident) else ''

    def __str__(self):
        return self.title


class Enrollment(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='enrollments')
    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name='enrollments')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        constraints = [models.UniqueConstraint(fields=['user', 'course'], name='one_enrollment')]


class Progress(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    lesson = models.ForeignKey(Lesson, on_delete=models.CASCADE)
    completed_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        constraints = [models.UniqueConstraint(fields=['user', 'lesson'], name='one_completion')]


class LoginAttempt(models.Model):
    key = models.CharField(max_length=64, unique=True)
    count = models.PositiveIntegerField(default=0)
    since = models.DateTimeField()
