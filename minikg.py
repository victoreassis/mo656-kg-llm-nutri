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

calcio_mg = nutri.calcio_mg
carboidrato_g = nutri.carboidrato_g
gluten_g = nutri.gluten_g
proteina_g = nutri.proteina_g
potassio_mg = nutri.potassio_mg
ferro_mg = nutri.ferro_mg

# Definindo os predicados como propriedades RDF
g.add((pertence_ao_grupo, RDF.type, RDF.Property))
g.add((tem_nutriente, RDF.type, RDF.Property))
g.add((calcio_mg, RDF.type, RDF.Property))
g.add((carboidrato_g, RDF.type, RDF.Property))
g.add((gluten_g, RDF.type, RDF.Property))
g.add((proteina_g, RDF.type, RDF.Property))
g.add((potassio_mg, RDF.type, RDF.Property))
g.add((ferro_mg, RDF.type, RDF.Property))


# Sujeitos (alimentos)
itens = ['banana', 'iogurte', 'arroz', 'trigo']
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
nutrientes = ['carboidrato', 'proteina', 'potassio', 'calcio', 'ferro', 'gluten']
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
g.add((itens_uris['banana'], carboidrato_g, Literal(28.0)))
g.add((itens_uris['banana'], potassio_mg, Literal(358.0)))

# Contexto: iogurte pertence ao grupo laticínio
g.add((grupos_uris['laticinio'], RDF.type, grupo))

g.add((itens_uris['iogurte'], RDF.type, Alimento))
g.add((itens_uris['iogurte'], pertence_ao_grupo, grupos_uris['laticinio']))
g.add((itens_uris['iogurte'], proteina_g, Literal(10.0)))
g.add((itens_uris['iogurte'], calcio_mg, Literal(120.0)))
g.add((itens_uris['iogurte'], gluten_g, Literal(0.0)))


# Contexto: arroz pertence ao grupo cereal
g.add((grupos_uris['cereal'], RDF.type, grupo))

g.add((itens_uris['arroz'], RDF.type, Alimento))
g.add((itens_uris['arroz'], pertence_ao_grupo, grupos_uris['cereal']))
g.add((itens_uris['arroz'], carboidrato_g, Literal(28.0)))
g.add((itens_uris['arroz'], ferro_mg, Literal(0.4)))

# Contexto: trigo pertence ao grupo cereal
g.add((itens_uris['trigo'], RDF.type, Alimento))
g.add((itens_uris['trigo'], pertence_ao_grupo, grupos_uris['cereal']))
g.add((itens_uris['trigo'], gluten_g, Literal(5.0)))
g.add((itens_uris['trigo'], carboidrato_g, Literal(75.0)))

# Salva o grafo
g.serialize("minikg.ttl", format="turtle")


