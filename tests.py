#!/usr/bin/env python3.6
import coverage
COV = coverage.coverage(branch=True, include='api*')
COV.set_option('report:show_missing', True)
COV.start()

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

	def test_products(self):
		# get llist of products
		rv, json = self.client.get('/products/')
		self.assertTrue(rv.status_code == 200)
		self.assertTrue(json['products'] == [])

		# add a product
		rv, json = self.client.post('/products/', data={'name': 'iphone x'})
		self.assertTrue(rv.status_code == 201)
		location = rv.headers['Location']
		rv, json = self.client.get(location)
		self.assertTrue(rv.status_code == 200)
		self.assertTrue(json['name'] == 'iphone x')
		rv, json = self.client.get('/products/')
		self.assertTrue(rv.status_code == 200)
		self.assertTrue(json['products'] == [location])

		# edit a product
		rv, json = self.client.put(location, data={'name': 'iphone 8'})
		self.assertTrue(rv.status_code == 200)
		rv, json = self.client.get(location)
		self.assertTrue(rv.status_code == 200)
		self.assertTrue(json['name'] == 'iphone 8')
		

if __name__ == '__main__':
	suite = unittest.TestLoader().loadTestsFromTestCase(TestAPI)
	unittest.TextTestRunner(verbosity=2).run(suite)
	COV.stop()
	COV.report()


