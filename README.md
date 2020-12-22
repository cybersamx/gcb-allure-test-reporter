# gcb-allure-test-reporter

Docker image for Google Cloud Build to convert an Allure test report to HTML and upload it to GCB.

## Overview

This project maintains a Python script that performs the following tasks:

1. Given an Allure test results directory, generate an HTML report.
1. Copy the HTML report to a GCS bucket.
1. Post the URL link to the HTML on Slack.

This script is designed to work in Google Cloud Build, GCP's CI/CD solution, as a step to provide better test reporting supplementing the default output from the CI/CD tool.

## Credits

This project is based on [cloudkite-io/Test-Report-Notifier](https://github.com/cloudkite-io/Test-Report-Notifier), a similar work that Cloudkite developed for Junit-Jest reporting.
