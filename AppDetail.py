from __future__ import division
import requests, json, os, time, sys, random
from datetime import datetime

# Define variables
output_file = '../output/%s_app_detail.txt' % (datetime.today().isoformat()[:10])
url_GetOwnedGames = 'http://store.steampowered.com/api/appdetails/'
params = {}
path_app_user = '../output/%s_app_user.txt' % (datetime.today().isoformat()[:10])

# Load app id from http://steamspy.com
if os.path.exists(path_app_user):
	with open(path_app_user, 'rb') as f:
		lst_app_id = set(json.load(f).keys())
else:
	r = requests.get('http://steamspy.com/api.php?request=all')
	dic_app_user = r.json()
	lst_app_id = set(dic_app_user.keys())
	print '\nLoad app id from http://steamspy.com.\n'
	with open(path_app_user, 'wb') as f:
		json.dump(dic_app_user, f)

# Load app detail
load_app_id = []
if os.path.exists(output_file):
	with open(output_file, 'rb') as f:
		temp = f.readlines()
	for line in temp:
		load_app_id.append(json.loads(line).keys()[0])
load_app_id = set(load_app_id)

total_count = len(lst_app_id)
current_count = len(load_app_id)
lst_app_id = list(lst_app_id - load_app_id)
print current_count, total_count
total_count1 = len(lst_app_id)

print '\nStart!\n'
# Get app detail and save in txt file
with open(output_file,'ab') as f:
	for i in xrange(total_count1):
		ID = lst_app_id[i]
		params['appids'] = ID
		for i in xrange(3):
			try:
				response = requests.get(url_GetOwnedGames, params = params)
				result = response.json()
				break
			except:
				time.sleep(5)
				pass
		f.write(json.dumps(result))
		f.write('\n')
		current_count += 1
		if current_count % 200 == 0:
			time.sleep(300)
			sys.stdout.write('\rStatus: {0:.2f}%'.format(current_count/total_count))
			sys.stdout.flush()
		else:
			time.sleep(.5)