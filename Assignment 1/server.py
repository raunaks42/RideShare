from datetime import datetime
from random import random

from flask import Flask, jsonify
from flask_restful import Api, Resource, reqparse
from requests import post

from database import execute, fetchone, fetchall

app = Flask(__name__)
api = Api(app)

port=80
URL="http://localhost:"+str(port)

class Users(Resource):
    def __init__(self):
        self.reqparser = reqparse.RequestParser()
        self.reqparser.add_argument('username', type = str, required = True)
        self.reqparser.add_argument('password', type = lambda x: hex(int(x, 16)), required = True)
        super(Users, self).__init__()

    def put(self):
        args = self.reqparser.parse_args(strict = True) #400 if extra args or less args
        username = args['username']
        password = args['password']
        req={
            'query':'insert',
            'table':'users',
            'values': {
                'username':username.
                'password':password
            }
        }
        res=post(URL+"/api/v1/db/write", json=req)
        

class User(Resource):
    def __init__(self):
        self.reqparser = reqparse.RequestParser()
        super(User, self).__init__()

    def delete(self, username):
        self.reqparser.parse_args(strict = True)

class Rides(Resource):
    def __init__(self):
        self.reqparser = reqparse.RequestParser()
        self.reqparser.add_argument('created_by', type = str, required = True)
        self.reqparser.add_argument('timestamp', type = lambda x: datetime.strptime(x, '%d-%m-%Y:%S-%M-%H'), required = True)
        self.reqparser.add_argument('source', type = int, required = True)
        self.reqparser.add_argument('destination', type = int, required = True)
        super(Rides, self).__init__()

    def post(self):
        args = self.reqparser.parse_args(strict = True)
        created_by = args['created_by']
        timestamp = args['timestamp']
        source = args['source']
        destination = args['destination']

class RideSD(Resource):
    def __init__(self):
        self.reqparser = reqparse.RequestParser()
        super(RideSD, self).__init__()

    def get(self, source, destination):
        self.reqparser.parse_args(strict = True)

class RideID(Resource):
    def get(self, id):
        reqparser = reqparse.RequestParser()
        reqparser.parse_args(strict = True)

    def post(self, id):
        reqparser = reqparse.RequestParser()
        reqparser.add_argument('username', type = str, required = True)
        args = reqparser.parse_args(strict = True)
        username = args['username']

    def delete(self, id):
        reqparser = reqparse.RequestParser()
        reqparser.parse_args(strict = True)

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
                if execute(delete_query):
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
api.add_resource(User, '/api/v1/users/<str:username>')
api.add_resource(Rides, '/api/v1/rides')
api.add_resource(RideSD, '/api/v1/rides?source=<int:source>&destination=<int:destination>')
api.add_resource(RideID, '/api/v1/rides/<int:id>')
api.add_resource(DBWrite, '/api/v1/db/write')
api.add_resource(DBRead, '/api/v1/db/read')


if __name__ == '__main__':
	app.run(port=port)
