import time
import json
import Salary_Specific
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

username = ""  # your email here
password = ""  # your password here

pages = 12
links = ["https://www.glassdoor.com/Salary/Google-Salaries-E9079.htm",
         "https://www.glassdoor.com/Salary/Apple-Salaries-E1138.htm",
         "https://www.glassdoor.com/Salary/Amazon-Salaries-E6036.htm",
         "https://www.glassdoor.com/Salary/Facebook-Salaries-E40772.htm",
         "https://www.glassdoor.com/Salary/LinkedIn-Salaries-E34865.htm",
         "https://www.glassdoor.com/Salary/Intuit-Salaries-E2293.htm",
         "https://www.glassdoor.com/Salary/Microsoft-Salaries-E1651.htm",
         "https://www.glassdoor.com/Salary/Adobe-Salaries-E1090.htm",
         "https://www.glassdoor.com/Salary/Salesforce-Salaries-E11159.htm",
         "https://www.glassdoor.com/Salary/NVIDIA-Salaries-E7633.htm",
         "https://www.glassdoor.com/Salary/VMware-Salaries-E12830.htm",
         "https://www.glassdoor.com/Salary/Cisco-Systems-Salaries-E1425.htm",
         "https://www.glassdoor.com/Salary/HP-Inc-Salaries-E1093161.htm",
         "https://www.glassdoor.com/Salary/IBM-Salaries-E354.htm",
         "https://www.glassdoor.com/Salary/Samsung-Electronics-Salaries-E3363.htm",
         "https://www.glassdoor.com/Salary/Bloomberg-L-P-Salaries-E3096.htm",
         "https://www.glassdoor.com/Salary/Qualcomm-Salaries-E640.htm",
         "https://www.glassdoor.com/Salary/Dropbox-Salaries-E415350.htm",
         "https://www.glassdoor.com/Salary/Walmart-Salaries-E715.htm",
         "https://www.glassdoor.com/Salary/Expedia-Group-Salaries-E9876.htm"]

def init_driver():
	"""
	Initiate the driver by detecting the platform the user use. Return a driver executable.
	"""
	if platform.system() == "Windows":
		driver = webdriver.Chrome(executable_path="chromedriver.exe")
	elif platform.system() == "Darwin":
		driver = webdriver.Chrome(
			executable_path="/Users/haoming/OneDrive/Files/Academy/UCSD/Fall2019/ECE143/42/Scraper/Salary_Scraper/chromedriver")
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
		user_field = driver.wait.until(
			EC.presence_of_element_located((By.NAME, "username")))
		pw_field = driver.find_element_by_xpath('//*[@id="userPassword"]')
		login_button = driver.find_element_by_xpath(
			'//*[@id="InlineLoginModule"]/div/div/div[1]/div[3]/form/div[3]/div[1]/button')
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
		meanPay = "-"
		jobTitle = salary.find("div", {"class": "salaryRow__JobInfoStyle__jobTitle strong"}).getText().strip()
		print(jobTitle)
		try:
			meanPay = salary.find("div", {"class": "salaryRow__JobInfoStyle__meanBasePay common__formFactorHelpers__showHH"}).getText().strip()
		except:
			meanPay = 'xxx'
		try:
			s_range = salary.find("div", { "class": "salaryRow__JobInfoStyle__range common__formFactorHelpers__showHH"}).getText().strip()
		except:
			s_range = "xxx"
		r = Salary_Specific.Salary_Specific(jobTitle, meanPay, s_range)
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
	currentURL = URL + "_P" + str(startPage) + ".htm"
	time.sleep(2)
	if (refresh):
		driver.get(currentURL)
		print("Getting " + currentURL)
	time.sleep(2)
	HTML = driver.page_source
	soup = BeautifulSoup(HTML, "html.parser")
	salaries = soup.find_all(
	    "div", {"class": ["row align-items-center m-0 salaryRow__SalaryRowStyle__row"]})
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
	with open('/tables/%s-%s-job-results.csv' % (keyword, place), 'wb')as csvfile:
		fieldnames = ["jobTitle", "meanPay", "Range"]
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
		pay = re.findall(r".*/Salary/(.*)-(.*)-.*", link)
		print("\nStarting data scraping ...")
		data = get_data(driver, link[:-4], 1, pages, [], True)
		print("\nExporting data to " + pay[0][0] + "salary" + ".csv")
		output_to_csv(pay[0][0], "salary", data)
	driver.quit()
