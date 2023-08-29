#!/usr/bin/env python
# reveice job from downloader to cone and alayze the given repos
import pika, sys, os
import analyzer

#TODO: make fail safe

def main():
    connection = pika.BlockingConnection(pika.ConnectionParameters(host='localhost'))
    channel = connection.channel()

    channel.queue_declare(queue='AnalyzerQueue')

    def callback(ch, method, properties, body):
        print(f" [x] Received {body}")
        fwdJobToAnalyzer(body)
    channel.basic_consume(queue='AnalyzerQueue', on_message_callback=callback, auto_ack=True)

    print(' [*] Waiting for messages. To exit press CTRL+C')
    channel.start_consuming()

def fwdJobToAnalyzer(body):
    analyzer.readUrlsFromJson(body)

if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        print('Interrupted')
        try:
            sys.exit(0)
        except SystemExit:
            os._exit(0)