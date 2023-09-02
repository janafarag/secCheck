#!/usr/bin/env python
# reveice job from downloader to cone and alayze the given repos
import pika, sys, os
import analyzer

# Get the environment variables
# user = os.environ["RABBITMQ_DEFAULT_USER"]
# password = os.environ["RABBITMQ_DEFAULT_PASS"]
# vhost = os.environ["RABBITMQ_DEFAULT_VHOST"]
rabbit_url = os.environ["RABBIT_URL"]

# # Create the credentials object
# credentials = pika.PlainCredentials(user, password)


def fwdJobToAnalyzer(body, channel, method):
    # consumer side exception handling

    success = analyzer.readUrlsFromJson(body)
    
def main():

    connection = pika.BlockingConnection(pika.ConnectionParameters(host='mq', heartbeat=600)) # heartbeat is set to 10 minutes
    channel = connection.channel()

    channel.queue_declare(queue='AnalyzerQueue2', durable=True)


    def callback(ch, method, properties, body):
        print(f" [x] Received {body}")

        try: 
            fwdJobToAnalyzer(body, ch, method) # approx 30 minutes for 68 jobs
            print(" [x] Done!!!!! YAY")
            ch.basic_ack(delivery_tag = method.delivery_tag) # default time for waiting for ack is 30 minutes
        except(Exception) as e:
            print(f"Execption was raisedddd>>{e}")

    channel.basic_qos(prefetch_count=1)
    # round robin by default if more wokers are active
    channel.basic_consume(queue='AnalyzerQueue2', on_message_callback=callback) # autoAck by default is False


    print(' [*] Waiting for messages. To exit press CTRL+C')
    channel.start_consuming()

if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        print('Interrupted')
        try:
            sys.exit(0)
        except SystemExit:
            os._exit(0)
