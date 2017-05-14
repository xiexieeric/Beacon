"""Beacon URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/1.10/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  url(r'^$', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  url(r'^$', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.conf.urls import url, include
    2. Add a URL to urlpatterns:  url(r'^blog/', include('blog.urls'))
"""
from django.conf.urls import url
from django.contrib import admin

from . import views

urlpatterns = [
    url(r'^admin/', admin.site.urls),
    url(r'^$', views.index),
    url(r'^signin/', views.signin),
    url(r'^register/', views.register),
    url(r'^signup/', views.signup),
    url(r'^home/', views.home),
    url(r'^list/', views.pair),

    url(r'^match/accept/(?P<pk>[\w ]+)/$', views.match_accept, name='match_accept'),
    url(r'^match/decline/(?P<pk>[\w ]+)/$', views.match_decline, name='match_decline'),
]
