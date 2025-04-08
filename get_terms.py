import time
import requests
import sys
from pywebcopy import save_website

url = "https://openai.com/policies/terms"

while True:
    try:
        response = requests.get(url)
        if response.status_code != 404:
            kwargs = {'bypass_robots': True, 'project_name': 'terms'}
            save_website(url, project_folder='./downloaded_site', **kwargs)
            sys.exit(0)
    except Exception as e:
        print(f"Error: {e}")
    time.sleep(600)