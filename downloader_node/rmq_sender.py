#!/usr/bin/env python
import pika
import json as js


def send_to_analyzer(body):
    connection = pika.BlockingConnection(pika.ConnectionParameters(host="mq"))
    channel = connection.channel()

    channel.queue_declare(queue="AnalyzerQueue2", durable= True)

    channel.basic_publish(exchange="", routing_key="AnalyzerQueue2", body=body, properties=pika.BasicProperties(
        delivery_mode=pika.spec.PERSISTENT_DELIVERY_MODE
    ))
    print(" [x] Sent analyzer job!'")
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
            host="mq" #host="192.168.221.130", port=5672, virtual_host="/", credentials=credentials
        )
    )
    channel = connection.channel()

    channel.queue_declare(queue="JobQueue")

    channel.basic_publish(exchange="", routing_key="JobQueue", body=json_body)
    print(f"{json_body}")
    connection.close()



