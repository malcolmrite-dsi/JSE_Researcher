
from request_web import SensGetter
import re
#http://196.30.126.229/V2/Controls/News/NewsList/NLJSONdata.aspx?jsecode=IMP&type=sens&filter=&search=
#https://www.profiledata.co.za/BrokerSites/BusinessLive/SENS.aspx?id=372260



def main():

    url = "https://www.profiledata.co.za/brokersites/businesslive/Controls/Toolbox/SensSearch/SSJSONdata.aspx?date=26%20Nov%202019&enddate=26%20Nov%202020&keyword=&sharecode=WHL&sectorcode="

    sens_ids, sens_titles, sens_dates = SensGetter.get_sens_id(SensGetter.get_html(url))
    for sens in sens_ids:
        print((sens))

    for title in sens_titles:
        print((title))

    for date in sens_dates:
        print(date)
if __name__ == '__main__':
    main()
