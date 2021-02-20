#!/usr/bin/python3
# -*- coding: utf-8 -*-
"""
Created on Sat Nov 28 10:00:02 2020

@author: amits
"""

from bs4 import BeautifulSoup
import datetime
import grequests
import logging
import pandas as pd
import os
import io
import re
import requests
import sys
import warnings
warnings.filterwarnings('ignore')



def downloadFiling(*factory_args, **factory_kwargs):
    """
    Decorator function to enable passing of extra arguments to response_hook
    function which is the event hook associated with requests sent by 
    grequests for each filing of interest for a company.
    
    Parameters
    ----------
    *factory_args : list
        Arguments passed to the function.
    **factory_kwargs : dict
        Keyword Arguments passed to the function.

    Returns
    -------
    response_hook : function
        The function containing post-processing logic to execute after a 
        filing page is fetched for a company by grequest.

    """
    def response_hook(response, *request_args, **request_kwargs):
        global base_url
        #global contract_search_pattern
        global text_pattern
        html_page = response.text
        soup = BeautifulSoup(html_page)
        content_div = soup.body.find(id = 'contentDiv')
        content = list(content_div.find('table', {'class': 'tableFile'}).children)
        if len(content) > 3:
            for exhibit in content[3::2]:
                data = exhibit.find_all('td', recursive = False)
                desc = data[3].get_text()
                #if contract_search_pattern.search(desc):
                fname = '--'.join([factory_kwargs['fdate'], factory_kwargs['ftype'], desc])
                fname = fname.replace('/', '') + '.txt'
                clink = base_url+data[2].a['href']
                res = requests.get(clink)
                page = BeautifulSoup(res.text)
                raw_text = page.body.get_text(" ", strip = True)
                with io.open(os.path.join(factory_kwargs['outdir'], fname), 'w', encoding = 'utf-8') as file:
                    file.write(raw_text)
    return response_hook


def exception_handler(*args, **kwargs):
    """

    Parameters
    ----------
    *args : list
        Arguments passed to function.
    **kwargs : dict
        Keyword arguments passed to function.

    Returns
    -------
    handle : function
        Exception Handling logic for response event hook associated with 
        requests sent by grequests for each filing of interest for a company.

    """
    def handle(request, exception):
        company_logger = logging.getLogger('company_failure')
        company_logger.debug('---'.join(['FILING ERROR', kwargs['cik'], flink]))
        company_logger.exception(exception)
    return handle


if __name__ == '__main__':
    ############################### Logging ##################################
    # Creating log directory
    current_time = datetime.datetime.now().strftime("%Y%m%d-%H%M%S")
    LOG_DIR = os.path.join(os.path.dirname("logs/" + current_time + "/"))
    os.makedirs(LOG_DIR, exist_ok=True)
    LOG_FILE = os.path.join(LOG_DIR, 'secEdgarScrape.log')
    PROCESSED = os.path.join(LOG_DIR, 'processed.log')
    FAILED = os.path.join(LOG_DIR, 'fail.log')
    # Module Level logger
    module_logger = logging.getLogger(__name__)
    module_logger.setLevel(logging.DEBUG)
    ## Formatter for stream handler
    stream_formatter = logging.Formatter("%(name)s - %(levelname)s - %(message)s")
    ## Stream Handler
    stream_handler = logging.StreamHandler(sys.stdout)
    stream_handler.setLevel(logging.CRITICAL)
    stream_handler.setFormatter(stream_formatter)
    module_logger.addHandler(stream_handler)
    ## Formatter for file handler
    file_formatter = logging.Formatter('%(asctime)s - %(name)s - %(lineno)d - %(levelname)s - %(message)s')
    ## File Handler for logging
    file_handler = logging.FileHandler(LOG_FILE)
    file_handler.setLevel(logging.DEBUG)
    file_handler.setFormatter(file_formatter)
    module_logger.addHandler(file_handler)
    
    ## Logger to record comapnys processed by scraper
    company_logger = logging.getLogger('company')
    company_logger.setLevel(logging.INFO)
    ## Formatter for file handler
    company_formatter = logging.Formatter('%(message)s')
    ## File Handler to record companys processed by scrapper
    processed_file_handler = logging.FileHandler(PROCESSED)
    processed_file_handler.setLevel(logging.INFO)
    company_logger.addHandler(processed_file_handler)

    ##########################################################################
    
    ############################## GLOBAL VARIABLES ##########################
    base_url = 'https://www.sec.gov'
    contracts = []
    #contract_search_pattern = re.compile(r'EX-\d+', re.I)
    search_url = 'https://www.sec.gov/cgi-bin/browse-edgar'
    text_pattern = re.compile(r'\w+')
    years = ['0'+x if len(x) == 1 else x for x in [str(i) for i in range(21)]]
    #years = [ '15', '16', '17', '18', '19', '20']
    #years = ['00']
    ##########################################################################
    
    # File loading
    try:
        assert len(sys.argv) == 2, "Wrong number of inputs!" 
        outbase = sys.argv[1]
        #df = pd.DataFrame({'cname': ['Microsoft', 'Pfizer'], 'tick': ['MSFT', 'PFE'], 'CIK': ['789019', '78003']})
        df = pd.DataFrame({'cname': ['Pfizer'], 'tick': ['PFE'], 'CIK': ['78003']})
    except AssertionError as e:
        module_logger.critical(e)
        logging.shutdown()
        sys.exit()
    except FileNotFoundError:
        module_logger.critical('Could not find the input file!')
        logging.shutdown()
        sys.exit()
    except pd.errors.ParserError as e:
        module_logger.critical('Error while parsing input file. See the log for more info..')
        module_logger.exception(e)
        logging.shutdown()
        sys.exit()
    except Exception as e:
        module_logger.critical('Error!')
        module_logger.exception(e)
        logging.shutdown()
        sys.exit()
    
    # Scraping
    try:
        # Creating the output directory
        os.makedirs(outbase, exist_ok = True)
        
        # Payload to be sent with each request to SEC edgar when searching 
        # for filings made by a company
        url_comps = {'action': 'getcompany', 'owner': 'exclude', 'count': '100'}
        for _, row in df.iterrows():
            for year in years:
                print(year)
                outdir = os.path.join(outbase, row[1], year)
                if not os.path.exists(outdir):
                    os.makedirs(outdir)
                company = []
                start = 0
                while True:
                    payload = {**url_comps, **{'CIK': row[2], 'start': start, \
                                               'datea': '20'+year+'0101', 'dateb': '20'+year+'1231'}}
                    response = requests.get(search_url, params = payload)
                    html_page = response.text
                    soup = BeautifulSoup(html_page)
                    content_div = soup.body.find(id = 'seriesDiv')
                    if not content_div:
                        break
                    content = list(content_div.find('table', {'class': 'tableFile2'}).children)
                    if len(content) <= 3:
                        break
                    for filing in content[3::2]:
                        data = filing.find_all('td', recursive = False)
                        fdate = data[-2].get_text()
                        ftype = data[0].get_text()
                        flink = base_url+data[1].a['href']
                        action_item = grequests.get(flink, callback = downloadFiling(ftype=ftype, fdate=fdate, outdir=outdir))
                        company.append(action_item)
                    # End of inner for
                    start += 100
                # End of while
                results = grequests.map(company, size = 1, exception_handler = exception_handler(cik = row[2]))
                company_logger.info(row[2])
            # End of outer for
    except Exception as e:
        module_logger.critical('Error!')
        module_logger.exception(e)
    finally:
        logging.shutdown()
