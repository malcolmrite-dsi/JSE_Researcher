from request_web import SensGetter
import csv

class CompanyGenerator():
    def get_all_companies():

        df = open("JSE_company_list.csv","w")
        csv_writer = csv.writer(df)

        csv_writer.writerow(["Share Code", "Short Name"])
        all_comp = ["4", "A", "B", "C", "D", "E", "F", "G", "H", "I", "J", "K", "L", "M","N", "O", "P", "Q", "R", "S","T","U","V", "W", "X", "Y", "Z"]
        for index in all_comp:
            url = f"https://www.sharedata.co.za/V2/Controls/Shares/ShareIndex/SIJSONData.aspx?indextype={index}&sortfield=FULLNAME"

            list = SensGetter.get_company_list(SensGetter.get_html(url))
            print(f'{index}' + " Loaded")
            for i in range(0,len(list)-1, 2):
                csv_writer.writerow([list[i], list[i+1]])

        df.close()
        return "JSE_company_list.csv"

    def get_top_40():
        df = open("TOP40_company_list.csv","w")
        csv_writer = csv.writer(df)

        csv_writer.writerow(["Share Code", "Short Name"])

        url = f"https://www.sharedata.co.za/V2/Controls/Shares/ShareIndex/SIJSONData.aspx?indextype=TOP40&sortfield=FULLNAME"
        codeCount = 0
        list = SensGetter.get_company_list(SensGetter.get_html(url))

        for i in range(0,len(list)-1, 2):
            csv_writer.writerow([list[i], list[i+1]])

        df.close()
        return "TOP40_company_list.csv"
