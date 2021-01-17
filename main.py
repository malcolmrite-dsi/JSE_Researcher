

#Importing custom library for web scraping
import request_web as rwb

from financial_analysis import FinancialAnalyser as fa
import matplotlib.pyplot as plt
import numpy as np
import re
import streamlit as st

import text_analysis as ta
from Company_List_Generator import CompanyGenerator


#http://196.30.126.229/V2/Controls/News/NewsList/NLJSONdata.aspx?jsecode=IMP&type=sens&filter=&search=
#https://www.profiledata.co.za/BrokerSites/BusinessLive/SENS.aspx?id=372260



def main():


    st.title("JSE Researcher-ALPHA_TESTING")
    st.subheader("*Cutting investment research from hours to minutes with the power of AI!*")
    st.sidebar.image("DSI-logo.jpg", use_column_width = True)
    st.sidebar.subheader("Africa DSI Final Project")
    st.sidebar.write("By Malcolm Wright")
    st.sidebar.write("App is still under development, almost all the features don't work.")
    section = st.sidebar.radio('Sections to Visit',('Company Background','Latest SENS', 'News Analyser', 'Financial Analysis','Stock Price Forecasting', 'Report Generator'))

    if section == 'Company Background':
        st.subheader('Company Background Summary')
        share_codes = rwb.SensGetter.get_share_code("JSE_company_list.csv")
        sharecode = st.selectbox("JSE Companies:", share_codes)
        generate = st.button("Generate Background")
        if sharecode != "" and generate:
            ta.Background.get_background(sharecode)

    if section == 'Latest SENS':
        st.subheader('Latest Stock Exchange News Service Information')
        share_codes = rwb.SensGetter.get_share_code("JSE_company_list.csv")
        sharecode = st.selectbox("JSE Companies:", share_codes)
        time_period = st.slider('How many SENS items should we Display?',1, 50)
        generate = st.button("Generate SENS")
        if sharecode != "" and generate:
            ta.NewsAnalyser.get_sens_in_app(sharecode, time_period)

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
            ta.NewsAnalyser.get_news_in_app(sharecode, time_period, details, subject)

    if section == 'Financial Analysis':
        st.subheader('Financial Analyser')
        subject = st.radio('JSE Sector or Company Analysis?',('Company', 'Sector'))
        if subject == "Company":
            share_codes = rwb.SensGetter.get_share_code("JSE_company_list.csv")
            sharecode = st.selectbox("JSE Companies:", share_codes)

        else:
            share_codes = rwb.SensGetter.get_share_code("Sector_List.csv")
            sharecode = st.selectbox("JSE Sectors:", share_codes)
            st.subheader("This may take a couple of minutes to analyse.")

        analysis = st.radio('Which type of analysis do you want to conduct?',('Income', 'Assets', "Cash Flow"))
        generate = st.button("Generate Analysis")
        if sharecode != "" and generate:
            with st.spinner("Analysing Financial Data....This May Take Some Time..."):
                fa.get_financials(sharecode, subject, analysis)

    if section == "Stock Price Forecasting":
        st.subheader('Stock Price Forecaster')

        share_codes = rwb.SensGetter.get_share_code("JSE_company_list.csv")
        sharecode = st.selectbox("JSE Companies:", share_codes)

        generate = st.button("Generate Forecast")
        if sharecode != "" and generate:
            with st.spinner("Analysing Stock Price Data....This May Take Some Time..."):
                st.write("Feature is still under construction")


if __name__ == '__main__':
    main()
