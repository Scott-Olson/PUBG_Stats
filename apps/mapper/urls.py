from django.conf.urls import url
from . import views

urlpatterns = [
	url(r'players/search', views.playerSearch),
	url(r'maps', views.mapsLanding),
	url(r'players', views.playersLanding),
	url(r'test', views.testApi),
	url(r'^', views.playersLanding)
]