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

        # Prepare
        self.pdf_url_prefix =\
            'https://businesssearch.sos.ca.gov/Document/RetrievePDF?Id='
        self.url_prefix = ("https://businesssearch.sos.ca.gov/CBS/SearchResults?"
                      "filing=False&SearchType=LPLLC&SearchCriteria=")
        self.filename = 'parcelinfo_lastlinedeleted_positivesentinellineprepended.csv'
        self.df = pd.read_csv(self.filename)['OWNNAME'].unique()
        self.url_suffix = "&SearchSubType=Keyword"
        self.browser = webdriver.Firefox()
        self.outfile = open('outfile.csv', 'w')

        # Execute
        self.soup = self.gather_all_pdfs()


    def gather_all_pdfs(self):
        '''Gather all pdfs'''

        for i in range(len(self.df))[6394:]:
#        for i in range(len(self.df)):
            print(i)
            print(self.df[i])
            
            result = self.gather_one_pdf(self.df[i])
            if result:
                return result
            


    def gather_one_pdf(self, query):
        '''gather one pdf'''

        url = self.url_prefix + query.replace(' ', '+') + self.url_suffix
        print(url)

        self.browser.get(url)

        # Make sure we get any results at all
        soup = BeautifulSoup(self.browser.page_source, 'html.parser')

        # Check for zero results
        n_results =\
            len(soup.find_all('td', attrs={'class':'dataTables_empty'}))
        if n_results != 0:
            self.outfile.write(query + ',' + '0' + '\n')
            self.outfile.flush()
            print("no results found!")
            # log something about finding zero results
            return

        # Check for more than one result
        buttons = soup.find_all('button')
        if len(buttons) != 1:
            self.outfile.write(query + ',' + str(len(buttons)) + '\n')
            self.outfile.flush()
            print("more than one result") 
            return

        # So now we have exactly one result
        print('exactly one result')


        # get button id and go to the PDF page
#        button_id = 'btnDetail-200725810008'
        button_id = buttons[0].attrs['id']
        print(button_id)

        try:
            the_button = self.browser.find_element_by_id(button_id)
        except:
            print('cannot find button')
            return soup
        the_button.click()


        soup = BeautifulSoup(self.browser.page_source, 'html.parser')

        tbodies = soup.find_all('tbody')
        if not tbodies:
            raise Exception("Error: Can't find table")
            return soup
        tbodies = tbodies[0]

        # Make sure all pdfs are available
        if "Image unavailable. Please request paper copy." in str(tbodies):
            self.outfile.write(query + ',' + 'Image unavailable' + '\n')
            self.outfile.flush()
            print("Image unavailable") 
            return
            

        for i in range(int(len(tbodies) / 3)):
            doctype = tbodies.find_all('td')[3 * i].text.strip()
            date = tbodies.find_all('td')[3 * i + 1].text.strip().replace('/', '-')

            # Debug
            return soup

            button = tbodies.find_all('td')[3 * i + 2].find_all('button')[0]

            suffix = str(button).split('value="')[1].split('"')[0]
            
            res = requests.get(self.pdf_url_prefix + suffix)
            filename = '_'.join([doctype, date, query]) + '.pdf'
            filename = filename.replace('/', '')

            with open(filename, 'wb') as o:
                o.write(res.content)


        print()
        return

            
#        buttons = soup.find_all('button')
#        #foo = #somefunction
#        pdf_url_prefix =\
#            'https://businesssearch.sos.ca.gov/Document/RetrievePDF?Id='
#        b = buttons
#        suffixes =\
#            [str(b[u]).split('value="')[1].split('"')[0] for u in range(len(b))]
#
#
#        # We need to get the doctype and sufiix corresponding to each 
#
#        for i in range(len(suffixes)):
#            res = requests.get(pdf_url_prefix + suffixes[i])
#            with open(query.replace(' ', '_') + str(i) + '.pdf', 'wb') as o:
#                o.write(res.content)
##        res = requests.get(suffixes[0])
##
##        with open(query.replace(' ', '_') + '.pdf', 'wb') as o:
##            o.write(res.content)
#
#        print()
#

        
if __name__ == "__main__":
    the_pdf_gatherer = PDF_Gatherer()
    soup = the_pdf_gatherer.soup
