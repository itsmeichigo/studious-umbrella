#!/usr/bin/env python3.6
import os
os.environ['DATABASE_URL'] = 'sqlite:///test.sqlite'

import unittest
from api import app, db, User
from test_client import TestClient

class TestAPI(unittest.TestCase):
	default_username = 'ichigo'
	default_password = 'cat'

	def setUp(self):
		self.app = app
		self.ctx = self.app.app_context()
		self.ctx.push()
		db.drop_all()
		db.create_all()
		u = User(username=self.default_username)
		u.set_password(self.default_password)
		db.session.add(u)
		db.session.commit()
		self.client = TestClient(self.app, u.generate_auth_token(), '')

	def tearDown(self):
		db.session.remove()
		db.drop_all()
		self.ctx.pop()

	def test_customers(self):
		# get list of customers
		rv, json = self.client.get('/customers/')
		self.assertTrue(rv.status_code == 200)
		self.assertTrue(json['customers'] == [])

		# add a customer
		rv, json = self.client.post('/customers/', data={'name': 'coraline'})
		self.assertTrue(rv.status_code == 201)
		location = rv.headers['Location']
		rv, json = self.client.get(location)
		self.assertTrue(rv.status_code == 200)
		self.assertTrue(json['name'] == 'coraline')
		rv, json = self.client.get('/customers/')
		self.assertTrue(rv.status_code == 200)
		self.assertTrue(json['customers'] == [location])

		# edit the customer
		rv, json = self.client.put(location, data={'name': 'caroline'})
		self.assertTrue(rv.status_code == 200)
		rv, json = self.client.get(location)
		self.assertTrue(rv.status_code == 200)
		self.assertTrue(json['name'] == 'caroline')

if __name__ == '__main__':
	unittest.main()

