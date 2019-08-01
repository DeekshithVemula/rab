import os
from flask import Flask
import pika
import time
import sys

service=sys.argv[1]
user=sys.argv[2]
pas=sys.argv[3]


workers = int(os.environ.get('GUNICORN_PROCESSES', '3'))
threads = int(os.environ.get('GUNICORN_THREADS', '1'))

forwarded_allow_ips = '*'
secure_scheme_headers = { 'X-Forwarded-Proto': 'https' }
application = Flask(__name__)

mi='aka'

@application.route("/")
def hello():
    credentials = pika.PlainCredentials(user,pas)
    parameters = pika.ConnectionParameters(service,5672,'/',credentials)
    connection = pika.BlockingConnection(parameters)
    channel = connection.channel()

    channel.exchange_declare(exchange='topic_logs', exchange_type='topic')

    result = channel.queue_declare('', exclusive=True)
    queue_name = result.method.queue

    binding_keys = ['anonymous.info']
    
    if not binding_keys:
        sys.stderr.write("Usage: %s [binding_key]...\n" % sys.argv[0])
        sys.exit(1)

    for binding_key in binding_keys:
        channel.queue_bind(
            exchange='topic_logs', queue=queue_name, routing_key=binding_key)

   


     def callback(ch, method, properties, body):
        global mi
        print(" [x] %r:%r" % (method.routing_key, body))
        mi=body
        connection.close()
    
    channel.basic_consume(
        queue=queue_name, on_message_callback=callback, auto_ack=True)

    channel.start_consuming()
    return mi

if __name__ == "__main__":
    application.run(host='0.0.0.0', port=8080)

    
