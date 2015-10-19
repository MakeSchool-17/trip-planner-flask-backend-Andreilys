from flask import Flask, request, make_response, jsonify
from flask_restful import Resource, Api
from pymongo import MongoClient
from bson.objectid import ObjectId
from utils.mongo_json_encoder import JSONEncoder
# Basic Setup
app = Flask(__name__)
mongo = MongoClient('localhost', 27017)
app.db = mongo.develop_database
api = Api(app)


class User(Resource):
    def post(self):
        new_user = request.json
        user_list = app.db.users
        result = user_list.insert_one(new_user)
        user = user_list.find_one({"_id": ObjectId(result.inserted_id)})
        return user

    def get(self, user_id):
        user_list = app.db.users
        user = user_list.find_one({"_id": ObjectId(user_id)})
        if user is None:
            response = jsonify(data=[])
            response.status_code = 404
            return response
        else:
            return user

api.add_resource(User, '/users/', '/users/<string:user_id>')


class Trip(Resource):
    # creating a trip with the waypoints
    def post(self):
        new_trip = request.json
        trip_list = app.db.trips
        result = trip_list.insert_one(new_trip)
        trip = trip_list.find_one({"_id": ObjectId(result.inserted_id)})
        return trip

    # retrieve a specific trip ID
    def get(self, trip_id=None):
        trip_list = app.db.trips
        trip = trip_list.find_one({"_id": ObjectId(trip_id)})
        if trip is None:
            response = jsonify(data=[])
            response.status_code = 404
            return response
        else:
            return trip

    # get all the trip ID's
    def get_all(self):
        trip_list = app.db.trips
        if trip_list is None:
            response = jsonify(data=[])
            response.status_code = 404
            return response
        else:
            return trip_list

    # updating a trip with waypoints
    def put(self, trip_id):
        trip = trip_list.find_one({"_id": ObjectId(trip_id)})
        if trip is None:
            response = jsonify(data=[])
            response.status_code = 404
            return response
        else:
            modifying_trip = request.json
            trip_list = app.db.trips
            trip = trip_list.update_one({"_id": ObjectId(trip_id)})
            return trip

    # deleting a specific waypoint
    def delete(self, trip_id):
        trip_collection = app.db.trips
        trip = trip_collection.find_one({"_id": ObjectId(trip_id)})
        if trip is None:
            response = jsonify(data=[])
            response.status_code = 404
            return response
        else:
            if trip["username"] == request.json["username"]:
                result = trip_collection.delete_one({"_id": ObjectId(trip_id)})
                if result.deleted_count == 1:
                    response = jsonify(data=[])
                    response.status_code = 200
                    return response
                else:
                    response = jsonify(data=[])
                    response.status_code = 500
                    return response
            else:
                response = jsonify(data=[])
                response.status_code = 401
                return response

api.add_resource(Trip, '/trips/', '/trips/<string:trip_id>')


# provide a custom JSON serializer for flaks_restful
@api.representation('application/json')
def output_json(data, code, headers=None):
    resp = make_response(JSONEncoder().encode(data), code)
    resp.headers.extend(headers or {})
    return resp

if __name__ == '__main__':
    # Turn this on in debug mode to get detailed information
    # about request related exceptions: http://flask.pocoo.org/docs/0.10/config
    app.config['TRAP_BAD_REQUEST_ERRORS'] = True
    app.run(debug=True)
