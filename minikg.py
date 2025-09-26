from rdflib import Graph, URIRef, Literal, Namespace, RDF
from rdflib.namespace import OWL, RDFS

# Namespaces
ex = Namespace("http://exemplo.org/")
nutri = Namespace("http://exemplo.org/nutri/")

g = Graph()
g.bind("ex", ex)
g.bind("nutri", nutri)

# Predicados
pertence_ao_grupo = nutri.pertence_ao_grupo
tem_nutriente = nutri.tem_nutriente

# Sujeitos (alimentos)
itens = ['banana', 'iogurte', 'arroz']
itens_uris = {}
for item in itens:
    itens_uris[item] = nutri[item]


# Objeto (grupo)
grupos = ['fruta', 'laticinio', 'cereal']
grupos_uris = {}
for grupo in grupos:
    g.add((nutri[grupo], RDF.type, nutri.Grupo))
    grupos_uris[grupo] = nutri[grupo]

grupo = nutri.Grupo
Alimento = nutri.Alimento

e_nutriente = nutri.Nutriente
#owl
g.add((pertence_ao_grupo, RDF.type, OWL.FunctionalProperty))

g.add((pertence_ao_grupo, RDFS.domain, Alimento))
g.add((pertence_ao_grupo, RDFS.range, grupo))

# Nutrientes
nutrientes = ['carboidrato', 'proteina', 'potassio', 'calcio', 'ferro']
nutriente_uris = {}
for n in nutrientes:
    nutriente_uris[n] = nutri[n]
    g.add((nutri[n], RDF.type, e_nutriente))

g.add((e_nutriente, RDF.type, RDF.Property))

g.add((Alimento, RDF.type, grupo))

# Contexto: banana pertence ao grupo fruta
g.add((grupos_uris['fruta'], RDF.type, grupo))

g.add((itens_uris['banana'], RDF.type, Alimento))
g.add((itens_uris['banana'], pertence_ao_grupo, grupos_uris['fruta']))
g.add((itens_uris['banana'], tem_nutriente, nutriente_uris['carboidrato']))
g.add((itens_uris['banana'], tem_nutriente, nutriente_uris['potassio']))

# Contexto: iogurte pertence ao grupo laticínio
g.add((grupos_uris['laticinio'], RDF.type, grupo))

g.add((itens_uris['iogurte'], RDF.type, Alimento))
g.add((itens_uris['iogurte'], pertence_ao_grupo, grupos_uris['laticinio']))
g.add((itens_uris['iogurte'], tem_nutriente, nutriente_uris['proteina']))
g.add((itens_uris['iogurte'], tem_nutriente, nutriente_uris['calcio']))


# Contexto: arroz pertence ao grupo cereal
g.add((grupos_uris['cereal'], RDF.type, grupo))

g.add((itens_uris['arroz'], RDF.type, Alimento))
g.add((itens_uris['arroz'], pertence_ao_grupo, grupos_uris['cereal']))
g.add((itens_uris['arroz'], tem_nutriente, nutriente_uris['carboidrato']))
g.add((itens_uris['arroz'], tem_nutriente, nutriente_uris['ferro']))


# Salva o grafo
g.serialize("minikg.ttl", format="turtle")


