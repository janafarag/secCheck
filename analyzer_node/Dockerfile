    # THIS IS A COMMENT
    FROM python:3.9
    WORKDIR /First_try
    COPY requirements.txt .
    RUN pip install -r requirements.txt

    # Update the APT repository to ensure we get the latest version of apache2
    RUN apt-get update -y 

    # Install apache2
    RUN apt-get install apache2 -y

    # Tell the container to expose port 80 to allow us to connect to the web server
    EXPOSE 80 

    # Tell the container to run the apache2 service
    CMD ["apache2ctl", "-D","FOREGROUND"]

    # update dependency check once before running #TODO: move to Dockerfile !!!
    # subprocess.run([ 'dependency-check.sh', '--updateonly'])

