from django.test import TestCase, Client, override_settings
from django.urls import reverse
from django.core import mail
from .models import User, Course, Lesson, Enrollment, Progress

@override_settings(EMAIL_BACKEND='django.core.mail.backends.locmem.EmailBackend')
class PlatformTests(TestCase):
    def setUp(self):
        self.student = User.objects.create_user('aluno@example.com', 'UmaSenha!Longa2026', first_name='Ana')
        self.other = User.objects.create_user('outro@example.com', 'UmaSenha!Longa2026', first_name='Bia')
        self.staff = User.objects.create_superuser('admin@example.com', 'UmaSenha!Longa2026', first_name='Admin')
        self.free = Course.objects.create(title='Curso aberto', slug='aberto', category='tecnologia', published=True)
        self.paid = Course.objects.create(title='Curso pago', slug='pago', category='estudos', price=49, published=True)
        self.lesson = Lesson.objects.create(course=self.free, title='Primeira aula', content='Conteúdo exclusivo', published=True)

    def test_signup_hashes_password_and_cannot_elevate_permissions(self):
        response = self.client.post(reverse('signup'), {'first_name':'Novo','email':'NOVO@example.com','password1':'OutraSenha!9345','password2':'OutraSenha!9345','is_staff':'True'})
        self.assertEqual(response.status_code, 302)
        user = User.objects.get(email='novo@example.com')
        self.assertTrue(user.check_password('OutraSenha!9345'))
        self.assertNotEqual(user.password, 'OutraSenha!9345')
        self.assertFalse(user.is_staff)

    def test_login_logout_and_rate_limit(self):
        self.assertRedirects(self.client.post(reverse('login'), {'username':'ALUNO@example.com','password':'UmaSenha!Longa2026'}), reverse('dashboard'))
        self.assertEqual(self.client.get(reverse('logout')).status_code, 405)
        self.client.post(reverse('logout'))
        for _ in range(8):
            self.client.post(reverse('login'), {'username':'aluno@example.com','password':'errada'})
        self.assertEqual(self.client.post(reverse('login'), {'username':'aluno@example.com','password':'errada'}).status_code, 429)

    def test_enrollment_and_isolated_progress(self):
        self.client.force_login(self.student)
        self.assertEqual(self.client.get(reverse('enroll', args=[self.free.slug])).status_code, 405)
        self.client.post(reverse('enroll', args=[self.free.slug]))
        self.client.post(reverse('complete', args=[self.lesson.pk]))
        self.client.post(reverse('complete', args=[self.lesson.pk]))
        self.assertEqual(Progress.objects.count(), 1)
        self.assertContains(self.client.get(reverse('dashboard')), '100% concluído')
        self.client.force_login(self.other)
        self.client.post(reverse('enroll', args=[self.free.slug]))
        self.assertContains(self.client.get(reverse('dashboard')), '0% concluído')
        self.assertEqual(Progress.objects.filter(user=self.other).count(), 0)

    def test_paid_and_unenrolled_content_are_protected(self):
        self.client.force_login(self.student)
        self.client.post(reverse('enroll', args=[self.paid.slug]))
        self.assertFalse(Enrollment.objects.filter(user=self.student).exists())
        response = self.client.get(reverse('lesson', args=[self.lesson.pk]))
        self.assertEqual(response.status_code, 302)
        self.assertEqual(self.client.post(reverse('complete', args=[self.lesson.pk])).status_code, 404)

    def test_drafts_and_admin_permissions(self):
        self.client.force_login(self.student)
        self.assertEqual(self.client.get(reverse('studio')).status_code, 302)
        self.assertEqual(self.client.post(reverse('new_course'), {'title':'Invasão'}).status_code, 302)
        Enrollment.objects.create(user=self.student, course=self.free)
        self.lesson.published = False
        self.lesson.save()
        self.assertEqual(self.client.get(reverse('lesson', args=[self.lesson.pk])).status_code, 404)
        self.free.published = False
        self.free.save()
        self.assertEqual(self.client.get(reverse('course', args=[self.free.slug])).status_code, 404)

    def test_staff_pages_and_access_grant(self):
        self.client.force_login(self.staff)
        for name, args in [('studio', []), ('new_course', []), ('edit_course', [self.free.pk]), ('new_lesson', [self.free.pk]), ('edit_lesson', [self.free.pk, self.lesson.pk]), ('grant_access', [self.paid.pk])]:
            self.assertEqual(self.client.get(reverse(name, args=args)).status_code, 200)
        self.client.post(reverse('grant_access', args=[self.paid.pk]), {'email':self.student.email})
        self.assertTrue(Enrollment.objects.filter(user=self.student, course=self.paid).exists())

    def test_csrf_and_text_escaping(self):
        client = Client(enforce_csrf_checks=True)
        client.force_login(self.student)
        self.assertEqual(client.post(reverse('enroll', args=[self.free.slug])).status_code, 403)
        Enrollment.objects.create(user=self.student, course=self.free)
        self.lesson.content = '<script>alert(1)</script>'
        self.lesson.save()
        self.client.force_login(self.student)
        response = self.client.get(reverse('lesson', args=[self.lesson.pk]))
        self.assertContains(response, '&lt;script&gt;')
        self.assertNotContains(response, '<script>alert')

    def test_password_reset_and_public_pages(self):
        for name in ['home', 'signup', 'login', 'password_reset', 'password_reset_done', 'password_reset_complete']:
            self.assertEqual(self.client.get(reverse(name)).status_code, 200)
        self.client.post(reverse('password_reset'), {'email':self.student.email})
        self.assertEqual(len(mail.outbox), 1)
        self.assertIn('/redefinir/', mail.outbox[0].body)

    def test_staff_can_publish_course_and_lesson(self):
        self.client.force_login(self.staff)
        response = self.client.post(reverse('new_course'), {'title':'Novo curso','slug':'novo','description':'Descrição','category':'tecnologia','theme':'blue','price':'0','level':'Iniciante','published':'on'})
        self.assertEqual(response.status_code, 302)
        course = Course.objects.get(slug='novo')
        response = self.client.post(reverse('new_lesson', args=[course.pk]), {'title':'Nova aula','module':'Um','position':'1','minutes':'10','content':'Texto original','published':'on'})
        self.assertEqual(response.status_code, 302)
        self.assertTrue(course.lessons.get().published)

    def test_video_host_validation(self):
        from .forms import LessonForm
        form = LessonForm({'title':'X','module':'M','position':'1','minutes':'5','content':'X','video_url':'https://malicioso.example/video'})
        self.assertFalse(form.is_valid())
        self.assertEqual(Lesson(video_url='https://youtu.be/abcdefghijk').embed_url, 'https://www.youtube-nocookie.com/embed/abcdefghijk')
