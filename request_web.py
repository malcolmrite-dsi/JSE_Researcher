import requests
from bs4 import BeautifulSoup
import pandas as pd
import re



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

    def get_sens_text(id):
        url = f'https://www.profiledata.co.za/BrokerSites/BusinessLive/SENS.aspx?id={id}'
        html = SensGetter.get_html(url)
        soup = BeautifulSoup(html, 'lxml')

        try:
            text = soup.find('pre').text.strip()
            stop = text.find("Produced by the JSE SENS Department")
            text = text[:stop]
            if text.find("Disclaimer -"):
                stop2 = text.find("Disclaimer -")
                text = text[:stop2]

        except:
            text = ''
            print(url)

        return text