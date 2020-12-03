from request_web import SensGetter
import csv
from Company_List_Generator import CompanyGenerator
from request_web import NewsGetter

def get_sens_training_data():
    file = CompanyGenerator.get_top_40()
    share_codes = SensGetter.get_share_code(file)
    for code in share_codes:
        url = f"https://www.profiledata.co.za/brokersites/businesslive/Controls/Toolbox/SensSearch/SSJSONdata.aspx?date=26%20Nov%202015&enddate=26%20Nov%202020&keyword=&sharecode={code}&sectorcode="

        sens_ids, sens_titles, sens_dates = SensGetter.get_sens_id(SensGetter.get_html(url))
        fs = open(f"train_data/raw_sens_data_{code}_5yrs.csv", "w")
        csv_writer = csv.writer(fs)

        csv_writer.writerow(["sens_title","Date","text"])

        for i, sens in enumerate(sens_ids):
            text = SensGetter.get_sens_text(sens)

            csv_writer.writerow([sens_titles[i], sens_dates[i] , text])

        fs.close()




def get_share_links(pg):
    url = f"https://za.investing.com/stock-screener/?sp=country::110|sector::a|industry::a|equityType::a%3Ename_trans;{pg}"
    links = NewsGetter.get_company_links(NewsGetter.get_html(url))

    return links

def get_train_headlines(page, code):
    url = f"https://www.moneyweb.co.za/company-news/page/{page}/?shareCode={code}"
    links, headlines = NewsGetter.get_news_headlines(NewsGetter.get_html(url))
    fs = open(f"train_data/raw_headline_data_{code}_pg{page}.csv", "w")
    csv_writer = csv.writer(fs)

    csv_writer.writerow(["headline","link"])

    for i, head in enumerate(headlines):

        csv_writer.writerow([head, links[i]])

    fs.close()



def main():
    file = CompanyGenerator.get_top_40()
    share_codes = SensGetter.get_share_code(file)
    for code in share_codes:
        get_train_headlines(1, code)

if __name__ == '__main__':
    main()
