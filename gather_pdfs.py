import requests
import pandas as pd
from bs4 import BeautifulSoup
from selenium import webdriver

class PDF_Gatherer:
    '''When instantiated, start up firefox and use it to scrape pdfs for each of
       the values in the 'OWNNAME' column.
    '''

    def __init__(self):
        '''Hang on to constants'''

        self.url_prefix = ("https://businesssearch.sos.ca.gov/CBS/SearchResults?"
                      "filing=False&SearchType=LPLLC&SearchCriteria=")
        self.filename = 'parcel_info_last_line_deleted.csv'
        self.df = pd.read_csv(self.filename)['OWNNAME'].unique()
        self.url_suffix = "&SearchSubType=Keyword"
        self.browser = webdriver.Firefox()

        self.gather_all_pdfs()


    def gather_all_pdfs(self):
        '''Gather all pdfs'''

        for query in self.df:
            print(query)
            self.gather_one_pdf(query)
            


    def gather_one_pdf(self, query):
        '''gather one pdf'''

        url = self.url_prefix + query + self.url_suffix

        self.browser.get(url)

        # Make sure we get any results at all
        soup = BeautifulSoup(self.browser.page_source, 'html.parser')
        n_results =\
            len(soup.find_all('td', attrs={'class':'dataTables_empty'}))
        if n_results != 0:
            print("no results found!")
            # log something about finding zero results
            return



        # get button id
        button_id = 'btnDetail-200725810008'
        the_button = self.browser.find_element_by_id(button_id)
        the_button.click()


        soup = BeautifulSoup(self.browser.page_source, 'html.parser')
        buttons = soup.find_all('button')
        #foo = #somefunction
        pdf_url_prefix =\
            'https://businesssearch.sos.ca.gov/Document/RetrievePDF?Id='
        b = buttons
        suffixes =\
            [str(b[u]).split('value="')[1].split('"')[0] for u in range(len(b))]

        if len(suffixes) > 1:
            print("Found more than one!")
            # Log something in the spreadsheet?
            return

        res = requests.get(suffixes[0])

        with open(query.replace(' ', '_') + '.pdf', 'wb') as o:
            o.write(res.content)

        print()
        exit()


        
if __name__ == "__main__":
    the_pdf_gatherer = PDF_Gatherer()
