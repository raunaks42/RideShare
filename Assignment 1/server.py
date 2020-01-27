from datetime import datetime
from random import random
import pandas as pd

from flask import Flask, jsonify, abort, request
from flask_restful import Api, Resource, reqparse
from requests import post

from database import execute, fetchone, fetchall

app = Flask(__name__)
api = Api(app)

port = 4000
URL = "http://localhost:"+str(port)

def sha1(value):
    if len(value)==40:
        int(value,16)
        return value
    raise ValueError('Length is not 40')

def mydatetime(value):
    datetime.strptime(value, '%d-%m-%Y:%S-%M-%H')
    return value

class Users(Resource):
    def __init__(self):
        self.reqparser = reqparse.RequestParser()
        self.reqparser.add_argument('username', type = str, required = True)
        self.reqparser.add_argument('password', type = sha1, required = True)
        super(Users, self).__init__()

    def put(self):
        args = self.reqparser.parse_args(strict = True) #400 if extra or less fields, non sha1 password
        username = args['username']
        password = args['password']
        req = {
            'query':'insert',
            'table':'users',
            'values': {
                'username':username,
                'password':password
            }
        }
        res = post(URL+"/api/v1/db/write", json = req)
        return {}, (201 if res.status_code==200 else 405) #405 if insert fail


class User(Resource):
    def delete(self, username):
        if not request.json:
            req = {
                'table': 'users',
                'columns': ['username'],
                'condition': {
                    'username': username
                }
            }
            res = post(URL+"/api/v1/db/read", json = req)
            if res.json():
                req = {
                    'query': 'delete',
                    'table': 'users',
                    'condition': {
                        'username': username
                    }
                }
                post(URL+"/api/v1/db/write", json = req)
                return {}, 200 
            return {}, 405 #username doesnt exist
        return {}, 400 #non empty request json


class Rides(Resource):
    def __init__(self):
        self.reqparser = reqparse.RequestParser()
        self.reqparser.add_argument('created_by', type = str, required = True)
        self.reqparser.add_argument('timestamp', type = mydatetime, required = True)
        self.reqparser.add_argument('source', type = int, required = True)
        self.reqparser.add_argument('destination', type = int, required = True)
        super(Rides, self).__init__()

    def post(self):
        args = self.reqparser.parse_args(strict = True) #400 if incorrect timestamp format, any extra/less fields
        created_by = args['created_by']
        timestamp = args['timestamp']
        source = args['source']
        destination = args['destination']
        
        enum = pd.read_csv('AreaNameEnum.csv')
        if source in enum['Area No'] and destination in enum['Area No'] and source!=destination:
            req = {
                'query': 'insert',
                'table': 'rides',
                'values': {
                    'created_by': created_by,
                    'timestamp': timestamp,
                    'source': source,
                    'destination': destination
                }
            }
            res1 = post(URL+"/api/v1/db/write", json = req)
            return {}, (201 if res1.status_code==200 else 405) #405 if given username doesnt exist
        return {}, 405 #if source/destination same or incorrect


class RideSD(Resource):
    def get(self, source, destination):
        if not request.json:
            enum = pd.read_csv('AreaNameEnum.csv')
            if source in enum['Area No'] and destination in enum['Area No'] and source!=destination:
                req = {
                    'table': 'rides',
                    'columns': ['rideId', 'created_by', 'timestamp'],
                    'condition': {
                        'source': source,
                        'destination': destination
                    }
                }
                res=post(URL+"/api/v1/db/read", json = req)
                res_json=[ride for ride in res.json() if datetime.strptime(ride['timestamp'], '%d-%m-%Y:%S-%M-%H') > datetime.now()]
                for ride in res_json:
                    ride['username']=ride.pop('created_by')
                return (res_json, 200) if res_json else ({}, 204) #204 if no rides
            return {}, 405 #if source/destination same or incorrect
        return {}, 400 #if non empty request body

class RideID(Resource):
    def get(self, id):
        if not request.json:
            req = {
                'table': 'rides',
                'columns': ['rideId', 'created_by', 'timestamp', 'source', 'destination'],
                'condition': {
                    'rideId': id
                }
            }
            res = post(URL+"/api/v1/db/read", json = req)
            if res.json():
                res_json=res.json()[0]
                req = {
                    'table': 'riders',
                    'columns': ['user'],
                    'condition': {
                        'rideId': id
                    }
                }
                resr = post(URL+"/api/v1/db/read", json = req)
                res_json['users']=[i['user'] for i in resr]
                return res_json, 200
            return {}, 204 #if no rides found
        return {}, 400 #if request json is not empty
        #idk 405 here

    def post(self, id):
        reqparser = reqparse.RequestParser()
        reqparser.add_argument('username', type = str, required = True)
        args = reqparser.parse_args(strict = True) #400 if any extra or less fields
        username = args['username']
        req = {
            'table': 'rides',
            'columns': ['rideId'],
            'condition': {
                'rideId': id
            }
        }
        res = post(URL+"/api/v1/db/read", json = req)
        if res.json():
            req = {
                'query': 'insert',
                'table': 'riders',
                'values': {
                    'rideId': id,
                    'user': username
                }
            }
            resw = post(URL+"/api/v1/db/write", json = req)
            return {}, (200 if resw.status_code==200 else 405) #405 if user not found or user already joined ride
        return {}, 204 #ride not found

    def delete(self, id):
        if not request.json:
            req = {
                'table': 'rides',
                'columns': ['rideId'],
                'condition': {
                    'rideId': id
                }
            }
            res = post(URL+"/api/v1/db/read", json = req)
            if res.json():
                req = {
                    'query': 'delete',
                    'table': 'riders',
                    'condition': {
                        'rideId': id
                    }
                }
                post(URL+"/api/v1/db/write", json = req)
                return {}, 200
            return {}, 405 #if ride not found
        return {}, 400 #if request json not empty

class DBWrite(Resource):
    def __init__(self):
        self.reqparser = reqparse.RequestParser()
        self.reqparser.add_argument('query', type = str, required = True)
        self.reqparser.add_argument('table', type = str, required = True)
        self.reqparser.add_argument('values', type = dict)
        self.reqparser.add_argument('condition', type = dict)
        super(DBWrite, self).__init__()

    def post(self):
        args = self.reqparser.parse_args()
        query = args['query']
        table = args['table']

        if query=='insert':
            if 'values' in args:
                values = args['values']
                insert_query = '''
                    INSERT INTO ''' + table + '(' + ','.join(values.keys()) + ') ' + '''
                    VALUES ''' + '(' + ','.join(map(repr, values.values())) + ')'
                if execute(insert_query):
                    return {}, 200
            return {}, 400
        
        elif query=='delete':
            if 'condition' in args:
                condition = args['condition']
                delete_query = '''
                    DELETE FROM ''' + table + '''
                    WHERE ''' + ' AND '.join(map(lambda x, y: x+'='+repr(y), condition.keys(), condition.values()))
                execute(delete_query)
                return {}, 200
            return {}, 400

class DBRead(Resource):
    def __init__(self):
        self.reqparser = reqparse.RequestParser()
        self.reqparser.add_argument('table', type = str, required = True)
        self.reqparser.add_argument('columns', type = list)
        self.reqparser.add_argument('condition', type = dict)
        super(DBRead, self).__init__()

    def post(self):
        args = self.reqparser.parse_args()
        table = args['table']
        if 'columns' in args:
            columns = args['columns']
            select_query = '''
                SELECT ''' + ','.join(columns) + '''
                FROM ''' + table + '''
                ''' + ('WHERE ' + ' AND '.join(map(lambda x, y: x+'='+repr(y), args['condition'].keys(), args['condition'].values())) if 'condition' in args else '')
            rows = fetchall(select_query)
            res = []
            for row in rows:
                res.append({columns[i]: row[i] for i in range(len(columns))})
            return res, 200
        return {}, 400


api.add_resource(Users, '/api/v1/users')
api.add_resource(User, '/api/v1/users/<string:username>')
api.add_resource(Rides, '/api/v1/rides')
api.add_resource(RideSD, '/api/v1/rides?source=<int:source>&destination=<int:destination>')
api.add_resource(RideID, '/api/v1/rides/<int:id>')
api.add_resource(DBWrite, '/api/v1/db/write')
api.add_resource(DBRead, '/api/v1/db/read')


if __name__ == '__main__':
	app.run(port = port, debug=True)

