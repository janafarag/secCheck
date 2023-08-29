#!/usr/bin/env python
# receive job from frontend to dowload gut clone urls according to given params
import pika, sys, os
import json as js
import dowloader
import rmq_sender

def main():
    rmq_sender.test()
    credentials = pika.PlainCredentials("guest", "guest")
    connection = pika.BlockingConnection(
        pika.ConnectionParameters(
            host="192.168.221.247", port=5672, virtual_host="/", credentials=credentials #umgebungvariablen
        )
    )
    channel = connection.channel()

    channel.queue_declare(queue="JobQueue")

    def callback(ch, method, properties, body):
        print(f" [x] Received {body}")
        fwdJobToDownloader(body)

    channel.basic_consume(queue="JobQueue", on_message_callback=callback, auto_ack=True)

    print(" [*] Waiting for messages. To exit press CTRL+C")
    channel.start_consuming()

# consume jobs with downloader to get info from API according to filters from UI
def fwdJobToDownloader(body):
    json_array = js.loads(body)
    api = json_array["data"] ["api"]

    if api == "repo":
        print('repo')
        dowloader.getUrlsToDownloadForRep(
            created_from=json_array["data"]["created_from"],
            created_till=json_array["data"]["created_till"],
            keyword=json_array["data"]["keyword"],
            language=json_array["data"]["language"],
            sort_by=json_array["data"]["sort_by"],
            order=json_array["data"]["order"]
        )
    if api == "code_general":
        dowloader.getUrlsToDownloadForCode(
            keyword=json_array["data"]["keyword"],
            label=json_array["data"]["label"],
            total_amount=json_array["data"]["total_amount"],
            sort_by=json_array["data"]["sort_by"],
            order=json_array["data"]["order"]
        )
    if api == "commits":
        dowloader.getUrlsToDownloadForCommits(
            keyword=json_array["data"]["keyword"],
            sort_by=json_array["data"]["sort_by"],
            order=json_array["data"]["order"]
        )
    if api == "issues":
        dowloader.getUrlsToDownloadForIssues(
            keyword=json_array["data"]["keyword"],
            state= json_array["data"]["state"],
            created_from=json_array["data"]["created_from"],
            created_till=json_array["data"]["created_till"],
            sort_by=json_array["data"]["sort_by"],
            order=json_array["data"]["order"]
        )


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("Interrupted")
        try:
            sys.exit(0)
        except SystemExit:
            os._exit(0)
