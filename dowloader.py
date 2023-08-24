import pprint
from git import repo
from pip._vendor import requests
from secrets_1 import access_token
import json as js

filename = "my_file"
global_counter = 1
limit_enabled = True
supported_languages = ["csharp", "java", "javascript", "python", "php", "go", "swift", "c", "cpp"] #spelling for repo filter
supported_language_strings = ["C#", "Java", "JavaScript", "Python", "PHP", "Go", "Swift", "C", "C++"] # spelling in language field/property


# TODO: paging
# TODO: get input from user / stop faking input


def downloader(repo_url, local_dir):
    # Check if the file has already been cloned
    # Clone repo to local directory
    repo.clone_from(url=repo_url, to_path=local_dir)


def getUrlsToDownloadForRep(
    created_from, created_till, keyword="", language="", sort_by="", order=""
):
    """_get clone URLs for repositories filtered by a specific language
    or a specific keyword or both_
        Jobs in JSON format with the necessary infromation for analysis are created (clone urls and language)

    Args:
        createdFrom(str): start date to filter repositories by
        createdTill(str): end date to filter repositories by
        keyword (str, optional): keyword to be filtered by in the repository info. Defaults to "".
        language (str, optional): langauge of the code/repository. Defaults to "".
        (options include: "csharp", "java", "javascript", "python", "php", "go", "swift", "c", "cpp")
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
    
    filter_languages = False
    if(language == ""): # if not language selected filter for only supported languages
        filter_languages = True
    # create jobs directly in method so there isn't an unnecessary iteration
    clone_urls, languages = processResponseForRep(resp, filter_languages)
    createJobForUrls(clone_urls, languages)


def getUrlsAndCommitHashToDownloadForCode(keyword, sort_by="", order=""):
    """_get clone urls with the unique hash codes for a specific commit in the repository
    filtering the code of all commits of all repositories by a specific keyword.
    purpose: analyying specific commits based on behavior while coding_
    Jobs in JSON format with the necessary infromation for analysis are created (clone urls and language and commit hashes)

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
    clone_urls_complete, languages = processRepoIds(repo_ids)
    commit_hashes = getCommitShaFromItems(code_response)
    createJobForUrls(clone_urls=clone_urls_complete, languages= languages, hashes= commit_hashes)
    


def getUrlsToDownloadForCode(keyword, label="", total_amount=0, sort_by="", order=""):
    """_get clone urls of repositories
    filtering the code of all commits of all repositories by a specific keyword
    purspose: analyzing most recent commit absed on general behavior while coding
    The repositories to be analyzed can be further filtered when filtering by the amount of existence
    a specific label
    purpose: analyze the workflow of the repository_
    Jobs in JSON format with the necessary infromation for analysis are created (clone urls and language)

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

    clone_urls_limited_and_unique, languages = processRepoIds(repo_ids)
    createJobForUrls(clone_urls= clone_urls_limited_and_unique, languages= languages)


def getUrlsToDownloadForCommits(keyword, sort_by="", order=""):
    """_get clone urls with the unique hash codes for a specific commit in the repository
    filtering all commit messages of all repositories by a specific keyword.
    purpose: analyzing specific commits based on behavior while coding (commiting)_
    Jobs in JSON format with the necessary infromation for analysis are created (clone urls and language and commit hashes)

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
    clone_urls, languages = processRepoIds(repo_ids)
    commit_hashes = getCommitShaFromItems(commit_response)
    createJobForUrls(clone_urls=clone_urls, languages= languages, hashes= commit_hashes)


def getUrlsToDownloadForIssues(keyword, state, created_from, created_till, sort_by="", order=""):
    """_get clone urls of the repositories
    filtering all issues of all repositories by a specific keyword.
    purpose: analyzing behavior while publishing issues and relation to security awareness_
    Jobs in JSON format with the necessary infromation for analysis are created (clone urls and language)

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
    clone_urls, languages = processRepoUrls(repo_urls_unique)
    createJobForUrls(clone_urls=clone_urls, languages= languages)


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


def processResponseForRep(response, filter_languages):
    """_process the response for the repository search and return the clone URLs
      in the response (response will include the amount )_

    Args:
        response(requests.Response) : reponse to an API call
        filter_languages (bool) : True if repositories should be filtered for all supported languages

    Returns:
        List[str]: list of clone URLs
        List[str]: list of corresponding languages
    """

    # get clone_urls of the repos that should be downloaded
    urls = []
    languages = []
    json_array = js.loads(response.text)

    if not filter_languages:

        for json in json_array["items"]:
            urls.append(json["clone_url"])
            languages.append(json["language"])
    else:
        for json in json_array["items"]:
            if(json["language"] in supported_language_strings):
                urls.append(json["clone_url"])
                languages.append(json["language"])

    #create a job with the given reponse directly after finishing, so nodes can start
    # doesn't matter if not the same length, cause nodes will take the next job when they are done
    return urls, languages



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
        List[str]: list of corresponding languages
    """
    urls = []
    languages = []

    for repo in rep_ids:
        response = getResponseForUrl(f"https://api.github.com/repositories/{ repo }")

        json_resp = js.loads(response.text)
        if(json_resp["language"] in supported_language_strings):
            urls.append(json_resp["clone_url"])
            languages.append(json_resp["language"])

    
    return urls, languages


def processRepoUrls(repo_urls):
    """_get clone URLs of the given repositories (repository URLs)_

    Args:
        repo_urls (List[str]): list of repository urls

    Returns:
    List [str]: list of clone urls of all repositories given in the repo_urls parameter
    can contain duplicate elements if the repository ids in the given list are duplicate.
    returns the clone urls in the same order corresponding to the given parameter.
    List[str]: list of corresponding languages

    """

    urls = []
    languages = []

    for repo in repo_urls:
        response = getResponseForUrl(f"{ repo }")  # TODO: check repo url if secure

        json_resp = js.loads(response.text)
        if(json_resp["language"] in supported_language_strings):
            urls.append(json_resp["clone_url"])
            languages.append(json_resp["language"])

    return urls, languages


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
    total_count = json_resp["total_count"]

    return total_count >= total_amount


# method to create jobs from given restriction with clone urls
# TODO: decide how many clone urls a job should include (e.g. 10 to download and analyze)
def createJobForUrls(clone_urls, languages, hashes = []):
    all_data = []
    global global_counter

    if hashes:
        for i in range(len(clone_urls)):
            all_data.append({"clone_urls": clone_urls[i], "language": languages[i], "hash": hashes[i]})

    else:
        for i in range(len(clone_urls)):
            all_data.append({"clone_urls": clone_urls[i], "language": languages[i], "hash": ""})

    with open(filename +  str(global_counter) + ".json", "w") as write_file:
        js.dump(all_data, write_file, indent=4)
        global_counter +=1
    write_file.close()


# TODO: move to analzyer.py
def readUrlsFromJson():

    global global_counter

    with open(filename + str(global_counter -1) + ".json", "r") as read_file:
        data = js.load(read_file)

    clone_urls = []
    languages = []
    hashes = []

    for item in data:
        clone_urls.append(item["clone_urls"])
        languages.append(item["language"])
        print(item["hash"] == "") # clone only most recent commit
        hashes.append(item["hash"])
        read_file.close()

    print(clone_urls)
    print(languages)
    print(hashes)



getUrlsToDownloadForCode("", "", "")
readUrlsFromJson()
getUrlsAndCommitHashToDownloadForCode("")
readUrlsFromJson()
getUrlsToDownloadForCommits("")
readUrlsFromJson()
getUrlsToDownloadForIssues("", "", "", "")
readUrlsFromJson()
getUrlsToDownloadForRep("", "")
readUrlsFromJson()
