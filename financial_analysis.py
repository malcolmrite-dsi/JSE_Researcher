import request_web as rwb
import matplotlib.pyplot as plt
import numpy as np
import streamlit as st


#For reference: https://www.toptal.com/finance/valuation/valuation-ratios
#https://www.investopedia.com/ask/answers/102714/what-are-main-income-statement-ratios.asp
class ValuationCalculator():
    def get_item_list(table):
        item_list = list(table[:,0])

        return item_list


    def calc_income_val(sharecode):

        return valuation_list


    def calc_val(table, sharecode, analysis):

        #Returns the current stock price of the selected company
        price = rwb.FinancialGetter.get_stock_price(sharecode)

        #Initialise the list to store the valuation metrics
        valuation_list = []

        #Returns the labels of the selected table as alist, to obtain the index later
        item_list = ValuationCalculator.get_item_list(table)

        #Returns the common valuation metrics for an income statement
        if analysis == "Income":

            noShares = table[item_list.index("Basic Average Shares"), 1]

            earnings = table[item_list.index("Net Income Common Stockholders"), 1]

            try:
                ebit = table[item_list.index("EBIT"), 1]
            except:
                ebit = 0

            try:
                intExpense = table[item_list.index("Interest Expense"), 1]
            except:
                intExpense = 0

            #Total Revenue of the company
            sales = table[item_list.index("Total Revenue"), 1]


            #Profit Margin
            valuation_list.append(str((round(((earnings) / sales), 4)) * 100) + "%")

            #Price to Earnings
            #https://www.investopedia.com/ask/answers/070314/how-do-i-calculate-pe-ratio-company.asp
            valuation_list.append(round(((noShares * price) / earnings), 2))

            #Price to Sales
            valuation_list.append(round(((noShares * price) / sales), 2))

            #Earnings per Share
            valuation_list.append(table[item_list.index("Basic EPS"), 1])

            #Times Interest Payment
            if intExpense != 0:
                valuation_list.append(round(((ebit) / intExpense), 2))

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
            noShares = inc_table[inc_item_list.index("Basic Average Shares"), 1]

            #Total Revenue of the company
            sales = inc_table[inc_item_list.index("Total Revenue"), 1]

            #Net Profit of the company
            earnings = inc_table[inc_item_list.index("Net Income Common Stockholders"), 1]

            if analysis == "Assets":

                #Total Assets
                totAssets = table[item_list.index("Total Assets"),1]

                #Net Tangible Assets: https://www.investopedia.com/terms/n/nettangibleassets.asp
                netTangAssets = table[item_list.index("Net Tangible Assets"),1]

                #For Minority Interest Definition: https://www.thebalance.com/minority-interest-on-the-balance-sheet-357286
                totLiabilities = table[item_list.index("Total Liabilities Net Minority Interest"),1]

                noShares = table[item_list.index("Ordinary Shares Number"), 1]

                #Shareholder Equity
                totEquity = table[item_list.index("Total Equity Gross Minority Interest"), 1]

                #https://www.wallstreetmojo.com/net-tangible-assets/
                intangibles = totAssets - netTangAssets  - totLiabilities

                #Price to Book Value Ratio
                valuation_list.append(round(((noShares * price) / totEquity), 2))

                #Return on assets: https://www.ruleoneinvesting.com/blog/how-to-invest/important-financial-metrics-that-we-use/
                valuation_list.append(str((round((earnings / totAssets), 4)) * 100 ) + "%")

                #Return on Equity: https://www.investopedia.com/ask/answers/102714/what-are-main-income-statement-ratios.asp
                valuation_list.append(str((round((earnings / totEquity), 4)) * 100 ) + "%")

                #Debt to Equity ratio
                valuation_list.append(round(((totLiabilities) / totEquity), 2))

                #Intangibles to Equity ratio (Book Value)
                valuation_list.append(round(((intangibles) / totEquity), 2))

            #The common valuations metrics used for Cash Flow items
            #https://www.oldschoolvalue.com/stock-valuation/best-investing-metrics-ratios/
            else:
                #Free Cash Flow
                freeCF = table[item_list.index("Free Cash Flow"), 1]

                #Price to Free Cash Flow ratio: https://www.investopedia.com/articles/stocks/11/analyzing-price-to-cash-flow-ratio.asp
                valuation_list.append(round(((noShares * price) / freeCF), 2))

                #Free Cash Flow to Sales ratio as a percentage
                valuation_list.append(str((round((freeCF / sales), 4)) * 100 ) + "%")

        return valuation_list

class FinancialAnalyser():

    #This function applies the correct url to obtain the relevant financial table requested
    def get_financial_info(sharecode, analysis):

        if analysis == "Income":
            url = f"https://finance.yahoo.com/quote/{sharecode}.JO/financials?p={sharecode}.JO"
        elif analysis == "Assets":
            url = f"https://finance.yahoo.com/quote/{sharecode}.JO/balance-sheet?p={sharecode}.JO"
        else:
            url = f"https://finance.yahoo.com/quote/{sharecode}.JO/cash-flow?p={sharecode}.JO"

        table, dates, currency, name = rwb.FinancialGetter.get_statement(rwb.FinancialGetter.get_html(url), analysis)

        return table, dates, currency, name

    #General method to obtain graphs and tables for the financial analysis feature
    def get_financials(code, subject, analysis):
        if subject == "Sector":
            icb = rwb.SensGetter.get_icb_code("Sector_List.csv")

            value = icb.iloc[(icb["Share Code"]==code).argmax(),1]
            sharecodes = rwb.FinancialGetter.get_sector_data(value)

            #Display a warning message to the user if there aren't any companies in the sector selected.
            if len(sharecodes) == 0:
                st.write("No available companies listed under this sector.")

            else:
                if analysis == "Income":
                    top_gain, top_profit, imp_share, top_share = FinancialAnalyser.plot_income(sharecodes)

                    st.subheader("Sector Breakdown")
                    st.write(f"{top_share} achieved the highest recent net profit amounting to {top_profit}. The breakdown of their financials is below.")
                    st.write(f"{imp_share} achieved the highest improved gain in net profit over its recent history, amounting to {top_gain*100} %. The breakdown of their financials is below.")


                    top_table, top_dates, top_currency, top_name = FinancialAnalyser.get_financial_info(top_share, analysis)

                    st.title(top_name)
                    st.subheader(f"{top_share}")
                    st.write(top_currency)
                    st.write(top_table)

                    imp_table, imp_dates, imp_currency, imp_name = FinancialAnalyser.get_financial_info(imp_share, analysis)

                    st.title(imp_name)
                    st.subheader(f"{imp_share}")
                    st.write(imp_currency)
                    st.write(imp_table)

                elif analysis == "Assets":
                    top_gain, top_assets, imp_share, top_share = FinancialAnalyser.plot_balance(sharecodes)

                    st.subheader("Sector Breakdown")
                    st.write(f"{top_share} achieved the highest recent total assets amounting to {top_assets*1000}. The breakdown of their financials is below.")
                    st.write(f"{imp_share} achieved the highest improved gain in total assets over its recent history, amounting to {top_gain*100} %. The breakdown of their financials is below.")

                    #Getting the financial info of the most improved company
                    top_table, top_dates, top_currency, top_name = FinancialAnalyser.get_financial_info(top_share, analysis)
                    st.title(top_name)
                    st.subheader(f"{top_share}")
                    st.write(top_currency)
                    st.write(top_table)

                    #Getting the financial info of the most improved company
                    imp_table, imp_dates, imp_currency, imp_name = FinancialAnalyser.get_financial_info(imp_share, analysis)

                    st.title(imp_name)
                    st.subheader(f"{imp_share}")
                    st.write(imp_currency)
                    st.write(imp_table)

                else:
                    top_gain, top_assets, imp_share, top_share = FinancialAnalyser.plot_cash(sharecodes)

                    st.subheader("Sector Breakdown")
                    st.write(f"{top_share} achieved the highest recent total assets amounting to {top_assets*1000}. The breakdown of their financials is below.")
                    st.write(f"{imp_share} achieved the highest improved gain in total assets over its recent history, amounting to {top_gain*100} %. The breakdown of their financials is below.")

                    #Getting the financial info of the most improved company
                    top_table, top_dates, top_currency, top_name = FinancialAnalyser.get_financial_info(top_share, analysis)
                    st.title(top_name)
                    st.subheader(f"{top_share}")
                    st.write(top_currency)
                    st.write(top_table)

                    #Getting the financial info of the most improved company
                    imp_table, imp_dates, imp_currency, imp_name = FinancialAnalyser.get_financial_info(imp_share, analysis)

                    st.title(imp_name)
                    st.subheader(f"{imp_share}")
                    st.write(imp_currency)
                    st.write(imp_table)

        #In financial analysis, if company is selected, this code displays the graph and data for the company
        if subject == "Company":

            #This condition graphs the income statement data of the specified company
            if analysis == "Income":
                top_gain, top_profit, imp_share, top_share = FinancialAnalyser.plot_income(code)

            #This condition graphs the balance sheet data of the specified company
            if analysis == "Assets":
                top_gain, top_profit, imp_share, top_share = FinancialAnalyser.plot_balance(code)

            #This condition graphs the cash flow items data of the specified company
            if analysis == "Cash Flow":
                top_gain, top_profit, imp_share, top_share = FinancialAnalyser.plot_cash(code)

            #If the data was avaible this condition displays the table specified with its title and currency
            if top_share != "":
                table, dates, currency, name = FinancialAnalyser.get_financial_info(top_share, analysis)
                table = table.to_numpy()
                valuation_list = ValuationCalculator.calc_val(table, code, analysis)

                #Using streamlit functions to display the table, title and currency on the GUI
                st.title(name)

                st.subheader("Valuation Metrics")
                st.write(valuation_list)

                st.subheader(analysis + " Table")
                st.write(currency)
                st.write(table)

            #If the data wasn't available the background of the company would be displayed instead
            else:
                text_list = rwb.CompanyGetter.get_company_background(rwb.NewsGetter.get_html(f"https://www.moneyweb.co.za/tools-and-data/click-a-company/{code}/"))

                for text in text_list:
                    st.subheader(text)

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
    def plot_income(sharecodes):
        analysis = "Income"

        #If it's only one share
        if isinstance(sharecodes, str) or len(sharecodes) == 1:
            try:
                if isinstance(sharecodes, list):
                    sharecodes = sharecodes[0]
                #Initialise the plotting figure to be dispalyed
                fig, ax = plt.subplots(figsize=(6, 6))

                table, dates, currency, name = FinancialAnalyser.get_financial_info(sharecodes, analysis)
                numTable = table.to_numpy()

                top_gain = (numTable[8,1] - numTable[8,-1]) / numTable[8,-1]
                top_profit = numTable[8,1]
                top_share = sharecodes

                imp_share = sharecodes
                st.title(name)

                #Print the title of the graph
                plt.title("Revenues and Profits")

                #Get the plotting indexes for the graphs
                oneIndex, twoIndex, threeIndex = FinancialAnalyser.get_plot_indexes(list(numTable[:,0]), analysis)

                #Plotting the graph lines with markers
                ax.plot(dates, numTable[oneIndex,1:], marker='o')

                ax.plot(dates, numTable[twoIndex,1:], marker='o')

                ax.plot(dates, numTable[threeIndex,1:], marker='o')

                plt.legend((numTable[oneIndex,0], numTable[twoIndex,0], numTable[threeIndex,0]))
                plt.xlabel('Time Periods')
                plt.ylabel(currency)


            except:
                st.write(f"{sharecodes} Data is Not Available" )
                top_gain = 0
                top_profit = 0
                top_share = ""
                imp_share = sharecodes

        #if it's multiple shares
        else:
            st.subheader("Shares in Sector:")
            st.write(sharecodes)
            rowLen = int(len(sharecodes) // 5) + 1
            colLen = 5
            rowCount = 1
            colCount = 1
            index = 1


            top_profit = -100000000
            top_gain = -10
            top_share = ""
            imp_share = ""
            plt.suptitle("Revenues and Profits")

            tot_count = 0

            if rowLen > 1:
                fig, ax = plt.subplots(nrows = rowLen, ncols = colLen, figsize=(16, 16))

                for row in ax:
                    for col in row:
                        code = sharecodes[tot_count]

                        try:
                            table, dates, currency, name = FinancialAnalyser.get_financial_info(code, analysis)
                            numTable = table.to_numpy()
                            if numTable[8,1] >= top_profit:
                                top_profit = numTable[8,1]
                                top_share = code

                            gain = (numTable[8,1] - numTable[8,-1]) / numTable[8,-1]
                            if gain >= top_gain:
                                top_gain = gain
                                imp_share = code
                            col.title.set_text(code)
                            #Get the plotting indexes for the graphs
                            oneIndex, twoIndex, threeIndex = FinancialAnalyser.get_plot_indexes(list(numTable[:,0]), analysis)

                            #Plotting the graph lines with markers
                            col.plot(dates, numTable[oneIndex,1:], marker='o')

                            col.plot(dates, numTable[twoIndex,1:], marker='o')

                            col.plot(dates, numTable[threeIndex,1:], marker='o')

                            col.legend((numTable[oneIndex,0], numTable[twoIndex,0], numTable[threeIndex,0]))
                            col.set_xticklabels(dates, rotation=45)

                        #If there's an error in the graphing process, the message below is displayed
                        except:
                            st.write(f"{code} Income Statement Data is Not Available" )

                        tot_count += 1
                        if len(sharecodes) == tot_count:
                            tot_count -= 1
            #If the amount of companies is less than five
            else:
                colLen = len(sharecodes)

                #Initialise plotting figures for the specified column length on one row
                fig, ax = plt.subplots(nrows = rowLen, ncols = colLen, figsize=(16, 8))
                for row in ax:
                    code = sharecodes[tot_count]

                    try:
                        table, dates, currency, name = FinancialAnalyser.get_financial_info(code, analysis)
                        numTable = table.to_numpy()
                        if numTable[8,1] >= top_profit:
                            top_profit = numTable[8,1]
                            top_share = code

                        gain = (numTable[8,1] - numTable[8,-1]) / numTable[8,-1]
                        if gain >= top_gain:
                            top_gain = gain
                            imp_share = code

                        #Display the company name for each graph
                        row.title.set_text(name)
                        #Get the plotting indexes for the graphs
                        oneIndex, twoIndex, threeIndex = FinancialAnalyser.get_plot_indexes(list(numTable[:,0]), analysis)

                        #Plotting the graph lines with markers
                        row.plot(dates, numTable[oneIndex,1:], marker='o')

                        row.plot(dates, numTable[twoIndex,1:], marker='o')

                        row.plot(dates, numTable[threeIndex,1:], marker='o')

                        row.legend((numTable[oneIndex,0], numTable[twoIndex,0], numTable[threeIndex,0]))
                        row.set_xticklabels(dates, rotation=45)


                    #If there's an error in the graphing process, the message below is displayed
                    except:
                        st.write(f"{code} Income Statement Data is Not Available" )

                    tot_count += 1
                    if len(sharecodes) == tot_count:
                        tot_count -= 1

        st.pyplot(fig)
        return top_gain, top_profit, imp_share, top_share

    def plot_balance(sharecodes):
        analysis = "Assets"

        if isinstance(sharecodes, str) or len(sharecodes) == 1:
            try:
                #Initialise the plotting figure to be dispalyed
                fig, ax = plt.subplots(figsize=(6, 6))

                if isinstance(sharecodes, list):
                    sharecodes = sharecodes[0]
                #Function to retrieve the table and dates for the specified company and analysis
                table, dates, currency, name = FinancialAnalyser.get_financial_info(sharecodes, analysis)
                numTable = table.to_numpy()

                top_gain = (numTable[0,1] - numTable[0,-1]) / numTable[0,-1]
                top_profit = numTable[0,1]
                top_share = sharecodes

                imp_share = sharecodes
                st.title(name)
                plt.title("Assets and Liabilities")
                #Get the plotting indexes for the graphs
                oneIndex, twoIndex, threeIndex = FinancialAnalyser.get_plot_indexes(list(numTable[:,0]), analysis)

                #Plotting the graph lines with markers
                ax.plot(dates, numTable[oneIndex,1:], marker='o')

                ax.plot(dates, numTable[twoIndex,1:], marker='o')

                ax.plot(dates, numTable[threeIndex,1:], marker='o')

                plt.legend((numTable[oneIndex,0], numTable[twoIndex,0], numTable[threeIndex,0]))

                plt.xlabel('Time Periods')
                plt.ylabel(currency)

            #If there's an error in the graphing process, the message below is displayed
            except:
                st.write(f"{sharecodes} Balance Sheet Data is Not Available" )
                top_gain = 0
                top_profit = 0
                top_share = ""
                imp_share = sharecodes
        #if it's multiple shares
        else:
            st.subheader("Shares in Sector:")
            st.write(sharecodes)

            rowLen = int(len(sharecodes) // 5) + 1
            colLen = 5
            rowCount = 1
            colCount = 1
            index = 1


            top_profit = -100000
            top_gain = -1
            top_share = ""
            imp_share = ""
            plt.suptitle("Assets and Liabilities")

            tot_count = 0


            if rowLen > 1:
                fig, ax = plt.subplots(nrows = rowLen, ncols = colLen, figsize=(16, 16))
                for row in ax:
                    for col in row:
                        code = sharecodes[tot_count]

                        try:
                            table, dates, currency, name = FinancialAnalyser.get_financial_info(code, analysis)
                            numTable = table.to_numpy()
                            if numTable[0,1] >= top_profit:
                                top_profit = numTable[0,1]
                                top_share = code

                            gain = (numTable[0,1] - numTable[0,-1]) / numTable[0,-1]
                            if gain >= top_gain:
                                top_gain = gain
                                imp_share = code
                            col.title.set_text(code)
                            #Get the plotting indexes for the graphs
                            oneIndex, twoIndex, threeIndex = FinancialAnalyser.get_plot_indexes(list(numTable[:,0]), analysis)

                            #Plotting the graph lines with markers
                            col.plot(dates, numTable[oneIndex,1:], marker='o')

                            col.plot(dates, numTable[twoIndex,1:], marker='o')

                            col.plot(dates, numTable[threeIndex,1:], marker='o')

                            col.legend((numTable[oneIndex,0], numTable[twoIndex,0], numTable[threeIndex,0]))
                            col.set_xticklabels(dates, rotation=45)

                        #If there's an error in the graphing process, the message below is displayed
                        except:
                            st.write(f"{code} Balance Sheet Data is Not Available" )

                        tot_count += 1
                        if len(sharecodes) == tot_count:
                            tot_count -= 1

            #Condition if the amount of companies is less than five
            else:
                colLen = len(sharecodes)
                fig, ax = plt.subplots(nrows = rowLen, ncols = colLen, figsize=(16, 8))
                for row in ax:
                    code = sharecodes[tot_count]

                    try:
                        table, dates, currency, name = FinancialAnalyser.get_financial_info(code, analysis)
                        numTable = table.to_numpy()
                        if numTable[0,1] >= top_profit:
                            top_profit = numTable[0,1]
                            top_share = code

                        gain = (numTable[0,1] - numTable[0,-1]) / numTable[0,-1]
                        if gain >= top_gain:
                            top_gain = gain
                            imp_share = code

                        #Display the company name for each graph
                        row.title.set_text(name)
                        #Get the plotting indexes for the graphs
                        oneIndex, twoIndex, threeIndex = FinancialAnalyser.get_plot_indexes(list(numTable[:,0]), analysis)

                        #Plotting the graph lines with markers
                        row.plot(dates, numTable[oneIndex,1:], marker='o')

                        row.plot(dates, numTable[twoIndex,1:], marker='o')

                        row.plot(dates, numTable[threeIndex,1:], marker='o')

                        row.legend((numTable[oneIndex,0], numTable[twoIndex,0], numTable[threeIndex,0]))
                        row.set_xticklabels(dates, rotation=45)
                    #If there's an error in the graphing process, the message below is displayed
                    except:
                        st.write(f"{code} Balance Sheet Data is Not Available" )

                    tot_count += 1
                    if len(sharecodes) == tot_count:
                        tot_count -= 1

        st.pyplot(fig)
        return top_gain, top_profit, imp_share, top_share

    def plot_cash(sharecodes):
        analysis = "Cash Flow"


        #If company was selected for subject, or there's only one company in the sector
        if isinstance(sharecodes, str) or len(sharecodes) == 1:

            try:

                #Extract the sigle sharecode if the sector list only has one company
                if isinstance(sharecodes, list):
                    sharecodes = sharecodes[0]

                #Initialise the plotting figure to be dispalyed
                fig, ax = plt.subplots(figsize=(6, 6))

                #Function to retrieve the table and dates for the specified company and analysis
                table, dates, currency, name = FinancialAnalyser.get_financial_info(sharecodes, analysis)
                numTable = table.to_numpy()


                top_gain = (numTable[0,1] - numTable[0,-1]) / numTable[0,-1]
                top_profit = numTable[0,1]
                top_share = sharecodes

                imp_share = sharecodes
                st.title(name)
                plt.title("Cash Flow Items")
                #Get the plotting indexes for the graphs
                oneIndex, twoIndex, threeIndex = FinancialAnalyser.get_plot_indexes(list(numTable[:,0]), analysis)

                #Plotting the graph lines with markers
                ax.plot(dates, numTable[oneIndex,1:], marker='o')

                ax.plot(dates, numTable[twoIndex,1:], marker='o')

                ax.plot(dates, numTable[threeIndex,1:], marker='o')
                ax.legend((numTable[oneIndex,0], numTable[twoIndex,0], numTable[threeIndex,0]))


                plt.xlabel('Time Periods')
                plt.ylabel(currency)

            #If there's an error in the graphing process, the message below is displayed
            except:
                st.write(f"{sharecodes} Cash Flow Data is Not Available" )
                top_gain = 0
                top_profit = 0
                top_share = ""
                imp_share = sharecodes

        #if it's multiple shares
        else:

            st.subheader("Shares in Sector:")
            st.write(sharecodes)
            rowLen = int(len(sharecodes) // 5) + 1
            colLen = 5
            rowCount = 1
            colCount = 1
            index = 1


            top_profit = -100000
            top_gain = -1
            top_share = ""
            imp_share = ""
            plt.suptitle("Cash Flow Items")

            tot_count = 0


            if rowLen > 1:
                fig, ax = plt.subplots(nrows = rowLen, ncols = colLen, figsize=(16, 16))
                for row in ax:
                    for col in row:
                        code = sharecodes[tot_count]


                        try:
                            table, dates, currency, name = FinancialAnalyser.get_financial_info(code, analysis)
                            numTable = table.to_numpy()
                            if numTable[0,1] >= top_profit:
                                top_profit = numTable[0,1]
                                top_share = code

                            gain = (numTable[0,1] - numTable[0,-1]) / numTable[0,-1]
                            if gain >= top_gain:
                                top_gain = gain
                                imp_share = code

                            #Display the company name for each graph
                            col.title.set_text(code)
                            #Get the plotting indexes for the graphs
                            oneIndex, twoIndex, threeIndex = FinancialAnalyser.get_plot_indexes(list(numTable[:,0]), analysis)

                            #Plotting the graph lines with markers
                            col.plot(dates, numTable[oneIndex,1:], marker='o')

                            col.plot(dates, numTable[twoIndex,1:], marker='o')

                            col.plot(dates, numTable[threeIndex,1:], marker='o')

                            col.legend((numTable[oneIndex,0], numTable[twoIndex,0], numTable[threeIndex,0]))
                            col.set_xticklabels(dates, rotation=45)
                        #If there's an error in the graphing process, the message below is displayed
                        except:
                            st.write(f"{code} Cash Flow Data is Not Available" )

                        tot_count += 1
                        if len(sharecodes) == tot_count:
                            tot_count -= 1

            #Condition if the amount of companies is less than five
            else:
                colLen = len(sharecodes)
                fig, ax = plt.subplots(nrows = rowLen, ncols = colLen, figsize=(16, 8))
                for row in ax:
                    code = sharecodes[tot_count]

                    try:
                        table, dates, currency, name = FinancialAnalyser.get_financial_info(code, analysis)
                        numTable = table.to_numpy()
                        if numTable[0,1] >= top_profit:
                            top_profit = numTable[0,1]
                            top_share = code

                        gain = (numTable[0,1] - numTable[0,-1]) / numTable[0,-1]
                        if gain >= top_gain:
                            top_gain = gain
                            imp_share = code

                        #Display the company name for each graph
                        row.title.set_text(name)
                        #Get the plotting indexes for the graphs
                        oneIndex, twoIndex, threeIndex = FinancialAnalyser.get_plot_indexes(list(numTable[:,0]), analysis)

                        #Plotting the graph lines with markers
                        row.plot(dates, numTable[oneIndex,1:], marker='o')

                        row.plot(dates, numTable[twoIndex,1:], marker='o')

                        row.plot(dates, numTable[threeIndex,1:], marker='o')

                        row.legend((numTable[oneIndex,0], numTable[twoIndex,0], numTable[threeIndex,0]))
                        row.set_xticklabels(dates, rotation=45)
                    #If there's an error in the graphing process, the message below is displayed
                    except:
                        st.write(f"{code} Cash Flow Data is Not Available" )

                    tot_count += 1
                    if len(sharecodes) == tot_count:
                        tot_count -= 1

        st.pyplot(fig)
        return top_gain, top_profit, imp_share, top_share
