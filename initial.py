import requests  # fazer requisições HTTP em Python, usada para interagir com APIs web e obter dados de fontes externas.
from bs4 import BeautifulSoup # analisar documentos HTML e XML. Ele cria uma árvore de análise para documentos que pode ser usada para extrair dados de HTML.
import time
import json

base_url = 'https://www.tbca.net.br/base-dados/'
url = base_url + "composicao_alimentos.php?pagina="
page = 1

data = {
    'Link': [],
    'Código': [],
    'Nome': [],
    'Nome Científico': [],
    'Grupo': [],
    'Marca': [],
}

collection = []

while (True):
  print(f"Fetching page {page}")

  response = requests.get(url + str(page))

  soup = BeautifulSoup(response.text, "html.parser")

  rows = soup.find('tbody').find_all('tr')

  if (len(rows) == 0):
    break
    
  for row in rows:
    cells = row.find_all('td')
    collection.append({
        "url": base_url + cells[0].find('a').get('href'),
        "code": cells[0].getText(),
        "name": cells[1].getText(),
        "scientific_name": cells[2].getText(),
        "group": cells[3].getText(),
        "brand": cells[4].getText()
    })

  # Pause execution for 10 seconds
  time.sleep(10)

  page += 1

print(f"Fetched data until page: {page}")

print(f"Items collected: {len(collection)}")

# Specify the filename for the JSON output
filename = "output.json"

# Open the file in write mode ('w') and use json.dump() to write the data
with open(filename, 'w') as f:
    json.dump(collection, f, indent=4) # indent=4 for pretty-printing

print(f"Data saved to {filename}")