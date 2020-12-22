#!/usr/bin/env python3

# CREDIT: Based on cloudkite-io/Test-Report-Notifier

import os
import glob
import subprocess

from google.cloud import storage

# Constants
GCS_URL = 'https://storage.googleapis.com'

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

# Upload to a html report to a GCS bucket.
def upload_html(html_dir, gcs_bucket, blob_name):
    storage_client = storage.Client()
    bucket = storage_client.bucket(gcs_bucket)

    try:
        upload_dir_to_gcs(html_dir, bucket, blob_name)
    except Exception as e:
        print('Unexpected error:', e)

    return '%s/%s/%s/index.html' %(GCS_URL, bucket.name, blob_name)

def main():
    results_dir = os.environ.get('RESULTS_DIR')
    html_dir = os.environ.get('HTML_DIR') or '/tmp/allure'
    bucket_name = os.environ.get('BUCKET_NAME') or 'apps-e2e-test-results'
    report_name = os.environ.get('REPORT_NAME') or 'allure'

    convert_html(results_dir, html_dir)
    bucket_url = upload_html(html_dir, bucket_name, report_name)

    print('Test report: %s' %(bucket_url))

if __name__ == '__main__':
    main()
