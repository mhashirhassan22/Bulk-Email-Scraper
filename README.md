# Bulk-Email-Scraper

## Description
This Python script is designed to scrape emails from a list of domains provided in a CSV file. The script navigates the main page and additional pages (such as 'contact' or 'about' pages) to find email addresses.This project is useful for researchers, marketers, and developers looking to gather email addresses for outreach or data analysis.

## Features
- Extracts emails from the main page and specific subpages (contact/about) using regex.
- Logs the scraping process and errors for easy debugging.
- Outputs results to a CSV file.
- Handles edge cases and invalid URLs gracefully.
- Polite crawling with customizable depth limits and delays.

## Installation
1. Clone the repository:
   `git clone https://github.com/yourusername/email-scraper.git`
2. Navigate to the project directory:
   `cd email-scraper`

3. Install the required packages:
`pip install -r requirements.txt`

## Usage
Prepare your input CSV file with columns as input.csv
Run the script:
`python scraper.py
`
Check the output CSV file (e.g., output.csv) for the results.

## Contributing
Contributions are welcome! Please fork the repository and submit pull requests. 

## Improvements
- Run scraper in background for larger files
- Deal with captcha
- Support for multi language -- especially pages keywords e.g. contact, about

## License
This project is licensed under the MIT License.

## Keywords
email scraper, web scraping, Python, BeautifulSoup, data extraction, automated scraping, contact information, email extraction, public repository, open source, domain scraping.
