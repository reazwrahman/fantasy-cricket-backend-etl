import requests
from bs4 import BeautifulSoup

def make_request(url:str):
    session = requests.Session()
    session.headers.update({
        # "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
        "User-Agent": "PostmanRuntime/7.44.0",
        "Accept-Language": "en-US,en;q=0.9",
        "Referer": "https://www.google.com/"
    })

    response = session.get(url)
    print(f'response from {url} is {response}')
    bs = BeautifulSoup(response.content, 'lxml')
    return bs 


def validate_link(URL): 
    try:
        bs = make_request(URL)
        table_body=bs.find_all('tbody') 
        
        if table_body == None: 
            return False 
        else: 
            return True
        
    except: 
        raise Exception('ScoreCardDf::ValidateLink(), Invalid Link was provided, Scraping Can not be completed' ) 
        