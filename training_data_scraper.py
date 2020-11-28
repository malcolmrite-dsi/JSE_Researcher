from request_web import SensGetter
import csv
from Company_List_Generator import CompanyGenerator

def main():
    file = CompanyGenerator.get_top_40()
    share_codes = SensGetter.get_share_code(file)
    for code in share_codes:
        url = f"https://www.profiledata.co.za/brokersites/businesslive/Controls/Toolbox/SensSearch/SSJSONdata.aspx?date=26%20Nov%202019&enddate=26%20Nov%202020&keyword=&sharecode={code}&sectorcode="

        sens_ids, sens_titles, sens_dates = SensGetter.get_sens_id(SensGetter.get_html(url))
        fs = open(f"train_data/raw_sens_data_{code}.csv", "w")
        csv_writer = csv.writer(fs)

        csv_writer.writerow(["sens_title","Date","text"])

        for i, sens in enumerate(sens_ids):
            text = SensGetter.get_sens_text(sens)

            csv_writer.writerow([sens_titles[i], sens_dates[i] , text])

        fs.close()


if __name__ == '__main__':
    main()
