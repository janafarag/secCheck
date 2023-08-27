filename = "my_file"
OUTPUTPATH = "output_file"
# OUTPUTPATH = "output_w_hash_file"
DEPENDENCY_CHECK_OUTPUT = 'dependency_output/'
import json as js
import subprocess
from git import Repo

def readUrlsFromJson():
    global global_counter

    with open(filename + str(1) + ".json", "r") as read_file: # test with first file
        data = js.load(read_file)

    clone_url = language = hash = clone_command = ""
    counter = 0

    #execute once:
    # Create a directory
    # subprocess.run(['mkdir', 'dependency_output'])

    # for item in data:
    for index in range(0,6):
        counter +=1
        # clone_url = item["clone_urls"]
        # language = item["language"]
        # if item["hash"] == "":  # clone only most recent commit
        #     cloneMostRecent(clone_url, OUTPUTPATH + str(counter))
        # else:
        #     hash = item["hash"]
        #     cloneWithHash(clone_url, hash, OUTPUTPATH + str(counter))

        results = analyze(OUTPUTPATH + str(counter), DEPENDENCY_CHECK_OUTPUT + str(counter)) # analyze one an then delete it, better for memory
        createJobForResults(results, language) # better for traffic in RabbitMQ
        deleteOutput(OUTPUTPATH + str(counter))
    read_file.close()


def cloneAndAnalayze(clone_command, language, filepath):
    pass

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
    #shell faster than bash, CLI faster than maven or gradle cause subprocess
    # creates a process inside parent without invoking a new shell
    print(filepath, output_path)
    subprocess.run([ 'dependency-check.sh','--scan', str(filepath), '--format',
                     'JSON', '--prettyPrint', '--out', output_path ])

def createJobForResults(results, language):
    pass

def deleteOutput(output_path):
    pass

readUrlsFromJson()