filename = "my_file"
CLONE_OUTPUTPATH = "clone_output"
DEPENDENCY_CHECK_OUTPUT = 'dependency_check_output'
import json as js
import subprocess
from git import Repo
import rmq_sender
import os, shutil



def readUrlsFromJson(json_body):

    # create directory
    os.mkdir(DEPENDENCY_CHECK_OUTPUT)

    body = js.loads(json_body)
    clone_url = language = hash = ""
    counter = 0

    # for item in data (max 25 items):
    # cloning and analyzing takes approx 3 minutes for 10 items/repositories
    for item in body:
        print(f"{item}")
        clone_url = item["clone_url"]
        language = item["language"]
        if item["hash"] == "":  # clone only most recent commit
            cloneMostRecent(clone_url, CLONE_OUTPUTPATH)
        else:
            hash = item["hash"]
            cloneWithHash(clone_url, hash, CLONE_OUTPUTPATH)

        analyze(CLONE_OUTPUTPATH , DEPENDENCY_CHECK_OUTPUT) # analyze one an then delete it, better for memory
        createJobForResults(DEPENDENCY_CHECK_OUTPUT + "/dependency-check-report.json", language) # better for traffic in RabbitMQ
        # delete output every time
        deleteOutput(CLONE_OUTPUTPATH, DEPENDENCY_CHECK_OUTPUT + "/dependency-check-report.json")

    #delete directory when finished
    shutil.rmtree(DEPENDENCY_CHECK_OUTPUT)



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
                      '--enableExperimental', '--disableRubygems' ])

def createJobForResults(path_to_results, language): #results already in JSON format
    #TODO: create a RabbitMQ job and add language to the results
    # add language to JSON
    print(f"print job for PATH: {path_to_results} and LANGUAGE: {language}")
    # Open the JSON file and read its contents
    with open(path_to_results, 'r') as f:
        json_data = f.read()

    json_array = js.loads(json_data)
    json_array['language'] = language
    json_data = js.dumps(json_array)

    # Load the JSON data into a Python dictionary
    print(json_data)
    rmq_sender.send_results(json_data)
    f.close()

def deleteOutput(clone_output, dependency_check_output):
    shutil.rmtree(clone_output)
    os.remove(dependency_check_output)

