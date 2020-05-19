import os
from flask import Flask, request, abort, jsonify
from sqlalchemy import Column, String, Integer, create_engine
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
from models import setup_db, Movies,Actors, drop_db_create_all
from auth import AuthError,requires_auth


class AuthError(Exception):
    def __init__(self, error, status_code):
        self.error = error
        self.status_code = status_code

def create_app(test_config=None):

	# create and configure the app
	app = Flask(__name__)
	setup_db(app)

	#--below function called only once in first --#
	#drop_db_create_all()
	

	CORS(app)
	#--CORS header--#
	@app.after_request
	def after_request(response):
		response.headers.add('Access-Control-Allow-Headers', 'Content-Type, Authorization, true')
		response.headers.add('Access-Control-Allow-Methods', 'GET,DELETE,POST,PATCH,OPTIONS')
		return response



	#---pagination--#
	def pagination(request,selection):
		page=request.args.get('page', 1, type=int)
		#-calculate start and end pages--#
		start=(page-1)*10
		end=start+10
		formatted_actors=[]
		# for actor in selection:
		# 	formatted_actors.append(actor.format())

		formatted_actors=[actor.format() for actor in selection]
		return formatted_actors[start:end]


	@app.route('/')
	def index():
		return jsonify({
			"success":"hello "+"world;"
			})


	#---GET methods to both endpoints ---to get list present---#

	@app.route('/actors', methods=['GET'])
	@requires_auth('get:actors')
	def get_actors_list(jwt):
		actors=Actors.query.all()
		if actors is None:
			abort(404)
		paginated_actors = pagination(request,actors)
		if len(paginated_actors)== 0:
			abort(404)

		return jsonify({
			'success': True,
			'actors': paginated_actors
			},200)


	@app.route('/movies', methods=['GET'])
	@requires_auth('get:movies')
	def get_movies_list(jwt):
		#---Get list of movies objects--#
		movies=Movies.query.order_by(Movies.id).all()
		if movies is None:
			abort(404)
		#---GEt paginated movies -list--#
		paginated_movies=pagination(request,movies)
		if len(paginated_movies)== 0:
			abort(404)

		return jsonify({
			'success': True,
			'movies': paginated_movies
			},200)

	#----POST method to endpoints actors and movies----#

	@app.route('/movies/create', methods=['POST'])
	@requires_auth('post:movies')
	def add_movies(jwt):
		#---get json data--#
		body=request.get_json()
		if body is None:
			abort(401)

		try:    
			new_title=body.get('title', '')
			new_release_date=body.get('release_date', '')

			if not (new_title and new_release_date):
				abort(400)
			movie=Movies(title=new_title, release_date=new_release_date)
			movie.insert()

			return jsonify({
				'success': True,
				'title': new_title,
				'message': new_title+" Added successfully",
				'id': movie.id
				},200)

		except Exception as e:
			print(e)
			abort(422)

	@app.route('/actors/create', methods=['POST'])
	@requires_auth('post:actors')
	def add_actors(jwt):
		#--Get request json
		body=request.get_json()
		if body is None:
			abort(400)#--does not contain valid json

		try:
			#--get form values to variables--#
			new_name=body.get('name', '')
			new_age=body.get('age', '')
			new_gender=body.get('gender', '')

			if not ( new_gender and new_age and new_name):
				abort(422)#--no data provided--#
			
			new_actor=Actors(name=new_name, age=new_age, gender=new_gender)
			new_actor.insert()

			return jsonify({
				'success': True,
				'id':new_actor.id,
				'name':new_actor.name
				},200)

		except Exception as e:
			print(e)
			abort(422)

	#----DELETE /actors & /movies require permission 'delete:movies' or 'delete:actors'
	@app.route('/movies/<int:id>', methods=['DELETE'])
	@requires_auth('delete:movies')
	def delete_specific_movie(jwt,id):
		movie=Movies.query.filter(Movies.id == id).first()

		if movie is None:
			abort(404)
		movie.delete()

		return jsonify({
			'success':True,
			'id':id,
			'message':"Deleted successfully"
			},200)

	@app.route('/actors/<int:id>', methods=['DELETE'])
	@requires_auth('delete:actors')
	def delete_specific_actor(jwt,id):
		#---Get specific actor id to delete---3
		actor=Actors.query.filter(Actors.id == id).first()
		if actor is None:
			abort(404)

		actor.delete()

		return jsonify({
			'success': True,
			'id': id
			},200)

	#---PATCH method to endpoints___#

	@app.route('/movies/<int:id>', methods=['PATCH'])
	@requires_auth('patch:movies')
	def update_speciifc_movie(jwt, id):
		#--GEt specific movie---#
		movie=Movies.query.filter(Movies.id == id).first()
		if movie is None:
			abort(404)

		body= request.get_json()
		# if body['title']:
		#   movie.title=body['title']
		# if body['release_date']:
		#   movie.release_date=body['release_date']
		new_title= body.get('title', movie.title)
		new_release_date= body.get('release_date', movie.release_date)



		movie.title=new_title
		movie.release_date=new_release_date

		movie.update()

		return jsonify({
			'success': True,
			'id':id,
			'movie':[movie.format()]
			},200)


	@app.route('/actors/<int:id>', methods=['PATCH'])
	@requires_auth('patch:actors')
	def update_specific_actor(jwt,id):
		#---Get specific actor--#
		actor=Actors.query.filter(Actors.id == id).first()
		if actor is None:
			abort(404)
		#----Get request json data--#
		body= request.get_json()

		# if body['name']:
		#   actor.name= body['name']
		# if body['age']:
		#   movie.age= body['age']
		# if body['gender']:
		#   movie.gender= body['gender']
		new_name=body.get('name', actor.name)
		new_age=body.get('age', actor.age)
		new_gender=body.get('gender', actor.gender)

		actor.name=new_name
		actor.age=new_age
		actor.gender=new_gender

		actor.update()

		return jsonify({
			'success': True,
			'updated_id': id,
			'acotr': [actor.format()]
			},200)


#---Error handlerss-----#
	@app.errorhandler(400)
	def bad_request(error):
		return jsonify({
			'success': False,
			'error': 400,
			'message': "bad_request"
			})
	#--Error handlers---#

	@app.errorhandler(401)
	def unauthorized(error):
		return jsonify({
			'success': False,
			'error': 401,
			'message': "unauthorized error"
			})

	@app.errorhandler(404)
	def resource_not_found(error):
		return jsonify({
			'success': False,
			'error': 404,
			'message': "resource_not_found"
			})

	@app.errorhandler(422)
	def unprocessable(error):
		return jsonify({
			'success': False,
			'error': 422,
			'message': "unprocessable"
			})

	@app.errorhandler(AuthError)
	def Authentication_fail_error(error):
		return jsonify({
			'success': False,
			'error': AuthError.status_code,
			'message': AuthError.error['description']
			}),AuthError.status_code

	return app



app = create_app()

if __name__ == '__main__':
	app.run(host='0.0.0.0', port=8080, debug=True)