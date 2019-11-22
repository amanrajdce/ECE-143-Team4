#!/usr/bin/env python
# coding: utf-8
# updated docstrings
# In[88]:


import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import math
import re
import seaborn as sns
from scipy import stats
import sys
import matplotlib as mpl
salary_data = pd.read_csv('./Scraper/SalaryScraper/fulltime_merged_salaries_company_table.csv')
salary_data_int = pd.read_csv('./Scraper/SalaryScraper/intern_merged_salaries_company_table.csv')


# ## 1.1 What kind of jobs can get the highest salary in the current days?
# #### salary range for categories

# In[89]:


def salary_of_category(d):
    '''
    for all non-0 input
    return range of this category as DataFrame
    parameter type: pd.DataFrame
    '''
    assert isinstance(d, pd.DataFrame)
    salary = d[d.salary_range.notnull()]['salary_range']
    s = salary.str.replace('K', '').str.replace('$', '').str.replace('€', '').str.replace('£', '').str.replace("Range: ", '')
    s = s.apply(lambda x: pd.Series(x.split(' - '))) 
    s = s.astype('int')
    return s


# In[90]:


def average_fulltime_by_category(data):
    '''
    compute the average range of salary per category
    return several DataFrames, each containing the series of the upper and lower range of a category
    parameter type: pd.DataFrame
    '''
    assert isinstance(data, pd.DataFrame)
    # group all category
    groups = data.groupby('category')
    eng = groups.get_group('engineering')
    it = groups.get_group('it')
    managerial = groups.get_group('managerial')
    marketing = groups.get_group('marketing')
    others = groups.get_group('others')
    sales = groups.get_group('sales')
    
    # Data frame of low / high salary
    ave_eng = (salary_of_category(eng))
    ave_it  = (salary_of_category(it))
    ave_managerial  = (salary_of_category(managerial))
    ave_marketing  = (salary_of_category(marketing))
    ave_others  = (salary_of_category(others))
    ave_sales  = (salary_of_category(sales))
    
    return ave_eng,ave_it,ave_managerial,ave_marketing,ave_others,ave_sales


# In[91]:


def salary_by_category(data):
    '''
    compute the average range of salary per category
    return several DataFrames, each containing the upper and lower range of a category (only two numbers)
    parameter type: pd.DataFrame
    '''
    assert isinstance(data, pd.DataFrame)
    # Data frame of low / high salary
    ave_eng,ave_it,ave_managerial,ave_marketing,ave_others,ave_sales = average_fulltime_by_category(data)
    
    # low / high average
    salary_eng = ave_eng.sum()/len(ave_eng)
    salary_it  = ave_it.sum()/len(ave_it)
    salary_mana  = ave_managerial.sum()/len(ave_managerial)
    salary_mk  = ave_marketing.sum()/len(ave_marketing)
    salary_others = ave_others.sum()/len(ave_others)
    salary_sales = ave_sales.sum()/len(ave_sales)
    
    return salary_eng, salary_it, salary_mana, salary_mk, salary_others, salary_sales


# In[92]:


def bar_group(file_name, x, y, title, size, classes, values, width=0.8):
    '''
    plot bar chart of category analysis. 
    file_name type: str
    x type: str
    y type: str
    title type: str
    size type: tuple
    classes type: list
    values type: list
    width type: float
    '''
    assert isinstance(file_name, str)
    assert isinstance(x ,str) and isinstance(y ,str) and isinstance(title ,str)
    assert isinstance(size, tuple)
    assert isinstance(classes, list)
    assert isinstance(values, list)
    assert isinstance(width, float)
    
    fig, ax = plt.subplots(figsize=size)
    plt.xlabel(x, fontsize = 12)
    plt.ylabel(y, fontsize = 12)
    total_data = len(values)
    classes_num = np.arange(len(classes))
    for i in range(total_data):
        bars = plt.bar(classes_num - width / 2. + i / total_data * width, values[i], 
                width=width / total_data, align="edge", animated=0.4)
        for rect in bars:
            height = rect.get_height()
            plt.text(rect.get_x() + rect.get_width()/2.0, height, '%d' % int(height), ha='center', va='bottom')
    plt.xticks(classes_num, classes, rotation=20, size=13)
    plt.title(title,fontsize=14)
    plt.legend(['Average high salary', 'Average low salary'], fontsize = 9)
    #fig.savefig(file_name, format='png', dpi=300)


# In[93]:


def plot_average_fulltime_by_category(data):
    '''
    plot bar chart of fulltime salary among category analysis.
    parameter type: pd.DataFrame
    '''
    assert isinstance(data, pd.DataFrame)
    
    mpl.rcParams['axes.prop_cycle'] = mpl.cycler(color=["lightblue", "gold"])
    salary_eng, salary_it, salary_mana, salary_mk, salary_others, salary_sales = salary_by_category(data)
    num_list2 = [salary_eng[0],salary_it[0],salary_mana[0],salary_mk[0],salary_others[0],salary_sales[0]]
    num_list1 = [salary_eng[1],salary_it[1],salary_mana[1],salary_mk[1],salary_others[1],salary_sales[1]]
    group = ['Engineering','IT','Managerial','Marketing', 'Sales', 'Others']
    bar_group('./graphs/a1_q1_2.png', 'Category of job', 'Average salary k/yr','Average salary range of fulltime jobs among categories',(8,5), group, [num_list1, num_list2])
    plt.show()


# ### 1.2 The distribution of salary in each category

# In[95]:


def plot_distribution_category(data):
    '''
    plot the distribution graph of each category
    one lower limit, the other the upper limit
    parameter type: pd.DataFrame
    '''
    assert isinstance(data, pd.DataFrame)
    
    # Data frame of low / high salary
    ave_eng,ave_it,ave_managerial,ave_marketing,ave_others,ave_sales = average_fulltime_by_category(data)
    # 1, 2
    f1, (ax1, ax2) = plt.subplots(2, 1, sharex=True, figsize=(8, 8))
    c1, c2, c3 = sns.color_palette('Set1', 3)
    sns.kdeplot(ave_eng[0], label = 'average low salary', shade=True, color=c2, ax=ax1).set_title('Engineering salary distribution', fontsize = 12, color = 'Green')
    ax1.set_xlabel('Salary per year', fontsize=10)
    ax1.set_ylabel('Percentage', fontsize=10)
    vals1 = ax1.get_yticks()
    ax1.set_yticklabels(['{:,.2%}'.format(x) for x in vals1])

    sns.kdeplot(ave_eng[1], label = 'average high salary',shade=True, color=c3, ax=ax1)
    sns.kdeplot(ave_it[0], label = 'average low salary', shade=True, color=c2, ax=ax2).set_title('IT salary distribution', fontsize = 12, color = 'Green')
    ax2.set_xlabel('Salary per year', fontsize=10)
    ax2.set_ylabel('Percentage', fontsize=10)
    vals2 = ax2.get_yticks()
    ax2.set_yticklabels(['{:,.2%}'.format(x) for x in vals2])
    sns.kdeplot(ave_it[1], label = 'average high salary',shade=True, color=c3, ax=ax2)
    f1.savefig('./graphs/a2_q1.png', format='png', dpi=300)
    
    # 3, 4
    f2, (ax3, ax4) = plt.subplots(2, 1, sharex=True, figsize=(8, 8))
    sns.kdeplot(ave_managerial[0], label = 'average low salary', shade=True, color=c2, ax=ax3).set_title('Managerial salary distribution', fontsize=12, color = 'Green')
    ax3.set_xlabel('Salary per year', fontsize=10)
    ax3.set_ylabel('Percentage', fontsize=10)
    vals3 = ax3.get_yticks()
    ax3.set_yticklabels(['{:,.2%}'.format(x) for x in vals3])

    sns.kdeplot(ave_managerial[1], label = 'average high salary',shade=True, color=c3, ax=ax3)
    sns.kdeplot(ave_marketing[0], label = 'average low salary', shade=True, color=c2, ax=ax4).set_title('Marketing salary distribution', fontsize=12, color = 'Green')
    sns.kdeplot(ave_marketing[1], label = 'average high salary',shade=True, color=c3, ax=ax4)
    ax4.set_xlabel('Salary per year', fontsize=10)
    ax4.set_ylabel('Percentage', fontsize=10)
    vals4 = ax4.get_yticks()
    ax4.set_yticklabels(['{:,.2%}'.format(x) for x in vals4])
    f2.savefig('./graphs/a3_q1.png', format='png', dpi=300)
    
    # 5, 6
    f, (ax5, ax6) = plt.subplots(2, 1, sharex=True, figsize=(8, 8))
    sns.kdeplot(ave_sales[0], label = 'average low salary', shade=True, color=c2, ax=ax5).set_title('Sales salary distribution', fontsize=12, color = 'Green')
    ax5.set_xlabel('Salary per year', fontsize=10)
    ax5.set_ylabel('Percentage', fontsize=10)
    vals5 = ax5.get_yticks()
    ax5.set_yticklabels(['{:,.2%}'.format(x) for x in vals5])

    sns.kdeplot(ave_sales[1], label = 'average high salary',shade=True, color=c3, ax=ax5)
    sns.kdeplot(ave_others[0], label = 'average low salary', shade=True, color=c2, ax=ax6).set_title('Other categories salary distribution', fontsize=12, color = 'Green')
    ax6.set_xlabel('Salary per year', fontsize=10)
    ax6.set_ylabel('Percentage', fontsize=10)
    vals6 = ax6.get_yticks()
    ax6.set_yticklabels(['{:,.2%}'.format(x) for x in vals6])
    sns.kdeplot(ave_others[1], label = 'average high salary',shade=True, color=c3, ax=ax6)
    f.savefig('./graphs/a4_q1.png', format='png', dpi=300)


# ### 1.3 What kind of interns get paid more?

# In[97]:


def plot_average_intern_by_category(data):
    '''
    plot bar chart of fulltime salary among category analysis.
    parameter type: pd.DataFrame
    '''
    assert isinstance(data, pd.DataFrame)
    mpl.rcParams['axes.prop_cycle'] = mpl.cycler(color=["lightblue", "gold"])
    salary_eng, salary_it, salary_mana, salary_mk, salary_others, salary_sales = salary_by_category(data)
    num_list2 = [salary_eng[0],salary_it[0],salary_mana[0],salary_mk[0],salary_others[0],salary_sales[0]]
    num_list1 = [salary_eng[1],salary_it[1],salary_mana[1],salary_mk[1],salary_others[1],salary_sales[1]]
    group = ['Engineering','IT','Managerial','Marketing', 'Sales', 'Others']
    bar_group('./graphs/a1_q1_2.png', 'Category of job', 'Average salary k/yr','Average salary range of intern jobs among categories',(8,5), group, [num_list1, num_list2])
    plt.show()


# ## 2. Which company pays more?
# ### 2.1 Fulltime jobs. 

# In[99]:


def salary_of_company(d):
    '''
    for all non-0 input
    return range of a certain company
    parameter type: pd.DataFrame
    '''
    assert isinstance(d, pd.DataFrame)
    
    salary = d[d.salary_range.notnull()]['salary_range']
    s = salary.str.replace('K', '').str.replace('$', '').str.replace('€', '').str.replace('£', '').str.replace("Range: ", '')
    s = s.apply(lambda x: pd.Series(x.split(' - '))) 
    s = s.astype('int')
    ave = s.sum()/len(s)
    return s, ave


# In[100]:


def bar_group_2(file_name, x, y, title, size, classes, values, width=0.8):
    '''
    basic plotting function for company-wise analysis
    file_name type: str
    x type: str
    y type: str
    title type: str
    size type: tuple
    classes type: list
    values type: list
    width type: float
    '''
    assert isinstance(file_name, str)
    assert isinstance(x ,str) and isinstance(y ,str) and isinstance(title ,str)
    assert isinstance(size, tuple)
    assert isinstance(classes, list)
    assert isinstance(values, list)
    assert isinstance(width, float)
    
    fig, ax = plt.subplots(figsize=size)
    plt.xlabel(x, fontsize = 20)
    plt.ylabel(y, fontsize = 20)
    total_data = len(values)
    classes_num = np.arange(len(classes))
    for i in range(total_data):
        bars = plt.bar(classes_num - width / 2. + i / total_data * width, values[i], 
                width=width / total_data, align="edge", animated=0.4)
        for rect in bars:
            height = rect.get_height()
            plt.text(rect.get_x() + rect.get_width()/2.0, height, '%d' % int(height), ha='center', va='bottom')
    plt.xticks(classes_num, classes, rotation=25, size=15)
    plt.title(title,fontsize=35)
    plt.legend(['Average high salary', 'Average low salary'], fontsize = 15)
    fig.savefig(file_name, format='png', dpi=300)


# In[101]:


def average_salary_company(data):
    '''
    compute the average lower and upper range of a company's salary    
    parameter type: pd.DataFrame
    '''
    assert isinstance(data, pd.DataFrame)
    
    groups_company = data.groupby('company')
    company_names = (list(groups_company.groups.keys()))
    num_companies = len(company_names)

    # compute the average range
    average = []
    salary_of_companies = []
    for i in range (num_companies):
        company = company_names[i]
        com = groups_company.get_group(company)
        s, ave = salary_of_company(com)
        salary_of_companies.append(s)
        average.append(ave)

    # sort the outcome
    outcome = zip(company_names, salary_of_companies, average)
    outcome = (list(outcome))
    outcome = sorted(outcome, key = lambda x: x[2][1], reverse = True)
    
    name_list = []
    num_list1 = []
    num_list2 = []
    for j in range (num_companies):
        name_list.append(outcome[j][0])
        num_list2.append(outcome[j][2][0])
        num_list1.append(outcome[j][2][1])
    # capitalize the companies' names  
    name_list = [c.title() for c in name_list]
    name_list = [c.upper() if c == "Ibm" or c == "Hp" else c for c in name_list]
    
    return name_list, num_list1, num_list2


# In[102]:


def plot_average_fulltime_salary_company(data):
    '''
    plot the average range of a company's salary
    parameter type: pd.DataFrame
    '''
    assert isinstance(data, pd.DataFrame)
    
    name_list, num_list1, num_list2 = average_salary_company(data)
    mpl.rcParams['axes.prop_cycle'] = mpl.cycler(color=["lightblue", "gold"])
    bar_group_2('./graphs/a1_q7_2.png', 'Company', 'Average salary k/yr','Average salary range of fulltime jobs among company',(18,10), name_list, [num_list1, num_list2])
    plt.show()


# ### 2.2 Which company pays more to intern jobs?

# In[104]:


def salary_of_company_int(d):
    '''
    for all non-0 input
    return range of a certain company
    distinguish hourly and yearly income
    using different function because the data in int_file are a bit different
    parameter type: pd.DataFrame
    '''
    assert isinstance(d, pd.DataFrame)
    
    salary = d[d.salary_range.notnull()]['salary_range']
    s = salary.str.replace('$', '').str.replace('€', '').str.replace('£', '').str.replace("Range: ", '').str.replace(" ", '').str.replace(" ", '')
    for j in s.index:
        line = s[j]
        i = line.split('-')
        if "K" in i[0]:
            i[0]=i[0].replace('K', '')
            i[0]=str(int(i[0])*1000/365/8)
            i[1]=i[1].replace('K', '')
            i[1]=str(int(i[1])*1000/365/8)
            ii = "-".join(i)
        ii = "-".join(i)
        s[j] = ii
    s = s.apply(lambda x: pd.Series(x.split('-'))) 
    s = s.astype('float')
    ave = s.sum()/len(s)
    return s, ave


# In[105]:


def average_salary_company_int(data):
    '''
    compute the average lower and upper range of a company's salary    
    parameter type: pd.DataFrame
    '''
    assert isinstance(data, pd.DataFrame)
    
    groups_company = data.groupby('company')
    company_names = (list(groups_company.groups.keys()))
    num_companies = len(company_names)

    # compute the average range
    average = []
    salary_of_companies = []
    for i in range (num_companies):
        company = company_names[i]
        com = groups_company.get_group(company)
        s, ave = salary_of_company_int(com)
        salary_of_companies.append(s)
        average.append(ave)

    # sort the outcome
    outcome = zip(company_names, salary_of_companies, average)
    outcome = (list(outcome))
    outcome = sorted(outcome, key = lambda x: x[2][1], reverse = True)
    
    name_list = []
    num_list1 = []
    num_list2 = []
    for j in range (num_companies):
        name_list.append(outcome[j][0])
        num_list2.append(outcome[j][2][0])
        num_list1.append(outcome[j][2][1])
    # capitalize the companies' names  
    name_list = [c.title() for c in name_list]
    name_list = [c.upper() if c == "Ibm" or c == "Hp" else c for c in name_list]
    
    return name_list, num_list1, num_list2


# In[106]:


def plot_average_intern_salary_company(data):
    '''
    plot the average range of a company's salary
    parameter type: pd.DataFrame
    '''
    assert isinstance(data, pd.DataFrame)
    
    name_list, num_list1, num_list2 = average_salary_company_int(data)
    mpl.rcParams['axes.prop_cycle'] = mpl.cycler(color=["lightblue", "gold"])
    bar_group_2('./graphs/a1_q7_2.png', 'Company', 'Average salary k/yr','Average salary range of intern among company',(18,10), name_list, [num_list1, num_list2])
    plt.show()


# ## 2. What is the distribution of job opportunities among different categories?

# In[108]:


def num_of_jobs_category(data):
    '''
    compute number of unique job titles in all categories
    parameter type: pd.DataFrame
    '''
    assert isinstance(data, pd.DataFrame)
    
    names = []
    num = []
    for category in data.groupby('category').groups:
        n = data.groupby('category').get_group(category)
        names.append(category)
        num.append(len(n.groupby('job_title').groups))
    outcome = zip(names, num)
    outcome = (list(outcome))
    outcome = sorted(outcome, key = lambda x: x[1], reverse = True)
    lengths = pd.DataFrame(data = outcome, columns = ['category','number'])
    return lengths


# In[109]:


def bar_group_3(file_name, x, y, title, size, classes, values, width=0.4):
    '''
    basic plotting function for job opportunity analysis
    file_name type: str
    x type: str
    y type: str
    title type: str
    size type: tuple
    classes type: list
    values type: list
    width type: float
    '''
    assert isinstance(file_name, str)
    assert isinstance(x ,str) and isinstance(y ,str) and isinstance(title ,str)
    assert isinstance(size, tuple)
    assert isinstance(classes, list)
    assert isinstance(values, list)
    assert isinstance(width, float)
    
    fig, ax = plt.subplots(figsize=size)
    plt.xlabel(x, fontsize = 12)
    plt.ylabel(y, fontsize = 12)
    total_data = len(values)
    classes_num = np.arange(len(classes))
    for i in range(total_data):
        bars = plt.bar(classes_num - width / 2. + i / total_data * width, values[i], 
                width=width / total_data, align="edge", animated=0.4)
        for rect in bars:
            height = rect.get_height()
            plt.text(rect.get_x() + rect.get_width()/2.0, height, '%d' % int(height), ha='center', va='bottom')
    plt.xticks(classes_num, classes, rotation=20, size=13)
    plt.title(title,fontsize=14)
    #plt.legend(['Average high', 'Average low'], fontsize = 9)
    fig.savefig(file_name, format='png', dpi=300)


# In[110]:


def plot_num_of_jobs_category(data):
    '''
    plot a bar chart illustrating the number of different job titles in categories
    parameter type: pd.DataFrame
    '''
    assert isinstance(data, pd.DataFrame)
    
    numbers = num_of_jobs_category(data)
    mpl.rcParams['axes.prop_cycle'] = mpl.cycler(color=["green"])
    names = ['Others', 'Engineering', 'Managerial', 'Sales', 'Marketing', "IT"]
    bar_group_3('./graphs/a1_q3_2.png','Category of job', 'Number of unique job titles', 'Distribution of job opportunities among categories',(8, 5), names, [numbers['number']])
    plt.show()


# In[ ]:




