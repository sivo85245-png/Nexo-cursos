import hashlib
from datetime import timedelta
from django.conf import settings
from django.contrib import messages
from django.contrib.auth import login
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib.auth.views import LoginView
from django.db.models import Count, Q
from django.shortcuts import get_object_or_404, redirect, render
from django.utils import timezone
from django.views.decorators.http import require_POST
from .forms import SignupForm, EmailLoginForm, CourseForm, LessonForm, AccessForm
from .models import User, Course, Lesson, Enrollment, Progress, LoginAttempt

staff_required = user_passes_test(lambda u: u.is_active and u.is_staff)

class SigninView(LoginView):
    template_name = 'registration/login.html'
    authentication_form = EmailLoginForm

    def post(self, request, *args, **kwargs):
        identity = request.POST.get('username', '').strip().lower()
        self.attempt_key = hashlib.sha256((settings.SECRET_KEY + identity).encode()).hexdigest()
        attempt = LoginAttempt.objects.filter(key=self.attempt_key).first()
        if attempt and attempt.since < timezone.now() - timedelta(minutes=15):
            attempt.delete()
            attempt = None
        if attempt and attempt.count >= 8:
            form = self.get_form()
            form.add_error(None, 'Muitas tentativas. Aguarda 15 minutos antes de tentar novamente.')
            return self.render_to_response(self.get_context_data(form=form), status=429)
        return super().post(request, *args, **kwargs)

    def form_invalid(self, form):
        from django.db.models import F
        attempt, _ = LoginAttempt.objects.get_or_create(key=self.attempt_key, defaults={'since': timezone.now()})
        LoginAttempt.objects.filter(pk=attempt.pk).update(count=F('count') + 1)
        return super().form_invalid(form)

    def form_valid(self, form):
        LoginAttempt.objects.filter(key=self.attempt_key).delete()
        return super().form_valid(form)

def home(request):
    courses = Course.objects.filter(published=True).annotate(lesson_count=Count('lessons', filter=Q(lessons__published=True)))
    q = request.GET.get('q', '').strip()
    category = request.GET.get('category', '')
    if q:
        courses = courses.filter(title__icontains=q)
    if category:
        courses = courses.filter(category=category)
    if request.GET.get('free') == '1':
        courses = courses.filter(price=0)
    return render(request, 'home.html', {'courses': courses, 'categories': Course.CATEGORIES, 'q': q, 'category': category})

def signup(request):
    form = SignupForm(request.POST or None)
    if request.method == 'POST' and form.is_valid():
        user = form.save()
        login(request, user)
        return redirect('dashboard')
    return render(request, 'form.html', {'form': form, 'title': 'O teu próximo passo começa aqui.', 'eyebrow': 'CRIA A TUA CONTA', 'button': 'Criar conta gratuita'})

def course_detail(request, slug):
    course = get_object_or_404(Course, slug=slug, published=True)
    enrolled = request.user.is_authenticated and Enrollment.objects.filter(user=request.user, course=course).exists()
    return render(request, 'course.html', {'course': course, 'lessons': course.lessons.filter(published=True), 'enrolled': enrolled})

@login_required
@require_POST
def enroll(request, slug):
    course = get_object_or_404(Course, slug=slug, published=True)
    if course.price > 0:
        messages.info(request, 'As inscrições pagas ainda não estão disponíveis. Nenhuma cobrança foi feita.')
        return redirect('course', slug=slug)
    Enrollment.objects.get_or_create(user=request.user, course=course)
    messages.success(request, 'Inscrição concluída. Bom estudo!')
    return redirect('course', slug=slug)

@login_required
def dashboard(request):
    rows = []
    for enrollment in request.user.enrollments.select_related('course').filter(course__published=True):
        lessons = enrollment.course.lessons.filter(published=True)
        total = lessons.count()
        done = Progress.objects.filter(user=request.user, lesson__in=lessons).count()
        next_lesson = lessons.exclude(progress__user=request.user).first() or lessons.first()
        rows.append({'course': enrollment.course, 'total': total, 'done': done, 'percent': round(done / total * 100) if total else 0, 'next': next_lesson})
    return render(request, 'dashboard.html', {'rows': rows})

@login_required
def lesson_detail(request, pk):
    lesson = get_object_or_404(Lesson.objects.select_related('course'), pk=pk, published=True, course__published=True)
    if not request.user.is_staff and not Enrollment.objects.filter(user=request.user, course=lesson.course).exists():
        messages.info(request, 'Inscreve-te no curso para abrir as aulas.')
        return redirect('course', slug=lesson.course.slug)
    return render(request, 'lesson.html', {'lesson': lesson, 'lessons': lesson.course.lessons.filter(published=True), 'done': Progress.objects.filter(user=request.user, lesson=lesson).exists()})

@login_required
@require_POST
def complete(request, pk):
    lesson = get_object_or_404(Lesson, pk=pk, published=True, course__published=True)
    get_object_or_404(Enrollment, user=request.user, course=lesson.course)
    if request.POST.get('undo'):
        Progress.objects.filter(user=request.user, lesson=lesson).delete()
    else:
        Progress.objects.get_or_create(user=request.user, lesson=lesson)
    return redirect('lesson', pk=pk)

@staff_required
def studio(request):
    return render(request, 'studio.html', {'courses': Course.objects.annotate(student_count=Count('enrollments', distinct=True)), 'students': User.objects.filter(is_staff=False).count()})

@staff_required
def edit_course(request, pk=None):
    course = get_object_or_404(Course, pk=pk) if pk else None
    form = CourseForm(request.POST or None, instance=course)
    if request.method == 'POST' and form.is_valid():
        course = form.save()
        messages.success(request, 'Curso guardado.')
        return redirect('edit_course', pk=course.pk)
    return render(request, 'edit_course.html', {'form': form, 'course': course})

@staff_required
def edit_lesson(request, course_pk, pk=None):
    course = get_object_or_404(Course, pk=course_pk)
    lesson = get_object_or_404(Lesson, pk=pk, course=course) if pk else None
    form = LessonForm(request.POST or None, instance=lesson)
    if request.method == 'POST' and form.is_valid():
        obj = form.save(commit=False)
        obj.course = course
        obj.save()
        messages.success(request, 'Aula guardada.')
        return redirect('edit_course', pk=course.pk)
    return render(request, 'form.html', {'form': form, 'title': 'Editar aula' if pk else 'Nova aula', 'eyebrow': course.title, 'button': 'Guardar aula'})

@staff_required
def grant_access(request, pk):
    course = get_object_or_404(Course, pk=pk)
    form = AccessForm(request.POST or None)
    if request.method == 'POST' and form.is_valid():
        user = User.objects.filter(email__iexact=form.cleaned_data['email']).first()
        if not user:
            form.add_error('email', 'O aluno precisa criar uma conta primeiro.')
        else:
            Enrollment.objects.get_or_create(user=user, course=course)
            messages.success(request, 'Acesso concedido ao aluno.')
            return redirect('studio')
    return render(request, 'form.html', {'form': form, 'title': 'Conceder acesso', 'eyebrow': course.title, 'button': 'Autorizar aluno'})
