import pprint
from git import repo
from pip._vendor import requests
from secrets_1 import access_token
import json as js

filename = "my_file.json"
limit_enabled = True


# TODO: collect language infos for all jobs to set language setting in owasp dependency check and filter not-supported languges
# so results are more accurate
# TODO: paging


def downloader(repo_url, local_dir):
    # Check if the file has already been cloned
    # Clone repo to local directory
    repo.clone_from(url=repo_url, to_path=local_dir)


def getUrlsToDownloadForRep(
    created_from, created_till, keyword="", language="", sort_by="", order=""
):  # repository langauge
    """_get clone URLs for repositories filtered by a specific language
    or a specific keyword or both_

    Args:
        createdFrom(str): start date to filter repositories by
        createdTill(str): end date to filter repositories by
        keyword (str, optional): keyword to be filtered by in the repository info. Defaults to "".
        language (str, optional): langauge of the code/repository. Defaults to "".
        (options include: js, python, ruby, java, csharp, php, typescript, swift, go, kotlin)
        sort_by (str, optional): property to be sorted by. Defaults to "".
        (options include: forks, stars)
        order (str, optional): order to be sorted with. Defaults to "".
        (options include: asc and desc)
    """
    keyword = "react"
    language = "js"
    created_from = "2019-01-01"
    created_till = "2020-12-31"
    sort_by = "stars"
    order = "desc"
    url = f"https://api.github.com/search/repositories?q=created:{created_from}..{created_till}+{keyword}+language:{language}&sort={sort_by}&order={order}"
    resp = getResponseForUrl(url)
    clone_urls = processResponseForRep(resp)


def getUrlsAndCommitHashToDownloadForCode(keyword, sort_by="", order=""):
    """_get clone urls with the unique hash codes for a specific commit in the repository
    filtering the code of all commits of all repositories by a specific keyword.
    purpose: analyying specific commits based on behavior while coding_

    Args:
        keyword (str): keyword that should be filtered by in the complete code
        filtering all commits for every repository.
        sort_by (str, optional): property to be sorted by. Defaults to "".
        (options include: forks, stars)
        order (str, optional): order to be sorted with. Defaults to "".
        (options include: asc and desc)
    """
    keyword = "bug"
    url = f"https://api.github.com/search/code?q={keyword}&sort={sort_by}&order={order}"
    code_response = getResponseForUrl(url)
    repo_ids = getRepIdsFromItems(code_response)
    clone_urls_complete = processRepoIds(repo_ids)
    commit_hashes = getCommitShaFromItems(code_response)
    clone_urls_with_commit_hashes = dict(zip(commit_hashes, clone_urls_complete))
    pprint.pprint(clone_urls_with_commit_hashes)


def getUrlsToDownloadForCode(keyword, label="", total_amount=0, sort_by="", order=""):
    """_get clone urls of repositories
    filtering the code of all commits of all repositories by a specific keyword
    purspose: analyzing most recent commit absed on general behavior while coding
    The repositories to be analyzed can be further filtered when filtering by the amount of existence
    a specific label
    purpose: analyze the workflow of the repository_

    Args:
        keyword (_type_): _description_
        label (str, optional): defualt Github label. Defaults to "".
        (options include: bug, documentation, duplicate, enhancement, good first issue, help wanted, invalid, question, wontfix)
        total_amount (int, optional): _description_. Defaults to 0.
        label and total_amount are both mandatory if limit_enabled is true
        ( aka label limit toggle button is on)
        sort_by (str, optional): property to be sorted by. Defaults to "".
        (options include: forks, stars)
        order (str, optional): order to be sorted with. Defaults to "".
        (options include: asc and desc)
    """

    keyword = "bug"
    url = f"https://api.github.com/search/code?q={keyword}&sort={sort_by}&order={order}"
    code_response = getResponseForUrl(url)
    repo_ids = getRepIdsFromItems(code_response)
    sort_by = "stars"
    order = "desc"

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


def getUrlsToDownloadForCommits(keyword, sort_by="", order=""):
    """_get clone urls with the unique hash codes for a specific commit in the repository
    filtering all commit messages of all repositories by a specific keyword.
    purpose: analyzing specific commits based on behavior while coding (commiting)_

    Args:
        keyword (str): keyword that should be filtered by in the complete code
        filtering all commits for every repository.
        sort_by (str, optional): property to be sorted by. Defaults to "".
        (options include: forks, stars)
        order (str, optional): order to be sorted with. Defaults to "".
        (options include: asc and desc)
    """
    keyword = "fix"
    sort_by = "stars"
    order = "desc"

    url = f"https://api.github.com/search/commits?q=message:{keyword}&sort={sort_by}&order={order}"
    commit_response = getResponseForUrl(url)
    repo_ids = getRepIdsFromItems(commit_response)
    clone_urls = processRepoIds(repo_ids)
    commit_hashes = getCommitShaFromItems(commit_response)
    clone_urls_with_commit_hashes = dict(zip(commit_hashes, clone_urls))
    pprint.pprint(clone_urls_with_commit_hashes)


def getUrlsToDownloadForIssues(keyword, state, created_from, created_till, sort_by="", order=""):
    """_get clone urls of the repositories
    filtering all issues of all repositories by a specific keyword.
    purpose: analyzing behavior while publishing issues and relation to security awareness_

    Args:
        state(str): state of the issues to be filtered by (options include: open and closed)
        createdFrom(str): start date to filter issues by
        createdTill(str): end date to filter issues by
        keyword (str): keyword that should be filtered by filtering
        all issues for every repository.
        sort_by (str, optional): property to be sorted by. Defaults to "".
        (options include: forks, stars)
        order (str, optional): order to be sorted with. Defaults to "".
        (options include: asc and desc)
    """

    keyword = "Zero Day"
    state = "closed"
    created_from = "2010-01-01"
    created_till = "2020-12-31"
    sort_by = "stars"
    order = "desc"
    url = f"https://api.github.com/search/issues?q={keyword}+is:issue+state:{state}+created:{created_from}..{created_till}&sort={sort_by}&order={order}"
    issues_response = getResponseForUrl(url)
    repo_urls = getRepoUrlsFromItems(issues_response)
    repo_urls_unique = list(set(repo_urls))
    clone_urls = processRepoUrls(repo_urls_unique)


def limitRepoIdsWithExistingLabels(label, rep_ids, total_amount):
    """_Return limited repository ids. Only return the repository ids that meet
    the defined criteria of having a specific label with a certain amount of times
    purpose: analyzing the workflow behavior_

    Args:
        label (str): Github default label
        rep_ids (List[int]): repository ids that should be filtered further by label criteria
        total_amount (int): amount of times a label has to be present in the repository
        to meet the filtering criteria

    Returns:
        List[int]: filtered list of repository ids
    """
    limited_repos = []
    label = "bug"
    total_amount = 1  # has at least one labeled bug

    for rep_id in rep_ids:
        url = f"https://api.github.com/search/labels?q={label}&repository_id={rep_id}"
        codeResponse = getResponseForUrl(url)
        if responseMeetsCriteria(codeResponse, total_amount):
            limited_repos.append(rep_id)

    return limited_repos


def getResponseForUrl(search_url):
    """_get the API repsonse of the Github API for a specific url_

    Args:
        search_url (str): search url for the Github API

    Returns:
     requests.Response : reponse to the API call
    """

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
    """_process the response for the repository search and return the clone URLs
      in the response_

    Returns:
        List[str]: list of clone URLs
    """

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
    """_return repository ids from the response
    (for code search and commit search response structures)_

    Args:
        response(requests.Response) : reponse to an API call

    Returns:
        List[int]: list of repository ids (can be duplicate in list)
    """
    rep_ids = []
    json_array = js.loads(response.text)

    for json in json_array["items"]:
        print(json["repository"]["id"])
        rep_ids.append(json["repository"]["id"])

    return rep_ids


def getCommitShaFromItems(response):
    """_return commit hashes (sha) from the response
    (for code search and commit search response structures)_

    Args:
        response(requests.Response) : reponse to an API call

    Returns:
        (List[str]): commit hashes (sha field)
    """
    commit_hashes = []
    json_array = js.loads(response.text)

    for json in json_array["items"]:
        print(json["sha"])
        commit_hashes.append(json["sha"])

    return commit_hashes


def getRepoUrlsFromItems(response):
    """_return repository urls from the response
    (for issues search response structures)_

    Args:
        response(requests.Response) : reponse to an API call

    Returns:
        (List[str]): list of repository URLs included in the reponse  (can be duplicate in list)
    """
    repo_urls = []
    json_array = js.loads(response.text)

    for json in json_array["items"]:
        print(json["repository_url"])
        repo_urls.append(json["repository_url"])

    return repo_urls


def processRepoIds(rep_ids):
    """get clone URLs of the given repositories (repository ids)

    Args:
        rep_ids (List[int]): list of repository ids

    Returns:
        List [str]: list of clone urls of all repositories given in the rep_ids parameter
        can contain duplicate elements if the repository ids in the given list are duplicate.
        returns the clone urls in the same order corresponding to the given parameter.
    """
    urls = []

    for repo in rep_ids:
        response = getResponseForUrl(f"https://api.github.com/repositories/{ repo }")

        json_resp = js.loads(response.text)
        print(json_resp["clone_url"])
        urls.append(json_resp["clone_url"])

    # probably these will be devided into 10 urls per JSON and forwarded as a job
    return urls


def processRepoUrls(repo_urls):
    """_get clone URLs of the given repositories (repository URLs)_

    Args:
        repo_urls (List[str]): list of repository urls

    Returns:
    List [str]: list of clone urls of all repositories given in the repo_urls parameter
    can contain duplicate elements if the repository ids in the given list are duplicate.
    returns the clone urls in the same order corresponding to the given parameter.

    """

    urls = []

    for repo in repo_urls:
        response = getResponseForUrl(f"{ repo }")  # TODO: check repo url if secure

        json_resp = js.loads(response.text)
        print(json_resp["clone_url"])
        urls.append(json_resp["clone_url"])

    # probably these will be devided into 10 urls per JSON and forwarded as a job
    return urls


def responseMeetsCriteria(response, total_amount):
    """_Return True if the given reponse meets the total amount criteria specified by the
    total_amount parameter_

    Args:
        response (requests.Response): reponse to an API call
        total_amount (int): threshhold for the total count in the respone

    Returns:
        True: if the total count in the response is equal to or higher than the specified threshhold
          by the parameter total_amount
    """
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
# getUrlsToDownloadForCommits("")
# getUrlsToDownloadForIssues("", "", "", "")
# getUrlsToDownloadForRep("", "")
