from django.conf.urls import patterns, include, url
from django.contrib import admin
from fb import views as fbViews
admin.autodiscover()

urlpatterns = patterns(
    '',
    url(r'^connect/$', fbViews.ConnectView.as_view()),
    url(r'^create/(\d+)$', fbViews.CreateView.as_view()),
    url(r'^report/(\d+)/$', fbViews.ReportView.as_view()),
    url(r'^facebook/(\d+)/$', fbViews.IndexView.as_view()),
    url(r'^facebook/$', fbViews.IndexView.as_view()),
    url(r'^ajax/', include('ajax.urls')),
    url(r'^admin/', include(admin.site.urls))
)
