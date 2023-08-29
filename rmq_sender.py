#!/usr/bin/env python
import pika
import json as js


def send_to_analyzer(body):
    connection = pika.BlockingConnection(pika.ConnectionParameters(host="localhost"))
    channel = connection.channel()

    channel.queue_declare(queue="AnalyzerQueue")

    channel.basic_publish(exchange="", routing_key="AnalyzerQueue", body=body)
    print(" [x] Sent analyzer job!'")
    connection.close()


def send_results(body):
    credentials = pika.PlainCredentials("guest", "guest")
    connection = pika.BlockingConnection(
        pika.ConnectionParameters(
            host="192.168.221.247", port=5672, virtual_host="/", credentials=credentials
        )
    )
    channel = connection.channel()

    channel.queue_declare(queue="DependencyCheckQueue")

    channel.basic_publish(exchange="", routing_key="DependencyCheckQueue", body=body)
    print(" [x] Sent resultsss!")
    connection.close()


def test():
    data = {
        "data": {
            "api": "repo",
            "keyword": "react",
            "language": "java",
            "created_from": "2022-04-17",
            "created_till": "2022-04-17",
            "sort_by": "stars",
            "order": "desc",
        }
    }

    json_body = js.dumps(data)

    credentials = pika.PlainCredentials("guest", "guest")
    connection = pika.BlockingConnection(
        pika.ConnectionParameters(
            host="192.168.221.247", port=5672, virtual_host="/", credentials=credentials
        )
    )
    channel = connection.channel()

    channel.queue_declare(queue="JobQueue")

    channel.basic_publish(exchange="", routing_key="JobQueue", body=json_body)
    print(f"{json_body}")
    connection.close()



