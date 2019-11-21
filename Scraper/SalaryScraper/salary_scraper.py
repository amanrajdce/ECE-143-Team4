import time
import json
import Salary
import unicodecsv as csv
import re
import platform
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.common.keys import Keys

username = "" # your email here
password = "" # your password here

pages = 100
# links = ["https://www.glassdoor.com/Salaries/intern-salary-SRCH_KO0,6.htm", 
#          "https://www.glassdoor.com/Salaries/marketing-salary-SRCH_KO0,9.htm",
#          "https://www.glassdoor.com/Salaries/engineering-salary-SRCH_KO0,11.htm",
#          "https://www.glassdoor.com/Salaries/it-salary-SRCH_KO0,2.htm",
#          "https://www.glassdoor.com/Salaries/finance-salary-SRCH_KO0,7.htm"]
links = ["https://www.glassdoor.com/Salaries/legal-salary-SRCH_KO0,5.htm",
		 "https://www.glassdoor.com/Salaries/pharmacy-salary-SRCH_KO0,8.htm",
		 "https://www.glassdoor.com/Salaries/customer-service-salary-SRCH_KO0,16.htm",
		 "https://www.glassdoor.com/Salaries/education-salary-SRCH_KO0,9.htm",
		 "https://www.glassdoor.com/Salaries/banking-salary-SRCH_KO0,7.htm"]


def init_driver():
	"""
	Initiate the driver by detecting the platform the user use. Return a driver executable.
	"""
	if platform.system() == "Windows":
		driver = webdriver.Chrome(executable_path = "chromedriver.exe")
	elif platform.system() == "Darwin":
		driver = webdriver.Chrome(executable_path="/Users/haoming/OneDrive/Files/Academy/UCSD/Fall2019/ECE143/42/Scraper/SalaryScraper/chromedriver")
	driver.wait = WebDriverWait(driver, 10)
	return driver

def login(driver, username, password):
	"""
	Login process. Initiate a chrome web driver and automatically input username and password to fake login.

	:param driver: driver executable to launch
	:type driver: executable
	:param username: username for glassdoor
	:type username: String
	:param password: Password for Glassdoor
	:type password: String
	"""
	driver.get("http://www.glassdoor.com/profile/login_input.htm")
	try:
		user_field = driver.wait.until(EC.presence_of_element_located((By.NAME, "username")))
		pw_field = driver.find_element_by_xpath('//*[@id="userPassword"]')
		login_button = driver.find_element_by_xpath('//*[@id="InlineLoginModule"]/div/div/div[1]/div[3]/form/div[3]/div[1]/button')
		user_field.send_keys(username)
		user_field.send_keys(Keys.TAB)
		time.sleep(1)
		pw_field.send_keys(password)
		time.sleep(1)
		login_button.click()
	except TimeoutException:
		print("TimeoutException! Username/password field or login button not found on glassdoor.com")

def parse_salaries_HTML(salaries, data):
	"""
	Parsing Process. By getting the data from salaries, parse the data on each tab.
	
	:param salaries: div for salary content
	:type salaries: beautifulsoup4 div
	:param data: data list for output
	:type data: List
	"""
	for salary in salaries:
		jobTitle = "-"
		company = "-"
		meanPay = "-"
		jobTitle = salary.find("div", {"class": "salaryRow__JobInfoStyle__jobTitle strong"}).getText().strip()
		company = salary.find("div", {"class": "salaryRow__JobInfoStyle__employerName"}).getText().strip()
		try:
			meanPay = salary.find("div", {"class": "salaryRow__JobInfoStyle__meanBasePay common__formFactorHelpers__showHH"}).getText().strip()
		except:
			meanPay = 'xxx'
		r = Salary.Salary(jobTitle, company, meanPay)
		data.append(r.dic)
	return data

def get_data(driver, URL, startPage, endPage, data, refresh):
	"""
	Get into to webpage that need to be parsed and scrape each part of the salary.
	
	:param driver: Web Driver
	:type driver: executable
	:param URL: Link that need to be parsed
	:type URL: Sting
	:param startPage: Starting page number
	:type startPage: int
	:param endPage: Ending page number
	:type endPage: int
	:param data: data that need to be returned
	:type data: list
	:param refresh: refresh the page or not
	:type refresh: bool
	"""
	if (startPage > endPage):
		return data
	print("\nPage " + str(startPage) + " of " + str(endPage))
	currentURL = URL + "_IP" + str(startPage) + ".htm"
	time.sleep(2)
	if (refresh):
		driver.get(currentURL)
		print("Getting " + currentURL)
	time.sleep(2)
	HTML = driver.page_source
	soup = BeautifulSoup(HTML, "html.parser")
	salaries = soup.find_all(
	    "div", {"class": ["salaryRow__JobInfoStyle__employerInfo col-10 pl"]})
	if (salaries):
		data = parse_salaries_HTML(salaries, data)
		print("Page " + str(startPage) + " scraped.")
		if (startPage % 10 == 0):
			print("\nTaking a breather for a few seconds ...")
			time.sleep(10)
		get_data(driver, URL, startPage + 1, endPage, data, True)
	else:
		print("Waiting ... page still loading or CAPTCHA input required")
		time.sleep(3)
		get_data(driver, URL, startPage, endPage, data, False)
	return data

def output_to_csv(keyword, place, scraped_data):
	"""Output the scrapped data into a csv file
	
	:param keyword: Keyword of the job
	:type keyword: String
	:param place: Location of the job
	:type place: String
	:param scraped_data: Data we scrapped
	:type scraped_data: list
	"""
	with open('%s-%s-job-results.csv' % (keyword, place), 'wb')as csvfile:
		fieldnames = ["jobTitle", "company", "meanPay"]
		writer = csv.DictWriter(
			csvfile, fieldnames=fieldnames, quoting=csv.QUOTE_ALL)
		writer.writeheader()
		if scraped_data:
			for data in scraped_data:
				writer.writerow(data)
		else:
			print("Your search for %s, in %s does not match any jobs" %(keyword, place))

if __name__ == "__main__":
	"""
	glassdoor web crawler and scraper providing salary data. 
	Forked and modified from [williamxie11](https://github.com/williamxie11/glassdoor-interview-scraper).
	Modifier: Haoming Zhang
	"""
	driver = init_driver()
	time.sleep(3)
	print("Logging into Glassdoor account ...")
	login(driver, username, password)
	time.sleep(10)
	for link in links:
		pay = re.findall(r".*/Salaries/(.*)-(.*)-.*", link)
		print("\nStarting data scraping ...")
		data = get_data(driver, link[:-4], 1, pages, [], True)
		print("\nExporting data to " + pay[0][0] + "salary" + ".csv")
		output_to_csv(pay[0][0], "salary", data)
	driver.quit()
