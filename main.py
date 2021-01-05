

#Importing custom library for web scraping
import request_web as rwb
import matplotlib.pyplot as plt
import re
import streamlit as st
from nltk.sentiment.vader import SentimentIntensityAnalyzer
import nltk
from Company_List_Generator import CompanyGenerator


#http://196.30.126.229/V2/Controls/News/NewsList/NLJSONdata.aspx?jsecode=IMP&type=sens&filter=&search=
#https://www.profiledata.co.za/BrokerSites/BusinessLive/SENS.aspx?id=372260

#Function to display the background info for a specified company
def get_background(code):
    text_list = rwb.CompanyGetter.get_company_background(rwb.NewsGetter.get_html(f"https://www.moneyweb.co.za/tools-and-data/click-a-company/{code}/"))

    for text in text_list:
        st.subheader(text)

@st.cache
def download_lexicon():
    nltk.download('vader_lexicon')

def add_label(score):
    if score < -0.5:
        label ="Negative"
    elif score < -0.05:
        label ="Slightly Negative"
    elif score < 0.05:
        label ="Neutral"
    elif score <= 0.5:
        label ="Slightly Positive"
    else:
        label ="Positive"
    return label

def get_sens_in_app(code, upperLimit):
    url = f"https://www.profiledata.co.za/brokersites/businesslive/Controls/Toolbox/SensSearch/SSJSONdata.aspx?date=26%20Nov%202010&enddate=31%20Dec%202020&keyword=&sharecode={code}&sectorcode="

    sens_ids, sens_titles, sens_dates = rwb.SensGetter.get_sens_id(rwb.SensGetter.get_html(url))

    for i, sens in enumerate(sens_ids[:upperLimit]):
        text = rwb.SensGetter.get_sens_text(sens, sens_titles[i])
        st.markdown(text)
        st.write("-------------------------------")

def get_financials(code, subject, analysis):
    if subject == "Company":
        fig, ax = plt.subplots(figsize=(6, 4))
        if analysis == "Income":
            url = f"https://finance.yahoo.com/quote/{code}.JO/financials?p={code}.JO"
            table, dates = rwb.FinancialGetter.get_statement(rwb.FinancialGetter.get_html(url), analysis)


            numTable = table.to_numpy()
            plt.title("Revenues and Profits")
            ax.plot(dates, numTable[0,1:], marker='o')
            ax.plot(dates, numTable[2,1:], marker='o')
            ax.plot(dates, numTable[8,1:], marker='o')
            plt.legend((numTable[0,0], numTable[2,0], numTable[8,0]))
            plt.xlabel('Time Periods')
            plt.ylabel('Rands (in Billions)')


        if analysis == "Assets":
            url = f"https://finance.yahoo.com/quote/{code}.JO/balance-sheet?p={code}.JO"
            table, dates = rwb.FinancialGetter.get_statement(rwb.FinancialGetter.get_html(url), analysis)

            numTable = table.to_numpy()
            plt.title("Assets and Liabilities")
            ax.plot(dates, numTable[0,1:], marker='o')
            ax.plot(dates, numTable[6,1:], marker='o')
            ax.plot(dates, numTable[11,1:], marker='o')
            plt.legend((numTable[0,0], numTable[6,0], numTable[11,0]))
            plt.xlabel('Time Periods')
            plt.ylabel('Rands (in Billions)')

        if analysis == "Cash Flow":
            url = f"https://finance.yahoo.com/quote/{code}.JO/cash-flow?p={code}.JO"
            table, dates = rwb.FinancialGetter.get_statement(rwb.FinancialGetter.get_html(url), analysis)

            numTable = table.to_numpy()
            plt.title("Cash Flow Items")
            ax.plot(dates, numTable[0,1:], marker='o')
            ax.plot(dates, numTable[6,1:], marker='o')
            ax.plot(dates, numTable[9,1:], marker='o')
            plt.legend((numTable[0,0], numTable[6,0], numTable[9,0]))
            plt.xlabel('Time Periods')
            plt.ylabel('Rands (in Billions)')
        st.pyplot(fig)
    return table

def get_news_in_app(code, time_period, detail, subject):
    download_lexicon()
    sid = SentimentIntensityAnalyzer()
    all_headlines = []
    all_links = []
    full_scores = []
    full_labels = []
    lowest = 1
    highest = -1
    sumScore = 0
    highestSent = 0
    lowestSent = 0
    with st.spinner("Loading Headlines...."):
        for page in range(1,time_period):
            if subject == "Company":
                url = f"https://www.moneyweb.co.za/company-news/page/{page}/?shareCode={code}"
                links, headlines = rwb.NewsGetter.get_news_headlines(rwb.NewsGetter.get_html(url))
            else:
                code = code.split(" ")
                code = "+".join(code)
                url = f"https://www.news24.com/news24/search?query={code}&pageNumber={page}"
                links, headlines = rwb.NewsGetter.get_sector_headlines(rwb.NewsGetter.get_html(url))


            for  i, head in enumerate(headlines):

                all_headlines.append(head)
                all_links.append(links[i])

                ss = sid.polarity_scores(head)
                sumScore += ss['compound']
                full_labels.append(add_label(ss['compound']))
                full_scores.append(ss['compound'])

        for i, head in enumerate(all_headlines):
            if full_scores[i] > highest:
                highest = full_scores[i]
                highestSent = i

            elif full_scores[i] < lowest:
                lowest = full_scores[i]
                lowestSent = i


    if detail == 'Summary' and len(all_headlines) >= 1:
        st.subheader(add_label(sumScore/(int(len(all_headlines)))))
        st.write("{0:0.3f}".format(sumScore/(int(len(all_headlines)))))
        st.write("The most positive headline is {0}, with a score of {1}, {2}. Here's the link {3}".format(all_headlines[highestSent], highest, full_labels[highestSent], all_links[highestSent]))
        st.write("The most negative headline is {0}, with a score of {1}, {2}. Here's the link {3}".format(all_headlines[lowestSent], lowest, full_labels[lowestSent], all_links[lowestSent]))

    elif detail == 'Full List':
        for  i, head in enumerate(all_headlines):
                st.write(head)
                st.write(all_links[i])
                st.write(full_scores[i], full_labels[i])
                st.write("----------------------------")

    elif len(all_headlines) == 0:
        st.write("There are currently no headlines for this company.")

def main():
    st.title("JSE Researcher-ALPHA_TESTING")
    st.subheader("*Cutting investment research from hours to minutes with the power of AI!*")
    st.sidebar.image("DSI-logo.jpg", use_column_width = True)
    st.sidebar.subheader("Africa DSI Final Project")
    st.sidebar.write("By Malcolm Wright")
    st.sidebar.write("App is still under development, almost all the features don't work.")
    section = st.sidebar.radio('Sections to Visit',('Company Background','Latest SENS', 'News Analyser', 'Financial Analysis','Financial Forecasting', 'Report Generator'))

    if section == 'Company Background':
        st.subheader('Company Background Summary')
        share_codes = rwb.SensGetter.get_share_code("JSE_company_list.csv")
        sharecode = st.selectbox("JSE Companies:", share_codes)
        generate = st.button("Generate Background")
        if sharecode != "" and generate:
            get_background(sharecode)

    if section == 'Latest SENS':
        st.subheader('Latest Stock Exchange News Service Information')
        share_codes = rwb.SensGetter.get_share_code("JSE_company_list.csv")
        sharecode = st.selectbox("JSE Companies:", share_codes)
        time_period = st.slider('How many SENS items should we Display?',1, 50)
        generate = st.button("Generate SENS")
        if sharecode != "" and generate:
            get_sens_in_app(sharecode, time_period)

    if section == 'News Analyser':

        st.subheader('News Headline Analyser')
        subject = st.radio('JSE Sector or Company Analysis?',('Company', 'Sector'))
        if subject == "Company":
            share_codes = rwb.SensGetter.get_share_code("JSE_company_list.csv")
            sharecode = st.selectbox("JSE Companies:", share_codes)
        else:
            share_codes = rwb.SensGetter.get_share_code("Sector_List.csv")
            sharecode = st.selectbox("JSE Sectors:", share_codes)
        time_period = st.slider('How many pages should we analyse?',2, 11)
        details = st.radio('Do you want the full list of the Headlines? Or just a Sentiment Summary',('Summary', 'Full List'))
        generate = st.button("Create List")
        if sharecode != "" and generate:
            get_news_in_app(sharecode, time_period, details, subject)

    if section == 'Financial Analysis':
        st.subheader('Financial Analyser')
        subject = st.radio('JSE Sector or Company Analysis?',('Company', 'Sector'))
        if subject == "Company":
            share_codes = rwb.SensGetter.get_share_code("JSE_company_list.csv")
            sharecode = st.selectbox("JSE Companies:", share_codes)
            analysis = st.radio('Which type of analysis do you want to conduct?',('Income', 'Assets', "Cash Flow"))
        else:
            share_codes = rwb.SensGetter.get_share_code("Sector_List.csv")
            sharecode = st.selectbox("JSE Sectors:", share_codes)

        generate = st.button("Generate Analysis")
        if sharecode != "" and generate:
            table = get_financials(sharecode, subject, analysis)
            st.write(table)

if __name__ == '__main__':
    main()
