import os
import subprocess

DIR = './tables'

companies = {
    'google': "https://www.glassdoor.com/Reviews/Google-Reviews-E9079.htm", 
    'apple': "https://www.glassdoor.com/Reviews/Apple-Reviews-E1138.htm", 
    'facebook': "https://www.glassdoor.com/Reviews/Facebook-Reviews-E40772.htm", 
    'amazon': "https://www.glassdoor.com/Reviews/Amazon-Reviews-E6036.htm", 
    'linkedin': "https://www.glassdoor.com/Reviews/LinkedIn-Reviews-E34865.htm", 
    'intuit': "https://www.glassdoor.com/Reviews/Intuit-Reviews-E2293.htm", 
    'microsoft': "https://www.glassdoor.com/Reviews/Microsoft-Reviews-E1651.htm", 
    'adobe': "https://www.glassdoor.com/Reviews/Adobe-Reviews-E1090.htm", 
    'salesforce': "https://www.glassdoor.com/Reviews/Salesforce-Reviews-E11159.htm", 
    'nvidia': "https://www.glassdoor.com/Reviews/NVIDIA-Reviews-E7633.htm", 
    'vmware': "https://www.glassdoor.com/Reviews/VMware-Reviews-E12830.htm", 
    'cisco': "https://www.glassdoor.com/Reviews/Cisco-Systems-Reviews-E1425.htm", 
    'hp': "https://www.glassdoor.com/Reviews/HP-Inc-Reviews-E1093161.htm", 
    'ibm': "https://www.glassdoor.com/Reviews/IBM-Reviews-E354.htm", 
    'samsung': "https://www.glassdoor.com/Reviews/Samsung-Electronics-Reviews-E3363.htm", 
    'bloomberg': "https://www.glassdoor.com/Reviews/Bloomberg-L-P-Software-Engineer-Reviews-EI_IE3096.0,13_KO14,31.htm", 
    'qualcomm': "https://www.glassdoor.com/Reviews/Qualcomm-Reviews-E640.htm", 
    'dropbox': "https://www.glassdoor.com/Reviews/Dropbox-Reviews-E415350.htm", 
    'walmart': "https://www.glassdoor.com/Reviews/Walmart-eCommerce-Reviews-E29449.htm", 
    'expedia': "https://www.glassdoor.com/Reviews/Expedia-Group-Reviews-E9876.htm"
}

if __name__ == '__main__':
    if not os.path.exists(DIR):
        os.mkdir(DIR)
    for company, link in companies.items():
        command = 'python main.py --headless --url "'+link+'" --limit 300 -f tables/'+company+'_reviews.csv'
        print(command)
        process = subprocess.Popen(command, shell=True, stdout=subprocess.PIPE)
        process.wait()
        assert process.returncode == 0
        print("finished scraping reviews from", link, '\n\n')