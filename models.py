from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import Column, String, Integer, create_engine
from flask_migrate import Migrate
from datetime import date

db=SQLAlchemy()

database_name="casting_agency"
database_path="postgres://gunarevuri@localhost:5432/{}".format(database_name)
def setup_db(app,database_path=database_path):
	app.config['SQLALCHEMY_DATABASE_URI']=database_path
	app.config['"SQLALCHEMY_TRACK_MODIFICATIONS"']=False
	db.app=app
	db.init_app(app)
	#db.create_all()

def drop_db_create_all():
	db.drop_all()
	db.create_all()
	db_initial_insert()

def db_initial_insert():
	#--adding initial values--#
	actor=Actors(name='avengers_actor', age=34, gender='Male')
	movie=Movies(title='avengers',release_date=date.today())
	movie.insert()
	actor.insert()


class Movies(db.Model):
	__tablename__="movies"
	id=Column(Integer() , primary_key= True)
	title=Column(String(), nullable=False)
	release_date=Column(String(), nullable=False)

	def __init__(self, title, release_date):
		self.title= title
		self.release_date= release_date

	def insert(self):
		db.session.add(self)
		db.session.commit()

	def delete(self):
		db.session.delete(self)
		db.session.commit()

	def update(self):
		db.session.commit()

	def format(self):
		return {
			'success': True,
			'id': self.id,
			'title': self.title,
			'release_date': self.release_date
			}


class Actors(db.Model):
	__tablename__="actors"
	id=Column(Integer(),primary_key=True)
	name=Column(String())
	age=Column(Integer())
	gender=Column(String())


	def __init__(self, name, age, gender):
		self.name= name
		self.age= age
		self.gender= gender

	def insert(self):
		db.session.add(self)
		db.session.commit()

	def delete(self):
		db.session.delete(self)
		db.session.commit()

	def update(self):
		db.session.commit()

	def format(self):
		return {
			'success':True,
			'name':self.name,
			'age':self.age,
			'gender':self.gender
			}





