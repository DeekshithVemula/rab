import os
from flask import Flask
import pika
import sys

service=sys.argv[1]
user=sys.argv[2]
pas=sys.argv[3]

workers = int(os.environ.get('GUNICORN_PROCESSES', '3'))
threads = int(os.environ.get('GUNICORN_THREADS', '1'))

forwarded_allow_ips = '*'
secure_scheme_headers = { 'X-Forwarded-Proto': 'https' }
application = Flask(__name__)

@application.route("/")
def hello():
    credentials = pika.PlainCredentials(user,pas)
    parameters = pika.ConnectionParameters(service,5672,'/',credentials)
    connection = pika.BlockingConnection(parameters)
    channel = connection.channel()

    channel.exchange_declare(exchange='topic_logs', exchange_type='topic')

    routing_key ='anonymous.info'
    message = 'Hello World!'
    channel.basic_publish(
        exchange='topic_logs', routing_key=routing_key, body=message)


    connection.close()
    return message

if __name__ == "__main__":
    application.run(host='0.0.0.0', port=8080)
