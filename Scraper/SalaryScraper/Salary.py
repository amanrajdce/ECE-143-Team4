class Salary:
	def __init__(self, jobTitle, company, meanPay):
		self.jobTitle = jobTitle
		self.company = company
		self.meanPay = meanPay
		self.dic = {
                    "jobTitle": jobTitle,
                    "company": company,
                    "meanPay": meanPay
                }
