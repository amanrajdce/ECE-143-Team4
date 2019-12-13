# Analysis on data scraped from Glassdoor
We scrape data from Glassdor first and then do some interesting analysis.

## Requirements
* Chrome v78
* Python3
* Python packages: ``bs4``, ``selenium``, ``unicodecsv``, ``pandas``, ``numpy``, ``nltk``
* Chromedriver from selenium webpage. https://chromedriver.chromium.org/downloads

## Scraping
1. Steps to scrape salary data:
  * First change director by ``cd Scraper/SalaryScraper`` and edit file ``salary_scraper_specific.py`` to include your Glassdor username and password.
  * Now run ``python salary_scraper_specific.py`` and wait till scraper stops.
2. Steps to scrape review data:
 * First change director by ``cd Scraper/ReviewScraper``, and then run command `python run_all.py`.

## Data pre-processing
After we obtain review and salary data for each company, the next step is to merge these individual tables and pre-process to clean the outliers. This stage generate following tables:
* ``merge_reviews_table.csv``
* ``fulltime_merged_salaries_company_table.csv``
* ``intern_merged_salaries_company_table.csv``

In order to generate above tables run ``python merge_table.py``

## Analysis
Our analysis procedure tries to answer following questions.
* Which company offers the highest average salary?
* Which field has more jobs?
* Are interns paid generously?
* Which job category provide the highest average salary?
* Which state in US offers the most job opportunities?
* Which city should you move if you are looking for a job?
* How do employees rate their CEOs?
* Will they recommend their company to their friends?
* What feedback do employees give for the companies they are working?

These analysis can be seen by running ``demo.ipynb`` notebook.
