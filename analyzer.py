filename = "my_file"
CLONE_OUTPUTPATH = "clone_output/"
DEPENDENCY_CHECK_OUTPUT = 'dependency_check_output/'
import json as js
import subprocess
from git import Repo


def pollForJobs():
    #TODO: implement with RabbitMQ
    pass

def readUrlsFromJson():

    with open(filename + str(1) + ".json", "r") as read_file: # test with first file containing 25 repos
        data = js.load(read_file)

    clone_url = language = hash = ""
    counter = 0

    # for item in data (max 25 items):
    # cloning and analyzing takes approx 3 minutes for 10 items/repositories
    for item in data:
        counter +=1
        clone_url = item["clone_urls"]
        language = item["language"]
        if item["hash"] == "":  # clone only most recent commit
            cloneMostRecent(clone_url, CLONE_OUTPUTPATH + str(counter))
        else:
            hash = item["hash"]
            cloneWithHash(clone_url, hash, CLONE_OUTPUTPATH + str(counter))

        analyze(CLONE_OUTPUTPATH + str(counter), DEPENDENCY_CHECK_OUTPUT + str(counter)) # analyze one an then delete it, better for memory
        createJobForResults(DEPENDENCY_CHECK_OUTPUT + str(counter), language) # better for traffic in RabbitMQ
        deleteOutput(CLONE_OUTPUTPATH + str(counter), DEPENDENCY_CHECK_OUTPUT + str(counter))
    read_file.close()



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
    # TODO: look for command line arguments to only output important and relevant data
    print(filepath, output_path)
    subprocess.run([ 'dependency-check.sh','--scan', str(filepath), '--format',
                     'JSON', '--prettyPrint', '--out', output_path, 
                      '--enableExperimental', '--disableRubygems' ])

def createJobForResults(path_to_results, language): #results already in JSON format
    #TODO: create a RabbitMQ job and add language to the results
    # add language to JSON
    print(f"print job for PATH: {path_to_results} and LANGUAGE: {language}")
    pass

def deleteOutput(clone_output, dependency_check_output):
    #TODO: delte both 
    pass

readUrlsFromJson()