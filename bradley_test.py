from selenium import webdriver
from bs4 import BeautifulSoup
import requests
import pandas as pd

# Notes:
# Use column "OWNNAME"
# If more than one result, put down an error code and skip
# Download all pdfs instead of scraping text
# Name the pdfs something useful so the folder can be searched
# should be one folder full of pdfs
# Some ownnames will be duplicates because single owners may own
#   multiple properties. Only do each ownname once; remove dupes


url_prefix = ("https://businesssearch.sos.ca.gov/CBS/SearchResults?"
              "filing=False&SearchType=LPLLC&SearchCriteria=")

df = pd.read_csv('parcel_info_last_line_deleted.csv')['OWNNAME']


search_query = "OW FAMILY 100 PIONEER".replace(" ", "+")
#search_query = "SANTA CRUZ CITY OF".replace(" ", "+")
url_suffix = "&SearchSubType=Keyword"

url = url_prefix + search_query + url_suffix


browser = webdriver.Firefox()



browser.get(url)

# Make sure we have any results at all
soup = BeautifulSoup(browser.page_source, 'html.parser')
#print(soup.find_all('td', attrs={'class': 'dataTables_empty'}))
#exit()
# get button id
button_id = 'btnDetail-200725810008'
the_button = browser.find_element_by_id(button_id)
the_button.click()

# Get pdfs
res = requests.get('https://businesssearch.sos.ca.gov/Document/RetrievePDF?Id=200725810008-22600401')
with open('_foo_bytes.pdf', 'wb') as o:
    o.write(res.content)

''''''
soup = BeautifulSoup(browser.page_source, 'html.parser')
buttons = soup.find_all('button')
#foo = #somefunction
pdf_url_prefix =\
    'https://businesssearch.sos.ca.gov/Document/RetrievePDF?Id='
b = buttons
suffixes = [str(b[u]).split('value="')[1].split('"')[0] for u in range(len(b))]
#[foo(pdf_url_prefix + suffix) for suffix in suffixes]

rows = soup.find_all('div', attrs={'class': 'row'})
desired_data = rows[8]
desired_data = desired_data.find_all('div')[1].text.strip()
desired_data = desired_data.replace(' Address', '').replace(' \n', '')
desired_data = desired_data.replace(' City, State, Zip', '')
desired_data = desired_data.split('Agent')

''''''
