# Introduction
This script can go through pages and pages of reviews in Glassdoor and scrape review data into a tidy CSV file. And it is mostly adopted from [iopsych's repo](https://github.com/iopsych/glassdoor-review-scraper).

# Prerequisites
1. Install [Chromedriver](http://chromedriver.chromium.org/) in the working directory.
2. Create a `secret.json` file containing the keys `username` and `password` with your Glassdoor login information, or pass those arguments at the command line. 

# Usage
```
usage: main.py [-h] [-u URL] [-f FILE] [--headless] [--username USERNAME]
               [-p PASSWORD] [-c CREDENTIALS] [-l LIMIT] [--start_from_url] 
               [--max_date MAX_DATE] [--min_date MIN_DATE]

optional arguments:
  -h, --help                                  show this help message and exit
  -u URL, --url URL                           URL of the company's Glassdoor landing page.
  -f FILE, --file FILE                        Output file.
  --headless                                  Run Chrome in headless mode.
  --username USERNAME                         Email address used to sign in to GD.
  -p PASSWORD, --password PASSWORD            Password to sign in to GD.
  -c CREDENTIALS, --credentials CREDENTIALS   Credentials file
  -l LIMIT, --limit LIMIT                     Max reviews to scrape
  --start_from_url                            Start scraping from the passed URL.
  
  --max_date MAX_DATE                         Latest review date to scrape. Only use this option
                                              with --start_from_url. You also must have sorted
                                              Glassdoor reviews ASCENDING by date.
                                              
  --min_date MIN_DATE                         Earliest review date to scrape. Only use this option
                                              with --start_from_url. You also must have sorted
                                              Glassdoor reviews DESCENDING by date.
``` 

### Example
1. Get the top 300 most popular reviews for Google  
  * find the review webpage of Google on Glassdoor, which is "https://www.glassdoor.com/Reviews/Google-Reviews-E9079.htm"
  * put the link into the command and run it, which would be as follows:  
`python main.py --headless --url "https://www.glassdoor.com/Reviews/Google-Reviews-E9079.htm" --limit 300 -f tables/google_reviews.csv`

2. Get the top 300 most popular reviews for Linkedin   
  * find the review webpage of Linkedin on Glassdoor, which is "https://www.glassdoor.com/Reviews/LinkedIn-Reviews-E34865.htm"
  * put the link into the command and run it, which would be as follows:  
`python main.py --headless --url "https://www.glassdoor.com/Reviews/LinkedIn-Reviews-E34865.htm" --limit 300 -f tables/linkedin_reviews.csv`

### Our scraping process
To reproducing our scraping process, run `python run_all.py` directly.
