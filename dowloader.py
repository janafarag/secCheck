from git import repo
from pip._vendor import requests
from secrets_1 import access_token
import json as js

filename = "my_file.json"


def downloader(repo_url, local_dir):
    # Check if the file has already been cloned
    # Clone repo to local directory
    repo.clone_from(url=repo_url, to_path=local_dir)

def getUrlsToDownloadForRep(keyword, language): # reposittory language
    keyword = "react"
    language = "js" #options include: js, python, ruby, java, csharp, php, typescript, swift, go, kotlin
    url = f"https://api.github.com/search/repositories?q={keyword}&language:{language}"
    resp = getResponseForUrl(url)
    processResponseForRep(resp)
    

def getUrlsToDownloadForCode(keyword): # exception handling if topic does not exist
    keyword = "bug"
    url = f"https://api.github.com/search/code?q={keyword}"
    codeResponse = getResponseForUrl(url)
    repo_ids = processResponseForCode(codeResponse)
    processRepoIds(repo_ids)


    # save a list of repository ids as a product and get for each one the clone url and put into a list
    # ability to minimize the search for label: e.g. bug and and e.g. only getting clone urls for repos with bugs
    # or repos with existing documentation, and maybe even a specific aamount


def getUrlsToDownloadForCommits(keyword, commitLang):
    keyword = "react"
    commitLang = "js"
    url = f"https://api.github.com/search/repositories?q={keyword}&language:{commitLang}"
    codeResponse = getResponseForUrl(url)
   

def getUrlsToDownloadForLabels(label, rep_id): #label: bug is interesting but repository id required
    pass
# can be used in combination with code search to limit the search for repos with existing 
# documentation labels or bug labels or a sspecific amount of them to filter the unique repo ids further and 
# make more assumptions about coding style maybe



def getResponseForUrl(search_url):
        
        response = requests.get(
        search_url,
        headers={
            "Accept": "application/vnd.github+json",
            "X-GitHub-Api-Version": "2022-11-28",
            "Authorization": access_token,
        },
        )
        return response


def processResponseForRep(response):
    ## download dependency api json from github

    # get clone_urls of the repos that should be downloaded
    urls = []
    json_array = js.loads(response.text)

    index = 0

    for json in json_array["items"]:
        print(json["clone_url"])
        urls.append(json["clone_url"])
        index = index + 1

    # probably these will be devided into 10 urls per JSON and forwarded as a job
    return urls

def processResponseForCode(response):
    ## download dependency api json from github

    # get ids of the repos that should be downloaded
    rep_ids = []
    json_array = js.loads(response.text)

    for json in json_array["items"]:
        print(json["repository"] ["id"])
        rep_ids.append(json["repository"] ["id"]) # no duplicate ids for efficiency write in Methodik

    rep_ids_unique = list(set(rep_ids))

    return rep_ids_unique

def processResponseForCommits(response):

    # get commit ids and build clone url with specific commit of the repos that should be downloaded
    # then analyse the commit and see if vuln how long ago published or known 
    # -> maybe detect vulnerable repositories with lack of awareness for security
    pass

def processRepoIds(rep_ids):

    # get clone_urls of the repos that should be downloaded
    urls = []

    for repo in rep_ids:
        response = getResponseForUrl(f"https://api.github.com/repositories/{ repo }")
        
        json_resp = js.loads(response.text)
        print(json_resp["clone_url"])
        urls.append(json_resp["clone_url"])
        
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


# createJobForUrls(getUrlsToDownload())
# readUrlsFromJson()
getUrlsToDownloadForCode("")
