import requests
import json
from tqdm import trange
import os
import time

# Load app_id
with open('../input/app_id.txt','r') as f:
	app_id = f.read().split('\n')

# Define variables
output_file = '../output/app_detail.txt'
app_num = len(app_id)
url_GetOwnedGames = 'http://store.steampowered.com/api/appdetails/'
params = {}

# Check if output file already exist
if os.path.isfile(output_file):
	os.remove(output_file)
	print 'Exist output file removed!'

# Get app detail and save in txt file
with open(output_file,'a') as f:
	for i in trange(app_num):
		ID = app_id[i]
		params['appids'] = ID
		try:
			response = requests.get(url_GetOwnedGames, params = params)
			line = response.text + '\n'
			f.write(line)
		except: 
			pass
		time.sleep(5)