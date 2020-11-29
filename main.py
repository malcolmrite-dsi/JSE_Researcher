
from request_web import SensGetter
import re
import streamlit as st
#http://196.30.126.229/V2/Controls/News/NewsList/NLJSONdata.aspx?jsecode=IMP&type=sens&filter=&search=
#https://www.profiledata.co.za/BrokerSites/BusinessLive/SENS.aspx?id=372260

def get_sens_in_app(code, time_period):

    url = f"https://www.profiledata.co.za/brokersites/businesslive/Controls/Toolbox/SensSearch/SSJSONdata.aspx?date=01%20Jan%20{time_period}&enddate=01%20Dec%20{time_period}&keyword=&sharecode={code}&sectorcode="

    sens_ids, sens_titles, sens_dates = SensGetter.get_sens_id(SensGetter.get_html(url))
    for sens in sens_ids:
        text = SensGetter.get_sens_text(sens)
        st.write(text)


def main():
    st.title("JSE Researcher-ALPHA_TESTING")
    st.subheader("*Cutting investment research from hours to minutes with the power of AI!*")

    st.sidebar.subheader("Africa DSI Final Project-")
    st.sidebar.write("By Malcolm Wright")
    st.sidebar.write("App is still under development, almost all the features don't work.")
    section = st.sidebar.radio('Sections to Visit',('SENS Analyser', 'Financial Forecasting', 'Report Generator'))

    if section == 'SENS Analyser':

        st.subheader('SENS Analyser')
        sharecode = st.text_area('Enter the share code of the JSE company:')
        time_period = st.radio('Select the Time Period',('2020', '2019', '2018'))
        generate = st.button("Output SENS")
        if sharecode != "" and generate:
            get_sens_in_app(sharecode, time_period)


    for sens in sens_ids:
        print((sens))

    for title in sens_titles:
        print((title))

    for date in sens_dates:
        print(date)
if __name__ == '__main__':
    main()
