from django.conf.urls import patterns, url
import views
urlpatterns = patterns(
    '',
    url(r'^top-travels/(\d+)$', views.TopTravelsView.as_view()),
    url(r'^top-travel-friends/(\d+)$', views.TopTravelFriendsView.as_view()),
    url(r'^furthest-friends/(\d+)$', views.FurthestFriendsView.as_view()),
)
