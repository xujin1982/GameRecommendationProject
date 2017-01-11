from app import app
from flask import render_template
import json
import sqlalchemy

engine = sqlalchemy.create_engine('mysql+mysqlconnector://root:1234@127.0.0.1/game_recommendation?charset=utf8mb4')


@app.route('/')
@app.route('/index')
def index():
    return "Hello, World!\n\nAppend /recommendation/<userid> to the current url\n\nSome availble userids: 76561197960358716, 76561197960520753, 76561197960776822, 76561197961634835"


@app.route('/recommendation/<userid>')
def recommendation(userid):
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
							lst_game_urls = lst_recommended_games)

