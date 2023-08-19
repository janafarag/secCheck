import pprint
from git import repo
from pip._vendor import requests
from secrets_1 import access_token
import json as js

filename = "my_file.json"
limit_enabled = True


def downloader(repo_url, local_dir):
    # Check if the file has already been cloned
    # Clone repo to local directory
    repo.clone_from(url=repo_url, to_path=local_dir)


def getUrlsToDownloadForRep(keyword, language):  # repository language
    keyword = "react"
    language = "js"  # options include: js, python, ruby, java, csharp, php, typescript, swift, go, kotlin
    url = f"https://api.github.com/search/repositories?q={keyword}&language:{language}"
    resp = getResponseForUrl(url)
    clone_urls = processResponseForRep(resp)


def getUrlsAndCommitHashToDownloadForCode(keyword):
    keyword = "bug"
    url = f"https://api.github.com/search/code?q={keyword}"
    code_response = getResponseForUrl(url)
    repo_ids = getRepIdsFromItems(code_response)
    clone_urls_complete = processRepoIds(repo_ids)
    commit_hashes = getCommitShaFromItems(code_response)
    clone_urls_with_commit_hashes = dict(zip(commit_hashes, clone_urls_complete))
    pprint.pprint(clone_urls_with_commit_hashes)


def getUrlsToDownloadForCode(
    keyword, label, total_amount
):  # exception handling if topic does not exist
    keyword = "bug"
    url = f"https://api.github.com/search/code?q={keyword}"
    code_response = getResponseForUrl(url)
    repo_ids = getRepIdsFromItems(code_response)

    # no duplicate ids for efficiency write in Methodik
    rep_ids_unique = list(set(repo_ids))

    if (
        limit_enabled
    ):  # maybe a toggle button with a drop down menu with possible lables
        limited_repos = limitRepoIdsWithExistingLabels(
            label, rep_ids_unique, total_amount
        )
        repo_ids = limited_repos

    clone_urls_limited_and_unique = processRepoIds(repo_ids)

    # save a list of repository ids as a product and get for each one the clone url and put into a list
    # ability to minimize the search for label: e.g. bug and and e.g. only getting clone urls for repos with bugs
    # or repos with existing documentation, and maybe even a specific aamount


def getUrlsToDownloadForCommits(keyword):
    keyword = "fix"

    url = f"https://api.github.com/search/commits?q=message:{keyword}"
    commit_response = getResponseForUrl(url)
    repo_ids = getRepIdsFromItems(commit_response)
    clone_urls = processRepoIds(repo_ids)
    commit_hashes = getCommitShaFromItems(commit_response)
    clone_urls_with_commit_hashes = dict(zip(commit_hashes, clone_urls))
    pprint.pprint(clone_urls_with_commit_hashes)


def limitRepoIdsWithExistingLabels(
    label, rep_ids, total_amount
):  # label: bug is interesting but repository id required
    limited_repos = []
    label = "bug"
    total_amount = 1  # has at least one labeled bug

    for rep_id in rep_ids:
        url = f"https://api.github.com/search/labels?q={label}&repository_id={rep_id}"
        codeResponse = getResponseForUrl(url)
        if responseMeetsCriteria(codeResponse, total_amount):
            limited_repos.append(rep_id)

    return limited_repos


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


def getRepIdsFromItems(response):
    ## download dependency api json from github

    # get ids of the repos that should be downloaded
    rep_ids = []
    json_array = js.loads(response.text)

    for json in json_array["items"]:
        print(json["repository"]["id"])
        rep_ids.append(json["repository"]["id"])

    return rep_ids


def getCommitShaFromItems(response):
    # get commit ids and build clone url with specific commit of the repos that should be downloaded
    # then analyse the commit and see if vuln how long ago published or known
    # -> maybe detect vulnerable repositories with lack of awareness for security

    # get commit hashes of the version that should be downloaded
    commit_hashes = []
    json_array = js.loads(response.text)

    for json in json_array["items"]:
        print(json["sha"])
        commit_hashes.append(json["sha"])

    return commit_hashes


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


def responseMeetsCriteria(response, total_amount):
    json_resp = js.loads(response.text)
    print(json_resp["total_count"])
    total_count = json_resp["total_count"]

    return total_count >= total_amount


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
# getUrlsToDownloadForCode("", "", "")
# getUrlsAndCommitHashToDownloadForCode("")
getUrlsToDownloadForCommits("")
