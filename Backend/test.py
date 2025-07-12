import requests
from bs4 import BeautifulSoup

url = "https://investor.sebi.gov.in/moneymatters-inc-exp.html"
response = requests.get(url)
soup = BeautifulSoup(response.text, 'html.parser')
text = soup.get_text(separator='\n')
paragraphs = []
for para in text.split('\n'):
    clean = para.strip()
    print(clean)
    if len(clean.split()) >= 30:
        paragraphs.append(clean)
print(paragraphs)
