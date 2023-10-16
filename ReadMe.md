@ -1,41 +0,0 @@
# secCheck (downloader_node and analyzer_node) usage

1. `docker compose build`
2. `docker docker compose up`

## API Endpoint examples for downloader.py

The file job_for_urls.json contains a list of examples (one for each API endpoint) of how the "data" variable from the frontend could be filled in the expected format
It is an example list of different job data for every API endpoint in the correct format for further processing 

# secCheck prerequsistes without Docker Compose (not needed anymore)

Feature branch to dowload projects from Github.
Exemplary this will be done to a subset of repositories

Steps to get it to work:

1. pip install gitpython

2. create a file named secrets_1.py with a Github acces Token for authentication with the following format:

`access_token = 'Bearer <PERSONAL_ACCESS_TOKEN_HERE>'`

3. install dependency check CLI with link in Github pages, link: 

https://jeremylong.github.io/DependencyCheck/dependency-check-cli/index.html

4. import GPG key to verify signature

`gpg --keyserver hkp://keyserver.ubuntu.com:80 --recv-keys 259A55407DD6C00299E6607EFFDE55BE73A2D1ED`

5. verify the signature 

`gpg --verify dependency-check-8.4.0-release.zip.asc`

6. Extract the zip file "dependency-check-8.4.0-release.zip" to a location on your computer and put the ‘bin’ directory into the path environment variable. e.g.: adding the PATH to .bashrc
(replace /path/to/dependency-check/bin with location to the bin folder of the extracted dependency check zip file)

`export PATH=$PATH:/path/to/dependency-check/bin`

7. Install and run RabbitMQ on localhost:

`docker run -d --hostname rmq --name rabbit-server -p 8080:15672 -p 5672:5672 rabbitmq:3-management`

7. install Pika for RabbitMQ

`python3 -m pip install pika --upgrade`

To activate virtual env:

`source .venv/bin/activate`

