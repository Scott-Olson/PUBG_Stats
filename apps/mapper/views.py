from django.shortcuts import render, redirect, HttpResponse
from django.contrib import messages
from pypubg import core
from .models import *
from pubg_python import *
import datetime

api = PUBG('eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJqdGkiOiJlNzI1OWQ0MC00MTE0LTAxMzYtMmEzMS0wZTFkM2RhMWZmOGIiLCJpc3MiOiJnYW1lbG9ja2VyIiwiaWF0IjoxNTI3MTIwNjc3LCJwdWIiOiJibHVlaG9sZSIsInRpdGxlIjoicHViZyIsImFwcCI6InB1YmdtYXBwZXJfZG9qbyJ9.ziHaEvP8_KEQ8V3LIlGb9CyKAPaRsxfGG1Qhq-dzqV8', Shard.PC_NA)

# Create your views here.
def landing(request):
	apiQuery()
	return render(request, 'mapper/index.html')

def mapsLanding(request):

	return render(request, 'mapper/maps.html')

def playersLanding(request):

	return render(request, 'mapper/players.html')

def playerSearch(request):

	context = apiSearch(request.POST["playerName"])

	return	render(request, 'mapper/players.html', context)

def itemsLanding(request):
	match = api.matches().get('499fb090-795e-477b-9978-97eb50b526cf')
	asset = match.assets[0]
	telemetry = api.telemetry('Item_Heal_FirstAid_C.png')
	assets_loaded = len(telemetry)
	player_kill_events = telemetry.events_from_type('LogPlayerKill')

	context ={
		"assets_loaded":assets_loaded
	}

	return render(request, 'mapper/items.html', context)




def testApi(request):
	response = api.samples().get()
	sample = api.players().filter(match_ids=['499fb090-795e-477b-9978-97eb50b526cf'])
	# print(sample[0].game_mode)
	print(type(sample))
	return HttpResponse(response)
















