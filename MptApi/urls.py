"""MptApi URL Configuration

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
from django.views.generic import TemplateView
from rest_framework_swagger.views import get_swagger_view
from rest_framework.schemas import get_schema_view

import timetable.views

schema_view = get_swagger_view(title='Pastebin API')

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api_schema', get_schema_view(title="api_schema", description="Schema for MptApi"), name="api_schema"),
    path('specialities/', timetable.views.SpecialitiesView.as_view()),
    path('groups/', timetable.views.GroupsView.as_view()),
    path('week/', timetable.views.WeekView.as_view()),
    path('timetable/', timetable.views.TimetableViews.as_view()),
    path('replacement/', timetable.views.ReplacementView.as_view()),
    path('docs/', TemplateView.as_view(
            template_name='docs.html',
            extra_context={'schema_url':'api_schema'}
            ), name='swagger-ui'),
]
