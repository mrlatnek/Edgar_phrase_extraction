# -*- coding: utf-8 -*-
"""
Created on Thu Feb 11 15:55:45 2021

@author: mrlat
"""

# -*- coding: utf-8 -*-
"""
Created on Wed Feb 10 16:14:59 2021

@author: mrlat
"""

from bs4 import BeautifulSoup
import requests
import re 
search_url = 'https://www.fda.gov/drugs/development-approval-process-drugs/patient-focused-drug-development-glossary'
html_page = requests.get(search_url).text
soup = BeautifulSoup(html_page)
content = soup.find_all("strong")
#content = soup.select('a.result-heading.p-small')
#for cont in content[50:100]:
   # print(cont)
all_words = []
for i in range(len(content)):
    all_words.append(content[i].text)

print(all_words)
all_words1 = []
for j in range(len(all_words)):
    tmp = all_words[j].split(" (")
    if len(tmp)==2:
        #re.sub('[^A-Za-z0-9]+', '', mystring)
        all_words1.append(re.sub('[^A-Za-z0-9 ]+', '', tmp[0]))
        all_words1.append(re.sub('[^A-Za-z0-9 ]+', '', tmp[1]))
    else:
        all_words1.append(re.sub('[^A-Za-z0-9 ]+', '', tmp[0]))
    
print(all_words[:20])
print(all_words1[:20])

with open('resources/PFI_patient_focused_vocab.txt', mode='wt', encoding='utf-8') as myfile:
    myfile.write('\n'.join(all_words1))
    

#<a class="result-heading p-small" href="https://www.gartner.com/en/information-technology/glossary/absorption-chillers">Absorption Chillers</a>
#