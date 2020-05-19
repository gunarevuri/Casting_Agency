import unittest
import os
import json
from flask_sqlalchemy import SQLAlchemy
from app import create_app
from models import Actors, Movies, setup_db, drop_db_create_all
from datetime import date
from config import bearer_tokens

#---Dict having auth header containing bearer token---#
casting_assistant_header= {'Authorization': bearer_tokens['casting_assistant']}
casting_director_header= {'Authorization': bearer_tokens['casting_director']}
executive_producer_header={'Authorization': bearer_tokens['excecutive_producer']}

#---RBAC tests---#
class AgencyTestCase(unittest.TestCase):
	""" This class called agency test case"""
	def setUp(self):
		self.app = create_app()
		self.client = self.app.test_client
		self.database_name ="test_casting_agency"
		self.database_path = "postgres://gunarevuri@localhost:5432/{}".format(self.database_name)
		setup_db(self.app, self.database_path)
		#drop_db_create_all()

		with self.app.app_context():
			self.db = SQLAlchemy()
			self.db.init_app(self.app)
			self.db.create_all()

	def tearDown(self):
		pass


	def test_add_new_movies(self):
		json_movie={'title' : "shiva movie", 'release_date' : date.today()}
		res=self.client().post('/movies/create', json = json_movie, headers = executive_producer_header)
		data=json.loads(res.data)

		self.assertEqual(res.status_code, 200)
		self.assertTrue(data['success'])
		self.assertEqual(data['id'], 2)


		#---Test Error post movie--3
	def test_error_422_new_movie(self):
		json_movie_error={'release_date' : date.today()}

		res=self.client().post('/movies/create', json = json_movie_error, headers = executive_producer_header)
		data=json.loads(res.data)

		self.assertEqual(res.status_code, 200)
		self.assertTrue(data['success'])

	#---Test to get all movies---#
	def test_get_movies(self):
		res = self.client().get('/movies', headers = casting_assistant_header)
		data = json.loads(res.data)
		
		self.assertEqual(res.status_code, 200)
		self.assertEqual(data['success'], True)

		#---test to get error 401---#
	def test_error_401_get_all_movies(self):
		res = self.client().get('/movies')
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 401)
        self.assertFalse(data['success'])

		#------test to get error in pagination---#
	def test_error_404_get_movies(self):
		res= self.client().get('/movies?page=12354',headers=casting_assistant_header)
		data=json.loads(res.data)

		self.assertEqual(res.status_code, 404)
		self.assertFalse(data['success'])

	#-------test /movies patch--------------------------#

	def test_update_movie(self):
		json_edit_movie = {'release_date' : date.today()}

		res = self.client().patch('/movies/1', json = json_edit_movie, headers = executive_producer_header)
		data=json.loads(res.data)

		self.assertEqual(res.status_code, 200)
		self.assertTrue(data['success'])
		self.assertEqual(data['id'], 1)

		#-----test 404 error edit movie----#
	def test_error_404_update_movie(self):
		json_edit_movie = {
			'release_date' : date.today()
		} 
		res = self.client().patch('/movies/123412', json = json_edit_movie, headers = executive_producer_header)
		data = json.loads(res.data)

		self.assertEqual(res.status_code, 404)
		self.assertFalse(data['success'])


	#------test Delete movie--------#

			#----test 401 without authorizatio header----#
	def test_error_401_delete_movie(self):
		#---without authorization header---#
		res=self.client().delete('/movies/1')
		data=json.loads(res.data)

		self.assertEqual(res.status_code, 401)
		self.assertFalse(data['success'])

			
		#----test 403 forbidden error---#
	def test_403_error_delete_movie(self):
		res=self.client().delete('/movies/1', headers = casting_assistant_header)
		data=json.loads(res.data)

		self.assertEqual(res.status_code, 403)
		self.assertFalse(data['success'])

		#--test delete /movies/1 200---#
	def test_200_delete_movie(self):
		res=self.client().delete('/movies/1', headers = executive_producer_header)
		data=json.loads(res.data)

		self.assertEqual(res.status_code, 200)
		self.assertTrue(data['success'])



	#------test for ACTORS Model---#
	def test_add_actor(self):
		json_add_actor={'name' : 'macCall', 'age' : 34, 'gender' : 'Male'}
		res=self.client().post('/actors/create', json = json_add_actor, headers = executive_producer_header)
		data=json.loads(res.data)

		self.assertEqual(res.status_code, 200)
		self.assertEqual(data['id'],2)
		self.assertTrue(data['success'])


	def test_401_error_adding_actor(self):
		json_add_actor={'name' : 'macCall', 'age' : 34, 'gender' : 'Male'}
		res=self.client().post('/actors/create', json = json_add_actor)
		data=json.loads(res.data)

		self.assertEqual(res.status_code, 401)
		self.assertFalse(data['success'])

	#---GET /actors ---#
	def test_get_all_actors(self):
		"""Test GET all actors."""
		res = self.client().get('/actors', headers = casting_assistant_header)
		data = json.loads(res.data)

		self.assertEqual(res.status_code, 200)
		self.assertTrue(data['success'])
		# self.assertTrue(len(data['actors']) > 0)

	def test_error_401_get_all_actors(self):
		"""Test GET all actors w/o Authorization."""
		res = self.client().get('/actors')
		data = json.loads(res.data)

		self.assertEqual(res.status_code, 401)
		self.assertFalse(data['success'])
		self.assertEqual(data['message'], 'Authorization header is expected.')

	def test_error_404_get_actors(self):
		"""Test Error GET all actors."""
		res = self.client().get('/actors?page=1125125125', headers = casting_assistant_header)
		data = json.loads(res.data)

		self.assertEqual(res.status_code, 404)
		self.assertFalse(data['success'])


	#-----Patch /actors/id-------#

		#---401 header not included----#
	def test_error_401_edit_actors(self):
		json_edit_actor={'name' : 'updated_name', 'age' : '40'}

		res=self.client().patch('/actors/1', json = json_edit_actor)
		data=json.loads(res.data)

		self.assertEqual(data.status_code, 401)
		self.assertFalse(data['success'])

	#------403 unauthorized error----#
	def test_error_403_edit_actor(self):
		json_edit_actor={'name' : 'updated_name', 'age' : '40'}

		res=self.client().post('/actors/1', json = json_edit_actor, headers = casting_assistant_header)
		data=json.loads(res.data)

		self.assertEqual(data.status_code, 403)
		self.assertFalse(data['success'])

		#-----200 edit actors----#
	def test_edit_actors(self):
		json_edit_actor={'name' : 'updated_name', 'age' : '40'}

		res=self.client().post('/actors/1', json = json_edit_actor, headers = executive_producer_header)
		data=json.loads(res.data)

		self.assertEqual(data.status_code, 200)
		self.assertFalse(data['success'])
		self.assertEqual(data['id'], id)


	#-----test for /actors DELETE----#
	def test_error_401_delete_actor(self):
		"""Test DELETE existing actor w/o Authorization"""
		res = self.client().delete('/actors/1')
		data = json.loads(res.data)

		self.assertEqual(res.status_code, 401)
		self.assertFalse(data['success'])
		#self.assertEqual(data['message'], 'Authorization header is expected.')

	def test_error_403_delete_actor(self):
		"""Test DELETE existing actor with missing permissions"""
		res = self.client().delete('/actors/1', headers = casting_assistant_header)
		data = json.loads(res.data)

		self.assertEqual(res.status_code, 403)
		self.assertFalse(data['success'])
		#self.assertEqual(data['message'], 'Permission not found.')

	def test_delete_actor(self):
		"""Test DELETE existing actor"""
		res = self.client().delete('/actors/1', headers = casting_director_header)
		data = json.loads(res.data)

		self.assertEqual(res.status_code, 200)
		self.assertTrue(data['success'])
		self.assertEqual(data['deleted'], '1')



if __name__==('__main__'):
	unittest.main()
