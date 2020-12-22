# gcb-allure-test-reporter

Docker image for Google Cloud Build to convert a set of Allure test result to an HTML report, upload it to GCB, and notify the event, including a link to the report, on a Slack channel.

## Overview

This project maintains a Python script that performs the following tasks:

1. Given an Allure test results directory, generate an HTML report.
1. Copy the HTML report to a GCS bucket.
1. Post the URL link to the HTML on Slack.

This script is designed to work in Google Cloud Build as a step to provide better test reporting, supplementing the default output from the CI/CD tool.

## Setup

1. Build a Docker image.

   ```bash
   # Since this is used in GCP, put it in GCR for best performance.
   $ docker build -t gcr.io/my-project/allure-reporter
   $ docker push gcr.io/my-project/allure-reporter
   ```

1. Include the docker image in a GCB pipeline.

   ```yaml
     - id: 'Upload test results and post to Slack'
       name: 'gcr.io/my-project/allure-reporter'
       env:
         - 'RESULTS_DIR=${_RESULTS_PATH}'
         - 'HTML_DIR=${_HTML_PATH}'
         - 'BUCKET_NAME=${_GCS_BUCKET}'
         - 'REPORT_NAME=${BUILD_ID}'
         - 'GCS_BUCKET=${_GCS_BUCKET}'
         - 'SLACK_CHANNEL=${_SLACK_CHANNEL}'
         - 'SLACK_WEBHOOK_URL=${_SLACK_WEBHOOK_URL}'
         - 'PROJECT_ID=${PROJECT_ID}'
         - 'BUILD_ID=${BUILD_ID}'
         - 'REPO_NAME=${REPO_NAME}'
         - 'BRANCH_NAME=${BRANCH_NAME}'
         - 'COMMIT_SHA=${COMMIT_SHA}'
   ```

## Credits

This project is based on [cloudkite-io/Test-Report-Notifier](https://github.com/cloudkite-io/Test-Report-Notifier), a similar work that Cloudkite developed for Junit-Jest reporting.
