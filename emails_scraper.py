import requests
from bs4 import BeautifulSoup
import pandas as pd
import re
from urllib.parse import urljoin, urlparse
from collections import deque
import csv
import logging
import time

# Configure logging
logging.basicConfig(level=logging.DEBUG, filename='scraper.log', filemode='a', format='%(asctime)s - %(levelname)s - %(message)s')

def extract_emails_from_text(text):
    email_pattern = re.compile(r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,7}\b')
    return email_pattern.findall(text)

def is_valid_url(url):
    parsed = urlparse(url)
    return bool(parsed.netloc) and bool(parsed.scheme)

def scrape_emails_from_url(url, max_depth=2):
    emails = set()
    urls_to_scrape = deque([(url, 0)])  # url with depth
    scraped_urls = set()

    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
    }

    while urls_to_scrape:
        current_url, depth = urls_to_scrape.popleft()
        logging.debug(f"Processing URL: {current_url} at depth {depth}")
        if current_url in scraped_urls or depth > max_depth:
            continue
        scraped_urls.add(current_url)

        try:
            response = requests.get(current_url, headers=headers, timeout=10)
            if response.status_code == 200:
                soup = BeautifulSoup(response.content, 'html.parser')
                emails.update(extract_emails_from_text(soup.get_text()))

                for a in soup.find_all('a', href=True):
                    href = a['href']
                    if 'mailto:' in href:
                        emails.add(href.split(':')[1])
                    elif any(keyword in a.text.lower() for keyword in ['contact', 'about']):
                        contact_url = urljoin(current_url, href)
                        if is_valid_url(contact_url) and contact_url not in scraped_urls:
                            urls_to_scrape.append((contact_url, depth + 1))

                # Additional method: Find all forms and check for email fields
                for form in soup.find_all('form'):
                    action = form.get('action')
                    if action:
                        form_url = urljoin(current_url, action)
                        if is_valid_url(form_url) and form_url not in scraped_urls:
                            urls_to_scrape.append((form_url, depth + 1))
        except Exception as e:
            logging.error(f"Error accessing {current_url}: {e}")
        time.sleep(0.5)  # polite crawling

    return emails

def main(input_csv, output_csv):
    df = pd.read_csv(input_csv, quotechar='"', quoting=csv.QUOTE_MINIMAL)

    with open(output_csv, 'a', newline='') as csvfile:
        fieldnames = ['email', 'domain']
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)

        if csvfile.tell() == 0:
            writer.writeheader()

        for index, row in df.iterrows():
            domain = row['domain']
            url = f"https://{domain}"

            if not is_valid_url(url):
                logging.error(f"Invalid URL: {url}")
                continue

            print(f"Scraping {url}")
            emails = scrape_emails_from_url(url)

            for email in emails:
                writer.writerow({
                    'email': email, 
                    'domain': domain
                })
                csvfile.flush()

    print(f"Scraping completed. Results saved to {output_csv}")

if __name__ == "__main__":
    input_csv = "input.csv"
    output_csv = "output.csv"
    main(input_csv, output_csv)
