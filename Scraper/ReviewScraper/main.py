'''Glassdoor Reviews Scraper

Given a company's landing page on Glassdoor and an output filename, this can 
scrape the following information about each employee review:

Review date, Employee position, Employee location, Employee status 
(current/former), Review title, Employee years at company, Number of helpful 
votes, Pros text, Cons text, Advice to mgmttext, Ratings for each of 5 
categories, Overall rating

----------
Oringal Author: Matthew Chatham(Jun, 2018) and iopsych(Jul, 2019)
link: https://github.com/iopsych/glassdoor-review-scraper
Modified by: Xiufeng Zhao(Nov, 2019)
'''

import time
import json
import urllib
import datetime as dt
from argparse import ArgumentParser

import logging
import pandas as pd
import numpy as np
import selenium
from selenium import webdriver as wd
from schema import SCHEMA

DEFAULT_URL = ('https://www.glassdoor.com/Overview/Working-at-'
               'Premise-Data-Corporation-EI_IE952471.11,35.htm')

parser = ArgumentParser()
parser.add_argument('-u', '--url',
    help='URL of the company\'s Glassdoor landing page.',
    default=DEFAULT_URL)
parser.add_argument('-f', '--file', default='glassdoor_ratings.csv',
    help='Output file.')
parser.add_argument('--headless', action='store_true',
    help='Run Chrome in headless mode.')
parser.add_argument('--username', help='Email address used to sign in to GD.')
parser.add_argument('-p', '--password', help='Password to sign in to GD.')
parser.add_argument('-c', '--credentials', help='Credentials file')
parser.add_argument('-l', '--limit', default=25,
    action='store', type=int, help='Max reviews to scrape')
parser.add_argument('--start_from_url', action='store_true',
    help='Start scraping from the passed URL.')
parser.add_argument(
    '--max_date', help='Latest review date to scrape.\
    Only use this option with --start_from_url.\
    You also must have sorted Glassdoor reviews ASCENDING by date.',
    type=lambda s: dt.datetime.strptime(s, "%Y-%m-%d"))
parser.add_argument(
    '--min_date', help='Earliest review date to scrape.\
    Only use this option with --start_from_url.\
    You also must have sorted Glassdoor reviews DESCENDING by date.',
    type=lambda s: dt.datetime.strptime(s, "%Y-%m-%d"))
args = parser.parse_args()

if not args.start_from_url and (args.max_date or args.min_date):
    raise Exception(
        'Invalid argument combination:\
        No starting url passed, but max/min date specified.')
elif args.max_date and args.min_date:
    raise Exception(
        'Invalid argument combination:\
        Both min_date and max_date specified.')

if args.credentials:
    with open(args.credentials) as f:
        d = json.loads(f.read())
        args.username = d['username']
        args.password = d['password']
else:
    try:
        with open('secret.json') as f:
            d = json.loads(f.read())
            args.username = d['username']
            args.password = d['password']
    except FileNotFoundError:
        msg = 'Please provide Glassdoor credentials.\
        Credentials can be provided as a secret.json file in the working\
        directory, or passed at the command line using the --username and\
        --password flags.'
        raise Exception(msg)

# set up logger
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)
ch = logging.StreamHandler()
ch.setLevel(logging.INFO)
logger.addHandler(ch)
formatter = logging.Formatter(
    '%(asctime)s %(levelname)s %(lineno)d\
    :%(filename)s(%(process)d) - %(message)s')
ch.setFormatter(formatter)

logging.getLogger('selenium').setLevel(logging.CRITICAL)
logging.getLogger('selenium').setLevel(logging.CRITICAL)


def scrape(field, review, author):
    '''
    this function scrapes sepecific data from reviews and return them all.

    param:
    field(str): name of function to call to extract specific info
    review(selenium.webdriver.remote.webelement.WebElement): review element
    author(selenium.webdriver.remote.webelement.WebElement): author element

    return:
    str: the needed info in string
    '''
    assert isinstance(field, str)
    assert isinstance(
            review, selenium.webdriver.remote.webelement.WebElement)
    assert isinstance(
            author, selenium.webdriver.remote.webelement.WebElement)
    
    def scrape_date(review):
        '''
        get datetime from review

        param:
        review(selenium.webdriver.remote.webelement.WebElement): web element

        return:
        str: datetime in string
        '''
        assert isinstance(
            review, selenium.webdriver.remote.webelement.WebElement)
        return review.find_element_by_tag_name(
            'time').get_attribute('datetime')

    def scrape_emp_title(review):
        '''
        get employee's title from review

        param:
        review(selenium.webdriver.remote.webelement.WebElement): web element

        return:
        str or np.nan: employee's title or return np.nan if not exists
        '''
        assert isinstance(
            review, selenium.webdriver.remote.webelement.WebElement)
        if 'Anonymous Employee' not in review.text:
            try:
                res = author.find_element_by_class_name(
                    'authorJobTitle').text.split('-')[1]
            except Exception:
                logger.warning('Failed to scrape employee_title')
                res = np.nan
        else:
            res = np.nan
        return res

    def scrape_location(review):
        '''
        get employee's location from review

        param:
        review(selenium.webdriver.remote.webelement.WebElement): web element

        return:
        str or np.nan: employee's location or np.nan if not exists
        '''
        assert isinstance(
            review, selenium.webdriver.remote.webelement.WebElement)
        if 'in' in review.text:
            try:
                res = author.find_element_by_class_name(
                    'authorLocation').text
            except Exception:
                res = np.nan
        else:
            res = np.nan
        return res
      
    def scrape_status(review):
        '''
        get employee's status from review

        param:
        review(selenium.webdriver.remote.webelement.WebElement): web element

        return:
        str or np.nan: employee's status or np.nan if not exists
        '''
        assert isinstance(
            review, selenium.webdriver.remote.webelement.WebElement)
        try:
            res = author.text.split('-')[0]
        except Exception:
            logger.warning('Failed to scrape employee_status')
            res = np.nan
        return res

    def scrape_rev_title(review):
        '''
        get review's title from review

        param:
        review(selenium.webdriver.remote.webelement.WebElement): web element

        return:
        str: review's title
        '''
        assert isinstance(
            review, selenium.webdriver.remote.webelement.WebElement)
        return review.find_element_by_class_name('summary').text.strip('"')
   
    def scrape_years(review):
        '''
        get working year from review

        param:
        review(selenium.webdriver.remote.webelement.WebElement): web element

        return:
        str: working year
        '''
        assert isinstance(
            review, selenium.webdriver.remote.webelement.WebElement)
        return review.find_element_by_class_name('mainText').text.strip('"')
   
    def scrape_helpful(review):
        '''
        get votes for helpful from review

        param:
        review(selenium.webdriver.remote.webelement.WebElement): web element

        return:
        str or np.nan: vote number or np.nan if not exists
        '''
        assert isinstance(
            review, selenium.webdriver.remote.webelement.WebElement)
        try: 
           s = review.find_element_by_class_name(
               'helpfulReviews').text.strip('""')
           res = s[s.find("(")+1:s.find(")")]
        except Exception:
            res=np.nan
        return res

    def scrape_pros(review):
        '''
        get what are pros in the company from review

        param:
        review(selenium.webdriver.remote.webelement.WebElement): web element

        return:
        str or np.nan: pros or np.nan if not exists
        '''
        assert isinstance(
            review, selenium.webdriver.remote.webelement.WebElement)
        try:
            expand = review.find_element_by_xpath(
                ".//span[contains(text(),'Show More')]").click()
        except Exception:
            pass    
        try:
            pros = review.find_element_by_xpath (
                ".//div/p[contains(text(),'Pros')]/following-sibling::p") 
            res = pros.text.strip('-')
        except Exception:
            res = np.nan
        return res      

    def scrape_cons(review):
        '''
        get what are cons in the company from review

        param:
        review(selenium.webdriver.remote.webelement.WebElement): web element

        return:
        str or np.nan: cons or np.nan if not exists
        '''
        assert isinstance(
            review, selenium.webdriver.remote.webelement.WebElement)
        try:
            expand = review.find_element_by_xpath(
                ".//span[contains(text(),'Show More')]").click()
        except Exception:
            pass
        try:
            cons = review.find_element_by_xpath (
                ".//div/div/p[contains(text(),'Cons')]/following-sibling::p")  
            res = cons.text.strip('-')
        except Exception:
            res = np.nan
        return res

    def scrape_advice(review):
        '''
        get advice from review

        param:
        review(selenium.webdriver.remote.webelement.WebElement): web element

        return:
        str or np.nan: advice or np.nan if not exists
        '''
        assert isinstance(
            review, selenium.webdriver.remote.webelement.WebElement)
        try:
            expand = review.find_element_by_xpath(
                ".//span[contains(text(),'Show More')]").click()
        except Exception:
            pass      
        try:
            advice = review.find_element_by_xpath (
                ".//div/p[contains(text(),'Advice')]/following-sibling::p")  
            res = advice.text.strip('-')
        except Exception:
            res = np.nan
        return res

    def scrape_overall_rating(review):
        '''
        get overall rating from review

        param:
        review(selenium.webdriver.remote.webelement.WebElement): web element

        return:
        str or np.nan: overall rating or np.nan if not exists
        '''
        assert isinstance(
            review, selenium.webdriver.remote.webelement.WebElement)
        try:
            ratings = review.find_element_by_class_name('gdStars')
            overall = ratings.find_element_by_class_name(
                'rating').find_element_by_class_name('value-title')
            res = overall.get_attribute('title')
        except Exception:
            res = np.nan
        return res

    def _scrape_subrating(i):
        '''
        get sub-rating from review

        param:
        i(int): choice of sub-rating

        return:
        str or np.nan: sub-rating or np.nan if not exists
        '''
        assert isinstance(
            review, selenium.webdriver.remote.webelement.WebElement)
        try:
            ratings = review.find_element_by_class_name('gdStars')
            subratings = ratings.find_element_by_class_name(
                'subRatings').find_element_by_tag_name('ul')
            this_one = subratings.find_elements_by_tag_name('li')[i]
            res = this_one.find_element_by_class_name(
                'gdBars').get_attribute('title')
        except Exception:
            res = np.nan
        return res

    def scrape_work_life_balance(review):
        '''
        get work life balance rating from review

        param:
        review(selenium.webdriver.remote.webelement.WebElement): web element

        return:
        str or np.nan: rating or np.nan if not exists
        '''
        assert isinstance(
            review, selenium.webdriver.remote.webelement.WebElement)
        return _scrape_subrating(0)

    def scrape_culture_and_values(review):
        '''
        get culture and values rating from review

        param:
        review(selenium.webdriver.remote.webelement.WebElement): web element

        return:
        str or np.nan: rating or np.nan if not exists
        '''
        assert isinstance(
            review, selenium.webdriver.remote.webelement.WebElement)
        return _scrape_subrating(1)

    def scrape_career_opportunities(review):
        '''
        get career and opportunities rating from review

        param:
        review(selenium.webdriver.remote.webelement.WebElement): web element

        return:
        str or np.nan: rating or np.nan if not exists
        '''
        assert isinstance(
            review, selenium.webdriver.remote.webelement.WebElement)
        return _scrape_subrating(2)

    def scrape_comp_and_benefits(review):
        '''
        get company and benefits rating from review

        param:
        review(selenium.webdriver.remote.webelement.WebElement): web element

        return:
        str or np.nan: rating or np.nan if not exists
        '''
        assert isinstance(
            review, selenium.webdriver.remote.webelement.WebElement)
        return _scrape_subrating(3)

    def scrape_senior_management(review):
        '''
        get senior management rating from review

        param:
        review(selenium.webdriver.remote.webelement.WebElement): web element

        return:
        str or np.nan: rating or np.nan if not exists
        '''
        assert isinstance(
            review, selenium.webdriver.remote.webelement.WebElement)
        return _scrape_subrating(4)

    funcs = [
        scrape_date,
        scrape_emp_title,
        scrape_location,
        scrape_status,
        scrape_rev_title,
        scrape_years,
        scrape_helpful,
        scrape_pros,
        scrape_cons,
        scrape_advice,
        scrape_overall_rating,
        scrape_work_life_balance,
        scrape_culture_and_values,
        scrape_career_opportunities,
        scrape_comp_and_benefits,
        scrape_senior_management
    ]
    fdict = dict((s, f) for (s, f) in zip(SCHEMA, funcs))
    return fdict[field](review)


def extract_from_page():
    '''
    extract specific info from webpage

    return:
    pd.DataFrame: data scraped from webpage
    '''

    def is_featured(review):
        '''
        check if a review has 'featuredFlag' or not

        param:
        review(selenium.webdriver.remote.webelement.WebElement): web element

        return:
        bool: True if it has and False if it doesn't
        '''
        assert isinstance(
            review, selenium.webdriver.remote.webelement.WebElement)
        try:
            review.find_element_by_class_name('featuredFlag')
            return True
        except selenium.common.exceptions.NoSuchElementException:
            return False

    def extract_review(review):
        '''
        extrace specific info from review

        param:
        review(selenium.webdriver.remote.webelement.WebElement): web element

        return:
        dict: result that contain specific info
        '''
        assert isinstance(
            review, selenium.webdriver.remote.webelement.WebElement)
        author = review.find_element_by_class_name('authorInfo')
        res = {}
        for field in SCHEMA:
            res[field] = scrape(field, review, author)

        assert set(res.keys()) == set(SCHEMA)
        return res

    
    logger.info(f'Extracting reviews from page {page[0]}')

    res = pd.DataFrame([], columns=SCHEMA)

    reviews = browser.find_elements_by_class_name('empReview')
    logger.info(f'Found {len(reviews)} reviews on page {page[0]}')

    for review in reviews:
        if not is_featured(review):
            data = extract_review(review)
            logger.info(f'Scraped data for "{data["review_title"]}"\
                ({data["date"]})')
            res.loc[idx[0]] = data
        else:
            logger.info('Discarding a featured review')
        idx[0] = idx[0] + 1

    if args.max_date and \
        (pd.to_datetime(res['date']).max() > args.max_date) or \
            args.min_date and \
            (pd.to_datetime(res['date']).min() < args.min_date):
        logger.info('Date limit reached, ending process')
        date_limit_reached[0] = True
    return res


def more_pages():
    '''
    find next page by css selector

    return:
    bool: whether it finds next page
    '''
    try:
        browser.find_element_by_css_selector(
            'a.pagination__ArrowStyle__nextArrow.' + 
            'pagination__ArrowStyle__disabled')
        return True
    except selenium.common.exceptions.NoSuchElementException:
        return False

def go_to_next_page():
    '''
    go to next page
    '''
    logger.info(f'Going to page {page[0] + 1}')
    next_ = browser.find_element_by_xpath(
        ".//li[@class='pagination__PaginationStyle__next']/a")
    browser.get(next_.get_attribute('href'))
    time.sleep(1)
    page[0] = page[0] + 1 


def navigate_to_reviews():
    '''
    navigate to review pages from the start page.

    return:
    bool: True if it is navigates to review page.
    '''
    logger.info('Navigating to company reviews')
    # start from the starting page
    browser.get(args.url)
    time.sleep(1)
    # navigate
    reviews_cell = browser.find_element_by_xpath(
        "//*[@id='EmpLinksWrapper']/div//a[2]")
    reviews_path = reviews_cell.get_attribute('href')
    browser.get(reviews_path)
    time.sleep(1)
    return True


def sign_in():
    '''
    sign in with username and password from secret.json file
    '''
    logger.info(f'Signing in to {args.username}')
    url = 'https://www.glassdoor.com/profile/login_input.htm'
    browser.get(url)
    # find field
    email_field = browser.find_element_by_name('username')
    password_field = browser.find_element_by_name('password')
    submit_btn = browser.find_element_by_xpath('//button[@type="submit"]')
    # fill info
    email_field.send_keys(args.username)
    password_field.send_keys(args.password)
    submit_btn.click()
    # wait for processing
    time.sleep(1)


def get_browser():
    '''
    get a controlled browser with help from chromedriver 

    return:
    webdriver.Chrome: the web browser to drive
    '''
    logger.info('Configuring browser')
    chrome_options = wd.ChromeOptions()
    if args.headless:
        chrome_options.add_argument('--headless')
    chrome_options.add_argument('log-level=3')
    browser = wd.Chrome(options=chrome_options)
    return browser


def get_current_page():
    '''
    get current page number

    return:
    int: current page number
    '''
    logger.info('Getting current page number')
    paging_control = browser.find_element_by_class_name('current')
    current = int(paging_control.find_element_by_xpath(
        '//ul//li[contains\
        (concat(\' \',normalize-space(@class),\' \'),\' current \')]\
        //span[contains(concat(\' \',\
        normalize-space(@class),\' \'),\' disabled \')]')
        .text.replace(',', ''))
    return current


def verify_date_sorting():
    '''
    sort data by date and raise exception if inputs are not enough
    '''
    logger.info('Date limit specified, verifying date sorting')
    ascending = urllib.parse.parse_qs(
        args.url)['sort.ascending'] == ['true']

    if args.min_date and ascending:
        raise Exception(
            'min_date required reviews to be sorted DESCENDING by date.')
    elif args.max_date and not ascending:
        raise Exception(
            'max_date requires reviews to be sorted ASCENDING by date.')


# get browser and variables globally ready
browser = get_browser()
page = [1]
idx = [0]
date_limit_reached = [False]

def main():
    '''
    this function integrates the functions above and scrapes data from 
    Glassdoor automatically, stores the file into the destination folder.
    '''
    start = time.time()
    logger.info(f'Scraping up to {args.limit} reviews.')
    # initialization of dataframe
    res = pd.DataFrame([], columns=SCHEMA)
    # sign in with secret.json
    sign_in()

    if not args.start_from_url:
        reviews_exist = navigate_to_reviews()
        if not reviews_exist:
            return
    elif args.max_date or args.min_date:
        verify_date_sorting()
        browser.get(args.url)
        page[0] = get_current_page()
        logger.info(f'Starting from page {page[0]:,}.')
        time.sleep(1)
    else:
        browser.get(args.url)
        page[0] = get_current_page()
        logger.info(f'Starting from page {page[0]:,}.')
        time.sleep(1)
    # start to scrape
    reviews_df = extract_from_page()
    res = res.append(reviews_df)
    while not more_pages()  and\
            len(res) < args.limit and\
            not date_limit_reached[0]:
        go_to_next_page()
        reviews_df = extract_from_page()
        res = res.append(reviews_df)
    # write output file
    logger.info(f'Writing {len(res)} reviews to file {args.file}')
    res.to_csv(args.file, index=False, encoding='utf-8')
    end = time.time()
    logger.info(f'Finished in {end - start} seconds')


if __name__ == '__main__':
    main()
