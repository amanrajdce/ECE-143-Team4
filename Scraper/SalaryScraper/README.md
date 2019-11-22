#  Salary Scraper for Glassdoor
This piece of code is heavily adapted from https://github.com/williamxie11/glassdoor-interview-scraper

## Usage
Run ``python salary_scraper_specific.py`` and wait until the scraper stops to scrape salary data for companies mentioned in ``companies.txt`` file in the main directory.

You can further modify the script and select for which specific company or job title you want scrape.
1. If you want to scrape for specific job titles.
  * Go to glassdoor and find which job title you want to scrape, copy the urls to ``links`` in ``salary_scraper.py`` and add your glassdoor username and password.
  * Run ``python salary_scraper.py`` and wait until the scraper stops.

2. If you want to scrape for specific company.
  * Go to glassdoor and find which company you want to scrape, copy the urls to ``links`` in ``salary_scraper_specific.py`` and add your glassdoor username and password.
  * Run ``python salary_scraper_specific.py`` and wait until the scraper stops.
