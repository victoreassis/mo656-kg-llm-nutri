import requests  # fazer requisições HTTP em Python, usada para interagir com APIs web e obter dados de fontes externas.
from bs4 import BeautifulSoup # analisar documentos HTML e XML. Ele cria uma árvore de análise para documentos que pode ser usada para extrair dados de HTML.
import time
import json

# TODO: Read json file
# TODO: Iterate through items
# TODO: Fetch dailed nutrional data for each item
# TODO: Save data as json

# Specify the filename for the JSON output
filename = "output.json"

with open(filename, 'r') as file:
    collection = json.load(file)

def save_json_file(filename, collection):
  # Open the file in write mode ('w') and use json.dump() to write the data
  with open(filename, 'w') as f:
      json.dump(collection, f, indent=4) # indent=4 for pretty-printing

  print(f"Data saved to {filename}")

counter = 1;

for item in collection:
  try:
    response = requests.get(item['url'])
  except:
    time.sleep(60)
    response = requests.get(item['url'])

  soup = BeautifulSoup(response.text, "html.parser")

  rows = soup.find('tbody').find_all('tr')

  if item.get('nutritional_values') != None:
    counter += 1
    continue
    
  item['nutritional_values'] = []

  for row in rows:
    cells = row.find_all('td')

    value = cells[2].getText();

    try:
        value = float(value.replace(',', '.'))
    except ValueError:
        pass
    
    item['nutritional_values'].append({
        "component": cells[0].getText(),
        "unity": cells[1].getText(),
        "value": value,
    })

  print(item)

  save_json_file('output.json', collection)

  print(counter)
  counter += 1

  # Pause execution for 15 seconds
  time.sleep(15)