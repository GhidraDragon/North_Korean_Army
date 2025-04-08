import argparse
import time
import requests
import sys
import os
import re
from collections import deque
from urllib.parse import urljoin
from pywebcopy import save_website
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.chrome.options import Options

def priority_bfs(start_url, depth=3):
    visited = set()
    queue = deque([(start_url, 0)])
    while queue:
        current_url, lvl = queue.popleft()
        if lvl <= depth and current_url not in visited:
            visited.add(current_url)
            print(f"Traversing: {current_url} (Level {lvl})")
            try:
                r = requests.get(current_url, headers={"User-Agent": "Mozilla/5.0"})
                if r.status_code == 404:
                    r = requests.get(current_url, headers={"User-Agent": "Mozilla/5.0 (X11; Linux x86_64)"})
                    if r.status_code == 404:
                        continue
                if r.status_code == 200:
                    soup = BeautifulSoup(r.text, 'html.parser')
                    for link in soup.find_all('a', href=True):
                        new_url = urljoin(current_url, link['href'])
                        if new_url.startswith('http'):
                            queue.append((new_url, lvl + 1))
            except:
                pass
    return visited

def sanitize_filename(url):
    return re.sub(r'[^A-Za-z0-9_\-]+', '_', url)

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--depth', type=int, default=3)
    args = parser.parse_args()

    url = "https://openai.com/policies/terms"
    screenshot_dir = "screenshots"
    os.makedirs(screenshot_dir, exist_ok=True)

    chrome_options = Options()
    chrome_options.add_argument("--headless")
    chrome_options.add_argument("--no-sandbox")

    driver = webdriver.Chrome(options=chrome_options)

    while True:
        try:
            response = requests.get(url)
            if response.status_code != 404:
                pages = priority_bfs(url, args.depth)
                for p in pages:
                    try:
                        driver.get(p)
                        screenshot_path = os.path.join(screenshot_dir, sanitize_filename(p) + ".png")
                        driver.save_screenshot(screenshot_path)
                        print(f"Screenshot saved: {screenshot_path}")
                        save_website(
                            p,
                            project_folder='./downloaded_site',
                            bypass_robots=True,
                            project_name='terms'
                        )
                        print(f"Downloaded: {p}")
                    except:
                        pass
                driver.quit()
                sys.exit(0)
        except:
            pass
        time.sleep(600)

if __name__ == "__main__":
    main()