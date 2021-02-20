# Edgar_phrase_extraction
Extract noun phrases and keywords using NER, Noun Phrase extraction, topic modeling (LDA) and and matching glossary terms. 

# Extracting Noun Phrases
Noun Phrase Extraction was done through NLTK noun phrase extractor on SEC filings for Microsoft and Pfizer. We processed 21 (2000-2020) years of all SEC filings by these two companies. Run MSFT.py for extracting Noun Phrases from filings of any company by providing the organization's SEC no, ticker and name. The code uses BeautifulSoup for web crawling, REGEX for cleaning the unstructured text data and NLTK for matching noun phrases.

# Extracting Glossary Terms
We used glossaries from Gartner and FDA for finding important terms for Tech Companies and Pharma Companies repectively. We processed 21 (2000-2020) years of all SEC filings by Microsoft and Pfizer for matching the glossary terms with the filings. Run Gartner.py and FDA.py for scrapping glossaries of Tech and Pharma companies respectively. For Pharma companies, FDA has released multiple glossaries and so all the glossaries will have to be scrapped individually. 
