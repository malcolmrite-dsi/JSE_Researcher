

#Importing custom library for web scraping
import request_web as rwb
#Importing custom library for financial analysis
from financial_analysis import FinancialAnalyser as fa

from stock_price_forecaster import StockForecaster as sf

import numpy as np
import re
import streamlit as st
from pathlib import Path
import text_analysis as ta
from Company_List_Generator import CompanyGenerator

from pdf_generator import PDFGenerator as pg
import base64
#http://196.30.126.229/V2/Controls/News/NewsList/NLJSONdata.aspx?jsecode=IMP&type=sens&filter=&search=
#https://www.profiledata.co.za/BrokerSites/BusinessLive/SENS.aspx?id=372260




def read_markdown_file(markdown_file):
    return Path(markdown_file).read_text()

def main():


    st.title("JSE Researcher")
    st.subheader("*Cutting investment research from hours to minutes with the power of Data!*")
    st.sidebar.image("Web_Images/DSI-logo.jpg", use_column_width = True)
    st.sidebar.subheader("Africa DSI Final Project")
    st.sidebar.write("By Malcolm Wright")

    section = st.sidebar.radio('Sections to Visit',("Help",'Company Background','Latest SENS', 'News Analyser', 'Financial Analysis','Stock Price Forecasting', 'PDF Report Generator'))

    if section == 'Help':
        #https://pmbaumgartner.github.io/streamlitopedia/markdown.html
        htmlmarkdown= read_markdown_file('README.md')
        st.markdown(htmlmarkdown, unsafe_allow_html=True)

    if section == 'Company Background':
        st.subheader('Company Background Summary')
        share_codes = rwb.SensGetter.get_share_code("Company_Lists/JSE_company_list.csv")
        sharecode = st.selectbox("Select a JSE Company:", share_codes)
        #Add Short Name to App
        st.write(rwb.SensGetter.find_share_name(sharecode, "Company_Lists/JSE_company_list.csv"))

        generate = st.button("Generate Background")
        if sharecode != "" and generate:
            ta.Background.get_background(sharecode)

    if section == 'Latest SENS':
        st.subheader('Latest Stock Exchange News Service Information')
        share_codes = rwb.SensGetter.get_share_code("Company_Lists/JSE_company_list.csv")
        sharecode = st.selectbox("Select a JSE Company:", share_codes)
        #Add Short Name to App
        st.write(rwb.SensGetter.find_share_name(sharecode, "Company_Lists/JSE_company_list.csv"))
        time_period = st.slider('How many SENS items should we Display?',1, 50)
        generate = st.button("Generate SENS")
        if sharecode != "" and generate:
            ta.NewsAnalyser.get_sens_in_app(sharecode, time_period)

    if section == 'News Analyser':

        st.subheader('News Headline Analyser')
        subject = st.radio('Would you like a JSE Sector or Company Analysis?',('Company', 'Sector'))
        if subject == "Company":
            share_codes = rwb.SensGetter.get_share_code("Company_Lists/JSE_company_list.csv")
            sharecode = st.selectbox("Select a JSE Company:", share_codes)
            #Add Short Name to App
            st.write(rwb.SensGetter.find_share_name(sharecode, "Company_Lists/JSE_company_list.csv"))
        else:
            share_codes = rwb.SensGetter.get_share_code("Company_Lists/Sector_List.csv")
            sharecode = st.selectbox("Select a JSE Sector:", share_codes)
        time_period = st.slider('How many pages should we analyse?',2, 11)
        details = st.radio('Do you want the full list of the Headlines? Or just a Sentiment Summary',('Summary', 'Full List'))
        generate = st.button("Create List")
        if sharecode != "" and generate:
            _, _, _, _, _, _, _ =ta.NewsAnalyser.get_news_in_app(sharecode, time_period, details, subject)

    if section == 'Financial Analysis':
        st.subheader('Financial Analyser')
        subject = st.radio('Would you like a JSE Sector or Company Analysis?',('Company', 'Sector'))
        if subject == "Company":
            share_codes = rwb.SensGetter.get_share_code("Company_Lists/JSE_company_list.csv")
            sharecode = st.selectbox("Select a JSE Company:", share_codes)
            #Add Short Name to App
            st.write(rwb.SensGetter.find_share_name(sharecode, "Company_Lists/JSE_company_list.csv"))
            options = ["Graphs", "Valuation Metrics", "Financial Table"]
        else:
            share_codes = rwb.SensGetter.get_share_code("Company_Lists/Sector_List.csv")
            sharecode = st.selectbox("Select a JSE Sector:", share_codes)
            st.subheader("This may take a couple of minutes to analyse.")
            options = st.multiselect("What type of information do you want to display?", ["Graphs", "Valuation Metrics"], ["Graphs", "Valuation Metrics"])

        analysis = st.radio('Which type of analysis do you want to conduct?',('Income', 'Assets', "Cash Flow"))
        generate = st.button("Generate Analysis")
        if sharecode != "" and generate:
            with st.spinner("Analysing Financial Data....This May Take Some Time..."):
                _, _, _ =fa.get_financials(sharecode, subject, analysis, options, False)

    if section == "Stock Price Forecasting":
        st.subheader('Stock Price Forecaster')

        share_codes = rwb.SensGetter.get_share_code("Company_Lists/TOP40_company_list.csv")
        sharecode = st.selectbox("Select a Top 40 JSE Company:", share_codes)
        st.write(rwb.SensGetter.find_share_name(sharecode, "Company_Lists/TOP40_company_list.csv"))
        duration = st.select_slider("How far do you want the prediction to go?", ["1 Day", "3 Days", "1 Week"])
        st.subheader("Caution: The further the prediction, the less accurate the result.")

        generate = st.button("Generate Forecast")
        if sharecode != "" and generate:
            with st.spinner("Analysing Stock Price Data....This May Take Some Time..."):
                prediction, confidence = sf.forecaster(sharecode, duration)


                st.write("The stock is expected to change by {0}% with a {1} % confidence".format(prediction, 100 - abs(confidence)))

    if section == "PDF Report Generator":
        st.subheader('PDF Report Generator')
        time_period = ""
        detail = ""
        subject = st.radio('Would you like a JSE Sector or Company Report?',('Company', 'Sector'))
        if subject == "Company":
            share_codes = rwb.SensGetter.get_share_code("Company_Lists/JSE_company_list.csv")
            sharecode = st.selectbox("Select a JSE Company:", share_codes)
            #Add Short Name to App
            st.write(rwb.SensGetter.find_share_name(sharecode, "Company_Lists/JSE_company_list.csv"))
            all_opts = ["Company Background", "News Analysis", "Latest SENS", "Financial Analysis"]
            default = ["Company Background","Financial Analysis"]
            options = st.multiselect("What categories do you want to in the report?", all_opts , default)
        elif subject == "Sector":
            share_codes = rwb.SensGetter.get_share_code("Company_Lists/Sector_List.csv")
            sharecode = st.selectbox("Select a JSE Sector:", share_codes)
            all_opts = ["News Analysis", "Financial Analysis"]
            default = ["News Analysis","Financial Analysis"]
            options = st.multiselect("What categories do you want to in the report?", all_opts , default)

        if "News Analysis" in options:
            time_period = st.slider('How many pages should we analyse?',2, 11)
            #details = st.radio('Do you want the full list of the Headlines? Or just a Sentiment Summary',('Summary', 'Full List'))
            detail = ""

        if "Financial Analysis" in options and subject == "Sector":
            finOptions = st.multiselect("What type of financial analysis information do you want to display?", ["Graphs", "Valuation Metrics"], ["Graphs", "Valuation Metrics"])
        else:
            finOptions = ["Graphs", "Valuation Metrics"]

        generate = st.button("Generate Report")
        if sharecode != "" and generate:
            with st.spinner("Generating Report....This May Take Some Time..."):

                report = pg.generate_report(sharecode,time_period, detail, subject, options, finOptions)


                st.markdown(report, unsafe_allow_html=True)



if __name__ == '__main__':
    main()
