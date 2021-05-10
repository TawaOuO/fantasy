from requests import get
from os import path
from os import remove
from json import dumps
import pandas as pd
import yahoo_fantasy_api as yfa
from yahoo_oauth import OAuth2
from datetime import datetime

now = datetime.now()
date = now.strftime('%Y-%m-%d')
year = now.strftime('%Y')

player_id_yf_list = pd.read_csv('player_id_ver_2021_05.csv')[['player_id', 'player_name']]
player_id_yf_dict = {}
for i in range(0, len(player_id_yf_list)):
	player_id_yf_dict[player_id_yf_list.player_name[i]] = player_id_yf_list.player_id[i]

def create_oauth2_json():
	consumer_key = input('Enter consumer key:')
	consumer_secret = input('Enter consumer secret:')
	creds = {'consumer_key': consumer_key, 'consumer_secret': consumer_secret}
	with open('oauth2.json', "w") as f:
	   f.write(dumps(creds))
	f.close()

def connect():
	sc = OAuth2(None, None, from_file='oauth2.json')
	gm = yfa.Game(sc, 'mlb')
	league_id_list = (gm.league_ids(year = int(year)))
	lg = gm.to_league(league_id_list[0])

	return lg

def DataDownload():
	if not path.exists('cache_exit.csv'):
		url = 'https://baseballsavant.mlb.com/leaderboard/statcast?type=' + Type + '&year=' + year +'&position=' + position + '&team=' + team + '&min=' + Min + '&csv=true'
		r = get(url)
		csv_file = r.content
		with open('cache_exit.csv', 'wb') as f:
			f.write(csv_file)
		f.close()
	if not path.exists('cache_percent.csv'):
		url = 'https://baseballsavant.mlb.com/leaderboard/percentile-rankings?type=' + Type + '&year=' + year + '&team=' + team + '&csv=true'
		r = get(url)
		csv_file = r.content
		with open('cache_percent.csv', 'wb') as f:
			f.write(csv_file)
		f.close()

def DataDelete():
	if path.exists('cache_exit.csv'):
		remove('cache_exit.csv')
	if path.exists('cache_percent.csv'):
		remove('cache_percent.csv')

def percent_owned(lg, player_id):
	player_data = lg.percent_owned(player_id)
	
	return player_data[0]['percent_owned']

def DataSort(lg):
	exit_data_list = pd.read_csv('cache_exit.csv')[['last_name', ' first_name', 'avg_hit_speed', 'ev95percent', 'brl_pa']]
	percent_data_list = pd.read_csv('cache_percent.csv')[['player_name', 'brl_percent', 'hard_hit_percent', 'exit_velocity', 'k_percent', 'bb_percent', 'whiff_percent', 'player_id']]
	target_player_id = pd.read_csv('cache_exit.csv')['player_id']
	player_id_list = []
	for index in target_player_id:
		player_id_list.append(index)
	
	#output_list = pd.DataFrame()
	for i in range(0, len(percent_data_list)):
		if percent_data_list.player_id[i] in player_id_list:
			try:
				if int(percent_data_list.brl_percent[i]) >= min_brl_percent and int(percent_data_list.hard_hit_percent[i]) >= min_hard_hit_percent and int(percent_data_list.exit_velocity[i]) >= min_exit_velocity_percent and int(percent_data_list.k_percent[i]) >= min_k_percent and int(percent_data_list.bb_percent[i]) >= min_bb_percent and int(percent_data_list.whiff_percent[i]) >= min_whiff_percent:
					player_id_yf = player_id_yf_dict[percent_data_list.player_name[i]]
					roster_percent = percent_owned(lg, [int(player_id_yf)])
					print('name:' + percent_data_list.player_name[i] + '    roster%:' + str(roster_percent))
					print('brl_percent:' + str(percent_data_list.brl_percent[i]))
					print('hard_hit_percent:' + str(percent_data_list.hard_hit_percent[i])) 
					print('exit_velocity:' + str(percent_data_list.exit_velocity[i]))
					print('k_percent:' + str(percent_data_list.k_percent[i])) 
					print('bb_percent:' + str(percent_data_list.bb_percent[i])) 
					print('whiff_percent:' + str(percent_data_list.whiff_percent[i]))
					print('------------------------------------------------')
			except ValueError:
				pass

			# try:
			# 	if int(percent_data_list.brl_percent[i]) >= min_brl_percent and int(percent_data_list.hard_hit_percent[i]) >= min_hard_hit_percent and int(percent_data_list.exit_velocity[i]) >= min_exit_velocity_percent and int(percent_data_list.k_percent[i]) >= min_k_percent and int(percent_data_list.bb_percent[i]) >= min_bb_percent and int(percent_data_list.whiff_percent[i]) >= min_whiff_percent:
			# 		series = pd.Series({'brl_percent': percent_data_list.brl_percent[i], 'hard_hit_percent': percent_data_list.hard_hit_percent[i], 'exit_velocity': percent_data_list.exit_velocity[i], 'k_percent': percent_data_list.k_percent[i], 'bb_percent':percent_data_list.bb_percent[i], 'whiff_percent':percent_data_list.whiff_percent[i]}, name = percent_data_list.player_name[i])
			# 		output_list = output_list.append(series)
			# except ValueError:
			# 	pass
	# if not os.path.exists('result/' + date + '_position=' + position + '&team=' + team + '&min=' + Min + '_sort.csv'):
	# 	output_list.to_csv('result/' + date + '_position=' + position + '&team=' + team + '&min=' + Min + '_sort.csv', encoding = 'utf-8-sig')

if __name__ == '__main__':
	if not path.exists('oauth2.json'):
		create_oauth2_json()
	Type = input('Please enter type of plater(batter or picther):')
	position = input("Please enter position of player (don't need to enter if you want all position or type is picther):")
	min_brl_percent = int(input('Please enter min_brl_percent:'))
	min_hard_hit_percent = int(input('Please enter min_hard_hit_percent:'))
	min_exit_velocity_percent = int(input('Please enter min_exit_velocity_percent:'))
	min_k_percent = int(input('Please enter min_k_percent:'))
	min_bb_percent = int(input('Please enter min_bb_percent:'))
	min_whiff_percent = int(input('Please enter min_whiff_percent:'))
	team = ''
	Min = 'Q'
	exit_path = DataDownload()
	lg = connect()
	DataSort(lg)
	DataDelete()
	input('press Enter to exit...')

