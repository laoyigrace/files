from django.conf.urls import patterns, include, url
from django.contrib import admin


from tac_ui import views

urlpatterns = patterns('',
    # Examples:
    # url(r'^$', 'tui.views.home', name='home'),
    # url(r'^blog/', include('blog.urls')),

    url(r'^admin/', include(admin.site.urls)),
    url(r'^tac_ui/$', views.index),
    url(r'^tac_ui/create', views.create)#,
   # url(r'^tac_ui/set_host', views.set_host),
   # url(r'^tac_ui/unset_host', views.unset_host)
)
