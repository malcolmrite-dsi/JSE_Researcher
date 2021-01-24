from fpdf import FPDF, HTMLMixin

import text_analysis as ta

#Importing custom library for web scraping
import request_web as rwb
#Importing custom library for financial analysis
from financial_analysis import FinancialAnalyser as fa
import os

class PDFGenerator():

    #Takes 6 arguments for the different operations
    def generate_report(code,time_period, detail, subject, options, finOptions):
        # save FPDF() class into a
        class MyFPDF(FPDF, HTMLMixin):
            pass

        # variable pdf
        pdf = FPDF()
        pdf.set_title(f"{code} Investment Report")

        PDFGenerator.create_intro_page(pdf,code, options)

        if "Company Background" in options:
            pdf.add_page()

            PDFGenerator.create_company_background(pdf,code)

            pdf.add_page()

            PDFGenerator.create_management_table(pdf,code)


        if "News Analysis" in options:
            pdf.add_page()

            PDFGenerator.create_news_analysis(pdf, code, time_period, detail, subject)

        if "Financial Analysis" in options:
            pdf.add_page()

            PDFGenerator.generate_financial_analysis(pdf, code, subject, finOptions)

        if "Latest SENS" in options:
            pdf.add_page()

            PDFGenerator.generate_latest_sens(pdf, code)


        # save the pdf with name .pdf
        report = pdf.output(dest="S")
        return report

    def create_intro_page(self, code, options):

        # Add a page
        self.add_page()

        # set style and size of font
        # that you want in the pdf
        self.set_font("Arial","B", size = 24)

        # create a cell
        self.cell(200, 60, txt = f"{code} Investment Report",
                 ln = 1, align = 'C')

        self.set_font("Arial","B", size = 18)
        self.cell(200, 20, txt = f"This Report Includes:",
                 ln = 10, align = 'C')
        self.set_font("Helvetica", size = 14)
        for feature in options:

            self.multi_cell(200, 10, txt = feature,
                      align = 'C')


    def create_company_background(self,code):

        # set style and size of font
        # that you want in the pdf
        self.set_font("Helvetica", "B",size = 24)

        text_list = rwb.CompanyGetter.get_company_background(rwb.NewsGetter.get_html(f"https://www.moneyweb.co.za/tools-and-data/click-a-company/{code}/"))

        # create a cell
        self.cell(200, 20, txt = f"{code} Company Background",
                 ln = 1, align = 'C')

        self.set_font("Helvetica",size = 11)
        # add another cell

        for text in text_list:


            text = text.encode('latin-1', 'replace').decode('latin-1')
            self.multi_cell(200, 5, txt = text,
                      align = 'L')
            self.cell(200, 5, txt = "---------------------------------------------------------------------",
                     ln = 1, align = 'L')

    def create_news_analysis(self, code, time_period, detail, subject):
        all_headlines, all_links, full_scores, full_labels, highestSent, lowestSent, sumScore = ta.NewsAnalyser.get_news_in_app(code, time_period, detail, subject)

        if len(all_headlines) >= 1:
            self.set_font("Helvetica", "B",size = 24)
            self.cell(200, 20, txt = f"{code} News Analysis",
                     ln = 1, align = 'C')
            self.set_font("Helvetica", "B",size = 12)
            self.multi_cell(200, 7,txt = "The News Analysis Summary Below. The content was found to be:")
            score = str(sumScore/(int(len(all_headlines))))
            self.multi_cell(200, 7,txt = ta.NewsAnalyser.add_label(float(score)))

            self.multi_cell(200, 7,txt = "With a Score of: {0:0.3f}".format(float(score)))

            self.set_font("Helvetica",size = 12, style = "I")
            self.multi_cell(200, 7,align = 'L',txt = "The most positive headline is {0}, with a score of {1}, {2}. Here's the link: {3}".format(all_headlines[highestSent], full_scores[highestSent] , full_labels[highestSent], all_links[highestSent]))
            self.multi_cell(200, 7, align = 'L',txt = "The most negative headline is {0}, with a score of {1}, {2}. Here's the link: {3}".format(all_headlines[lowestSent], full_scores[lowestSent], full_labels[lowestSent], all_links[lowestSent]))

            self.multi_cell(200, 5, txt = "---------------------------------------------------------------------",
                     align = 'L')

            for  i, head in enumerate(all_headlines):
                self.set_font("Helvetica", "B",size = 11)
                self.multi_cell(200, 5,txt = head)

                self.set_font("Helvetica",size = 11, style = "U")
                self.multi_cell(200, 5,txt = all_links[i])
                self.set_font("Helvetica",size = 11)
                text = str(full_scores[i]) + "  " + str(full_labels[i])
                self.multi_cell(200, 5,txt = text)
                self.multi_cell(200, 5, txt = "---------------------------------------------------------------------",
                         align = 'L')

        elif len(all_headlines) == 0:
            self.cell(200, 2,txt = "There are currently no headlines for this company.")

    def create_management_table(self, code):
        #For reference: https://pyfpdfbook.wordpress.com/2015/03/22/table-using-only-cell-borders/
                # Remember to always put one of these at least once.
        self.set_font("Helvetica",size = 11)

        # Effective page width, or just epw
        epw = self.w - 2*self.l_margin

        # Set column width to 1/4 of effective page width to distribute content
        # evenly across table and page
        col_width = epw/3

        # Since we do not need to draw lines anymore, there is no need to separate
        # headers from data matrix.
        try:
            data =  rwb.CompanyGetter.get_management(rwb.NewsGetter.get_html(f"https://finance.yahoo.com/quote/{code}.JO/profile?p={code}.JO"))
        except:
            data = ["Data is not available"]

        # Text height is the same as current font size
        th = self.font_size

        # Line break equivalent to 4 lines
        self.ln(4*th)

        self.set_font("Helvetica",style = "B", size = 11)
        self.cell(epw, 0.0, 'Management Team', align='C')
        self.set_font("Helvetica",size = 9)
        self.ln(2* th)
        data = data.to_numpy()
        # Here we add more padding by passing 2*th as height
        #Can't Text Wrap with this particular module, without breaking the table
        for row in data:
            col_count = 0
            for datum in row:
                # Enter data in colums
                #Dictates column widths for the table
                col_width_dict = {0: epw*(4/10), 1:epw/2, 2:epw/10}

                self.cell(col_width_dict[col_count], 2*th, str(datum), border=1)
                col_count += 1

            self.ln(2*th)
    def add_table_header(self, table, epw, subject):
        columns = table.columns
        #Set header font style
        self.set_font("Helvetica",style = "B",size = 9)
        # Text height is the same as current font size
        th = self.font_size
        #Dictates column widths for the table
        if subject == "Company":
            col_width = epw / (len(columns))
        else:
            col_width = epw / (len(columns) + 1)
            self.cell(col_width, 2*th, "Index/Share Codes", border=1)

        for col in columns:

            # Enter data in colums
            if isinstance(col, str):
                self.cell(col_width, 2*th, str(col), border=1)
            else:
                self.cell(col_width, 2*th, str(col[0]), border=1)

        self.ln(2*th)

    def table_generator(self, table, epw, subject):
        # Text height is the same as current font size
        th = self.font_size
        companies = table.index

        table = table.to_numpy()
        for i, row in enumerate(table):
            #Dictates column widths for the table

            col_width = epw/(len(row))
            if subject == "Sector":
                col_width = epw/(len(row) + 1)
                self.cell(col_width, 2*th, str(companies[i]), border=1)

            for datum in row:
                # Enter data in colums


                self.cell(col_width, 2*th, str(datum), border=1)


            self.ln(2*th)
        self.ln(2*th)

    def generate_financial_analysis(self, code, subject, finOptions):
        self.set_font("Helvetica",style = "B",size = 24)
        analysis = "Income"

        # create a cell
        self.cell(200, 20, txt = f"{code} Financial Analysis",
                 ln = 1, align = 'C')

        table, valuation_list = fa.get_financials(code, subject, "Income", finOptions, True)

        self.set_font("Helvetica",size = 9)





        # Effective page width, or just epw
        epw = self.w - 2*self.l_margin

        # Set column width to 1/4 of effective page width to distribute content
        # evenly across table and page
        col_width = epw/5

        if "Graphs" in finOptions:
            #https://discuss.streamlit.io/t/creating-a-pdf-file-generator/7613/10
            self.image(f"tmpfile.{code}_{analysis}.png", w = epw  )
            self.add_page()
            os.remove(f"tmpfile.{code}_{analysis}.png") 


        #Can't Text Wrap with this particular module, without breaking the table
        PDFGenerator.add_table_header(self, valuation_list, epw, subject)

        self.set_font("Helvetica",size = 9)
        #Generate the valuation table in the PDF report
        PDFGenerator.table_generator(self, valuation_list, epw, subject)

        PDFGenerator.add_table_header(self, table, epw, subject)

        self.set_font("Helvetica",size = 9)
        PDFGenerator.table_generator(self, table, epw, subject)


    def generate_latest_sens(self, code):
        url = f"https://www.profiledata.co.za/brokersites/businesslive/Controls/Toolbox/SensSearch/SSJSONdata.aspx?date=26%20Nov%202010&enddate=31%20Dec%202020&keyword=&sharecode={code}&sectorcode="
        # set style and size of font
        # that you want in the pdf
        self.set_font("Helvetica", "B",size = 24)

        # create a cell
        self.cell(200, 20, txt = f"{code} Latest SENS",
                 ln = 1, align = 'C')
        sens_ids, sens_titles, sens_dates = rwb.SensGetter.get_sens_id(rwb.SensGetter.get_html(url))

        self.set_font("Helvetica",size = 11)
        for i, sens in enumerate(sens_ids[:5]):
            text = rwb.SensGetter.get_sens_text(sens, sens_titles[i])
            text = text.encode('latin-1', 'replace').decode('latin-1')
            self.multi_cell(200, 5, txt = text,
                      align = 'L')
            self.cell(200, 5, txt = "---------------------------------------------------------------------",
                     ln = 1, align = 'L')
