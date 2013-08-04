from django.conf.urls import patterns, include, url
from django.contrib import admin
from fb import views as fbViews
admin.autodiscover()

urlpatterns = patterns(
    '',
    url(r'^facebook/connect/$', fbViews.ConnectView.as_view()),
    url(r'^facebook/create/$', fbViews.CreateView.as_view()),
    url(r'^facebook/$', fbViews.IndexView.as_view()),
    url(r'^report/(\d+)/$', fbViews.ReportView.as_view()),
    url(r'^admin/', include(admin.site.urls))
)
