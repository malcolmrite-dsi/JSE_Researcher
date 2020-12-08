
import request_web as rwb
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
def download_lexicon():
    nltk.download('vader_lexicon')

def get_news_in_app(code, time_period, detail, subject):
    download_lexicon()
    sid = SentimentIntensityAnalyzer()
    all_headlines = []
    all_links = []
    full_scores = []
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
                url = f"https://www.news24.com/news24/search?query={code}&pageNumber={page}"
                links, headlines = rwb.NewsGetter.get_sector_headlines(rwb.NewsGetter.get_html(url))


            for  i, head in enumerate(headlines):

                all_headlines.append(head)
                all_links.append(links[i])

                ss = sid.polarity_scores(head)
                sumScore += ss['compound']
                full_scores.append(ss['compound'])

        for i, head in enumerate(all_headlines):
            if full_scores[i] > highest:
                highest = full_scores[i]
                highestSent = i

            elif full_scores[i] < lowest:
                lowest = full_scores[i]
                lowestSent = i


    if all_headlines == 0:
        all_headlines = 1

    if detail == 'Summary':
        st.write("{:0.3f}".format(sumScore/(int(len(all_headlines)))))
        st.write("The most positive headline is {0}, with a score of {1}. Here's the link {2}".format(all_headlines[highestSent], highest, all_links[highestSent]))
        st.write("The most negative headline is {0}, with a score of {1}. Here's the link {2}".format(all_headlines[lowestSent], lowest, all_links[lowestSent]))

    if detail == 'Full List':
        for  i, head in enumerate(all_headlines):
                st.write(head)
                st.write(all_links[i])
                st.write(full_scores[i])
                st.write("----------------------------")


def main():
    st.title("JSE Researcher-ALPHA_TESTING")
    st.subheader("*Cutting investment research from hours to minutes with the power of AI!*")

    st.sidebar.subheader("Africa DSI Final Project-")
    st.sidebar.write("By Malcolm Wright")
    st.sidebar.write("App is still under development, almost all the features don't work.")
    section = st.sidebar.radio('Sections to Visit',('Company Background', 'News Analyser', 'Financial Forecasting', 'Report Generator'))

    if section == 'Company Background':
        st.subheader('Company Background Summary')
        share_codes = rwb.SensGetter.get_share_code("JSE_company_list.csv")
        sharecode = st.selectbox("JSE Companies:", share_codes)
        generate = st.button("Generate Background")
        if sharecode != "" and generate:
            get_background(sharecode)

    if section == 'News Analyser':

        st.subheader('News Headline Analyser')
        subject = st.radio('JSE sector or Company analysis?',('Company', 'Sector'))
        if subject == "Company":
            share_codes = rwb.SensGetter.get_share_code("JSE_company_list.csv")
            sharecode = st.selectbox("JSE Companies:", share_codes)
        else:
            share_codes = rwb.SensGetter.get_share_code("Sector_List.csv")
            sharecode = st.selectbox("JSE Sectors:", share_codes)
        time_period = st.slider('How many pages should we analyse?',1, 10)
        details = st.radio('Do you want the full list of the Headlines? Or just a Sentiment Summary',('Summary', 'Full List'))
        generate = st.button("Create List")
        if sharecode != "" and generate:
            get_news_in_app(sharecode, time_period, details, subject)



if __name__ == '__main__':
    main()
