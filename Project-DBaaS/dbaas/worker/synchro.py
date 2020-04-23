import pika
from database import execute, fetchone, fetchall
import json

def do_synchronize(ch,method,properties,body):
    #sync local dbase for eventual consistency
    action = json.loads(body)['request'] #deserialize the body
    print("SYNCHRO RECEIVED")
    if (action['query'] == "clear"):
        db_clear()
    else:
        if ("condition" in action):
            db_write(action["query"],action["table"],action["values"],action["condition"])
        else:
            db_write(action["query"],action["table"],action["values"])
    ch.basic_ack(delivery_tag=method.delivery_tag)

def db_clear():
    tables = ["rides", "riders", "users"]
    for table in tables:
        delete_query = '''
        DELETE FROM ''' + table
        execute(delete_query)
    return {}, 200

def db_write(query,table,values,condition=None):
    query = query
    table = table
    if query == 'insert':
        if values:
            #values = values
            insert_query = '''
                INSERT INTO ''' + table + '(' + ','.join(values.keys()) + ') ' + '''
                VALUES ''' + '(' + ','.join(map(repr, values.values())) + ')'
            if execute(insert_query):
                return 200
        return 400
    elif query == 'delete':
        if condition:
            delete_query = '''
                DELETE FROM ''' + table + '''
                WHERE ''' + ' AND '.join(map(lambda x, y: x + '=' + repr(y), condition.keys(), condition.values()))
            execute(delete_query)
            return 200
        return 400

connection = pika.BlockingConnection(pika.ConnectionParameters(host='bunny'))
sync_channel = connection.channel()
r = sync_channel.queue_declare("",exclusive=True)
sync_channel.exchange_declare(exchange = "syncQ",exchange_type='fanout')
sync_channel.queue_bind(exchange='syncQ',queue=r.method.queue,routing_key='')
sync_channel.basic_consume(queue = r.method.queue, on_message_callback = do_synchronize)
print("SYNCHRO")
sync_channel.start_consuming()