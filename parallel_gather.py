import random
import requests
import pandas as pd
import multiprocessing
from multiprocessing import Pool
from bs4 import BeautifulSoup
from selenium import webdriver
from multiprocessing import pool

class Dispatcher:
    '''Read the data, find out how many cores we have, cut up the data into
       that many chunks. Dispatch those chunks to that many gatherers.
    '''

    def __init__(self):
        self.n_cores = multiprocessing.cpu_count()
        self.filename = ('parcelinfo_lastlinedeleted_'
                         'positivesentinellineprepended.csv')
        self.ownnames = list(pd.read_csv(self.filename)['OWNNAME'].unique())



    def chunks(self, the_list, n_chunks):
        '''yield chunks of size n or less from the list'''

        n = len(the_list) // n_chunks + 1
        for i in range(0, len(the_list), n):
            yield the_list[i: i + n]


    def dispatch(self):
        with Pool(self.n_cores) as p:
            p.map(Gather_Listed_PDFs, self.chunks(self.ownnames, self.n_cores))



class Gather_Listed_PDFs:
    '''Take a list of ownnames and gather associated pdfs, as well as a label
       used to label the outputfile uniquely.
    '''

    def __init__(self, ownnames):
        self.df = ownnames

        # Prepare
        self.url_prefix = ("https://businesssearch.sos.ca.gov/CBS/"
                           "SearchResults?filing=False&SearchType="
                           "LPLLC&SearchCriteria={}&SearchSubType=Keyword")
        self.pdf_url_prefix = ('https://businesssearch.sos.ca.gov/'
                               'Document/RetrievePDF?Id=')

        self.browser = webdriver.Chrome()
        label = str(random.randint(0, 10 ** 20))
        self.outfile = open('outfile_2019-02-19-part-{}.csv'.format(label), 'w')


        starting_index = 0
        self.diagnostic_soup = self.gather_all_pdfs(starting_index)


    def gather_all_pdfs(self, starting_index):
        '''Gather all pdfs'''

        for i in range(len(self.df))[starting_index:]:
            print('\n\n#{}'.format(i))
            print('OWNNAME: {}'.format(self.df[i]))

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
#        print("Search URL".format(url))

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

            with open('pdfs/' + filename, 'wb') as o:
                o.write(res.content)


        print()
        return


if __name__ == "__main__":
    the_pdf_gatherer = Dispatcher()
    the_pdf_gatherer.dispatch()
