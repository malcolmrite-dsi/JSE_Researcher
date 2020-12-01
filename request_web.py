import requests
from bs4 import BeautifulSoup
import pandas as pd
import re

class NewsGetter():
    """docstring for NewsGetter."""
    def get_html(url):
        response = requests.get(url)
        if not response.ok:
            print(f'Code: {response.status_code}, url: {url}')
        return response.text


    def get_company_links(html):
        all_company_links = []

        soup = BeautifulSoup(html, 'lxml')

        #pattern = r'^ViewSENSWithHighlight'
        companypage = soup.find_all('a', target_="_blank")

        for share in companypage:
            share = share.get("href")

            link = "https://za.investing.com" + share

            all_company_links.append(link)

        return all_company_links

    def get_news_headlines(html):
        all_company_headlines = []
        all_company_links = []
        soup = BeautifulSoup(html, 'lxml')

        #pattern = r'^ViewSENSWithHighlight'
        newspage = soup.find_all('a', class_="article-item--url")

        for headline in newspage:
            newslink = headline.get("href")
            headline = headline.get("aria-label")

            link = newslink

            all_company_links.append(link)
            all_company_headlines.append(headline)

        return all_company_links, all_company_headlines

class SensGetter():
    def get_html(url):
        response = requests.get(url)
        if not response.ok:
            print(f'Code: {response.status_code}, url: {url}')
        return response.text

    def get_share_code(filename):
        comp_list = []
        companies = pd.read_csv(filename)
        codes = companies["Share Code"]
        for code in codes:
            comp_list.append(code)

        return comp_list

    def get_sens_id(html):
        all_sens = []
        all_titles = []
        all_dates = []

        soup = BeautifulSoup(html, 'lxml')

        pattern = r'^ViewSENSWithHighlight'
        senspage = soup.find_all('td', onclick=re.compile(pattern))

        for sens in senspage:
            sens = sens.get("onclick")
            start = sens.find("ViewSENSWithHighlight(") + len("ViewSENSWithHighlight(")
            end = sens.find(')', start)
            report = sens[start:end]

            all_sens.append(report)

        for sens in senspage:
            try:
                title = sens.text.strip()

                title = title.split(" - ")
                final_title = title[-1]
                final_title = final_title.split(" : ")[-1]
            except:
                final_title = ''

            all_titles.append(final_title)

        dates = soup.find_all('td', class_="TableRow_border smalltext")

        for date in dates:
            date = date.text.strip()
            date = date.split(",")[0]
            all_dates.append(date)

        return all_sens, all_titles, all_dates

    def get_company_list(html):
        company_list = []
        soup = BeautifulSoup(html, 'lxml')
        companypage = soup.find_all('a')

        for company in companypage:

            if (company.text.strip() != ""):
                print(company.text.strip())
                company_list.append(company.text.strip())
        return company_list

    def get_sens_text(id, title):
        url = f'https://www.profiledata.co.za/BrokerSites/BusinessLive/SENS.aspx?id={id}'
        html = SensGetter.get_html(url)
        soup = BeautifulSoup(html, 'lxml')

        try:
            text = soup.find('pre').text.strip()
            start = text.find(title) + len(title)
            stop = text.find("Produced by the JSE SENS Department")
            text = text[start:stop]
            if text.find("Sponsor"):
                stop2 = text.find("Sponsor")
                text = text[:stop2]
            if text.find("Ends."):
                stop3 = text.find("Ends.")
                text = text[:stop3]

        except:
            text = ''
            print(url)

        return text
