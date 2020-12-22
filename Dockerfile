FROM python:3.8.6-buster

### --- Set up Python for Allure generation, upload, and notification ---

WORKDIR /usr/local

# Python packages needed to run the scripts
RUN pip3 install requests
RUN pip3 install google-cloud-storage

# copy test_notifier script to docker container
COPY allure_reporter.py ./bin/allure-reporter

# make script executable
RUN chmod a+x ./bin/allure-reporter

### --- Set up OpenJDK for java that is needed by allure ---

RUN apt-get update && \
    apt-get install -y openjdk-11-jre-headless && \
    apt-get clean

### --- Set up Allure ---

ENV ALLURE_VERSION 2.13.8

# Download and install allure.
RUN wget https://repo.maven.apache.org/maven2/io/qameta/allure/allure-commandline/${ALLURE_VERSION}/allure-commandline-${ALLURE_VERSION}.zip
RUN unzip allure-commandline-${ALLURE_VERSION}.zip && \
    ln -s ../allure-${ALLURE_VERSION}/bin/allure bin/allure

ENTRYPOINT ["/usr/local/bin/allure-reporter"]
