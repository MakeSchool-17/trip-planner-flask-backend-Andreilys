import server
import unittest
import json
from pymongo import MongoClient
from base64 import b64encode


class FlaskrTestCase(unittest.TestCase):

    def setUp(self):
        self.app = server.app.test_client()
        # Run app in testing mode to retrieve exceptions and stack traces
        server.app.config['TESTING'] = True

        # Inject test database into application
        mongo = MongoClient('localhost', 27017)
        db = mongo.test_database
        server.app.db = db

        # Drop collection (significantly faster than dropping entire db)
        db.drop_collection('myobjects')

        # MyObject tests

    def test_creating_user(self):
        print("Creating user")
        response = self.app.post('/users/',
            data=json.dumps(dict(username="name", password="github")),
            content_type='application/json')

        responseJSON = json.loads(response.data.decode())

        self.assertEqual(response.status_code, 200)
        assert 'application/json' in response.content_type
        assert 'name' in responseJSON["username"]

    def test_getting_user(self):
        print("Getting user")
        # pass a user ID
        username = "name"
        password = "github"
        headers = {'Authorization': 'Basic ' + b64encode("{0}:{1}".format(username, password).encode("utf-8")).decode("utf-8")}
        response = self.app.get('/users/', headers=headers)
        print(response)
        # inserted_user = user_collection.find_one({"username": 'name'})
        # print(user_collection)

        # headers = {'Authorization': 'Basic ' + b64encode("{0}:{1}".format(username, password).encode("utf-8")).decode("utf-8")}
        # response = self.app.get('/users/' + username, headers=headers)
        #
        # responseJSON = json.loads(response.data.decode())
        #
        # self.assertEqual(response.status_code, 200)
        # assert 'application/json' in response.content_type
        # assert 'name' in responseJSON["username"]
        #
    #
    # def test_checking_auth(self):
    #     break
    #
    # def test_posting_myobject(self):
    #     response = self.app.post(
    #         '/trips/',
    #         data=json.dumps(dict(name="A object")),
    #         content_type='application/json')
    #
    #     responseJSON = json.loads(response.data.decode())
    #
    #     self.assertEqual(response.status_code, 200)
    #     assert 'application/json' in response.content_type
    #     assert 'A object' in responseJSON["name"]
    #
    # def test_getting_object(self):
    #     print("Tests getting object")
    #     response = self.app.post(
    #         '/trips/',
    #         data=json.dumps(dict(name="Another object")),
    #         content_type='application/json')
    #
    #     postResponseJSON = json.loads(response.data.decode())
    #     postedObjectID = postResponseJSON["_id"]
    #
    #     response = self.app.get('/trips/' + postedObjectID)
    #     responseJSON = json.loads(response.data.decode())
    #
    #     self.assertEqual(response.status_code, 200)
    #     assert 'Another object' in responseJSON["name"]
    #
    # def test_getting_non_existent_object(self):
    #     response = self.app.get('/trips/55f0cbb4236f44b7f0e3cb23')
    #     self.assertEqual(response.status_code, 404)
    #
    # def test_modifying_object(self):
    #     break
    #
    # def test_deleting_object(self):
    #     break

if __name__ == '__main__':
    unittest.main()
