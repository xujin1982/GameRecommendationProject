from __future__ import division
import requests, json, os, time, sys, random
from datetime import datetime
from multiprocessing.dummy import Pool as ThreadPool

# split list
def split_list(lst_long,n):
	lst_splitted = []
	if len(lst_long) % n == 0:
		totalBatches = len(lst_long) // n
	else:
		totalBatches = len(lst_long) // n + 1
	for i in xrange(totalBatches):
		lst_short = lst_long[i*n:(i+1)*n]
		lst_splitted.append(lst_short)
	return lst_splitted

# work status bar
def show_work_status(singleCount, totalCount, currentCount = 0):
	currentCount += singleCount
	percentage = currentCount / totalCount * 100
	status = '+' * int(percentage) + '-' * (100 - int(percentage))
	sys.stdout.write('\rStatus: [{0}] {1:.2f}%'.format(status,percentage))
	sys.stdout.flush()
	if percentage >= 100:
		print '\n'

# Get user game inventory and save in txt file with multiprocessing
def get_info(steam_user_id):
	time.sleep(random.random() + random.randint(2,5))
	result =  {}
	for ID in steam_user_id:
		params['steamid'] = ID
		for j in xrange(3):
			try:
				r = requests.get(url_GetOwnedGames, params = params)
				user_invenory = r.json().get('response').get('games')
				result.update({ID:user_invenory})
				time.sleep(.1)
				break
			except:
				time.sleep(.1)
				pass
	return result


if __name__ == '__main__':
	# Load API key
	with open('../input/steam_API.txt','r') as f:
	    API = f.readlines()

	# Load steam_user_id
	with open('../input/steam_user_id.txt','r') as f:
		steam_user_id = set(f.read().splitlines())

	# Define variables
	output_file = '../output/%s_user_inventory.json' % (datetime.today().isoformat()[:10])
	header = 'Mozilla/5.0 (Windows; U; Windows NT 5.0; en-US; rv:1.8b4) Gecko/20050910 SeaMonkey/1.0a'
	params = {'key': API, 'format': 'json','headers':header}
	url_GetOwnedGames = 'http://api.steampowered.com/IPlayerService/GetOwnedGames/v0001/'

	# Check if output file already exist
	if os.path.exists(output_file):
		with open(output_file, 'rb') as f:
			json_crawled_data = json.load(f)
			set_crawled_user_id = set(json_crawled_data.keys())
	else:
		json_crawled_data = {}
		set_crawled_user_id = set([])

	total_count = len(steam_user_id)
	current_count = len(set_crawled_user_id)
	lst_remaining_id = list(steam_user_id - set_crawled_user_id)

	num_processer = 20
	p = ThreadPool(num_processer)

	print 'Start!\n'
	for lst_steam_id in split_list(lst_remaining_id,1000):
		temp_dict = p.map(get_info, split_list(lst_steam_id,50))
		for temp in temp_dict:
			json_crawled_data.update(temp)

		with open(output_file,'wb') as f:
		    json.dump(json_crawled_data,f)

		lst_len = len(lst_steam_id)
		show_work_status(lst_len,total_count,current_count)
		current_count += lst_len

	p.close()
	print '\nDone!'