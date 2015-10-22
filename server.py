from flask import Flask, request, make_response, jsonify
from flask_restful import Resource, Api
from pymongo import MongoClient
from bson.objectid import ObjectId
from utils.mongo_json_encoder import JSONEncoder
import bcrypt
from functools import wraps

# Basic Setup
app = Flask(__name__)
mongo = MongoClient('localhost', 27017)
app.db = mongo.develop_database
api = Api(app)
app.bcrypt_rounds = 12


def check_auth(username, password):
    user_list = app.db.users
    user = user_list.find_one({"username": username})
    if user is None:
        return False
    # the password that was stored in the database (currently hashed)
    stored_pw = user["password"]
    encoded_pw = password.encode("utf-8")
    hashed_pw = bcrypt.hashpw(encoded_pw, stored_pw)
    # TODO the passwords here are messed up
    return stored_pw == hashed_pw


def requires_auth(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        auth = request.authorization
        if not auth or not check_auth(auth.username, auth.password):
            message = {'error': 'Basic Auth Required.'}
            resp = jsonify(message)
            resp.status_code = 401
            return resp
        return f(*args, **kwargs)
    return decorated


class Users(Resource):
    @requires_auth
    def get(self):
        username = request.authorization.username
        user_list = app.db.users
        user = user_list.find_one({"username": username})
        if user is None:
            response = jsonify(data=[])
            response.status_code = 404
            return response
        else:
            del user["password"]
            return user

    def post(self):
        new_user = request.json
        user_collection = app.db.users
        encoded_pw = new_user["password"].encode('utf-8')
        hashed_pw = bcrypt.hashpw(encoded_pw, bcrypt.gensalt(app.bcrypt_rounds))
        new_user["password"] = hashed_pw
        result = user_collection.insert_one(new_user)
        # why do I need to return here?
        inserted_user = user_collection.find_one({"_id": ObjectId(result.inserted_id)})
        del inserted_user['password']  # DO NOT return hashed password to client
        return inserted_user


api.add_resource(Users, '/users/', '/users/<string:user_id>')


class Trips(Resource):
    @requires_auth
    # get all functionality
    # if I set trip_id to none, and I pass a value, will it change?
    def get(self, trip_id=None):
        # retrieve database of trips (resource)
        trip_collection = app.db.trips
        if trip_id:
            trip = trip_collection.find_one({"_id": ObjectId(trip_id)})
            # if none throw an error
            if trip is None:
                response = jsonify(data=[])
                response.status_code = 404
                return response
            else:
                return trip
        else:
            # TODO figure out Get All method
            user_trips = trip_collection.find({"username": request.authorization.username})
            return list(user_trips)

    # posts a new trip with ID
    @requires_auth
    def post(self):
        new_trip = request.json
        new_trip["username"] = request.authorization.username
        # Should I add a username/pw to this json request?
        trip_collection = app.db.trips
        result = trip_collection.insert_one(new_trip)
        new_trip = trip_collection.find_one({"_id": ObjectId(result.inserted_id)})
        return new_trip

    # what does trip_id get input from?
    @requires_auth
    def put(self, trip_id):
        new_trip = request.json
        trip_collection = app.db.trips
        old_trip = trip_collection.update_one({"_id": ObjectId(trip_id)}, {'$set': new_trip}, upsert=False)
        mod_trip = trip_collection.find_one({"_id": ObjectId(trip_id)})
        return mod_trip

    # Takes in trip_id, deletes, and returns response
    @requires_auth
    def delete(self, trip_id):
        trip_collection = app.db.trips
        trip_collection.delete_one({"_id": ObjectId(trip_id)})
        deleted_object = trip_collection.find_one({"_id": ObjectId(trip_id)})
        # should return False since it deleted the object
        if not deleted_object:
            response = jsonify(data=[])
            response.status_code = 200
            return response
        else:
            response = jsonify(data=[])
            response.status_code = 304
            return response

api.add_resource(Trips, '/trips/', '/trips/<string:trip_id>')


# provide a custom JSON serializer for flaks_restful
@api.representation('application/json')
def output_json(data, code, headers=None):
    resp = make_response(JSONEncoder().encode(data), code)
    resp.headers.extend(headers or {})
    return resp

if __name__ == '__main__':
    # Turn this on in debug mode to get detailled information about request related exceptions: http://flask.pocoo.org/docs/0.10/config/
    app.config['TRAP_BAD_REQUEST_ERRORS'] = True
    app.run(debug=True)
