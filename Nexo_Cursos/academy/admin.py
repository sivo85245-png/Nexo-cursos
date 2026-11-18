from django.contrib import admin
from .models import Course, Lesson, Enrollment, Progress
admin.site.register([Course, Lesson, Enrollment, Progress])
