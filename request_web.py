
#Import Libraries
import requests
from bs4 import BeautifulSoup
import pandas as pd
import re
from datetime import datetime



#Class for getting company background informantion
class CompanyGetter():
    def get_html(url):
        response = requests.get(url)
        if not response.ok:
            print(f'Code: {response.status_code}, url: {url}')
        return response.text

    def get_management(html):
        all_persons = []

        soup = BeautifulSoup(html, 'lxml')
        managepage = soup.find('table', class_= "W(100%)")
        managepage = managepage.find_all('tr')
        for person in managepage:

            #Initialise list for each person
            details = []
            person = person.find_all('span')
            for field in person:
                #Populate the details for a person in the management team with this list
                details.append(field.text.strip())

            #Add the details to the larger list of of the management staff
            all_persons.append(details)

        return all_persons

    def get_company_background(html):
        all_company_text = []

        soup = BeautifulSoup(html, 'lxml')

        #pattern = r'^ViewSENSWithHighlight'
        companypage = soup.find('div', class_="row tools-container m0010")
        companypage = companypage.find_all('p')
        for text in companypage:
            text = text.text.strip()
            all_company_text.append(text)

        return all_company_text

class FinancialGetter():
    def get_html(url):
        response = requests.get(url)
        if not response.ok:
            print(f'Code: {response.status_code}, url: {url}')
        return response.text

    def get_sector_data(code):
        all_codes = []
        if len(str(code)) == 3:
            code = "0" + str(code)

        url = f"https://www.sharedata.co.za/V2/Controls/Shares/ShareIndex/SIJSONData.aspx?indextype=SI_sector:{code}&sortfield=FULLNAME"
        html = FinancialGetter.get_html(url)
        soup = BeautifulSoup(html, 'lxml')
        codeCounter = 0
        sectorcodes = soup.find_all("a")
        for code in sectorcodes:
            if codeCounter % 3 == 0:
                all_codes.append(code.text.strip())

            codeCounter += 1
        return all_codes

    #Function to get the currency of the company selected
    def get_currency(soup):

        currency = ""

        curr = soup.find('span', {'class': "Fz(xs) C($tertiaryColor) Mstart(25px) smartphone_Mstart(0px) smartphone_D(b) smartphone_Mt(5px)"})

        currencies = curr.find_all("span")
        currency = curr.text

        return currency

    def get_stock_title(soup):
        heading = ""

        head = soup.find("h1" , {"class": "D(ib) Fz(18px)"})

        return head.text

    def get_stock_price(code):
        url = f"https://finance.yahoo.com/quote/{code}.JO?p={code}.JO"
        html = FinancialGetter.get_html(url)

        soup = BeautifulSoup(html, 'lxml')

        try:
            prices = soup.find_all('span', {'class': "Trsdu(0.3s) Fw(b) Fz(36px) Mb(-4px) D(ib)"})
            for price in prices:
                price = price.text
                price = price.replace(',', '')

                price = float(price) / 100

        except:
            price = 0

        return price


    def get_statement(html, type):
        soup = BeautifulSoup(html, 'lxml')
        financials = []
        header = soup.find('div', {'class': "D(tbhg)"})
        periods = []

        columns = header.find_all("span")
        for item in columns:
            periods.append(item.text)

        newspage = soup.find_all('div', {'data-test': "fin-row"})
        for item in newspage:
            row = []
            textRow = item.find_all("span")
            for textItem in textRow:
                row.append(textItem.text)

            financials.append(row)
            traindata = pd.DataFrame(financials, columns = [periods])
            if type == "Income" or type == "Cash Flow":
                traindata = traindata.drop(columns = ["ttm"], level = 0)

        traindata.iloc[:,1:] = traindata.iloc[:,1:].apply(lambda x: x.str.replace(',', '').astype('float'))
        headers = traindata.columns[1:].values.tolist()
        dates = []
        for date in headers:

                #datetime_object = datetime.strptime(date[0], '%m/%d/%Y')

            dates.append(date[0])


        currency = FinancialGetter.get_currency(soup)
        name = FinancialGetter.get_stock_title(soup)
        

            #traindata = []
            #dates = []
            #currency = ""
            #name = ""
        return traindata, dates, currency, name


"""Class for getting the news headlines for a specific share code
    Three functions are currnetly contained in this class.
    get_html(url) = retrive the HTML for a given URL utilising the request library
    get_sector_headlines(html) = Retrieves headlines from the News24 website, for the specified Sector
    get_news_headlines(html) = Retrieves headlines from the MoneyWeb website, for the specified CompanyGetter

"""
class NewsGetter():
    """docstring for NewsGetter."""
    def get_html(url):
        #Function to retrive html
        response = requests.get(url)

        #If there was an error in the retrieval process. Print the error message
        if not response.ok:
            print(f'Code: {response.status_code}, url: {url}')
        return response.text


    def get_sector_headlines(html):

        #Initialise two lists to store the headlines and the links retrieved for the sector
        all_company_headlines = []
        all_company_links = []

        #Use BeautifulSoup to make the HTML useable
        soup = BeautifulSoup(html, 'lxml')

        pattern = "https:"

        #This finds the artcles on the page
        newspage = soup.find_all('a', class_= "article-item--url")

        #Iterate over each article
        for headline in newspage:
            #Extracting the headline text
            head = headline.get("aria-label")

            #Extracting the headline link
            newslink = headline.get("href")

            #If the link is internal, add the news24 url to make it useable.
            if newslink.find(pattern):
                newslink = "https://www.news24.com"+newslink

            else:
                newslink = newslink


            link = newslink

            #Append the news likn and headline to the list
            all_company_links.append(link)
            all_company_headlines.append(head)

        #Return the links and headlines
        return all_company_links, all_company_headlines


    def get_news_headlines(html):

        #Initialise two lists to store the headlines and the links retrieved for the sector
        all_company_headlines = []
        all_company_links = []
        soup = BeautifulSoup(html, 'lxml')


        #This finds the artcles on the page
        newspage = soup.find_all('h3', class_= "title list-title m0005")

        #Iterate over each article
        for headline in newspage:
            #Extracting the headline text
            headline = headline.find("a")

            #Extracting the headline link
            newslink = headline.get("href")

            headline = headline.text.strip()

            #Append the news likn and headline to the list
            all_company_links.append(newslink)
            all_company_headlines.append(headline)

        return all_company_links, all_company_headlines

#Class for getting the SENS text or headline for a specific share code
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

    def get_icb_code(filename):

        sectors = pd.read_csv(filename)


        return sectors

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

    def get_sector_list(html):
        sectors = []
        icb_codes = []
        soup = BeautifulSoup(html, 'lxml')

        codeTable = soup.find("tbody")
        icbRows = codeTable.find_all("tr")

        for row in icbRows:
            fieldCount = -1
            columns = row.find_all("td")

            for item in columns:
                item = item.find("span")
                if fieldCount == 0:

                    print(item.text.strip())
                    sectors.append(item.text.strip())
                elif fieldCount == 1:

                    print(item.text.strip())
                    icb_codes.append(item.text.strip())

                fieldCount += 1


        return sectors, icb_codes


    def get_sens_text(id, title):
        url = f'https://www.profiledata.co.za/BrokerSites/BusinessLive/SENS.aspx?id={id}'
        html = SensGetter.get_html(url)
        soup = BeautifulSoup(html, 'lxml')

        try:
            text = soup.find('pre').text.strip()
            start = text.find(title) + len(title)
            stop = text.find("Produced by the JSE SENS Department")
            text = text[:stop]
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
