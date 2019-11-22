"""
This part of script does analysis on review table and
ceo rating table.
"""
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
import warnings
warnings.filterwarnings("ignore")
import string
import nltk
from nltk.sentiment.vader import SentimentIntensityAnalyzer
from utils import abbrev_us_state

anlyzer = SentimentIntensityAnalyzer()
review_table = 'Scraper/ReviewScraper/merged_reviews_table.csv'
ceo_table = 'Scraper/ReviewScraper/ceo_ratings.csv'


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


def compute_pos_neg_review_percent(review):
    """
    """
    gb = review.groupby('company')
    comp = gb.indices.keys()
    review = {'positive': [], 'negative': [], 'neutral': []}

    def process_group(gname):
        df = gb.get_group(gname)
        total = 2 * len(df)

        pros = df['pros'].apply(lambda x: anlyzer.polarity_scores(x))
        pos = pros.apply(lambda x: 1 if x['pos'] >= 0.4 else 0)
        pos = int(sum(pos.values)/total * 100)

        cons = df['cons'].apply(lambda x: anlyzer.polarity_scores(x))
        neg = cons.apply(lambda x: 1 if x['neg'] >= 0.4 else 0)
        neg = int(sum(neg.values)/total * 100)

        neu = 100 - (pos + neg)

        return pos, neg, neu


    for c in comp:
        pos, neg, neu = process_group(c)
        review['positive'].append(pos)
        review['negative'].append(neg)
        review['neutral'].append(neu)

    comp = [c.upper() if c == "ibm" or c == "hp" else c.title() for c in comp]

    return comp, review


def compute_career_rating(review):
    """
    """
    review = review[pd.notnull(review['rating_career'])]
    review = review[pd.notnull(review['rating_comp'])]

    gb = review.groupby('company')
    comp = gb.indices.keys()
    rating = {'compensation': [], 'career': []}

    def process_group(gname):
        df = gb.get_group(gname)

        career = sum(df['rating_career']) / len(df['rating_career'])
        compens = sum(df['rating_comp']) / len(df['rating_comp'])

        return compens, career

    for c in comp:
        compens, career = process_group(c)
        rating['compensation'].append(compens)
        rating['career'].append(career)

    comp = [c.upper() if c == "ibm" or c == "hp" else c.title() for c in comp]

    return comp, rating


def plot_city_most_jobs(review_table, savefig=False):
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
        fig.savefig('graphs/a1_q2a.png', format='png', dpi=300)


def plot_state_most_jobs(review_table, savefig=False):
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
        fig.savefig('graphs/a1_q2b.png', format='png', dpi=300)


def plot_approve_of_ceo(ceo_table, savefig=False):
    """
    """
    ceo_table = pd.read_csv(ceo_table)
    # this drops HP as we don't have CEO approval rating
    ceo_table = ceo_table.dropna()
    ceo_table.reset_index(drop=True, inplace=True)

    company = ceo_table['company'].values
    company = [c.title() if c != "IBM" else c for c in company]
    recom = ceo_table['recommend_to_a_friend'].values
    approve = ceo_table['approve_of_ceo'].values

    # Plot
    fig, ax = plt.subplots(1, 1, figsize=(25, 11))
    x = list(range(len(company)))
    total_width, n = 0.6, 2
    width = total_width / n
    ax.bar(
        x, approve, width=width, label='approve of CEO',
        tick_label=company, color='green'
    )
    for i in range(len(x)):
        x[i] = x[i] + width
    ax.bar(
        x, recom, width=width, label='recommend to friend', color='orange'
    )
    #ax.set_xlabel('Company', fontsize=20)
    ax.set_ylabel('Percentage', fontsize=25)
    ax.set_title('Which company people recommends the most?', fontsize=25)
    ax.legend(fontsize=20)
    ax.tick_params(labelsize=20)
    plt.xticks(rotation=45)
    ax.tick_params(labelsize=20)
    if savefig:
        fig.savefig('graphs/a1_q6.png', format='png', dpi=300)


def plot_pos_neg_reviews(review_table, savefig=False):
    """
    """
    review_table = pd.read_csv(review_table)
    company, reviews = compute_pos_neg_review_percent(review_table.copy())
    positive = np.asarray(reviews['positive'])
    negative = np.asarray(reviews['negative'])
    neutral = np.asarray(reviews['neutral'])

    # Plot
    fig, ax = plt.subplots(1, 1, figsize=(25, 11))
    x = list(range(len(company)))
    width = 0.35
    ax.bar(
        x, positive, width=width, label='positive', color='green',
        tick_label=company
    )
    ax.bar(
        x, negative, width=width, bottom=positive, label='negative',
        color='red'
    )
    ax.bar(
        x, neutral, width=width, bottom=positive+negative, label='neutral',
        color='orange'
    )
    #ax.set_xlabel('Company', fontsize=20)
    ax.set_ylabel('Percentage', fontsize=25)
    ax.set_title('Distribution of polarity of reviews among companies?', fontsize=25)
    ax.legend(fontsize=20)
    ax.tick_params(labelsize=20)

    plt.xticks(rotation=45)
    ax.tick_params(labelsize=20)
    if savefig:
        fig.savefig('graphs/a1_q4a.png', format='png', dpi=300)


def plot_career_comp_rating(review_table, savefig=False):
    """
    """
    review_table = pd.read_csv(review_table)
    company, rating = compute_career_rating(review_table.copy())

    # Plot
    fig, ax = plt.subplots(1, 1, figsize=(25, 11))
    x = list(range(len(company)))
    total_width, n = 0.6, 2
    width = total_width / n

    ax.bar(
        x, rating['compensation'], width=width, label='compensation',
        tick_label=company, color='green'
    )
    for i in range(len(x)):
        x[i] = x[i] + width
    ax.bar(
        x, rating['career'], width=width, label='career opportunitis',
        color='orange'
    )
    #ax.set_xlabel('Company', fontsize=20)
    ax.set_ylabel('Rating (max 5)', fontsize=25)
    ax.set_title('What is rating of these companies based on compensation and career opportunities?', fontsize=25)
    ax.legend(fontsize=20)
    ax.tick_params(labelsize=20)
    plt.xticks(rotation=45)
    ax.tick_params(labelsize=20)
    if savefig:
        fig.savefig('graphs/a1_q4b.png', format='png', dpi=300)


if __name__ == "__main__":
    plot_city_most_jobs(review_table, True)
    plot_state_most_jobs(review_table, True)
    plot_career_comp_rating(review_table, True)
    plot_approve_of_ceo(ceo_table, True)
    plot_pos_neg_reviews(review_table, True)
