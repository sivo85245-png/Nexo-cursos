from django.urls import path, reverse_lazy
from django.contrib.auth import views as auth
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('cadastro/', views.signup, name='signup'),
    path('entrar/', views.SigninView.as_view(), name='login'),
    path('sair/', auth.LogoutView.as_view(), name='logout'),
    path('minhas-aulas/', views.dashboard, name='dashboard'),
    path('curso/<slug:slug>/', views.course_detail, name='course'),
    path('curso/<slug:slug>/inscrever/', views.enroll, name='enroll'),
    path('aula/<int:pk>/', views.lesson_detail, name='lesson'),
    path('aula/<int:pk>/concluir/', views.complete, name='complete'),
    path('studio/', views.studio, name='studio'),
    path('studio/novo/', views.edit_course, name='new_course'),
    path('studio/curso/<int:pk>/', views.edit_course, name='edit_course'),
    path('studio/curso/<int:pk>/acesso/', views.grant_access, name='grant_access'),
    path('studio/curso/<int:course_pk>/aula/', views.edit_lesson, name='new_lesson'),
    path('studio/curso/<int:course_pk>/aula/<int:pk>/', views.edit_lesson, name='edit_lesson'),
    path('recuperar/', auth.PasswordResetView.as_view(success_url=reverse_lazy('password_reset_done')), name='password_reset'),
    path('recuperar/enviado/', auth.PasswordResetDoneView.as_view(), name='password_reset_done'),
    path('redefinir/<uidb64>/<token>/', auth.PasswordResetConfirmView.as_view(success_url=reverse_lazy('password_reset_complete')), name='password_reset_confirm'),
    path('redefinir/concluido/', auth.PasswordResetCompleteView.as_view(), name='password_reset_complete'),
]
