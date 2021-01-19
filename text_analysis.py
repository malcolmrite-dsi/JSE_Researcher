#Importing custom library for web scraping
import request_web as rwb
import streamlit as st
from nltk.sentiment.vader import SentimentIntensityAnalyzer
import nltk

class Background():
    #Function to display the background info for a specified company
    def get_background(code):
        text_list = rwb.CompanyGetter.get_company_background(rwb.NewsGetter.get_html(f"https://www.moneyweb.co.za/tools-and-data/click-a-company/{code}/"))

        for text in text_list:
            st.subheader(text)

        #Function to display the Management Team Table
        management = rwb.CompanyGetter.get_management(rwb.NewsGetter.get_html(f"https://finance.yahoo.com/quote/{code}.JO/profile?p={code}.JO"))
        st.subheader("Management Team")
        st.table(management)
        st.write("Pay is in ZA Rands")


class NewsAnalyser():
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

    #Method to scrape a specific amount of SENS items from Profile Data via Business Live
    def get_sens_in_app(code, upperLimit):
        url = f"https://www.profiledata.co.za/brokersites/businesslive/Controls/Toolbox/SensSearch/SSJSONdata.aspx?date=26%20Nov%202010&enddate=31%20Dec%202020&keyword=&sharecode={code}&sectorcode="

        sens_ids, sens_titles, sens_dates = rwb.SensGetter.get_sens_id(rwb.SensGetter.get_html(url))

        for i, sens in enumerate(sens_ids[:upperLimit]):
            text = rwb.SensGetter.get_sens_text(sens, sens_titles[i])
            st.write(i+1)
            st.subheader(text)
            st.write("----------------------------------")


    def get_news_in_app(code, time_period, detail, subject):
        NewsAnalyser.download_lexicon()
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
                    full_labels.append(NewsAnalyser.add_label(ss['compound']))
                    full_scores.append(ss['compound'])

            for i, head in enumerate(all_headlines):
                if full_scores[i] > highest:
                    highest = full_scores[i]
                    highestSent = i

                elif full_scores[i] < lowest:
                    lowest = full_scores[i]
                    lowestSent = i


        if detail == 'Summary' and len(all_headlines) >= 1:
            st.subheader(NewsAnalyser.add_label(sumScore/(int(len(all_headlines)))))
            st.write("Score: {0:0.3f}".format(sumScore/(int(len(all_headlines)))))
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
