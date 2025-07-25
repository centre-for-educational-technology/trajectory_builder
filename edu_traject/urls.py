"""
URL configuration for edu_traject project.

"""

from django.contrib import admin
from django.urls import path, include
from .views import change_language

from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path("admin/", admin.site.urls),
    path("", include("users.urls")),
    path("trajectory/",include("teacher.urls")),
    path("student/",include("student.urls")),
]

urlpatterns += [ path('change-lang/<lang_code>', change_language, name='change_language')]

urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
