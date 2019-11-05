import json
import requests
from bs4 import BeautifulSoup
#https://www.yelp.com/developers/documentation/v3/business_search
#https://clearbit.com/logo

# class Chen_query():
#
#     def __init__():
#         self.query = "restaurants+in+Evanston"
#         self.url = "https://maps.googleapis.com/maps/api/place/textsearch/json?query={}&key=AIzaSyCKIqJvGmVUw3KU44e6jLU3A0Aiia9JbyE".format(query)
#
#
#     def get_location(self):
#         req = requests.get(self.url)
#         locations = json.dump(req.json())
#         print locations.keys()
#
#

class LocationGenerator():
    API_KEY = "g9Wv_YFCXFiT37EgtZ0yuRBDAw1OfQZZ3cIoaBriSB5pe_fEnY41M73_rFc0Wkb8RAqYkV-0GRUEG-g_7dKFKQn7ykmA4Bzp85HJRDUy5bIKSmKfeIUc378V7rq_XXYx"
    def __init__(self):
        self.url = 'https://api.yelp.com/v3/businesses/search'
        self.headers = {
            'Authorization': 'Bearer {}'.format(self.API_KEY),
        }
    def get_location(self, params=None):
        url_params = {
            'term': 'food',
            'location': 'Evanston, IL'
        }
        response = requests.get(url=self.url, headers=self.headers, params=url_params)
        locations = json.loads(response.content)
        print(locations)
        for i in range(len(locations['businesses'])):
            location = locations['businesses'][i]
            print('Location: {}'.format(location))
            print('name: {}'.format(location.get('name')))
            loc_url = location['url']
            print('Yelp url: {}'.format(loc_url))
            location_page = requests.get(url=loc_url)
            if location_page.status_code != 200:
                print('unable to crawl')
                continue
            soup = BeautifulSoup(location_page.content, 'html.parser')
            if not soup:
                print('not soup')
                continue
            for a in soup.find_all('a', href=lambda href: href and "biz_redir" in href and 'url' in href and 'website_link_type=website' in href):
                redir_website = a['href']
                index_s = redir_website.find('url=')
                index_e = redir_website.find('&', index_s)
                url_posfix = redir_website[index_s: index_e]
                url_posfix.replace('http%3A%2F%2F', '')
                logo_url = 'http://logo.clearbit.com/{}'.format(url_posfix)
                logo = requests.get(url=logo_url)
                if logo.status_code == 200:
                    print('find logo: {}'.format(logo_url))
                else:
                    print('not found logo')
            print('--------------------')



a = LocationGenerator()
print(a.get_location())