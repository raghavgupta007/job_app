# -*- coding: utf-8 -*-
"""
"""
'''
* Project: Data Focus Python
* File: main.c
* Author(s):  Raghav Gupta
'''
########################################################################################################################
################################IMPORT REQUIRED#########################################################################
########################################################################################################################
'''Imports required '''
import requests
from bs4 import BeautifulSoup
import csv
from datetime import datetime
import pandas as pd
from selenium.common.exceptions import NoSuchElementException, ElementClickInterceptedException
from selenium import webdriver
import time
from tkinter import *
import tkinter as tk
from tkinter import messagebox
import numpy as np
from scipy import stats
import matplotlib.pyplot as plt
import seaborn as sns
import plotly
import plotly.express as px
from tabulate import tabulate
import warnings
warnings.filterwarnings("ignore")
########################################################################################################################
################################INDEED.COM USING BEAUTIFUL SOUP#########################################################
########################################################################################################################

# Generalize the model with a function
def get_url(position):
    template = 'https://www.indeed.com/jobs?q={}'
    url = template.format(position)
    return url


# scrape jobs from indeed using beautiful soup
#Function to scrape jobs with indeed using Beautiful Soup
def get_Indeed_Jobs(position):
    # print(position)
    records = []                                                        #records temporarily holds all data scrapped from indeed
    url = get_url(position)                                             #get_url fn() will get the url for position searched by user
    # print(v0.get())
    if v0.get() == 2:                                                   #v0.get() = 1 if dynamic search by user;#v0.get() = 2 if static search by user
        page_count = 3                                                  #for static search scrape only 3 pages
    while True:                                                         #main loop to scrape data from indeed.com
        response = requests.get(url)
        soup = BeautifulSoup(response.text, 'html.parser')
        cards = soup.find_all('a', class_='tapItem')
        if v0.get() == 2:                                               #for static searching only: decrement page_count by 1 for each page
            page_count -= 1                                             #as we want to scrape only 3 pages
            if page_count == 0:                                         #break after scrapping 3 pages
                break
        for card in cards:
            record = get_record(card)                                   #main function that will scrape data from indeed.com
            records.append(record)
        try:
            url = 'https://www.indeed.com' + soup.find('a', {'aria-label': 'Next'}).get('href')
        except AttributeError:                                          #Exception handling
            break
    return pd.DataFrame(records,
                        columns=['Title', 'Company', 'Location', 'Summary', 'Salary', 'Post_Date', 'Extract_Date'])


def get_record(card):
    title = card.find('h2', {"class": "jobTitle"}).text                         #code to find "title" of the job
    try:
        company = card.find('span', {"class": "companyName"}).text              #code to find "company" of the job
    except:
        company = -1
    try:
        location = card.find('div', {"class": "companyLocation"}).text          #code to find "location" of the job
    except:
        location = -1
    try:
        summary = card.find('div', {"class": "job-snippet"}).text               #code to find "summary" of the job
    except:
        summary = -1
    try:
        salary = card.find('div', {"class": "attribute_snippet"}).text          #code to find "salary" of the job
    except AttributeError:
        salary = ''
    posting = card.find('span', {"class": "date"}).text                         #code to find "posting date" of the job
    today = datetime.today().strftime('%Y-%m-%d')
    record = (title, company, location, summary, salary, posting, today)
    print("Job Title: {}".format(title))
    print("Salary Estimate: {}".format(salary))
    print("Company Name: {}".format(company))
    print("Location: {}".format(location))
    print("Summary: {}".format(summary))
    print("@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@")
    return record


######################################################################################################################
##################################CAREERBUILDER.COM USING BEAUTIFUL SOUP##############################################
######################################################################################################################


# generating url from position
def get_url1(position):
    template = 'https://www.careerbuilder.com/jobs?keywords={}'
    url = template.format(position)

    return url


# extracting job data from a single record
def get_record1(card):
    atag = card.a
    job_title = atag.get('aria-label')
    print(job_title)
    job_url = 'https://www.careerbuilder.com/' + atag.get('href')
    data = card.find('div', {'class': 'data-details'})
    spans = data.find_all('span')
    company = spans[0].text.strip()
    location = spans[1].text.strip()

    try:
        job_payment = card.findAll('div', {'class': 'block'})
        job_salary = job_payment[1].text.strip()
    except AttributeError:
        job_salary = ''
    date = card.find('div', {'class': 'data-results-publish-time'}).text.strip()

    record = (job_title, job_url, company, job_salary, date)
    print(job_salary)

    return record


def get_careerbuilder_jobs(position):
    records = []
    url = get_url1(position)
    print(url)

    # extracting job data
    while True:
        response = requests.get(url)
        print(response)
        bsobj = BeautifulSoup(response.text, 'html.parser')
        cards = bsobj.find_all('li', {'class': 'data-results-content-parent relative'})

        for card in cards:
            record = get_record1(card)
            records.append(record)

        break


########################################################################################################################
##################################GLASSDOOR.COM USING SELENIUM##########################################################
########################################################################################################################

#This function is used for scrapping data from Glassdoor.com using selenium
#It will open the chrome page with glassdoor url with the job profile searched by the user
#and will automatically start scrapping after waiting for 5 seconds
#Dynamic search option from user will scrape entire data (30 pages approx, 900 jobs) taking approximately 15-20 mins
#Static search option from user will stop the search after scrapping 2 pages
def get_Glassdoor_jobs(keyword):
    options = webdriver.ChromeOptions()
    chrome_path = r'./chromedriver'                                                 #path containing chrome driver used for selenium
    driver = webdriver.Chrome(executable_path=chrome_path,                          #execute chrome driver
                              options=options)
    driver.set_window_size(1120, 1000)                                              #set window size of chrome driver
    # print(v0.get())
    url = "https://www.glassdoor.com/Job/jobs.htm?sc.keyword=" + keyword            #glassdoor url with keyword cntaining the job_profile searched by user
    driver.get(url)
    # print(url)
    jobs = []
    isfirstTime = True
    if v0.get() == 1:                                                               #If Dynamic search will scrape all pages
        page_count = 30
    else:                                                                           #If Static search wll scrape only 2 pages
        page_count = 2
    while True:
        if page_count == 0:
            break
        job_buttons = driver.find_elements_by_class_name('react-job-listing')
        page_count = page_count - 1                                                 #Decrement page_count with each page to keep track of pages scrapped
        i = 0
        for job_button in job_buttons:
            try:
                job_button.click()
                time.sleep(1)
                collected_successfully = False
            except:
                continue
                # print('test')

            if isfirstTime:
                try:
                    time.sleep(5)
                    # driver.find_element_by_xpath( '//*[@id="JAModal"]/div/div[2]/span/svg').click()
                    driver.find_element_by_css_selector('[alt="Close"]').click()
                    time.sleep(1)
                    print(' x out worked')
                except:
                    print(' x out not worked')
            i += 1

            while not collected_successfully:
                try:
                    # print('test2')
                    companyurl = '//*[@id="MainCol"]/div[1]/ul/li[{}]/div[2]/div[1]/a/span'
                    joburl = '//*[@id="MainCol"]/div[1]/ul/li[{}]/div[2]/a/span'
                    locationurl = '//*[@id="MainCol"]/div[1]/ul/li[{}]/div[2]/div[2]/span'
                    updatedcomp_url = companyurl.format(i)
                    updatedjob_url = joburl.format(i)
                    updatedloc_url = locationurl.format(i)
                    company_name = driver.find_element_by_xpath(updatedcomp_url).text
                    location = driver.find_element_by_xpath(updatedloc_url).text
                    job_title = driver.find_element_by_xpath(updatedjob_url).text
                    collected_successfully = True
                # print(location)
                # print(job_title)
                # print(company_name)
                except:
                    # print('test3')
                    time.sleep(5)

            try:
                salaryurl = '//*[@id="MainCol"]/div[1]/ul/li[{}]/div[2]/div[3]/div[1]/span'
                updatedsalary_url = salaryurl.format(i)
                salary_estimate = driver.find_element_by_xpath(updatedsalary_url).text
            except NoSuchElementException:
                salary_estimate = -1

            # print(salary_estimate)

            try:
                ratingurl = '//*[@id="MainCol"]/div[1]/ul/li[{}]/div[1]/span'
                updatedrating_url = ratingurl.format(i)
                rating = driver.find_element_by_xpath(updatedrating_url).text
            except:
                rating = -1

            # print(rating)

            print("Job Title: {}".format(job_title))
            print("Salary Estimate: {}".format(salary_estimate))
            print("Rating: {}".format(rating))
            print("Company Name: {}".format(company_name))
            print("Location: {}".format(location))

            try:
                if isfirstTime:
                    time.sleep(5)
                    isfirstTime = False
                    time.sleep(1)
                    driver.find_element_by_xpath('//*[@id="SerpFixedHeader"]/div/div/div[3]').click()

                try:
                    size = driver.find_element_by_xpath('//*[@id="EmpBasicInfo"]/div[1]/div/div[1]/span[2]').text
                except:
                    size = -1
                try:
                    founded = driver.find_element_by_xpath('//*[@id="EmpBasicInfo"]/div[1]/div/div[2]/span[2]').text
                except:
                    founded = -1
                try:
                    industry = driver.find_element_by_xpath('//*[@id="EmpBasicInfo"]/div[1]/div/div[4]/span[2]').text
                except:
                    industry = -1
                try:
                    sector = driver.find_element_by_xpath('//*[@id="EmpBasicInfo"]/div[1]/div/div[5]/span[2]').text
                except:
                    sector = -1
                try:
                    revenue = driver.find_element_by_xpath('//*[@id="EmpBasicInfo"]/div[1]/div/div[6]/span[2]').text
                except:
                    revenue = -1
                try:
                    type_of_ownership = driver.find_element_by_xpath(
                            '//*[@id="EmpBasicInfo"]/div[1]/div/div[3]/span[2]').text
                except:
                    type_of_ownership = -1
            except NoSuchElementException:
                size = -1
                founded = -1
                industry = -1
                sector = -1
                revenue = -1
                type_of_ownership = -1

            print("Size: {}".format(size))
            print("Founded: {}".format(founded))
            print("Type of Ownership: {}".format(type_of_ownership))
            print("Industry: {}".format(industry))
            print("Sector: {}".format(sector))
            print("Revenue: {}".format(revenue))
            print("@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@")

            jobs.append({"job_title": job_title,
                         "salary_estimate": salary_estimate,
                         "Rating": rating,
                         "company_name": company_name,
                         "Location": location,
                         "Size": size,
                         "founded": founded,
                         "industry": industry,
                         "sector": sector,
                         "revenue": revenue,
                         "type_of_ownership": type_of_ownership})
        try:
            driver.find_element_by_xpath('//*[@id="FooterPageNav"]/div/ul/li[7]/a').click()
            time.sleep(5)
        except NoSuchElementException:
            print("Scraping terminated")
            break
    # print(jobs)
    return pd.DataFrame(jobs).reset_index()


########################################################################################################################
###################################PLOTTING GRAPHS#####################################################################
########################################################################################################################
import re

def plots(keyword):
    # job_profile='analyst'
    # print(keyword)
    # performing analysis on glassdoor data
    if re.search('data', keyword):
        df1 = pd.read_csv('./Uncleaned_DS_jobs.csv')
    elif re.search('software', keyword):
        df1 = pd.read_csv('./Uncleaned_se_jobs.csv')
    elif re.search('analyst', keyword):
        df1 = pd.read_csv('./Uncleaned_analyst_jobs.csv')
    #performing cleaning on the raw scraped data
    df1[["City", "State"]] = df1.Location.str.split(',', 1, expand=True)

    df1 = df1[df1 != '-1']
    df1['min_salary'], df1['max_salary'] = df1['salary_estimate'].str.split('-').str
    df1 = df1.dropna()

    df1['Min_salary1'] = df1['min_salary'].str[1:3]
    df1['Max_salary1'] = df1['max_salary'].str[2:5]

    df1['Max_salary1'] = df1['Max_salary1'].map(lambda x: x.rstrip('K'))
    df1['Min_salary1'] = df1['Min_salary1'].map(lambda x: x.rstrip('K'))

    df1['Average_salary'] = df1[['Min_salary1', 'Max_salary1']].astype(float).mean(axis=1)

    # print(df1)
    # plot chloropleth chart of no of jobs by state
    df2 = df1.groupby(["State"])["index"].count().reset_index(name="Num_jobs")
    df2['Statev2'] = df2['State'].str[-2:]
    # print(df2)
    fig = px.choropleth(df2,
                        locations='Statev2',
                        color='Num_jobs',
                        color_continuous_scale='spectral_r',
                        hover_name='Num_jobs',
                        locationmode='USA-states',
                        scope='usa')
    fig.show()

    # plotting average salary histogram
    df1.Average_salary.hist()
    plt.title('Average salary distribution')
    plt.xlabel('Salary')
    plt.tight_layout()

    # plotting rating histogram
    rat = df1['Rating'][df1['Rating'] != -1]
    rat.hist()
    print('The number that appears the most:', '\n', stats.mode(rat))
    plt.xlabel('Rating')
    plt.title('Company rating distribution')
    plt.tight_layout()

    # plotting average salary by state
    blank_remove_st = df1[df1['State'] != 'blank']
    grouped_sal_st = blank_remove_st.groupby('State')['Average_salary'].mean().sort_values(ascending=False)
    print("The most paid jobs are in", grouped_sal_st.index[0], "Average salary:", grouped_sal_st[0])
    print("The worst paid jobs are in", grouped_sal_st.index[-1], "Average salary:", grouped_sal_st[-1])
    plt.figure(figsize=(16, 6))
    plt.title('Average salary by state')
    chart = sns.barplot(x=grouped_sal_st.index, y=grouped_sal_st)
    plt.show()

    # plotting average salary box plot
    df1.boxplot(column=['Average_salary']).set(xticklabels=[])
    plt.ylabel('Salary')
    plt.title('Average salary')
    plt.tight_layout()
    plt.show()

    # plotting average salary by different company ratings
    rat = df1['Rating'][df1['Rating'] != -1]
    group_names = ['Bad', 'Poor', 'OK', 'Good', 'Very good', 'Excellent ']
    start = rat.min()
    stop = rat.max()
    bins = np.linspace(start, stop, num=7)
    df1['company_rating'] = pd.cut(rat, bins, labels=group_names)
    ndf = df1.groupby('company_rating', as_index=False)['Average_salary'].mean()
    plt.figure(figsize=(7, 6))
    plt.title('Average salary with different company ratings')
    chart = sns.barplot(x=ndf['company_rating'], y=ndf['Average_salary'])
    plt.show()

    # plotting jobs by industry
    df2 = df1[df1['industry'] != '-1']
    fig, ax = plt.subplots(figsize=(10, 10))
    chart = sns.barplot(x=df2.industry.value_counts().index, y=df2.industry.value_counts())
    _ = chart.set_xticklabels(chart.get_xticklabels(), rotation=90)
    plt.savefig('Job industry count.png')
    plt.show()

    # plotting jobs by sector
    df2 = df1[df1['sector'] != '-1']
    fig, ax = plt.subplots(figsize=(10, 10))
    chart = sns.barplot(x=df2.sector.value_counts().index, y=df2.sector.value_counts())
    _ = chart.set_xticklabels(chart.get_xticklabels(), rotation=90)
    plt.savefig('Job Sector count.png')
    plt.show()

    ##########################RECOMMENDATIONS############################################################
    ###########################################################################################

    glassdoor = pd.read_csv('./Indeed_jobs.csv')

    indeed = pd.read_csv('./Glassdoor_jobs.csv')
    df1 = pd.concat([glassdoor, indeed], axis=0)
    df1 = df1[df1['job_title'].notna()]
    # print(df1)

    df1['salary_estimate'] = df1['salary_estimate'].str.replace('From ', '')

    df1['salary_estimate'] = df1['salary_estimate'].str.replace('Up to ', '')

    # df1 = df1.drop(df1[df1.salary_estimate.str.contains('Part')].index)

    # df1 = df1.drop(df1[df1.salary_estimate.str.contains('an hour')].index)
    # df1 = df1.drop(df1[df1.salary_estimate.str.contains('a day')].index)
    # df1 = df1.drop(df1[df1.salary_estimate.str.contains('month')].index)

    df1['min_salary'], df1['max_salary'] = df1['salary_estimate'].str.split('-').str

    df1 = df1[df1['max_salary'].notna()]

    df1['Min_salary1'] = df1['min_salary'].str[1:4]
    df1['Max_salary1'] = df1['max_salary'].str[2:5]

    df2 = df1[df1.Min_salary1 != '']
    df2 = df2[df2.Max_salary1 != '']

    # print(df2)

    df2['Max_salary1'] = df2['Max_salary1'].map(lambda x: x.rstrip('K'))

    df2['Min_salary1'] = df2['Min_salary1'].map(lambda x: x.rstrip('K'))

    df2['Average_salary'] = df2[['Min_salary1', 'Max_salary1']].astype(float).mean(axis=1)

    # print(df2)

    df2 = df2.drop_duplicates()
    # print(df2)

    df3 = df2.sort_values('Average_salary', ascending=False)
    df4 = df3.head(30)

    # df5=df4[['job_title','company_name','Location','Average_salary']]
    df5 = df4[['job_title', 'company_name', 'Average_salary']]
    # print(df5)

    keys = ['job_title', 'company_name', 'Average_salary']

    print("\n\n\n\n")
    print("******* Our Top Job Recommendations based on your search*******")
    print(tabulate(df5, headers='keys', tablefmt='psql'))


########################################################################################################################
######################################BASIC GUI USING TKINTER FOR TAKING USER INPUT#####################################
########################################################################################################################
job_profile = ""
def show_entry_fields():                                                           #Function called when user click "Start Scrapping" button
    print("Job Profile: %s\n" % (e1.get()))
    job_profile = e1.get()                                                         #Job_profile contains position searched by user
    df3 = get_Indeed_Jobs(job_profile)                                             #function to scrape jobs from indeed.com
    df3.to_csv('./Indeed_jobs.csv', index=False)                                   #writing scrapped data from indeed.com into csv
    df4 = get_Glassdoor_jobs(job_profile)                                          #function to scrape data from Glassdoor.com using selenium
    df4.to_csv('./Glassdoor_jobs.csv', index=False)                                #writing scrapped data from glassdoor.com into csv
    # df3=get_careerbuilder_jobs(job_profile)
    # df3.to_csv('C:/Users/soodp/Documents/Python Project/careerbuilder_jobs.csv', index=False)
    e1.delete(0, tk.END)

def show_graphs():                                                                 #function called when user clicks "show graphs" button
    job_profile = e1.get()
    plots(job_profile)                                                             #Function to display graph and maps with the data scrapped from indeed,glassdoor and careerbuilder
master = tk.Tk()
Console = Text(master)
Console.pack()
Label(master, text="Job Profile").place(x=40, y=40)                                #code to set position and text of search button
e1 = tk.Entry(master)
e1.place(x=150, y=40)
master.title("The Job Scrapper")                                                   #Code to Set the title of the APP: "The Job Scrapper"
master.geometry("400x400+550+300")                                                 #Code to set te window size of the application gui

def msg():                                                                         #function to display pop-up warning when user select dynamic search option
    messagebox.showwarning("Warning", "dynamic scrapping will take 20 mins")


v0 = tk.IntVar()
r1 = tk.Radiobutton(master, text="Dynamic", variable=v0, value=1, command=msg)      # Radiobutton for Dynamic searching
r1.place(x=80, y=120)                                                               # Code to set Dynamic search button position on gui
r2 = tk.Radiobutton(master, text="Static", variable=v0, value=2)                    # Radiobutton for Static searching
r2.place(x=180, y=120)                                                              #Code to set Static search button position on gui

tk.Button(master,                                                                   #End Button to quit the application
          text='End',
          command=master.quit).place(x=140, y=280)
tk.Button(master,                                                                   #Show Graph button to display graphs
          text='Show Graphs',
          command=show_graphs).place(x=70, y=200)

tk.Button(master, text='Start Scrapping', command=show_entry_fields).place(x=170, y=200)        #Start Scrapping button

master.mainloop()
tk.mainloop()

#####################################END################################################################################
