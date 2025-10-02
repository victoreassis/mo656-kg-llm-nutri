import pandas as pd
from rdflib import SKOS, Graph, Literal, RDF, RDFS, Namespace, URIRef, XSD, OWL, SKOS
import os
import urllib.parse

g = Graph()

g.parse("C:\\Users\\Jacson\\Desktop\\websemantica\\mo656-kg-llm-nutri\\grafo_taco.ttl", format="ttl")
g .parse("C:\\Users\\Jacson\\Desktop\\websemantica\\mo656-kg-llm-nutri\\tbca_props.ttl", format="ttl")

g.bind("owl", OWL)
g.bind("skos", SKOS)

# Namespaces
TACO = Namespace("http://mo656/taco/")
TBCA = Namespace("http://mo656/tbca/")

grupo_alimentar = ["Cereais e derivados", "Verduras, hortalicas e derivados", "Frutas e derivados", "Gorduras e oleos", "Carnes e derivados", "Pescados e frutos do mar", "Leite e derivados", "Bebidas alcoolicas e não alcoolicas", "Ovos e derivados", "Produtos acucarados", "Miscelaneas", "Outros alimentos industrializados", "Alimentos preparados", "Leguminosas e derivados", "Nozes e sementes"]

for grupo in grupo_alimentar:
    grupo = grupo.replace(" ", "_").replace(",", "").replace("-", "_").lower()
    g.add((TACO[grupo], SKOS.exactMatch, TBCA[grupo]))



g.serialize("C:\\Users\\Jacson\\Desktop\\websemantica\\mo656-kg-llm-nutri\\grafo_taco_tbca.ttl", format="ttl")

