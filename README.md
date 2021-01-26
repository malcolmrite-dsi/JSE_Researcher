# JSE_Researcher
Final Africa DSI Project

This project was done by Malcolm Wright (me). This project references a lot of online sources, some of which can be found in the code as comments. Unfortunetely, I wasn't able to collate all of the references in one place in time. 

The share code of the desired comapny you want to research can be quickly searched online.

Enjoy!

Ths Site: https://share.streamlit.io/malcolmrite-dsi/jse_researcher/main/main.py
Git Repository: https://github.com/malcolmrite-dsi/JSE_Researcher

## Instructions
### Company Background

1. Click the drop down menu and select share code/company you want to view. A short name of that company should appear to confirm your selection.
2. Click the Generate Background button to produce the background result. The company details and management details should appear below the button.

### Latest SENS (Stock Market News Service)

1. Click the drop down menu and select share code/company you want to view. A short name of that company should appear to confirm your selection.
2. Use the slider to indicate how many SENS news items do you want the app to retrieve.
3. Click the Generate SENS button to produce the SENS items below the button. Some of the text may be weirdly formatted, this is due to how Streamlit handles that particular text format

### News Analyser

1. Select whether you want to analyse sector news or company news from the top radio buttons on the centre of the page.
2. Click the drop down menu and select share code/sector you want to view. A short name of that company should appear to confirm your selection, if you choose company analysis.
NB. The drop down list should automatically change based on step 1.
3. Use the slider to indicate how many pages the app should analyse, these are pages from the websites the app is retrieving the headlines from. MoneyWeb for company analysis, and Fin24 for sector analysis
4. The last radio buttons above the create list button ask if you want a summary or full list. The summary displays the average analysis score, which is between -1 (Most Negative) and +1 (Most Positive). 
The summary also displays the most positive article, and most negative it found within the parameters. (The model is not perfect, so some scores and/or artcles may not make sense). 
The full list just displays the headline, link and score for each headline. NB. I didn't have time to fix the issue of repeating headlines, this may be due to the website itself.
5. Finally press the Create List button to generate the results. 

### Financial Analysis

1. Select whether you want to analyse sector news or company news from the top radio buttons on the centre of the page.
2. Click the drop down menu and select share code/sector you want to view. A short name of that company should appear to confirm your selection, if you choose company analysis.
NB. The drop down list should automatically change based on step 1.
3. For Sector Analysis, do to speed considerations, you can select if you want both the graphs and the valuation metrics. Or only one of those options. Company analysis assumes both. NB On the live app, for large sectors such as Real Estate and Mining, Finance may block the app from continuous scraping, so don't be alarmed if the data becomes unavailable mid the load.
4. The type of analysis would need to be selected. This is based on the three main financial statements from a company. 
5. Finally press the Generate Analysis button to generate the results. The first you should see is the graph, if selected. Then the detailed valuation metrics for all the companies in the sector, or for the one share if it's company analysis. Lastly for company analysis, the financial statement should be displayed. NB. Some shares have unavailble data from Yahoo Finance, which is where the data is retrieved. In this case, a blank plot is shown, and text would appear to show that's the case.

### Stock Price Forecasting

1. Click the drop down menu and select share code/company you want to view from the JSE Top 40 List. A short name of that company should appear to confirm your selection.
2. Use the slider to select either a 1 day, 3 days or 1 week prediction. NB. This was a last minute addition, so the model seems to only work for short term results. 
3. Finally press the Generate Forecast button to generate the resulting prediction. NB. For a lot of these predictions, a 0.0% is predicted, this is more to do with the model's quality. 

### PDF Generator
1. Select whether you want to analyse sector news or company news from the top radio buttons on the centre of the page.
2. Click the drop down menu and select share code/sector you want to view. A short name of that company should appear to confirm your selection, if you choose company analysis.
NB. The drop down list should automatically change based on step 1.
3. Below the drop dow list, there's a category box with default options. Here you can place any or all of the first four main features for company analysis, or the two main features (News Analysis and Financial Analysis) for sector analysis. The options for these featureds should pop up as you select them, except for latest SENS, which was preset to 5 items, due to the computation speed needed to write the text as PDF.
4. Press the Generate Report button to generate a download link to the report.
5. Finally, click the hyperlink listed below the button once the progress bar is done. This should trigger your browser to ask whether you want to save or open the file. You can now save the report to your local directory. 
