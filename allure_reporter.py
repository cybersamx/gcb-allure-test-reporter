#!/usr/bin/env python3

# CREDIT: Based on cloudkite-io/Test-Report-Notifier

import os
import glob
import json
import requests
import subprocess

from google.cloud import storage

# Constants
GCS_URL = 'https://storage.googleapis.com'
GCB_URL = 'https://console.cloud.google.com'

# Copy a local directory to GCS. Google Cloud SDK only supports single file upload so we recursively
# upload all files in a local directory.
def upload_dir_to_gcs(local_dir, bucket, blob_name):
    if os.path.isdir(local_dir):
        for local_file in glob.glob(local_dir + '/**'):
            if os.path.isfile(local_file):
                remote_path = os.path.join(blob_name, local_file[1 + len(local_dir):])
                blob = bucket.blob(remote_path)
                blob.upload_from_filename(local_file)

                print('File {} uploaded to {}.'.format(local_file, blob_name))
            else:
                upload_dir_to_gcs(local_file, bucket, blob_name + '/' + os.path.basename(local_file))


# Convert an allure test report from allure test results directory.
def convert_html(results_dir, html_dir):
    try:
        if os.path.exists(results_dir):
            subprocess.run(["allure", "generate", results_dir, "-c", "-o", html_dir])
        else:
            print('Dir {} does not exist.'.format(results_dir))
    except Exception as e:
        print('Unexpected error:', e)
        exit(1)


# Upload to a html report to a GCS bucket.
def upload_html(html_dir, gcs_bucket, blob_name):
    storage_client = storage.Client()
    bucket = storage_client.bucket(gcs_bucket)

    try:
        upload_dir_to_gcs(html_dir, bucket, blob_name)
    except Exception as e:
        print('Unexpected error:', e)
        exit(1)

    return '%s/%s/%s/index.html' % (GCS_URL, bucket.name, blob_name)


# Post the link and result to Slack.
def post_to_slack(slack_channel, slack_text, build_id, project_id, slack_webhook_url, repo_name, branch_name, commit):
    slack_user_name = 'ReportBot'
    cloudbuild_url = '%s/cloud-build/builds/%s?project=%s' % (GCB_URL, build_id, project_id)

    # Dump
    print('slack_channel:', slack_channel)
    print('slack_text:', slack_text)
    print('build_id:', build_id)
    print('project_id:', project_id)
    print('slack_webhook_url:', slack_webhook_url)
    print('repo_name:', repo_name)
    print('branch_name:', branch_name)
    print('commit:', commit)

    slack_data = {
        'channel': slack_channel,
        'text': '%s test suite has completed' % repo_name,
        'username': slack_user_name,
        'blocks': [
            {
                'type': 'section',
                'text': {
                    'type': 'mrkdwn',
                    'text': ':tada: %s test suite has completed.' % repo_name
                }
            },
            {
                'type': 'section',
                'fields': [
                    {
                        'type': 'mrkdwn',
                        'text': '*Repo Name:*\n %s' % repo_name
                    },
                    {
                        'type': 'mrkdwn',
                        'text': '*Branch Name:*\n %s \n' % branch_name
                    }
                ]
            },
            {
                'type': 'section',
                'text': {
                    'type': 'mrkdwn',
                    'text': '*Commit:*\n %s' % commit
                }
            },
            {
                'type': 'actions',
                'block_id': 'view_test_result',
                'elements': [
                    {
                        'type': 'button',
                        'text': {
                            'type': 'plain_text',
                            'text': 'View Test Result'
                        },
                        'style': 'primary',
                        'url': slack_text
                    },
                    {
                        'type': 'button',
                        'text': {
                            'type': 'plain_text',
                            'text': 'View Cloudbuild Run'
                        },
                        'url': cloudbuild_url
                    }
                ]
            }
        ]
    }

    print('slack_data', slack_data)

    response = requests.post(slack_webhook_url,
                             data=json.dumps(slack_data),
                             headers={'Content-Type': 'application/json'})

    if response.status_code != 200:
        raise ValueError(
            'Request to slack returned an error %s, the response is:\n%s' % (response.status_code, response.text)
        )


def main():
    results_dir = os.environ.get('RESULTS_DIR')
    html_dir = os.environ.get('HTML_DIR') or '/tmp/allure'
    bucket_name = os.environ.get('BUCKET_NAME') or 'apps-e2e-test-results'
    report_name = os.environ.get('REPORT_NAME') or 'allure-report'
    slack_channel = os.environ.get('SLACK_CHANNEL')
    slack_webhook_url = os.environ.get('SLACK_WEBHOOK_URL')
    build_id = os.environ.get('BUILD_ID')
    project_id = os.environ.get('PROJECT_ID')
    repo_name = os.environ.get('REPO_NAME')
    branch_name = os.environ.get('BRANCH_NAME')
    commit = os.environ.get('COMMIT_SHA')

    convert_html(results_dir, html_dir)
    bucket_url = upload_html(html_dir, bucket_name, report_name)
    post_to_slack(slack_channel, bucket_url, build_id, project_id, slack_webhook_url, repo_name, branch_name, commit)

    print('Test report: %s' % bucket_url)


if __name__ == '__main__':
    main()
