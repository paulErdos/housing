import requests
import pandas as pd
from bs4 import BeautifulSoup
from selenium import webdriver

class PDF_Gatherer:
    '''When instantiated, start up firefox and use it to scrape pdfs for each of
       the values in the 'OWNNAME' column.
    '''

    def __init__(self, starting_index=0):
        '''Hang on to constants'''

        # Prepare
        self.url_prefix = ("https://businesssearch.sos.ca.gov/CBS/"
                           "SearchResults?filing=False&SearchType="
                           "LPLLC&SearchCriteria={}&SearchSubType=Keyword")
        self.pdf_url_prefix = ('https://businesssearch.sos.ca.gov/'
                               'Document/RetrievePDF?Id=')
        self.filename = ('parcelinfo_lastlinedeleted_'
                         'positivesentinellineprepended.csv')
        self.df = pd.read_csv(self.filename)['OWNNAME'].unique()
        self.browser = webdriver.Firefox()
        self.outfile = open('outfile.csv', 'w')

        # Execute
        self.diagnostic_soup = self.gather_all_pdfs(starting_index)


    def gather_all_pdfs(self, starting_index):
        '''Gather all pdfs'''

        for i in range(len(self.df))[starting_index:]:
            print('\n\n#{}'.format(i))
            print('OWNNAME: {}'.format(self.df[i]))

            # Navigate to page
            # Check number of results
            # button_exists(button_id), but don't do the button click here.
            # Then do the button click
            # Then verify table validity
            # Then harvest the pdfs
            
            
            result = self.gather_one_pdf(self.df[i])
            if result:
                return result


    def gather_one_pdf(self, query):
        '''gather one pdf

           TODO:
            Break this code up into the following functions, which will be
            called in this function.
            # Navigate to page
            # Check number of results
            # button_exists(button_id), but don't do the button click here.
            # Then do the button click
            # Then verify table validity
            # Then harvest the pdfs

        '''

        url = self.url_prefix.format(query.replace(' ', '+'))
        print("Search URL".format(url))

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
    the_pdf_gatherer = PDF_Gatherer(14253)
    soup = the_pdf_gatherer.soup
