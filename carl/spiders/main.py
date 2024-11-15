import scrapy
import json

class MainSpider(scrapy.Spider):
    name = "main"
    allowed_domains = ["locations.carlsjr.com"]
    start_urls = ["https://locations.carlsjr.com/"]
    def parse(self, response):
        states =  response.xpath('//div[contains(@class, "Directory-content")]//ul[contains(@class, "Directory-listLinks")]//li[contains(@class, "Directory-listItem")]')
        for state in states:
            test = state.xpath('./a/@href').get()
            yield response.follow(test, callback=self.parse_cities)



    def parse_cities(self, response):
        citie_s = response.xpath('//div[contains(@class, "Directory-content")]//ul[contains(@class, "Directory-listLinks")]//li[contains(@class, "Directory-listItem")]')
        for city in citie_s:
            store_url = city.xpath('./a/@href').get()
            yield response.follow(store_url, callback=self.extract_stores)


    def extract_stores(self, response):
        url_ss = response.xpath('//div[contains(@class, "Teaser-cta")]')
        for url_s in url_ss:
            store = url_s.xpath('.//a/@href').get()
            yield response.follow(store, callback=self.get_data)
    
    def get_data(self, response):
        html_resp = response.xpath('//div[contains(@class, "Core-card")]')
        json_data = response.xpath('(//script[@type="application/ld+json"])[2]/text()').get()
        data_days_json = response.xpath('//div[@class="c-hours-details-wrapper js-hours-table"]/@data-days').get()
        data_days = json.loads(data_days_json)
        data = json.loads(json_data)

        hours = html_resp.xpath('.//h3/text()').get()

        hour_dict = {}
        count = 0
        days = ["sunday", "monday", "tuesday", "wednesday", "thursday", "friday", "saturday"]
        for countt,day in enumerate(data_days):
            open_time = day[0]
            close_time = day[1]

            open_t = f"{open_time[:2]}:{open_time[2:]}am"
            close_t = f"{close_time[:2]}:{close_time[2:]}pm"

            hour_dict[days[countt]] = {
                'open' : open_t,
                'close' : close_t
            }


        loc_dict = {
            "type" : "Point",
            "coordinates": [
                data['geo']['longitude'],
                data['geo']['latitude']
            ]
        }
        yield{
            'name' : data['name'],
            'phone_number' : data['telephone'],
            'address' : data['address']['streetAddress'],
            'type' : data['address']['@type'],
            'location' : loc_dict,
            'url' : data['url'],
            'hours' : hour_dict
        }
