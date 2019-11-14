class Salary_Specific:
	def __init__(self, jobTitle, meanPay, s_range):
		self.jobTitle = jobTitle
		self.meanPay = meanPay
		self.s_range = s_range
		self.dic = {
				"jobTitle": jobTitle,
				"meanPay": meanPay,
				"Range" : s_range}
