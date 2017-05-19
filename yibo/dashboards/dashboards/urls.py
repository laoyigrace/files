"""dashboards URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/1.8/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  url(r'^$', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  url(r'^$', Home.as_view(), name='home')
Including another URLconf
    1. Add an import:  from blog import urls as blog_urls
    2. Add a URL to urlpatterns:  url(r'^blog/', include(blog_urls))
"""
from django.conf.urls import include, url
from django.contrib import admin
from jenkins_analyze import views as jenkins_analyze_view



urlpatterns = [
    url(r'^admin/', include(admin.site.urls)),
    url(r'^jenkins_analyze/$', jenkins_analyze_view.index),
    url(r'^jenkins_analyze/builds$', jenkins_analyze_view.builds),
    url(r'^jenkins_analyze/jobs$', jenkins_analyze_view.jobs),
    url(r'^jenkins_analyze/tempest_models_info',
        jenkins_analyze_view.tempest_models_info),
    url(r'^jenkins_analyze/send_email',
        jenkins_analyze_view.notify_by_email),
    url(r'^jenkins_analyze/update_results',
        jenkins_analyze_view.update_results),
    url(r'^jenkins_analyze/latest_package_version',
        jenkins_analyze_view.latest_package_version),
    url(r'^jenkins_analyze/tempest_test_cases',
        jenkins_analyze_view.tempest_test_cases),
    url(r'^jenkins_analyze/sub_email',
        jenkins_analyze_view.sub_email),
    url(r'^jenkins_analyze/unsub_email',
        jenkins_analyze_view.unsub_email),

]
