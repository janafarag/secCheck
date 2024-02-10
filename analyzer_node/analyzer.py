from git import Repo
import json as js
import subprocess
import os
import os, shutil
import rmq_sender

CLONE_OUTPUTPATH = "analyzer_node/clone_output"
DEPENDENCY_CHECK_OUTPUT = 'analyzer_node/dependency_check_output'




def readUrlsFromJson(json_body):

    # create directory
    if not os.path.exists('analyzer_node'): # directory doesn't exist in docker
        os.mkdir('analyzer_node')
    os.mkdir(DEPENDENCY_CHECK_OUTPUT)

    body = js.loads(json_body)
    clone_url = language = hash = ""
    counter = 0
    success = False

    # for item in data (one item at a time):
    # cloning and analyzing takes approx 3 minutes for 10 items/repositories
    clone_url = body["clone_url"]
    language = body["language"]
    if body["hash"] == "":  # clone only most recent commit
        cloneMostRecent(clone_url, CLONE_OUTPUTPATH)
    else:
        hash = body["hash"]
        cloneWithHash(clone_url, hash, CLONE_OUTPUTPATH)

    analyze(CLONE_OUTPUTPATH , DEPENDENCY_CHECK_OUTPUT) # analyze one an then delete it, better for memory
    createJobForResults(DEPENDENCY_CHECK_OUTPUT + "/dependency-check-report.json", language, clone_url) # better for traffic in RabbitMQ
    # delete output every time
    deleteOutput(CLONE_OUTPUTPATH, DEPENDENCY_CHECK_OUTPUT + "/dependency-check-report.json")

    #delete directory when finished
    shutil.rmtree(DEPENDENCY_CHECK_OUTPUT)
    success = True

    return success



def cloneWithHash(clone_url, commit_hash, output_path ):
    # Clone the repository
    repo = Repo.init(output_path)
    origin = repo.create_remote('origin', clone_url)
    origin.fetch()

    # Checkout the specific commit
    commit = repo.commit(commit_hash)
    repo.git.checkout(commit)

def cloneMostRecent(clone_url, output_path ):
    # Clone the repository
    repo = Repo.clone_from(clone_url, output_path, depth=1)

    # Checkout the HEAD commit
    repo.git.checkout('HEAD')

def analyze(filepath, output_path):
    print(filepath, output_path)
    subprocess.run([ 'dependency-check.sh','--scan', str(filepath), '--format',
                     'JSON', '--prettyPrint', '--out', output_path, 
                      '--enableExperimental', '--disableRubygems' , '--disableBundleAudit', '--noupdate'])

def createJobForResults(path_to_results, language, clone_url): #results already in JSON format
    # add language to JSON
    print(f"print job for PATH: {path_to_results} and LANGUAGE: {language}")
    # Open the JSON file and read its contents
    with open(path_to_results, 'r') as f:
        json_data = f.read()

    json_array = js.loads(json_data)
    json_array['language'] = language
    git_link = clone_url.replace(".git","")
    json_array['git_link'] = git_link
    json_data = js.dumps(json_array)

    # rmq_sender.send_results(json_data) # TODO: uncomment
    rmq_sender.send_test_after_analyzer(json_data)
    f.close()

def deleteOutput(clone_output, dependency_check_output):
    shutil.rmtree(clone_output)
    os.remove(dependency_check_output)

