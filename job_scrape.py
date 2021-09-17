# -*- coding: utf-8 -*-
"""
Created on Thu Sep 16 15:04:10 2021

@author: User
"""

from selenium import webdriver
from shutil import which
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
import time
import lxml
from bs4 import BeautifulSoup
import pandas as pd
import re

chrome_path = which("chromedriver")
driver = webdriver.Chrome(executable_path = chrome_path)
driver.get("https://tw.indeed.com/")
search_box = driver.find_element_by_xpath('//*[@id="text-input-what"]')
search_box.send_keys("data analyst")
search_box.send_keys(Keys.ENTER)
count = 0
data_job_df = pd.DataFrame({'Job_Link':[], 'Title':[], 'Company':[], 'Location':[], 'Salary':[], 'Date':[]})
while True:
    soup = BeautifulSoup(driver.page_source, "lxml")
    job_list = soup.select('div.mosaic.mosaic-provider-jobcards.mosaic-provider-hydrated > a')
    #Click off popup screen
    try:
        close = WebDriverWait(driver, 5).until(EC.element_to_be_clickable((By.XPATH, '//*[@id="popover-x"]/button')))
        close.click()
    except:
        pass
    
    #Scrape Job Vacancies
    for job in job_list:
        try:
            link = job.get("href")
            linkf = "https://tw.indeed.com" + link
            title = job.select('h2.jobTitle.jobTitle-color-purple > span')[0].text
            company = job.select('pre span.companyName')[0].text
            loc = job.select('div.companyLocation')[0].text
            date = job.select('span.date')[0].text
            try:
                salary = job.select('span.salary-snippet')[0].text
            except:
                salary = 'N/A' 
            print(linkf, title, company, loc, salary, date)
            count += 1
        except:
            pass
        data_job_df = data_job_df.append({'Job_Link':linkf, 'Title':title, 'Company':company, 'Location':loc, 'Salary':salary, 'Date':date}, ignore_index = True)
    print(count)
    #Next Page
    try:
        btn = soup.find('a', attrs = {'aria-label': re.compile('下一頁')}).get('href')
        button = soup.select('#resultsCol > nav > div > ul > li:nth-child(6) > a')[0].get("href")
        driver.get('https://tw.indeed.com' + btn)
    except:
        print("Successfully Scraped.")
        break
    count = 0



#Sort the DataFrame
data_job_df["Date"] = data_job_df["Date"].apply(lambda x: x[:2].strip())
def convert(x):
    if x.isnumeric():
        x = int(x)
    elif x == "今天":
        x = 0
    else:
        x = x[:-1]
        x = int(x)
    return x
data_job_df["Date"] = data_job_df["Date"].apply(convert)
data_job_df = data_job_df.sort_values("Date")


data_job_df.to_csv("C://Users//User//Documents//Data Processing//2021_Zita_bs4//data_job2.csv", encoding = 'utf_8_sig', line_terminator = "\n")
driver.close()

#################################################################
#目標: 把爬到的東西自動寄到某個email信箱
import smtplib, ssl
from email.mime.text import MIMEText
from email.mime.base import MIMEBase
from email.mime.multipart import MIMEMultipart
from email import encoders
import os

#Infos
sender = 'webscrapingprac@gmail.com'
receiver = 'dewboiler2@gmail.com'

#Create Message
msg = MIMEMultipart()
msg['Subject'] = 'New Jobs on Indeed'  #標題
msg['From'] = sender
msg['To'] = ','.join(receiver)  #可以有多個receiver

#Adds a csv file as an attachment to the email
part = MIMEBase('application', 'octet-stream')
part.set_payload(open('C://Users//User//Documents//Data Processing//2021_Zita_bs4//data_job2.csv', 'rb').read())  #打開+閱讀目標csv
encoders.encode_base64(part)
part.add_header('Content-Disposition', 'attachment', filename=os.path.basename('data_job2.csv'))   #filename記得使用os.path.basename，才抓得到檔案!
msg.attach(part)

#Will login to your email and actually send the message above to the receiver
s = smtplib.SMTP_SSL(host = 'smtp.gmail.com', port = 465)
s.login(user = 'webscrapingprac@gmail.com', password = 'tubecity0212')
s.sendmail(sender, receiver, msg.as_string())
s.quit()


