from flask import Flask, render_template
from bs4 import BeautifulSoup
import re
import sqlalchemy,requests, json, time


# Initialize the Flask application
app = Flask(__name__)

engine = sqlalchemy.create_engine('mysql+mysqlconnector://root:1234@127.0.0.1/game_recommendation?charset=utf8mb4')


@app.route('/')
@app.route('/index')
def index():
    return render_template('index.html')	

@app.route('/recommendation')
def recommendation_index():
	lst_userid = []
	for i in range(4):
		tempid = engine.execute('''
			SELECT user_id FROM tbl_recommend_games
			ORDER BY RAND()
			LIMIT 1;
			''').first()[0]
		for n in xrange(3):
			try:
				url = 'https://steamcommunity.com/profiles/' + str(tempid)
				r = requests.get(url)
				soup = BeautifulSoup(r.content,'lxml')
				for tag in soup.find_all('img'):
					temp = tag['src']
					if not re.search('full.jpg',temp) == None:
						pic = temp
				time.sleep(0.1)
				break
			except:
				pic = 'https://steamcdn-a.akamaihd.net/steamcommunity/public/images/avatars/fe/fef49e7fa7e1997310d705b2a6158ff8dc1cdfeb_full.jpg'
				time.sleep(0.1)
				pass
		lst_userid.append([tempid,pic])	
	return render_template('recommendation_index.html', lst_userid=lst_userid)



@app.route('/recommendation/<userid>')
def recommendation(userid):
	for n in xrange(3):
		try:
			url = 'https://steamcommunity.com/profiles/' + str(userid)
			r = requests.get(url)
			soup = BeautifulSoup(r.content,'lxml')
			for tag in soup.find_all('img'):
				temp = tag['src']
				if not re.search('full.jpg',temp) == None:
					pic = temp
			time.sleep(0.1)
			break
		except:
			pic = 'https://steamcdn-a.akamaihd.net/steamcommunity/public/images/avatars/fe/fef49e7fa7e1997310d705b2a6158ff8dc1cdfeb_full.jpg'
			time.sleep(0.1)
			pass
			
	result = engine.execute('''
		SELECT g0,g1,g2,g3,g4,g5,g6,g7,g8,g9 FROM tbl_recommend_games WHERE user_id=%s;
		''' % userid).first()

	lst_recommended_games = []
	for app_id in result:
		app_data = engine.execute('''
						SELECT name,initial_price,header_image FROM tbl_steam_app WHERE steam_appid = %s;
					''' % app_id).first()
		if not app_data == None:
			app_data = app_data.values()
			app_data.append(app_id)
			lst_recommended_games.append(app_data)


# Template from https://startbootstrap.com
# https://startbootstrap.com/template-overviews/1-col-portfolio/
	return render_template( 'recommendation.html',
							userid = userid,
							lst_game_urls = lst_recommended_games,
							pic = pic)

if __name__ == "__main__":
    app.run(debug=True)

