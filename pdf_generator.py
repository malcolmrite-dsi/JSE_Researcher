from fpdf import FPDF
import text_analysis as ta

#Importing custom library for web scraping
import request_web as rwb


class PDFGenerator():

    def generate_report(code,time_period, detail, subject, options):
        # save FPDF() class into a
        # variable pdf
        pdf = FPDF()
        pdf.set_title(f"{code} Investment Report")

        PDFGenerator.create_intro_page(pdf,code, options)

        if "Company Background" in options:
            pdf.add_page()

            PDFGenerator.create_company_background(pdf,code)


        if "News Analysis" in options:
            pdf.add_page()

            PDFGenerator.create_news_analysis(pdf, code, time_period, detail, subject)

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
