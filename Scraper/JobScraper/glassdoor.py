from lxml import html, etree
import requests
import re
import os
import sys
import unicodecsv as csv
import argparse
import json
import time
import re

def parse_with_key(keyword, place):

    headers = {	'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
                'accept-encoding': 'gzip, deflate, sdch, br',
                'accept-language': 'en-GB,en-US;q=0.8,en;q=0.6',
                'referer': 'https://www.glassdoor.com/',
                'upgrade-insecure-requests': '1',
                'user-agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Ubuntu Chromium/51.0.2704.79 Chrome/51.0.2704.79 Safari/537.36',
                'Cache-Control': 'no-cache',
                'Connection': 'keep-alive'
    }

    location_headers = {
        'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.01',
        'accept-encoding': 'gzip, deflate, sdch, br',
        'accept-language': 'en-GB,en-US;q=0.8,en;q=0.6',
        'referer': 'https://www.glassdoor.com/',
        'upgrade-insecure-requests': '1',
        'user-agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Ubuntu Chromium/51.0.2704.79 Chrome/51.0.2704.79 Safari/537.36',
        'Cache-Control': 'no-cache',
        'Connection': 'keep-alive'
    }
    data = {"term": place,
            "maxLocationsToReturn": 10}

    location_url = "https://www.glassdoor.com/findPopularLocationAjax.htm?"
    try:
        # Getting location id for search location
        print("Fetching location details")
        location_response = requests.post(location_url, headers=location_headers, data=data).json()
        place_id = location_response[0]['locationId']
        job_litsting_url = 'https://www.glassdoor.com/Job/jobs.htm'
        # Form data to get job results
        data = {
            'clickSource': 'searchBtn',
            'sc.keyword': keyword,
            'locT': 'C',
            'locId': place_id,
            'jobType': ''
        }

        job_listings = []
        if place_id:
            response = requests.post(job_litsting_url, headers=headers, data=data)
            # extracting data from
            # https://www.glassdoor.com/Job/jobs.htm?suggestCount=0&suggestChosen=true&clickSource=searchBtn&typedKeyword=andr&sc.keyword=android+developer&locT=C&locId=1146821&jobType=
            parser = html.fromstring(response.text)
            # Making absolute url 
            base_url = "https://www.glassdoor.com"
            parser.make_links_absolute(base_url)
            #jl hoover
            XPATH_ALL_JOB = '//li[@class="jl"]'
            XPATH_NAME = './/a/text()'
            XPATH_JOB_URL = './/a/@href'
            XPATH_LOC = './/span[@class="subtle loc"]/text()'
            # XPATH_COMPANY = './/div[@class="flexbox empLoc"]/div/text()'
            XPATH_COMPANY = './/div[@class= "jobInfoItem jobEmpolyerName"]/text()'
            # XPATH_SALARY = './/span[@class="green small"]/text()'
            XPATH_SALARY = './/span[@class="salaryText"]/text()'
            XPATH_NEXT_PAGE = '//*[@id="FooterPageNav"]/div/ul/li[7]/a/@href'
            
            a = parser.xpath(XPATH_NEXT_PAGE)[0]
            print("next page:", a)

            listings = parser.xpath(XPATH_ALL_JOB)
            for job in listings:
                raw_job_name = job.xpath(XPATH_NAME)
                raw_job_url = job.xpath(XPATH_JOB_URL)
                raw_lob_loc = job.xpath(XPATH_LOC)
                raw_company = job.xpath(XPATH_COMPANY)
                raw_salary = job.xpath(XPATH_SALARY)

                # Cleaning data
                job_name = ''.join(raw_job_name).strip('–') if raw_job_name else None
                job_location = ''.join(raw_lob_loc) if raw_lob_loc else None
                raw_state = re.findall(",\s?(.*)\s?", job_location)
                state = ''.join(raw_state).strip()
                raw_city = job_location.replace(state, '')
                city = raw_city.replace(',', '').strip()
                company = ''.join(raw_company).replace('–','')
                salary = ''.join(raw_salary).strip()
                job_url = raw_job_url[0] if raw_job_url else None

                jobs = {
                    "Name": job_name,
                    "Company": company,
                    "State": state,
                    "City": city,
                    "Salary": salary,
                    "Location": job_location,
                    "Url": job_url
                }
                job_listings.append(jobs)
            joblistings = parse_with_url(a, job_listings)

            return job_listings
        else:
            print("location id not available")

    except:
        print("Failed to load locations")

def parse_with_url(a, job_listings):

    headers = {	'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
                'accept-encoding': 'gzip, deflate, sdch, br',
                'accept-language': 'en-GB,en-US;q=0.8,en;q=0.6',
                'referer': 'https://www.glassdoor.com/',
                'upgrade-insecure-requests': '1',
                'user-agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Ubuntu Chromium/51.0.2704.79 Chrome/51.0.2704.79 Safari/537.36',
                'Cache-Control': 'no-cache',
                'Connection': 'keep-alive'
                }

    try:
        count = 0
        while True:
        # for i in range(10):
            if count % 5 == 0:
                time.sleep(5)
            time.sleep(1)
            count += 1
            print("Item scraped:", len(job_listings))
            response = requests.get(a, headers=headers)
            parser = html.fromstring(response.text)
            # Making absolute url
            base_url = "https://www.glassdoor.com"
            parser.make_links_absolute(base_url)
            #jl hoover
            XPATH_ALL_JOB = '//li[@class="jl"]'
            XPATH_NAME = './/a/text()'
            XPATH_JOB_URL = './/a/@href'
            XPATH_LOC = './/span[@class="subtle loc"]/text()'
            XPATH_COMPANY = './/div[@class= "jobInfoItem jobEmpolyerName"]/text()'
            XPATH_SALARY = './/span[@class="salaryText"]/text()'
            XPATH_NEXT_PAGE = '//*[@id="FooterPageNav"]/div/ul/li[7]/a/@href'

            a = parser.xpath(XPATH_NEXT_PAGE)[0]
            print("next page:", a)

            listings = parser.xpath(XPATH_ALL_JOB)
            for job in listings:
                raw_job_name = job.xpath(XPATH_NAME)
                raw_job_url = job.xpath(XPATH_JOB_URL)
                raw_lob_loc = job.xpath(XPATH_LOC)
                raw_company = job.xpath(XPATH_COMPANY)
                raw_salary = job.xpath(XPATH_SALARY)

                # Cleaning data
                job_name = ''.join(raw_job_name).strip(
                    '–') if raw_job_name else None
                job_location = ''.join(
                    raw_lob_loc) if raw_lob_loc else None
                raw_state = re.findall(",\s?(.*)\s?", job_location)
                state = ''.join(raw_state).strip()
                raw_city = job_location.replace(state, '')
                city = raw_city.replace(',', '').strip()
                company = ''.join(raw_company).replace('–', '')
                salary = ''.join(raw_salary).strip()
                job_url = raw_job_url[0] if raw_job_url else None

                jobs = {
                    "Name": job_name,
                    "Company": company,
                    "State": state,
                    "City": city,
                    "Salary": salary,
                    "Location": job_location,
                    "Url": job_url
                }
                job_listings.append(jobs)
    except:
        print(sys.exc_info()[0])
    return job_listings


def output_to_csv(keyword, place, scraped_data):
        with open('%s-%s-job-results.csv' % (keyword, place), 'wb')as csvfile:
            fieldnames = ['Name', 'Company', 'State', 'City', 'Salary', 'Location', 'Url']
            writer = csv.DictWriter(
                csvfile, fieldnames=fieldnames, quoting=csv.QUOTE_ALL)
            writer.writeheader()
            if scraped_data:
                for data in scraped_data:
                    writer.writerow(data)
            else:
                print("Your search for %s, in %s does not match any jobs" %
                    (keyword, place))

if __name__ == "__main__":
    '''
    Parsing with Keyword and location:
        python3 glassdoor.py -key "Android developer", "San Diego"
    Parsing with url:
        python3 glassdoor.py -url "https://www.glassdoor.com/Job/engineering-jobs-SRCH_KO0,11.htm"
    Parsing with file:
        python3 glassdoor.py -file
    '''
    '''
    This project was modified from https://www.scrapehero.com/how-to-scrape-job-listings-from-glassdoor-using-python-and-lxml/
    Implement by Haoming Zhang at UCSD, 2019
    '''
    if len(sys.argv) == 4 and sys.argv[1] == "-key":
        keyword = sys.argv[2]
        place = sys.argv[3]
        print("Fetching job details")
        scraped_data = parse_with_key(keyword, place)
        output_to_csv(keyword, place, scraped_data)
        print("Writing data to output file")
    elif len(sys.argv) == 3 and sys.argv[1] == "-url":
        url = sys.argv[2]
        print("Fetching job details")
        scraped_data = []
        scraped_data = parse_with_url(url, scraped_data)
        try:
            job = re.findall(r".*/Job/(.*)-(.*)-.*",url)
            output_to_csv(job[0][0], job[0][1], scraped_data)
        except:
            output_to_csv("", "", scraped_data)
        print("Writing data to output file")
    elif len(sys.argv) == 2 and sys.argv[1] == "-file":
        with open("address.txt", "r") as f:
            contents = f.readlines()
            for url in contents:
                url = url.strip()
                print("Fetching job details")
                scraped_data = []
                scraped_data = parse_with_url(url, scraped_data)
                try:
                    job = re.findall(r".*/Job/(.*)-(.*)-.*", url)
                    output_to_csv(job[0][0], job[0][1], scraped_data)
                except:
                    output_to_csv("", "", scraped_data)
                print("Writing data to output file")
    else:
        print('''
Parsing with Keyword and location:
    python3 glassdoor.py -key "Android developer", "San Diego"
Parsing with url:
    python3 glassdoor.py -url "https://www.glassdoor.com/Job/engineering-jobs-SRCH_KO0,11.htm"
Parsing with file:
    python3 glassdoor.py -file
''')

