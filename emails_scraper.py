"""
Bulk Email Scraper For Websites.

This script scrapes emails from a list of domains provided in a CSV file. It navigates the main page and specific subpages
(e.g., 'contact', 'about') to find email addresses and saves the results in a CSV file.
"""

import re
import csv
import logging
import time
from collections import deque
from urllib.parse import urljoin, urlparse

import requests
from bs4 import BeautifulSoup
import pandas as pd

# Configure logging
logging.basicConfig(level=logging.DEBUG, filename='scraper.log', filemode='a',
                    format='%(asctime)s - %(levelname)s - %(message)s')


def extract_emails_from_text(text):
    """
    Extract emails from a given text using regex pattern matching.

    :param text: Text content from which emails are to be extracted
    :return: List of emails found in the text
    """
    email_pattern = re.compile(r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,7}\b')
    return email_pattern.findall(text)


def is_valid_url(url):
    """
    Validate a URL by checking its scheme and netloc.

    :param url: URL string to be validated
    :return: Boolean indicating if the URL is valid
    """
    parsed = urlparse(url)
    return bool(parsed.netloc) and bool(parsed.scheme)


def scrape_emails_from_page(soup):
    """
    Extract emails from a BeautifulSoup object representing a page's content.

    :param soup: BeautifulSoup object containing the page content
    :return: Set of emails found in the page content
    """
    emails = set(extract_emails_from_text(soup.get_text()))
    for a in soup.find_all('a', href=True):
        href = a['href']
        if 'mailto:' in href:
            emails.add(href.split(':')[1])
    return emails


def find_contact_pages(soup, base_url):
    """
    Find 'contact' or 'about' pages linked from the main page.

    :param soup: BeautifulSoup object containing the page content
    :param base_url: The base URL to resolve relative links
    :return: List of contact page URLs
    """
    contact_pages = []
    for a in soup.find_all('a', href=True):
        if any(keyword in a.text.lower() for keyword in ['contact', 'about']):
            contact_url = urljoin(base_url, a['href'])
            if is_valid_url(contact_url):
                contact_pages.append(contact_url)
    return contact_pages


def scrape_emails_from_url(url, max_depth=2):
    """
    Scrape emails from a given URL and its 'contact' or 'about' pages.

    :param url: The starting URL to scrape emails from
    :param max_depth: Maximum depth to search for URLs
    :return: Set of unique emails found
    """
    emails = set()
    urls_to_scrape = deque([(url, 0)])  # url with depth
    scraped_urls = set()

    headers = {
        'User-Agent': ('Mozilla/5.0 (Windows NT 10.0; Win64; x64) '
                       'AppleWebKit/537.36 (KHTML, like Gecko) '
                       'Chrome/91.0.4472.124 Safari/537.36')
    }

    while urls_to_scrape:
        current_url, depth = urls_to_scrape.popleft()
        logging.debug("Processing URL: %s at depth %d", current_url, depth)
        if current_url in scraped_urls or depth > max_depth:
            continue
        scraped_urls.add(current_url)

        try:
            response = requests.get(current_url, headers=headers, timeout=10)
            if response.status_code == 200:
                soup = BeautifulSoup(response.content, 'html.parser')
                emails.update(scrape_emails_from_page(soup))

                if depth < max_depth:
                    contact_pages = find_contact_pages(soup, current_url)
                    urls_to_scrape.extend((page, depth + 1) for page in contact_pages)

                # Additional method: Find all forms and check for email fields
                for form in soup.find_all('form'):
                    action = form.get('action')
                    if action:
                        form_url = urljoin(current_url, action)
                        if is_valid_url(form_url) and form_url not in scraped_urls:
                            urls_to_scrape.append((form_url, depth + 1))
        except requests.RequestException as e:
            logging.error("Error accessing %s: %s", current_url, e)
        time.sleep(1)  # polite crawling

    return emails


def main(input_csv_file, output_csv_file):
    """
    Main function to read domains from input CSV, scrape emails, and save to output CSV.

    :param input_csv_file: Path to input CSV file with domains
    :param output_csv_file: Path to output CSV file to save scraped emails
    """
    df = pd.read_csv(input_csv_file, quotechar='"', quoting=csv.QUOTE_MINIMAL)

    with open(output_csv_file, 'a', newline='', encoding='utf-8') as csvfile:
        fieldnames = ['email', 'domain']
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)

        if csvfile.tell() == 0:
            writer.writeheader()

        for _, row in df.iterrows():
            domain = row['domain']
            url = f"https://{domain}"

            if not is_valid_url(url):
                logging.error("Invalid URL: %s", url)
                continue

            print(f"Scraping {url}")
            emails = scrape_emails_from_url(url)

            for email in emails:
                writer.writerow({
                    'email': email,
                    'domain': domain
                })
                csvfile.flush()

    print(f"Scraping completed. Results saved to {output_csv_file}")


if __name__ == "__main__":
    INPUT_CSV = "input.csv"
    OUTPUT_CSV = "output.csv"
    main(INPUT_CSV, OUTPUT_CSV)
  
