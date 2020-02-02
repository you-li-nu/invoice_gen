import requests

class MenuParser():
	def __init__(self, url):
		self.url = url
		req = requests.get(url=self.url)
		from bs4 import BeautifulSoup
		soup = BeautifulSoup(req.content, 'html.parser')
		for i in soup.find_all('span', {'class': 'item-title'}):
			t = i.text
			print (t)
			if '.' in t:
				print (t[t.index('.')+1:].strip())
		
		
m = MenuParser('https://www.allmenus.com/il/evanston/494140-ten-mile-house/menu/')
