from git import repo
from pip._vendor import requests
from secrets_1 import access_token
import json as js

filename = "my_file.json"


def downloader(repo_url, local_dir):
    # Check if the file has already been cloned
    # Clone repo to local directory
    repo.clone_from(url=repo_url, to_path=local_dir)


def getUrlsToDownload():
    ## download dependency api json from github
    url = "https://api.github.com/search/repositories?q=Q"

    response = requests.get(
        url,
        headers={
            "Accept": "application/vnd.github+json",
            "X-GitHub-Api-Version": "2022-11-28",
            "Authorization": access_token,
        },
    )

    # get ids of the repos that should be downloaded
    repo_urls = {}
    urls = []
    json_array = js.loads(response.text)
    print(json_array)
    index = 0

    for json in json_array["items"]:
        print(json["clone_url"])
        urls.append(json["clone_url"])
        # repo_urls[json['clone_url']] = index
        index = index + 1

    # probably these will be devided into 10 urls per JSON and forwarded as a job
    return urls


# method to create jobs from given restriction with clone urls
# TODO: decide how many clone urls a job should include (e.g. 10 to download and analyze)
def createJobForUrls(urls):
    f = open(filename, "w")
    js.dump(urls, f)
    f.close()


# method to read jobs from the specified json file
def readUrlsFromJson():
    f = open(filename, "r")
    url_list = js.load(f)
    f.close()


createJobForUrls(getUrlsToDownload())
readUrlsFromJson()
