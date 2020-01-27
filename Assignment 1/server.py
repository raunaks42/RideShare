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
        try:
            int(value,16)
            return value
        except:
            abort(400)
    abort(400)

def mydatetime(value):
    try:
        datetime.strptime(value, '%d-%m-%Y:%S-%M-%H')
        return value
    except:
        abort(400)

class Users(Resource):
    def __init__(self):
        self.reqparser = reqparse.RequestParser()
        self.reqparser.add_argument('username', type = str, required = True)
        self.reqparser.add_argument('password', type = sha1, required = True)
        super(Users, self).__init__()

    def put(self):
        args = self.reqparser.parse_args(strict = True) #400 if extra args or less args
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
        return {}, (201 if res.status_code==200 else 405)


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
                resd = post(URL+"/api/v1/db/write", json = req)
                return {}, (200 if resd.status_code==200 else 405)
            return {}, 405
        return {}, 400


class Rides(Resource):
    def __init__(self):
        self.reqparser = reqparse.RequestParser()
        self.reqparser.add_argument('created_by', type = str, required = True)
        self.reqparser.add_argument('timestamp', type = mydatetime, required = True)
        self.reqparser.add_argument('source', type = int, required = True)
        self.reqparser.add_argument('destination', type = int, required = True)
        super(Rides, self).__init__()

    def post(self):
        args = self.reqparser.parse_args(strict = True)
        created_by = args['created_by']
        timestamp = args['timestamp']
        source = args['source']
        destination = args['destination']
        
        enum = pd.read_csv('AreaNameEnum.csv')
        if source in enum['Area No'] and destination in enum['Area No']:
            del enum
            req = {
                'table':'rides',
                'columns': ['MAX(rideId)']
            }
            res = post(URL+"/api/v1/db/read", json = req)
            rideId = (res.json()['MAX(rideId)']+1 if res.status_code==200 else 1)
            req = {
                'query': 'insert',
                'table': 'rides',
                'values': {
                    'rideId': rideId,
                    'created_by': created_by,
                    'timestamp': timestamp,
                    'source': source,
                    'destination': destination
                }
            }
            res1 = post(URL+"/api/v1/db/write", json = req)
            return {}, (201 if res1.status_code==200 else 405)
        return {}, 405


class RideSD(Resource):
    def get(self, source, destination):
        if not request.json:
            enum = pd.read_csv('AreaNameEnum.csv')
            if source in enum['Area No'] and destination in enum['Area No']:
                del enum
                req = {
                    'table': 'rides',
                    'columns': ['rideId', 'created_by', 'timestamp'],
                    'condition': {
                        'source': source,
                        'destination': destination
                    }
                }
                res=post(URL+"/api/v1/db/read", json = req)
                res_json=res.json()
                res_json['username']=res_json.pop('created_by')
                return ({}, 405) if res.status_code==400 else ( (res_json, 200) if res_json else ({}, 204) )
            return {}, 405
        return {}, 400

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
            if res.status_code==200:
                if res.json():
                    res_json=res.json()
                    req = {
                        'table': 'riders',
                        'columns': ['user'],
                        'condition': {
                            'rideId': id
                        }
                    }
                    resr = post(URL+"/api/v1/db/read", json = req)
                    res_json['users']=list(resr.json().values())
                    return res_json, 200
                return {}, 204
            return {}, 405
        return {}, 400

    def post(self, id):
        reqparser = reqparse.RequestParser()
        reqparser.add_argument('username', type = str, required = True)
        args = reqparser.parse_args(strict = True)
        username = args['username']
        req = {
            'table': 'rides',
            'columns': ['rideId'],
            'condition': {
                'rideId': id
            }
        }
        res = post(URL+"/api/v1/db/read", json = req)
        if res.status_code==200:
            req = {
                'query': 'insert',
                'table': 'riders',
                'values': {
                    'rideId': id,
                    'user': username
                }
            }
            resw = post(URL+"/api/v1/db/write", json = req)
            return {}, (200 if resw.status_code==200 else 405)
        return {}, 204

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
                resd=post(URL+"/api/v1/db/write", json = req)
                return {}, (200 if resd.status_code==200 else 405)
            return {}, 405
        return {}, 400

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
                execres=execute(delete_query)
                print(execres)
                if execres:
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
            if rows:
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

