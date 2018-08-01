from __future__ import unicode_literals
from django.db import models
from pubg_python import *
import datetime

# %matplotlib inline

import numpy as np
import matplotlib.pyplot as plt
import pandas as pd
import seaborn as sns
from scipy.ndimage.filters import gaussian_filter
import matplotlib.cm as cm
from matplotlib.colors import Normalize

from scipy.misc.pilutil import imread

# Create your models here.
class heatMapCreater():
	# creates a heat map of killed players, not my own code but adapted to run on server start rather than on demand as its very resource intensive
	df = pd.read_csv('input/PUBG_MatchData_Flattened.tsv', sep='\t')

	edf = df.loc[df['map_id'] == 'ERANGEL']
	mdf = df.loc[df['map_id'] == 'MIRAMAR']

	# print(edf.head())
	# print(mdf.head())

	def killer_victim_df_maker(df):
		victim_x_df = df.filter(regex='victim_position_x')
		victim_y_df = df.filter(regex='victim_position_y')
		killer_x_df = df.filter(regex='killer_position_x')
		killer_y_df = df.filter(regex='killer_position_y')

		victim_x_s = pd.Series(victim_x_df.values.ravel('F'))
		victim_y_s = pd.Series(victim_y_df.values.ravel('F'))
		killer_x_s = pd.Series(killer_x_df.values.ravel('F'))
		killer_y_s = pd.Series(killer_y_df.values.ravel('F'))

		vdata={'x': victim_x_s, 'y':victim_y_s}
		kdata={'x': killer_x_s, 'y':killer_y_s}

		victim_df = pd.DataFrame(data = vdata).dropna(how='any')
		victim_df = victim_df[victim_df['x']>0]
		killer_df = pd.DataFrame(data = kdata).dropna(how='any')
		killer_df = killer_df[killer_df['x']>0]
		return killer_df,victim_df

	ekdf,evdf = killer_victim_df_maker(edf)
	mkdf,mvdf = killer_victim_df_maker(mdf)

	print(ekdf.head())
	print(evdf.head())
	print(mkdf.head())
	print(mvdf.head())
	print(len(ekdf), len(evdf), len(mkdf), len(mvdf))

	def heatmap(x, y, s, bins=100):
		heatmap, xedges, yedges = np.histogram2d(x, y, bins=bins)
		heatmap = gaussian_filter(heatmap, sigma=s)

		extent = [xedges[0], xedges[-1], yedges[0], yedges[-1]]
		return heatmap.T, extent

	def divbutnotbyzero(a,b):
		c = np.zeros(a.shape)
		for i, row in enumerate(b):
			for j, el in enumerate(row):
				if el==0:
					c[i][j] = a[i][j]
				else:
					c[i][j] = a[i][j]/el
		return c
	plot_data_ev = evdf[['x', 'y']].values
	plot_data_ek = ekdf[['x', 'y']].values
	plot_data_mv = mvdf[['x', 'y']].values
	plot_data_mk = mkdf[['x', 'y']].values

	plot_data_ev = plot_data_ev*4040/800000
	plot_data_ek = plot_data_ek*4040/800000
	plot_data_mv = plot_data_mv*976/800000
	plot_data_mk = plot_data_mk*976/800000


	bg = imread('input/erangel.jpg')
	hmap, extent = heatmap(plot_data_ev[:,0], plot_data_ev[:,1], 0, bins=800)
	hmap2, extent2 = heatmap(plot_data_ek[:,0], plot_data_ek[:,1], 0, bins=800)
	hmap3 = divbutnotbyzero(hmap,hmap2)
	alphas = np.clip(Normalize(0, hmap3.max()/100, clip=True)(hmap)*1.5, 0.0, 1.)
	colors = Normalize(hmap3.max()/100, hmap3.max()/20, clip=True)(hmap)
	colors = cm.rainbow(colors)
	colors[..., -1] = alphas

	fig, ax = plt.subplots(figsize=(24,24))
	ax.set_xlim(0, 4096); ax.set_ylim(0, 4096)
	ax.imshow(bg)
	ax.imshow(colors, extent=extent, origin='lower', cmap=cm.rainbow, alpha=0.5)
	plt.gca().invert_yaxis()
	plt.savefig('apps/mapper/static/mapper/images/testErangel.jpg',bbox_inches='tight')

	bg = imread('input/miramar.jpg')
	hmap, extent = heatmap(plot_data_mv[:,0], plot_data_mv[:,1], 0, bins=800)
	hmap2, extent2 = heatmap(plot_data_mk[:,0], plot_data_mk[:,1], 0, bins=800)
	hmap3 = divbutnotbyzero(hmap,hmap2)
	alphas = np.clip(Normalize(0, hmap3.max()/100, clip=True)(hmap)*1.5, 0.0, 1.)
	colors = Normalize(hmap3.max()/100, hmap3.max()/20, clip=True)(hmap)
	colors = cm.rainbow(colors)
	colors[..., -1] = alphas


	fig, ax = plt.subplots(figsize=(24,24))
	ax.set_xlim(0, 1000); ax.set_ylim(0, 1000)
	ax.imshow(bg)
	ax.imshow(colors, extent=extent, origin='lower', cmap=cm.rainbow, alpha=0.5)
	plt.gca().invert_yaxis()
	plt.savefig('apps/mapper/static/mapper/images/testMiramar.jpg',bbox_inches='tight')  



api = PUBG('eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJqdGkiOiJlNzI1OWQ0MC00MTE0LTAxMzYtMmEzMS0wZTFkM2RhMWZmOGIiLCJpc3MiOiJnYW1lbG9ja2VyIiwiaWF0IjoxNTI3MTIwNjc3LCJwdWIiOiJibHVlaG9sZSIsInRpdGxlIjoicHViZyIsImFwcCI6InB1YmdtYXBwZXJfZG9qbyJ9.ziHaEvP8_KEQ8V3LIlGb9CyKAPaRsxfGG1Qhq-dzqV8', Shard.PC_NA)


def apiSearch(playerName):
	print('\n in here \n')
	try:	
		players = api.players().filter(player_names=[playerName])
		print('\n api request made\n')
		if players:
			print('\n player found', players, '\n')
			player = players[0]
			matches = []
			playerKills = 0
			matchCount = 0
			walkDistance = 0
			longestKill = 0
			deaths = 0
			wins = 0
			topten = 0
			killStreak = 0
			roadKills = 0
			timeSurvived = 0
			headShot = 0
			mostKills = 0
			mostDamage = 0
			for matchOne in player.matches:
				match = api.matches().get(matchOne.id)
				matches.append(match)
				print(match.game_mode)
				playerID = player.id
				print(playerID)
				rosters = match.rosters
				
				for roster in rosters:
					participants = roster.participants
					for playerOne in participants:
						if playerOne.name == playerName:
							print("\nstats avail\n")
							playerKills += playerOne.kills
							matchCount += 1
							walkDistance += playerOne.walk_distance
							roadKills += playerOne.road_kills
							timeSurvived += playerOne.time_survived
							headShot += playerOne.headshot_kills
							print(playerOne.death_type)
							if playerOne.death_type != 'alive':
								deaths += 1
							print("win place: ",playerOne.win_place)
							if playerOne.win_place == 1:
								wins += 1
							if playerOne.win_place <= 10:
								topten += 1
							if playerOne.longest_kill > longestKill:
								longestKill = playerOne.longest_kill
							if playerOne.kill_streaks > killStreak:
								killStreak = playerOne.kill_streaks
							if playerOne.kills > mostKills:
								mostKills = playerOne.kills
							if playerOne.damage_dealt > mostDamage:
								mostDamage = playerOne.damage_dealt	
							print("kills: ",playerOne.kills)
							print("longest kill: ",playerOne.longest_kill)
							print("walk distance: ",playerOne.walk_distance)

			print("player kills: ", playerKills)
			print("match count: ", matchCount)		
			print("walk distance: ", walkDistance)
			print("longest kills: ", longestKill)
			if deaths > 0:			
				kdAvg = playerKills/deaths
			else:
				kdAvg = playerKills
			if matchCount > 0:
				timeAvg = timeSurvived/matchCount/60
				winPerc = (wins/matchCount)*100	
				topPerc = (topten/matchCount)*100
			print("K/D avg: ", kdAvg)	
			context={
				"player":player,
				"matches":matches,
				"kills":playerKills,
				"kdAvg": kdAvg,
				"matchCount": matchCount,
				"walkDistance": walkDistance,
				"longestKill": longestKill,
				'wins': wins,
				"topten": topten,
				"killStreak": killStreak,
				"timeAvg": timeAvg,
				"roadKills":roadKills,
				"winPerc":winPerc,
				"topPerc":topPerc,
				"headShot": headShot,
				"mostKills": mostKills,
				"mostDamage": mostDamage,


				}
			return context
	except:
		print('\n player not found', playerName ,'\n')
		context={
			"player": 'No player found in the database'
			}	
		return context

def apiQuery():
	sample = api.samples().get()
	return sample
