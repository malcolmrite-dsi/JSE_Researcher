import scrapy
import json

class QuotesScraper(scrapy.Spider):
    name = "quotes"

    def start_requests(self):
        start_urls = [
            'http://196.30.126.229/v2/Scripts/News.aspx?c=IMP&x=JSE'
        ]

        headers = {
            "Accept": "application/json, text/javascript, */*; q=0.01",
            "Accept-Encoding": "gzip, deflate",
            "Accept-Language": "en-US,en;q=0.9",
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "Host": "196.30.126.229",
            "Pragma": "no-cache",
            "Referer": "http://196.30.126.229/v2/Scripts/News.aspx?c=IMP&x=JSE",
            "User-Agent":" Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/86.0.4240.198 Safari/537.36",
            "X-Requested-With": "XMLHttpRequest"
        }


    def parse(self, response):
        url = "http://196.30.126.229/V2/Controls/News/NewsList/NLJSONdata.aspx?jsecode=IMP&type=sens&filter=&search="

        yield scrapy.Request(url=url, callback=self.parse_api, headers = self.headers)

    def parse_api(self, response):
        raw_data = response.body
        with open("IMP_SENS", "wb") as f:
            f.write(raw_data)
