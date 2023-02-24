"""config URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path
from apps.views import uploadFile
from apps.views import index
# django-ninja 및 view 함수
from apps.views import *

# Static (for img)
from django.conf.urls.static import static
from django.conf import settings


urlpatterns = [
    # Django-Ninja Api
    path("api/", api.urls),
    # 메인 페이지
    # path("", index, name="index"),
    path("", uploadFile, name = 'uploadFile'),
    path("main/",index, name='index'),
    path('admin/', admin.site.urls),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
