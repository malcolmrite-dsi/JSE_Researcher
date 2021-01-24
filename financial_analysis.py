
#Custom library containing web scraping functions
import request_web as rwb
import matplotlib.pyplot as plt
import numpy as np
import streamlit as st
import pandas as pd
import timeit
import time
#Saving images as tempfiles
import tempfile

#For reference: https://www.toptal.com/finance/valuation/valuation-ratios
#https://www.investopedia.com/ask/answers/102714/what-are-main-income-statement-ratios.asp
class ValuationCalculator():
    def get_item_list(table):
        item_list = list(table[:,0])


        return item_list

    #Returns the currency conversion for stocks that have financial data in a different currency
    def get_currency_conversion(currencyText):
        #Currency conversions to ZAR as of 18/01/2021
        curr_dict = {"ZAR":1.0, "NGN":0.040, "USD":15.17, "GBP":20.59, "EUR":18.13}

        #If the only text doesn't indicate the currency then ZAR is assumed
        if currencyText == "All numbers in thousands":
            conversion = curr_dict["ZAR"]

        #This section extracts the currency from the financial data
        else:
            currTextList = currencyText.split(".")
            firstPortion = currTextList[0]
            firstPortionList = firstPortion.split(" ")

            if firstPortionList[2] in curr_dict:
                conversion = curr_dict[firstPortionList[2]]

        return conversion


    def calc_sector_val(sharecodes, analysis):
        sector_details_cols = [""]
        total_cap = 0
        names = []
        if analysis != "Cash Flow":
            #Initialise the dummy pandas series, to place the added values
            sector_calc = pd.Series([0,0,0,0,0], index = [0,1,2,3,4])
            sector_details = pd.Series([0,0,0,0,0],index = [0,1,2,3,4])
        else:
            #Initialise the dummy pandas series, to place the added values
            sector_calc = pd.Series([0,0], index = [0,1])
            sector_details = pd.Series([0,0],index = [0,1])
        for code in sharecodes:

            try:
                #Get the financial table for a company
                table, dates, currency, name = FinancialAnalyser.get_financial_info(code, analysis)
                names.append([code, name])
                table = table.to_numpy()

                    #Returns the labels of the selected table as alist, to obtain the index later
                item_list = ValuationCalculator.get_item_list(table)

                    #Get the valuation metrics for a specified company
                val_table, inc_table, inc_item_list = ValuationCalculator.calc_val(table, code, analysis, currency)

                sector_details = pd.concat([sector_details, val_table["Values"].round(2)], axis=1)

                    #Returns the current stock price of the selected company
                price = rwb.FinancialGetter.get_stock_price(code)

                market_cap = inc_table[inc_item_list.index("Basic Average Shares"),1] * price

                    #Multiplying company metrics by market cap to proportion the average accurately
                values = val_table["Values"] * market_cap

                    #Add the valuation metrics for each company
                sector_calc = sector_calc.add(values, fill_value = 0)

                    #Add to the total cap of the sector in order to divide out the market caps later
                total_cap += market_cap

                sector_details_cols.append(code)
            except Exception as inst:

                st.write(f"{code} Data is Not Sufficient" )




        #st.write(names)
        #Divide the total by the amount of companies in the sector
        sector_valuation = sector_calc / (total_cap)
        sector_valuation = sector_valuation.round(1)
        sector_valuation = pd.concat([val_table["Metrics"], sector_valuation], axis=1)
        sector_valuation.columns = ["Metrics", "Average Values"]

        sector_details.columns = sector_details_cols
        sector_details.drop("", inplace=True, axis = 1)

        sector_details.index = val_table["Metrics"]
        sector_details = sector_details.T

        #sector_details = sector_details.add(values, fill_value = 0)


        return sector_valuation, sector_details, names

    def calc_val(table, sharecode, analysis, currency):

        #Returns the current stock price of the selected company
        price = rwb.FinancialGetter.get_stock_price(sharecode)

        conversion = ValuationCalculator.get_currency_conversion(currency)

        #Initialise the list to store the valuation metrics
        valuation_list = pd.DataFrame(columns = ["Metrics", "Values", "Analysis"])

        #Returns the labels of the selected table as alist, to obtain the index later
        item_list = ValuationCalculator.get_item_list(table)

        #Returns the common valuation metrics for an income statement
        if analysis == "Income":

            #Extract the number of shares issued from the company
            noShares = table[item_list.index("Basic Average Shares"), 1]

            earnings = table[item_list.index("Net Income Common Stockholders"), 1] * conversion

            #Extract the EBIT of the company
            try:
                ebit = table[item_list.index("EBIT"), 1] * conversion
            except:
                ebit = 0

            try:
                intExpense = table[item_list.index("Interest Expense"), 1] * conversion
            except:
                intExpense = 0


            #Total Revenue of the company
            sales = table[item_list.index("Total Revenue"), 1] * conversion

            #Profit Margin
            profitM = (round(((earnings) / sales), 3)) * 100

            #Conditions to determine if the profit margin is good:https://corporatefinanceinstitute.com/resources/knowledge/accounting/profit-margin/
            if profitM > 20:
                result = "Good"
            elif profitM <= 0:
                result = "Bad/Unprofitable"
            elif profitM > 5:
                result = "Average"
            else:
                result = "Low"

            profitM = {"Metrics":"Profit Margin %", "Values": profitM, "Analysis":result}
            valuation_list = valuation_list.append(profitM,ignore_index=True)

            #Price to Earnings
            #https://www.investopedia.com/ask/answers/070314/how-do-i-calculate-pe-ratio-company.asp
            ratioPE = round(((noShares * price) / earnings), 2)

            #Hard to find an exact good number
            if ratioPE > 40:
                result = "Generally Over Valued."
            elif ratioPE < 0:
                result = "Unprofitable"
            else:
                result = "Lower PE = Better Value"

            pe = {"Metrics":"Price to Earnings", "Values":ratioPE,"Analysis":result}
            valuation_list = valuation_list.append(pe,ignore_index=True)

            #Price to Sales
            ratioPS = round(((noShares * price) / sales), 2)

            #Hard to find an exact good number

            if ratioPS > 20:
                result = "Generally Over Valued."
            elif ratioPS < 1:
                result = "Generally Good Value"
            else:
                result = "Lower PS = Better Value"

            ps ={"Metrics":"Price to Sales", "Values":ratioPS,"Analysis":result}
            valuation_list = valuation_list.append(ps,ignore_index=True)

            #Earnings per Share
            ratioEPS = round((earnings / noShares), 2)

            if ratioEPS > price:
                result = "Very Undervalued"
            elif ratioEPS < 0:
                result = "Unprofitable"
            else:
                result = "Check sector analysis."


            eps = {"Metrics":"Earnings per Share", "Values":ratioEPS,"Analysis":result}
            valuation_list = valuation_list.append(eps,ignore_index=True)

            #Times Interest Payment
            if intExpense != 0:
                ratioTIP = round(((ebit) / intExpense), 2)
                #https://www.investopedia.com/ask/answers/030615/what-does-high-times-interest-earned-ratio-signify-regard-companys-future.asp
            else:
                ratioTIP = 0

            if ratioTIP > 5:
                result = "Low Risk"
            elif ratioTIP > 2.5:
                result = "Acceptable Risk"
            elif ratioTIP == 0:
                result = "Data Not Available"
            else:
                result = "High Risk/Financially Unstable"


            tip = {"Metrics":"Times Interest Payment", "Values":ratioTIP,"Analysis":result}
            valuation_list = valuation_list.append(tip,ignore_index=True)

            inc_table = table
        #Returns the common valuation metrics for a balance sheet
        #https://www.investopedia.com/financial-edge/1012/useful-balance-sheet-metrics.aspx
        #https://www.oldschoolvalue.com/financials-accounting/balance-sheet-ratios/
        else:
            income_table, _, _, _ = FinancialAnalyser.get_financial_info(sharecode, "Income")

            #Convert the table to a numpy array for ease of slicing
            inc_table = income_table.to_numpy()

            #Returns the labels of the selected table as alist, to obtain the index later
            inc_item_list = ValuationCalculator.get_item_list(inc_table)

            #Total number of shares issues currently
            noShares = inc_table[inc_item_list.index("Basic Average Shares"), 1] * conversion

            #Total Revenue of the company
            sales = inc_table[inc_item_list.index("Total Revenue"), 1] * conversion

            #Net Profit of the company
            earnings = inc_table[inc_item_list.index("Net Income Common Stockholders"), 1] * conversion

            if analysis == "Assets":

                #Total Assets
                totAssets = table[item_list.index("Total Assets"),1] * conversion

                #Net Tangible Assets: https://www.investopedia.com/terms/n/nettangibleassets.asp
                netTangAssets = table[item_list.index("Net Tangible Assets"),1] * conversion

                #For Minority Interest Definition: https://www.thebalance.com/minority-interest-on-the-balance-sheet-357286
                totLiabilities = table[item_list.index("Total Liabilities Net Minority Interest"),1] * conversion

                noShares = table[item_list.index("Ordinary Shares Number"), 1]

                #Shareholder Equity
                totEquity = table[item_list.index("Total Equity Gross Minority Interest"), 1] * conversion

                #https://www.wallstreetmojo.com/net-tangible-assets/
                intangibles = totAssets - netTangAssets  - totLiabilities

                #Price to Book Value Ratio
                ratioPB = (round(((noShares * price) / totEquity), 2))

                #https://www.investopedia.com/ask/answers/010915/what-considered-good-price-book-ratio.asp
                if ratioPB > 3:
                    result = "Generally Overvalued"
                elif ratioPB < 1:
                    result = "Generally Undervalued"
                else:
                    result = "Check sector analysis"

                pb ={"Metrics":"Price to Book Value", "Values":ratioPB,"Analysis":result}
                valuation_list = valuation_list.append(pb,ignore_index=True)

                #Return on assets: https://www.ruleoneinvesting.com/blog/how-to-invest/important-financial-metrics-that-we-use/
                returnOA = (round((earnings / totAssets), 4)) * 100

                if returnOA > 10:
                    result = "Good"
                elif returnOA <= 0:
                    result = "Bad"
                elif returnOA > 3:
                    result = "Average"
                else:
                    result = "Low"

                roa = {"Metrics":"Return on Assets %", "Values": returnOA, "Analysis":result}
                valuation_list = valuation_list.append(roa,ignore_index=True)

                #Return on Equity: https://www.investopedia.com/ask/answers/102714/what-are-main-income-statement-ratios.asp
                returnOE = (round((earnings / totEquity), 4)) * 100

                #https://www.investopedia.com/terms/r/returnonequity.asp
                if returnOE > 15:
                    result = "Good"
                elif returnOE <= 0:
                    result = "Very Bad"
                elif returnOE > 10:
                    result = "Average"
                else:
                    result = "Low"

                roe = {"Metrics":"Return on Equity %", "Values": returnOE, "Analysis":result}
                valuation_list = valuation_list.append(roe,ignore_index=True)

                #Debt to Equity ratio
                ratioDE = (round(((totLiabilities) / totEquity), 2))

                #https://www.investopedia.com/ask/answers/040915/what-considered-good-net-debttoequity-ratio.asp
                if ratioDE > 2:
                    result = "Generally Over Leveraged"
                elif ratioDE < 1:
                    result = "Optimal"
                else:
                    result = "Average"

                db ={"Metrics":"Debt to Equity", "Values":ratioDE,"Analysis":result}
                valuation_list = valuation_list.append(db,ignore_index=True)


                #Intangibles to Assets ratio: https://corporatefinanceinstitute.com/resources/knowledge/finance/goodwill-to-assets-ratio/
                returnIA = (round(((intangibles) / totAssets), 2)) * 100


                if returnIA > 40:
                    result = "Likely Strong Brand"
                elif returnIA < 10:
                    result = "Likely Assets Focused"
                else:
                    result = "Average"

                ie ={"Metrics":"Intangibles to Assets %", "Values": returnIA,"Analysis":result}
                valuation_list = valuation_list.append(ie,ignore_index=True)
                item_list = inc_item_list

            #The common valuations metrics used for Cash Flow items
            #https://www.oldschoolvalue.com/stock-valuation/best-investing-metrics-ratios/
            else:
                #Free Cash Flow
                freeCF = table[item_list.index("Free Cash Flow"), 1] * conversion

                #Price to Free Cash Flow ratio: https://www.investopedia.com/articles/stocks/11/analyzing-price-to-cash-flow-ratio.asp
                ratioPCF = (round(((noShares * price) / freeCF), 2))

                #https://www.nasdaq.com/articles/using-price-cash-flow-find-value-screen-week-2014-02-18
                if ratioPCF > 30:
                    result = "Very Poor"
                elif ratioPCF > 20:
                    result = "Poor"
                elif ratioPCF <= 10 and ratioPCF > 0:
                    result = "Good"
                elif ratioPCF < 0:
                    result = "Poor and Unprofitable"
                else:
                    result = "Average"

                pcf ={"Metrics":"Price to Free Cash Flow", "Values":ratioPCF, "Analysis":result}
                valuation_list = valuation_list.append(pcf,ignore_index=True)

                #Free Cash Flow to Sales ratio as a percentage
                ratioCFS = (round((freeCF / sales), 4)) * 100

                #https://wealthyeducation.com/free-cash-flow-to-sales-ratio

                if ratioCFS > 5:
                    result = "Good"
                elif ratioCFS > 1:
                    result = "Worrying"
                else:
                    result = "Poor"

                cfs ={"Metrics":"Free Cash Flow to Sales %", "Values": ratioCFS, "Analysis":result}
                valuation_list = valuation_list.append(cfs,ignore_index=True)
                item_list = inc_item_list
        return valuation_list, inc_table, item_list

class FinancialAnalyser():

    #This function applies the correct url to obtain the relevant financial table requested
    def get_financial_info(sharecode, analysis):

        if analysis == "Income":
            url = f"https://finance.yahoo.com/quote/{sharecode}.JO/financials?p={sharecode}.JO"
        elif analysis == "Assets":
            url = f"https://finance.yahoo.com/quote/{sharecode}.JO/balance-sheet?p={sharecode}.JO"
        else:
            url = f"https://finance.yahoo.com/quote/{sharecode}.JO/cash-flow?p={sharecode}.JO"

        #time.sleep(1)
        table, dates, currency, name = rwb.FinancialGetter.get_statement(rwb.FinancialGetter.get_html(url), analysis)

        return table, dates, currency, name

    #General method to obtain graphs and tables for the financial analysis feature
    def get_financials(code, subject, analysis, options, pdf):
        if subject == "Sector":
            table = []
            valuation_list = []
            icb = rwb.SensGetter.get_icb_code("Sector_List.csv")

            value = icb.iloc[(icb["Share Code"]==code).argmax(),1]
            sharecodes = rwb.FinancialGetter.get_sector_data(value)

            #Display a warning message to the user if there aren't any companies in the sector selected.
            if len(sharecodes) == 0:
                st.write("No available companies listed under this sector.")

            #If there are companies in the sector, the financials are extracted
            elif "Graphs" in options:
                success, fig = FinancialAnalyser.plot_finance(sharecodes, analysis)

                if pdf != True:
                    st.pyplot(fig)
                else:
                    with tempfile.NamedTemporaryFile(delete=False, suffix=".png") as tmpfile:
                        fig.savefig(f"tmpfile.{code}_{analysis}.png")
            #If the valuation is selected run this function
            if "Valuation Metrics" in options and len(sharecodes) != 0:
                #If the app is used, use streamlit to display the data
                if pdf != True:
                    start = timeit.default_timer()
                    #Display all of the sharecodes of the sector
                    st.subheader("Shares in Sector:")
                    st.write(sharecodes)

                    st.subheader("Sector Valuation Averages")

                #Return the average valuation metrics for the sector
                avgValues, sector_details, names = ValuationCalculator.calc_sector_val(sharecodes, analysis)


                if pdf != True:
                    st.write(sector_details)
                    #Display those metrics
                    st.write(avgValues)
                    stop = timeit.default_timer()
                    st.write('Time: ', round(stop - start, 2))
                    st.write('Average Time per Share: ', round((stop - start)/len(sharecodes), 2))


                table = sector_details
                valuation_list = avgValues

        #In financial analysis, if company is selected, this code displays the graph and data for the company
        if subject == "Company":

            #This condition graphs the specified analysis of the specified company
            success, fig = FinancialAnalyser.plot_finance(code, analysis)

            #If the data was avaible this condition displays the table specified with its title and currency
            if success:

                table, dates, currency, name = FinancialAnalyser.get_financial_info(code, analysis)
                val_table = table.to_numpy()
                valuation_list,_,_ = ValuationCalculator.calc_val(val_table, code, analysis, currency)

                names = name
                if pdf != True:
                    #Using streamlit functions to display the table, title and currency on the GUI
                    st.pyplot(fig)
                    st.title(name)

                    st.subheader("Valuation Metrics")
                    st.write(valuation_list)

                    st.subheader(analysis + " Table")
                    st.write(currency)
                    st.write(table)
                else:
                    with tempfile.NamedTemporaryFile(delete=False, suffix=".png") as tmpfile:
                        fig.savefig(f"tmpfile.{code}_{analysis}.png")

            #If the data wasn't available the background of the company would be displayed instead
            else:
                if pdf != True:
                    text_list = rwb.CompanyGetter.get_company_background(rwb.NewsGetter.get_html(f"https://www.moneyweb.co.za/tools-and-data/click-a-company/{code}/"))

                    for text in text_list:
                        st.subheader(text)

        return table, valuation_list, names
    #This function returns the three indexes used for plotting the graphs in the financial_analysis feature
    def get_plot_indexes(numList, analysis):

        #Top three Financial metrics to graph for the income statement
        if analysis == "Income":

            TRIndex = numList.index("Total Revenue")
            try:
                GPIndex = numList.index("Gross Profit")
            except:
                GPIndex = numList.index("Pretax Income")

            NPIndex = numList.index("Net Income Common Stockholders")

        #Top three financial metrics to graph for the balance sheet
        elif analysis == "Assets":
            TRIndex = numList.index("Total Assets")
            try:
                GPIndex = numList.index("Net Debt")
            except:
                GPIndex = numList.index("Total Debt")

            NPIndex = numList.index("Total Equity Gross Minority Interest")

        #Top three financial metrics to graph for the cash flow items.
        else:
            TRIndex = numList.index("Operating Cash Flow")
            try:
                GPIndex = numList.index("Free Cash Flow")
            except:
                GPIndex = numList.index("End Cash Position")

            NPIndex = numList.index("Financing Cash Flow")

        return TRIndex, GPIndex, NPIndex
    #Method to plot the income statement graphs for either a single company or a sector

    def plot_chart(fig, ax, sharecodes, analysis):

        table, dates, currency, name = FinancialAnalyser.get_financial_info(sharecodes, analysis)
        table = table.to_numpy()
        #Get the plotting indexes for the graphs
        oneIndex, twoIndex, threeIndex = FinancialAnalyser.get_plot_indexes(list(table[:,0]), analysis)



        #Plotting the graph lines with markers
        ax.plot(dates, table[oneIndex,1:], marker='o')

        ax.plot(dates, table[twoIndex,1:], marker='o')

        ax.plot(dates, table[threeIndex,1:], marker='o')

        fig.legend((table[oneIndex,0], table[twoIndex,0], table[threeIndex,0]), loc = 7)

        return currency, dates, name

    def plot_finance(sharecodes, analysis):

        success = True
        #If it's only one share
        if isinstance(sharecodes, str) or len(sharecodes) == 1:
            try:
                if isinstance(sharecodes, list):
                    sharecodes = sharecodes[0]
                #Initialise the plotting figure to be dispalyed
                fig, ax = plt.subplots(figsize=(6, 6))

                currency, _ , _= FinancialAnalyser.plot_chart(fig, ax, sharecodes, analysis)
                plt.ylabel(currency)
                plt.xlabel('Time Periods')

                if analysis == "Income":
                    #Print the title of the graph
                    plt.title("Revenues and Profits")

                elif analysis == "Assets":
                    #Print the title of the graph
                    plt.title("Assets and Liabilities")

                else:
                    plt.title("Cash Flow Items")

            except:
                st.write(f"{sharecodes} Data is Not Available" )
                success = False

        else:
            rowLen = int(len(sharecodes) // 5) + 1
            colLen = 5
            rowCount = 1
            colCount = 1
            index = 1

            tot_count = 0

            if rowLen > 1:
                fig, ax = plt.subplots(nrows = rowLen, ncols = colLen, figsize=(16, 16))

                for row in ax:
                    for col in row:
                        code = sharecodes[tot_count]
                        try:
                            col.title.set_text(code)
                            currency, dates, name = FinancialAnalyser.plot_chart(col, col, code, analysis)
                            col.set_xticklabels(dates, rotation=45)
                        #If there's an error in the graphing process, the message below is displayed
                        except Exception as inst:
                            st.write(f"{code} {analysis} Data is Not Available" )
                            st.write(f"{inst}" )

                        tot_count += 1
                        if len(sharecodes) == tot_count:
                            tot_count -= 1

            #If the amount of companies is less than five
            else:
                #Custom number of columns in the plotted figure
                colLen = len(sharecodes)

                #Initialise plotting figures for the specified column length on one row
                fig, ax = plt.subplots(nrows = rowLen, ncols = colLen, figsize=(16, 8))
                for row in ax:
                    code = sharecodes[tot_count]
                    try:

                        currency, dates, name  = FinancialAnalyser.plot_chart(row, row, code, analysis)
                        row.set_xticklabels(dates, rotation=45)

                        row.title.set_text(name)
                    #If there's an error in the graphing process, the message below is displayed
                    except:
                        st.write(f"{code} {analysis} Data is Not Available" )

                    tot_count += 1
                    if len(sharecodes) == tot_count:
                        tot_count -= 1

            if analysis == "Income":
                #Print the title of the graph
                plt.suptitle("Revenues and Profits")

            elif analysis == "Assets":
                #Print the title of the graph
                plt.suptitle("Assets and Liabilities")

            else:
                plt.suptitle("Cash Flow Items")


        return success, fig
