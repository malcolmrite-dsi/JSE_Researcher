
from request_web import SensGetter
from request_web import NewsGetter
import re
import streamlit as st
#http://196.30.126.229/V2/Controls/News/NewsList/NLJSONdata.aspx?jsecode=IMP&type=sens&filter=&search=
#https://www.profiledata.co.za/BrokerSites/BusinessLive/SENS.aspx?id=372260

def get_sens_in_app(code, time_period):
    if time_period == '21':
        loopEnd = 2
    elif time_period == '42':
        loopEnd = 3
    else:
        loopEnd = 4
    for page in range(1,loopEnd):
        url = f"https://www.news24.com/news24/search?query={term}&pageNumber={page}"

        with st.spinner("Loading Headlines...."):
            links, headlines = NewsGetter.get_news_headlines(NewsGetter.get_html(url))

        for  i, head in enumerate(headlines):

            st.write(head)
            st.write(links[i])
            st.write("-----------------")


def main():
    st.title("JSE Researcher-ALPHA_TESTING")
    st.subheader("*Cutting investment research from hours to minutes with the power of AI!*")

    st.sidebar.subheader("Africa DSI Final Project-")
    st.sidebar.write("By Malcolm Wright")
    st.sidebar.write("App is still under development, almost all the features don't work.")
    section = st.sidebar.radio('Sections to Visit',('News Analyser', 'Financial Forecasting', 'Report Generator'))

    if section == 'News Analyser':

        st.subheader('News Headline Analyser')
        sharecode = st.text_area('Enter the name of the JSE company:')
        time_period = st.radio('Select the Number of Articles to Analyse',('21', '42', '63'))
        generate = st.button("Create List")
        if sharecode != "" and generate:
            get_sens_in_app(sharecode, time_period)



if __name__ == '__main__':
    main()
