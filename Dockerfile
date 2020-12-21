# Use OpenJDK as the base image for Java needed to run Allure.
FROM openjdk:8-jre-alpine

### --- Set up Python for Allure generation, upload, and notification ---

# Install Python3 to generate the html reports from Allure test results.
RUN apk add --no-cache \
    python3 \
    py3-pip

WORKDIR /usr/local

# Python packages needed to run the scripts
RUN pip3 install requests
#RUN pip3 install google-cloud-storage

# copy test_notifier script to docker container
COPY ./allure_html_generator.py ./bin/allure-html-generator

# make script executable
RUN chmod a+x ./bin/allure-html-generator

### --- Set up Allure ---

ENV ALLURE_VERSION 2.13.8

# Download and install allure.
RUN wget https://repo.maven.apache.org/maven2/io/qameta/allure/allure-commandline/${ALLURE_VERSION}/allure-commandline-${ALLURE_VERSION}.zip
RUN unzip allure-commandline-${ALLURE_VERSION}.zip && \
    ln -s ../allure-${ALLURE_VERSION}/bin/allure bin/allure

ENTRYPOINT ["/bin/sh"]
