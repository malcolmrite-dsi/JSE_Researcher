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
                table = sharecodes
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
                    top_gain, top_assets, imp_share, top_share = plot_balance(sharecodes)

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

            if analysis == "Income":
                top_gain, top_profit, imp_share, top_share = FinancialAnalyser.plot_income(code)

            if analysis == "Assets":
                top_gain, top_profit, imp_share, top_share = FinancialAnalyser.plot_balance(code)


            if analysis == "Cash Flow":
                top_gain, top_profit, imp_share, top_share = FinancialAnalyser.plot_cash(code)

            if top_share != "":
                table, dates, currency, name = FinancialAnalyser.get_financial_info(top_share, analysis)

                st.title(name)
                st.write(currency)
                st.write(table)
            else:
                text_list = rwb.CompanyGetter.get_company_background(rwb.NewsGetter.get_html(f"https://www.moneyweb.co.za/tools-and-data/click-a-company/{code}/"))

                for text in text_list:
                    st.subheader(text)



    #Method to plot the income statement graphs for either a single company or a sector
    def plot_income(sharecodes):
        analysis = "Income"
        st.write(sharecodes)
        #If it's only one share
        if isinstance(sharecodes, str):
            try:
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

            rowLen = int(len(sharecodes) // 4) + 1
            colLen = 4
            rowCount = 1
            colCount = 1
            index = 1
            fig, ax = plt.subplots(nrows = rowLen, ncols = colLen, figsize=(16, 12))

            top_profit = -100000
            top_gain = -1
            top_share = ""
            imp_share = ""
            plt.suptitle("Revenues and Profits")
            #tot_table= np.array([[0,0,0], [0,0,0], [0,0,0]])
            tot_count = 0

            st.write(ax)

            if rowLen > 1:

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
                            #col.plot(dates, numTable[2,1:], marker='o')
                            col.plot(dates, numTable[8,1:], marker='o')
                            col.set_xticklabels(dates, rotation=45)
                            col.legend((numTable[0,0], numTable[8,0]))
                        except:
                            st.write(f"{code} Data is Not Available" )

                        tot_count += 1
                        if len(sharecodes) == tot_count:
                            tot_count -= 1
            else:
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
                        row.title.set_text(code)
                        row.plot(dates, numTable[0,1:], marker='o')
                        col.plot(dates, numTable[8,1:], marker='o')
                        #row.plot(dates, numTable[8,1:], marker='o')
                        row.set_xticklabels(dates, rotation=45)
                        row.legend((numTable[0,0], numTable[8,0]))
                    except:
                        st.write(f"{code} Data is Not Available" )

                    tot_count += 1
                    if len(sharecodes) == tot_count:
                        tot_count -= 1

        st.pyplot(fig)
        return top_gain, top_profit, imp_share, top_share

    def plot_balance(sharecodes):
        analysis = "Assets"
        st.write(sharecodes)
        if isinstance(sharecodes, str):
            try:
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
                plt.title("Assets and Liabilities")
                ax.plot(dates, numTable[0,1:], marker='o')
                ax.plot(dates, numTable[6,1:], marker='o')
                ax.plot(dates, numTable[3,1:], marker='o')
                plt.legend((numTable[0,0], numTable[6,0], numTable[3,0]))
                plt.xlabel('Time Periods')
                plt.ylabel(currency)
            except:
                st.write(f"{sharecodes} Data is Not Available" )
                top_gain = 0
                top_profit = 0
                top_share = ""
                imp_share = sharecodes
        else:

            rowLen = int(len(sharecodes) // 4) + 1
            colLen = 4
            rowCount = 1
            colCount = 1
            index = 1
            fig, ax = plt.subplots(nrows = rowLen, ncols = colLen, figsize=(16, 12))

            top_profit = -100000
            top_gain = -1
            top_share = ""
            imp_share = ""
            plt.suptitle("Assets and Liabilities")
            #tot_table= np.array([[0,0,0], [0,0,0], [0,0,0]])
            tot_count = 0

            st.write(ax)

            if rowLen > 1:

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
                            #col.plot(dates, numTable[2,1:], marker='o')
                            col.plot(dates, numTable[8,1:], marker='o')
                            col.set_xticklabels(dates, rotation=45)
                            col.legend((numTable[0,0], numTable[8,0]))
                        except:
                            st.write(f"{code} Data is Not Available" )

                        tot_count += 1
                        if len(sharecodes) == tot_count:
                            tot_count -= 1
            else:
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
                        row.title.set_text(code)
                        row.plot(dates, numTable[0,1:], marker='o')
                        col.plot(dates, numTable[8,1:], marker='o')
                        #row.plot(dates, numTable[8,1:], marker='o')
                        row.set_xticklabels(dates, rotation=45)
                        row.legend((numTable[0,0], numTable[8,0]))
                    except:
                        st.write(f"{code} Data is Not Available" )

                    tot_count += 1
                    if len(sharecodes) == tot_count:
                        tot_count -= 1

        st.pyplot(fig)
        return top_gain, top_profit, imp_share, top_share

    def plot_cash(sharecodes):
        analysis = "Cash Flow"
        st.write(sharecodes)
        if isinstance(sharecodes, str):
            try:
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
                ax.plot(dates, numTable[0,1:], marker='o')
                ax.plot(dates, numTable[2,1:], marker='o')
                ax.plot(dates, numTable[4,1:], marker='o')
                plt.legend((numTable[0,0], numTable[2,0], numTable[4,0]))
                plt.xlabel('Time Periods')
                plt.ylabel(currency)
            except:
                st.write(f"{sharecodes} Data is Not Available" )
                top_gain = 0
                top_profit = 0
                top_share = ""
                imp_share = sharecodes
        else:

            rowLen = int(len(sharecodes) // 5) + 1
            colLen = 5
            rowCount = 1
            colCount = 1
            index = 1
            fig, ax = plt.subplots(nrows = rowLen, ncols = colLen, figsize=(16, 12))

            top_profit = -100000
            top_gain = -1
            top_share = ""
            imp_share = ""
            plt.suptitle("Cash Flow Items")
            #tot_table= np.array([[0,0,0], [0,0,0], [0,0,0]])
            tot_count = 0

            st.write(ax)

            if rowLen > 1:

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
                            ax.plot(dates, numTable[0,1:], marker='o')
                            ax.plot(dates, numTable[2,1:], marker='o')
                            ax.plot(dates, numTable[4,1:], marker='o')
                            col.set_xticklabels(dates, rotation=45)
                            col.legend((numTable[0,0], numTable[2,0], numTable[4,0]))
                        except:
                            st.write(f"{code} Data is Not Available" )

                        tot_count += 1
                        if len(sharecodes) == tot_count:
                            tot_count -= 1
            else:
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
                        row.title.set_text(code)
                        ax.plot(dates, numTable[0,1:], marker='o')
                        ax.plot(dates, numTable[2,1:], marker='o')
                        ax.plot(dates, numTable[4,1:], marker='o')
                        row.set_xticklabels(dates, rotation=45)
                        row.legend((numTable[0,0], numTable[2,0], numTable[4,0]))
                    except:
                        st.write(f"{code} Data is Not Available" )

                    tot_count += 1
                    if len(sharecodes) == tot_count:
                        tot_count -= 1

        st.pyplot(fig)
        return top_gain, top_profit, imp_share, top_share
