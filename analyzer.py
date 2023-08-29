filename = "my_file"
CLONE_OUTPUTPATH = "clone_output/"
DEPENDENCY_CHECK_OUTPUT = 'dependency_check_output/'
import json as js
import subprocess
from git import Repo
import rmq_sender



def readUrlsFromJson(json_body):

    body = js.loads(json_body)
    clone_url = language = hash = ""
    counter = 0

    # for item in data (max 25 items):
    # cloning and analyzing takes approx 3 minutes for 10 items/repositories
    for item in body:
        print(f"{item}")
        counter +=1
        clone_url = item["clone_url"]
        language = item["language"]
        if item["hash"] == "":  # clone only most recent commit
            cloneMostRecent(clone_url, CLONE_OUTPUTPATH + str(counter))
        else:
            hash = item["hash"]
            cloneWithHash(clone_url, hash, CLONE_OUTPUTPATH + str(counter))

        analyze(CLONE_OUTPUTPATH + str(counter), DEPENDENCY_CHECK_OUTPUT + str(counter)) # analyze one an then delete it, better for memory
        createJobForResults(DEPENDENCY_CHECK_OUTPUT + str(counter), language) # better for traffic in RabbitMQ
        deleteOutput(CLONE_OUTPUTPATH + str(counter), DEPENDENCY_CHECK_OUTPUT + str(counter))



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
    with open(path_to_results + "/dependency-check-report.json", 'r') as f:
        json_data = f.read()

    json_array = js.loads(json_data)
    json_array['language'] = language
    json_data = js.dumps(json_array)

    # Load the JSON data into a Python dictionary
    print(json_data)
    rmq_sender.send_results(json_data)
    f.close()

def deleteOutput(clone_output, dependency_check_output):
    #TODO: delte both 
    pass
