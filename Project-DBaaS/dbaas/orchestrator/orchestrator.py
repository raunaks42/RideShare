from datetime import datetime
from flask import Flask, jsonify, request, current_app, abort
from flask_restful import Api, Resource, reqparse
import pandas as pd
import flask_restful
from requests import post,get
from werkzeug.exceptions import HTTPException
import os
import subprocess
import pika
import json
import uuid
import time
from logging.config import dictConfig

dictConfig({
    'version': 1,
    'formatters': {'default': {
        'format': '[%(asctime)s] %(levelname)s in %(module)s: %(message)s',
    }},
    'handlers': {'wsgi': {
        'class': 'logging.StreamHandler',
        'stream': 'ext://flask.logging.wsgi_errors_stream',
        'formatter': 'default'
    }},
    'root': {
        'level': 'DEBUG',
        'handlers': ['wsgi']
    }
})
app = Flask(__name__)
api = Api(app)

connection = pika.BlockingConnection(pika.ConnectionParameters(host='bunny'))
channel_r = connection.channel()
channel_r.queue_declare("readQ")
channel_w = connection.channel()
channel_w.queue_declare("writeQ")
class ReadRpcClient(object):
    def __init__(self):
        self.connection = pika.BlockingConnection(pika.ConnectionParameters(host='bunny'))
        self.channel = self.connection.channel()
        result = self.channel.queue_declare(queue='', exclusive=True)
        self.callback_queue = result.method.queue
        self.channel.basic_consume(queue=self.callback_queue,on_message_callback=self.on_response,auto_ack=True)

    def on_response(self, ch, method, props, body):
        if self.corr_id == props.correlation_id:
            self.response = json.loads(body)

    def call(self,request):
       
        self.response = None
        self.corr_id = str(uuid.uuid4())
        self.channel.basic_publish(
            exchange='',
            routing_key='readQ',
            properties=pika.BasicProperties(
                reply_to=self.callback_queue,
                correlation_id=self.corr_id,
            ),
            body=json.dumps(request))
        retries = 0
        while self.response is None:
            if (retries == 5):
                break
            retries +=1
            self.connection.process_data_events()
            time.sleep(0.5 * retries)
            
        if (self.response):
            return self.response["data"],self.response["status"]
        else:
            return {}, 503 #service unavailable

class WriteRpcClient(object):
    def __init__(self):
        self.connection = pika.BlockingConnection(pika.ConnectionParameters(host='bunny'))
        self.channel = self.connection.channel()
        result = self.channel.queue_declare(queue='', exclusive=True)
        self.callback_queue = result.method.queue
        self.channel.basic_consume(queue=self.callback_queue,on_message_callback=self.on_response,auto_ack=True)

    def on_response(self, ch, method, props, body):
        if self.corr_id == props.correlation_id:
            self.response = json.loads(body)

    def call(self,request):
        
        self.response = None
        self.corr_id = str(uuid.uuid4())
        self.channel.basic_publish(
            exchange='',
            routing_key='writeQ',
            properties=pika.BasicProperties(
                reply_to=self.callback_queue,
                correlation_id=self.corr_id,
            ),
            body=json.dumps(request))
        retries = 0
        while self.response is None:
            if (retries == 5):
                break
            retries +=1
            self.connection.process_data_events()
            time.sleep(0.5 * retries)
        if (self.response):
            return self.response["data"],self.response["status"]
        else:
            return {}, 503 #service unavailable
#@app.after_request
def after(response):
    with open("orchestrator_logs.csv", 'a') as log:
        if os.stat("orchestrator_logs.csv").st_size == 0:
            print('Type;Path;Request Body;;Response Code;Response Body', file=log)
        else:
            print(request.method, end=";", file=log)
            print(request.path, end=";", file=log)
            # print(str(request.headers).strip(), end=";",file=log)
            print(request.json, end=";", file=log)
            print(response.status, end=";", file=log)
            # print(response.headers, end=";", file=log)
            print(response.json, file=log)
    return response

def mydatetime(value):
    datetime.strptime(value, '%d-%m-%Y:%S-%M-%H')
    return value

class DBWrite(Resource):
    def post(self):
        #write request received, add to the writeQ
        #channel_w.basic_publish(exchange = '',routing_key='writeQ',body=json.dumps(request.get_json()))
        writer = WriteRpcClient()
        response = writer.call(request.get_json())
        return response

class DBRead(Resource):
    def post(self):
        #read request received, add to the readQ
        #channel_r.basic_publish(exchange = '',routing_key='readQ',body=json.dumps(request.get_json()))
        reader = ReadRpcClient()
        response = reader.call(request.get_json())
        return response

class DBClear(Resource):
    def post(self):
        #clear request (write), add to the writeQ
        data = {"query":"clear"}
        #channel_w.basic_publish(exchange = '',routing_key='writeQ',body=json.dumps(data))
        writer = WriteRpcClient()
        response = writer.call(data)
        return response

api.add_resource(DBWrite, '/api/v1/db/write')
api.add_resource(DBRead, '/api/v1/db/read')
api.add_resource(DBClear, '/api/v1/db/clear')

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=9500)
