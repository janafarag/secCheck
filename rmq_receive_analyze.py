#!/usr/bin/env python
# reveice job from downloader to cone and alayze the given repos
import pika, sys, os
import analyzer

#TODO: make fail safe

def main():
    connection = pika.BlockingConnection(pika.ConnectionParameters(host='localhost'))
    channel = connection.channel()

    channel.queue_declare(queue='AnalyzerQueue')

    # sever side exception handling
    channel.confirm_delivery() # confirm delivery to acocunt for network failures'
    def on_return(ch, method, properties, body):
        print(f" [x]  Message returned: {body}")
    def on_cancel(ch, method, properties, body):
        print(f" [x] Message cancelled: {body}")
    # register handlers for confirmations
    channel.add_on_return_callback(on_return) # server returns unroutable message
    channel.add_on_cancel_callback(on_cancel) # server cancels a consumer

    def callback(ch, method, properties, body):
        print(f" [x] Received {body}")
        fwdJobToAnalyzer(body, channel, method)

    channel.basic_consume(queue='AnalyzerQueue', on_message_callback=callback, auto_ack=False)

    print(' [*] Waiting for messages. To exit press CTRL+C')
    channel.start_consuming()

def fwdJobToAnalyzer(body, channel, method):
    # consumer side exception handling
    try:
        success = analyzer.readUrlsFromJson(body)

        if(success):
            channel.basic_ack(delivery_tag=method.delivery_tag)
        else:
            channel.basic_reject(delivery_tag=method.delivery_tag,requeue= True)
    
    except(Exception) as e :
        print(e)
        channel.basic_reject(delivery_tag=method.delivery_tag, requeue= True)

if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        print('Interrupted')
        try:
            sys.exit(0)
        except SystemExit:
            os._exit(0)