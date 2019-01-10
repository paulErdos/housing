from selenium import webdriver
from bs4 import BeautifulSoup

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
search_query = "OW FAMILY 100 PIONEER".replace(" ", "+")
url_suffix = "&SearchSubType=Keyword"

url = url_prefix + search_query + url_suffix


browser = webdriver.Firefox()
browser.get(url)

# get button id
button_id = 'btnDetail-200725810008'
the_button = browser.find_element_by_id(button_id)
the_button.click()

with open('page.html', 'w') as o:
    o.write(browser.page_source)


soup = BeautifulSoup(browser.page_source, 'html.parser')

rows = soup.find_all('div', attrs={'class': 'row'})
desired_data = rows[8]
desired_data = desired_data.find_all('div')[1].text.strip()
desired_data = desired_data.replace(' Address', '').replace(' \n', '')
desired_data = desired_data.replace(' City, State, Zip', '')
desired_data = desired_data.split('Agent')


