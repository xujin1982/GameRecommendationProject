import requests
import json
from tqdm import trange
import os

# Load API key
with open('../input/steam_API.txt','r') as f:
	API = f.read()

# Load steam_user_id
with open('../input/steam_user_id.txt','r') as f:
	steam_user_id = f.read().split('\n')

# Define variables
output_file = '../output/user_game_inventory.txt'
user_num = len(steam_user_id)
params = {'key': API, 'format': 'json'}
url_GetOwnedGames = 'http://api.steampowered.com/IPlayerService/GetOwnedGames/v0001/'

# Check if output file already exist
if os.path.isfile(output_file):
	os.remove(output_file)
	print 'Exist output file removed!'

# Get user game inventory and save in txt file
with open(output_file,'a') as f:
	for i in trange(user_num):
		ID = steam_user_id[i]
		params['steamid'] = ID
		try:
			response = requests.get(url_GetOwnedGames, params = params)
			line = json.dumps({ID : response.json()['response'] }) + '\n'
			f.write(line)
		except: 
			pass	