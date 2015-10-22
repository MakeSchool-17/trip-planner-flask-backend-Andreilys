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
        db.drop_collection('users')
        db.drop_collection('trips')

        self.app.post('/users/',
            data=json.dumps(dict(username="name", password="github")),
            content_type='application/json')

    def headers(self):
        headers = {'Authorization': 'Basic '
                        + b64encode("{0}:{1}".format("name", "github").encode("utf-8")).decode("utf-8")}
        return headers

    def test_creating_user(self):
        print("Creating user")
        response = self.app.post('/users/',
            data=json.dumps(dict(username="name2", password="github2")),
            content_type='application/json')

        responseJSON = json.loads(response.data.decode())

        self.assertEqual(response.status_code, 200)
        assert 'application/json' in response.content_type
        assert 'name' in responseJSON["username"]

    def test_getting_user(self):
        print("Test getting a user")
        # pass a user ID
        headers = self.headers()
        response = self.app.get('/users/', headers=headers)

        responseJSON = json.loads(response.data.decode())
        self.assertEqual(response.status_code, 200)
        assert 'application/json' in response.content_type
        assert 'name' in responseJSON["username"]

    def test_posting_trip(self):
        print("Test posting a trip")
        headers = self.headers()
        response = self.app.post(
            '/trips/',
            data=json.dumps(dict(trip="Paris")),
            content_type='application/json', headers=headers)

        responseJSON = json.loads(response.data.decode())
        self.assertEqual(response.status_code, 200)
        assert 'application/json' in response.content_type
        assert 'Paris' in responseJSON["trip"]

    def test_getting_all_trips(self):
        print("Getting all trips")
        self.test_posting_trip()
        headers = {'Authorization': 'Basic '
                    + b64encode("{0}:{1}".format("name", "github").encode("utf-8")).decode("utf-8")}
        response = self.app.get(
            '/trips/', headers=headers)
        # this returns a list of dictionaries (aka trips)
        responseJSON = json.loads(response.data.decode())
        self.assertEqual(response.status_code, 200)
        assert "Paris" in responseJSON[0]["trip"]

    def test_getting_trip(self):
        print("Tests getting a trip")
        headers = self.headers()
        response = self.app.post(
            '/trips/',
            data=json.dumps(dict(trip="Paris")),
            content_type='application/json', headers=headers)
        responseJSON = json.loads(response.data.decode())
        # saving object id variable for later
        object_id = responseJSON["_id"]

        # this returns all the trips I need
        response = self.app.get(
            '/trips/' + object_id, headers=headers)
        responseJSON = json.loads(response.data.decode())

        self.assertEqual(response.status_code, 200)
        assert 'Paris' in responseJSON["trip"]

    def test_getting_non_existent_object(self):
        headers = {'Authorization': 'Basic '
                    + b64encode("{0}:{1}".format("name", "github").encode("utf-8")).decode("utf-8")}
        response = self.app.get('/trips/55f0cbb4236f44b7f0e3cb23', headers=headers)
        self.assertEqual(response.status_code, 404)

    def test_modifying_object(self):
        headers = self.headers()
        response = self.app.post(
            '/trips/',
            data=json.dumps(dict(trip="Paris", waypoint="Montreal")),
            content_type='application/json', headers=headers)
        responseJSON = json.loads(response.data.decode())
        # saving object id variable for later
        object_id = responseJSON["_id"]

        response = self.app.put('/trips/' + object_id, data=json.dumps(dict(trip="Toronto", waypoint="Lithuania")),
        content_type='application/json', headers=headers)
        responseJSON = json.loads(response.data.decode())
        assert "Toronto" in responseJSON["trip"]
        #
    def test_deleting_object(self):
        headers = self.headers()
        response = self.app.post(
            '/trips/',
            data=json.dumps(dict(trip="Paris", waypoint="Montreal")),
            content_type='application/json', headers=headers)
        responseJSON = json.loads(response.data.decode())
        # saving object id variable for later
        object_id = responseJSON["_id"]

        response = self.app.delete("/trips/" + object_id, headers=headers)
        self.assertEqual(response.status_code, 200)

if __name__ == '__main__':
    unittest.main()
