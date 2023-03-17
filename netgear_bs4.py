import requests
from bs4 import BeautifulSoup

url = 'https://geotagging.indosatooredoo.com/astweb/ast_insurance_main.php'
# url = 'https://homeventory.id/api/auth/login/'
page = requests.get(url)

# print(page.content)
soup = BeautifulSoup(page.content, features='html.parser')
res = soup.find(id='doc-site_id')
print(res)
