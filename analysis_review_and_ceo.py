"""
This part of script does analysis on review table and
ceto rating table.
"""
import pandas as pd
import numpy as np
import string
import matplotlib.pyplot as plt
from utils import abbrev_us_state

review_table = './Scraper/ReviewScraper/merged_reviews_table.csv'
ceo_table = './Scraper/ReviewScraper/ceo_ratings.csv'

def compute_most_job_by_city(jobs, top=10):
    """
    """
    jobs = jobs[pd.notnull(jobs['location'])]
    jobs['city'] = jobs['location'].apply(lambda x: x.split(", ")[0].lower())
    gb = jobs.groupby('city')

    city_num = dict(gb.size())
    num_city = sorted([(v, k) for k,v in city_num.items()], key=lambda x: x[0], reverse=True)[:top]
    count = [x[0] for x in num_city]
    cities = [x[1].title().replace(" ", "\n") for x in num_city]

    return count, cities

def city_most_jobs(review_table, savefig=False):
    """
    Return the graph with which city in US offers most job.
    """
    review_table = pd.read_csv(review_table)
    city_count, cities = compute_most_job_by_city(review_table.copy())

    fig, ax = plt.subplots(1, 1, figsize=(18, 10))
    ax.bar(cities, city_count, facecolor="green", width=0.5)
    #ax.set_xlabel('Cities', fontsize=20)
    ax.set_ylabel('Number of jobs', fontsize=25)
    ax.set_title('Which city in the US offers the most job opportunities? (2017-2019)', fontsize=25)
    ax.tick_params(labelsize=20)
    if savefig:
        fig.savefig('./graphs/a1_q2a.png', format='png', dpi=300)


def compute_most_job_by_state(jobs, top=10):
    """
    """
    jobs = jobs[pd.notnull(jobs['location'])]
    jobs['state'] = jobs['location'].apply(lambda x: x.split(", ")[-1])

    gb = jobs.groupby('state')
    state_num = dict(gb.size())
    num_state = sorted([(v, k) for k,v in state_num.items()], key=lambda x: x[0], reverse=True)[:top]
    count = [x for x,_ in num_state]
    states = [x if len(abbrev_us_state[x])>12 else abbrev_us_state[x].replace(" ", "\n") for _,x in num_state]

    return count, states

def state_most_jobs(review_table, savefig=False):
    """
    Return the graph with which city in US offers most job.
    """
    review_table = pd.read_csv(review_table)
    count_state, states = compute_most_job_by_state(review_table.copy())

    # Plot
    fig, ax = plt.subplots(1, 1, figsize=(18, 10))
    ax.bar(states, count_state, facecolor="green", width=0.5)
    #ax.set_xlabel('States', fontsize=20)
    ax.set_ylabel('Number of jobs', fontsize=25)
    ax.set_title('Which state in US offers the most job opportunities?  (2017-2019)', fontsize=25)
    ax.tick_params(labelsize=16)
    if savefig:
        fig.savefig('./graphs/a1_q2b.png', format='png', dpi=300)

def approve_of_ceo(ceo_table):
    """
    """
    ceo_table = pd.read_csv(ceo_table)
