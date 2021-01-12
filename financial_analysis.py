import request_web as rwb
import matplotlib.pyplot as plt
import numpy as np
import streamlit as st


class FinancialAnalyser():

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

                #Using streamlit functions to display the table, title and currency on the GUI
                st.title(name)
                st.write(currency)
                st.write(table)

            #If the data wasn't available the background of the company would be displayed instead
            else:
                text_list = rwb.CompanyGetter.get_company_background(rwb.NewsGetter.get_html(f"https://www.moneyweb.co.za/tools-and-data/click-a-company/{code}/"))

                for text in text_list:
                    st.subheader(text)



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

                plt.title("Revenues and Profits")
                ax.plot(dates, numTable[0,1:], marker='o')
                ax.plot(dates, numTable[2,1:], marker='o')
                ax.plot(dates, numTable[8,1:], marker='o')
                plt.legend((numTable[0,0], numTable[2,0], numTable[8,0]))
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
                            col.plot(dates, numTable[0,1:], marker='o')
                            col.plot(dates, numTable[2,1:], marker='o')
                            col.plot(dates, numTable[8,1:], marker='o')
                            col.set_xticklabels(dates, rotation=45)
                            col.legend((numTable[0,0], numTable[2,0],numTable[8,0]))

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
                        row.plot(dates, numTable[0,1:], marker='o')
                        row.plot(dates, numTable[2,1:], marker='o')
                        row.plot(dates, numTable[8,1:], marker='o')
                        row.set_xticklabels(dates, rotation=45)
                        row.legend((numTable[0,0], numTable[2,0], numTable[8,0]))

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
                ax.plot(dates, numTable[0,1:], marker='o')
                ax.plot(dates, numTable[6,1:], marker='o')
                ax.plot(dates, numTable[3,1:], marker='o')
                plt.legend((numTable[0,0], numTable[6,0], numTable[3,0]))
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
                            col.plot(dates, numTable[0,1:], marker='o')
                            col.plot(dates, numTable[2,1:], marker='o')
                            col.plot(dates, numTable[1,1:], marker='o')
                            col.set_xticklabels(dates, rotation=45)
                            col.legend((numTable[0,0], numTable[2,0], numTable[1,0]))

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
                        row.plot(dates, numTable[0,1:], marker='o')
                        row.plot(dates, numTable[1,1:], marker='o')
                        row.plot(dates, numTable[2,1:], marker='o')
                        row.set_xticklabels(dates, rotation=45)
                        row.legend((numTable[0,0], numTable[1,0], numTable[2,0]))

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

                if isinstance(sharecodes, list):
                    sharecodes = sharecodes[0]
                #Function to retrieve the table and dates for the specified company and analysis
                table, dates, currency, name = FinancialAnalyser.get_financial_info(sharecodes, analysis)
                numTable = table.to_numpy()

                #Initialise the plotting figure to be dispalyed
                fig, ax = plt.subplots(figsize=(6, 6))

                top_gain = (numTable[0,1] - numTable[0,-1]) / numTable[0,-1]
                top_profit = numTable[0,1]
                top_share = sharecodes

                imp_share = sharecodes
                st.title(name)
                plt.title("Cash Flow Items")
                ax.plot(dates, numTable[0,1:], marker='o')
                ax.plot(dates, numTable[2,1:], marker='o')
                ax.plot(dates, numTable[4,1:], marker='o')
                plt.legend((numTable[0,0], numTable[2,0], numTable[4,0]))
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
                            col.plot(dates, numTable[0,1:], marker='o')
                            col.plot(dates, numTable[2,1:], marker='o')
                            col.plot(dates, numTable[4,1:], marker='o')
                            col.set_xticklabels(dates, rotation=45)
                            col.legend((numTable[0,0], numTable[2,0], numTable[4,0]))

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
                        row.plot(dates, numTable[0,1:], marker='o')
                        row.plot(dates, numTable[2,1:], marker='o')
                        row.plot(dates, numTable[4,1:], marker='o')
                        row.set_xticklabels(dates, rotation=45)
                        row.legend((numTable[0,0], numTable[2,0], numTable[4,0]))

                    #If there's an error in the graphing process, the message below is displayed
                    except:
                        st.write(f"{code} Cash Flow Data is Not Available" )

                    tot_count += 1
                    if len(sharecodes) == tot_count:
                        tot_count -= 1

        st.pyplot(fig)
        return top_gain, top_profit, imp_share, top_share
