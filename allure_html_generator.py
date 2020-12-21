#!/usr/bin/env python3

import os
import subprocess

def convert_html(allure_dir):
    try:
        html_dir = '/tmp/allure'

        if os.path.exists(allure_dir):
            subprocess.run(["allure", "generate", allure_dir, "-c", "-o", html_dir])

        else:
            print('Dir {} does not exist.'.format(allure_dir))
    except Exception as e:
        print('Unexpected error:', e)

def main():
    allure_dir = os.environ.get('ALLURE_DIR')

    convert_html(allure_dir)


if __name__ == '__main__':
    main()
