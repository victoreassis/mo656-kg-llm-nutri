import json
import urllib.parse
from rdflib import Graph, Namespace, Literal, RDF, RDFS, XSD, URIRef
import unicodedata

# Carregar os dados do JSON
with open("output.json", "r", encoding="utf-8") as f:
    data = json.load(f)

# Definir namespaces
TBCA = Namespace("http://mo656/tbca/")
RDF_NS = RDF
RDFS_NS = RDFS
XSD_NS = XSD

# Criar grafo
g = Graph()
g.bind("tbca", TBCA)
g.bind("rdf", RDF_NS)
g.bind("rdfs", RDFS_NS)
g.bind("xsd", XSD_NS)

# relacionamentos
g.add((TBCA.perteneceAoGrupo, RDF.type, RDF.Property))

def substituir_acentos(valor: str) -> str:
    # Normaliza o texto em forma NFD (Normalization Form Canonical Decomposition)
    # isso separa as letras dos seus acentos, por exemplo, 'á' vira 'a' + '\u0301'
    valor = unicodedata.normalize('NFKD', valor)
    # Filtra e concatena apenas os caracteres que não são diacríticos (acentos)
    # Os diacríticos têm a categoria "Mn" (Mark, Nonspacing)
    return "".join([c for c in valor if not unicodedata.combining(c)])

def normalizar_uri(nome: str) -> str:
    """Transforma nome em URI com percent-encoding"""
    return urllib.parse.quote(substituir_acentos(nome).replace(" ", "_").replace("/","").replace("(","").replace(")","").replace(",","").lower())

def normalizar_predicado(componente: str, unidade: str) -> str:
    """Cria predicado no formato Nutriente_Unidade"""
    comp_norm = substituir_acentos(componente.replace(" ", "_").replace("-", "_"))
    predicado = f"{comp_norm}_{unidade}"
    return urllib.parse.quote(predicado)

grupos_alimentares = {
    'Leguminosas e derivados': "Leguminosas e derivados",
    'Nozes e sementes': "Nozes e sementes",
    'Alimentos industrializados': "Outros alimentos industrializados",
    'Vegetais e derivados': "Verduras, hortaliças e derivados",
    'Cereais e derivados': "Cereais e derivados",
    'Miscelâneas': "Miscelâneas",
    'Gorduras e óleos': "Gorduras e óleos",
    'Alimentos para fins especiais': "Alimentos para fins especiais",
    'Leite e derivados': "Leite e derivados",
    'Açúcares e doces': "Produtos açucarados",
    'Ovos e derivados': "Ovos e derivados",
    'Carnes e derivados': "Carnes e derivados",
    'Bebidas ': "Bebidas (alcoólicas e não alcoólicas)",
    'Fast food': "Alimentos preparados",
    'Frutas e derivados': "Frutas e derivados",
    'Pescados e frutos do mar': "Pescados e frutos do mar",
}

primeira_iteracao = True

# Construir RDF
for alimento in data:
    nome = alimento["name"]
    print(f"Criando item {nome}")
    grupo_alimentar = alimento["group"]
    alimento_uri = URIRef(f"http://mo656/tbca/{normalizar_uri(nome)}")

    # Tipo e label
    g.add((alimento_uri, RDF_NS.type, TBCA.Alimento))
    g.add((alimento_uri, RDFS_NS.label, Literal(nome)))

    # Nutrientes
    for n in alimento["nutritional_values"]:
        componente_nutricional = n["component"]
        valor = n["value"]
        unidade = n["unity"]

        if valor in ["-", "NA", "tr"]:
            valor = "0.0"

        predicado = TBCA[normalizar_predicado(componente_nutricional, unidade)]

        if primeira_iteracao:
            prop = TBCA[predicado]
            g.add((prop, RDF.type, RDF.Property))

        try:
            valor_numerico = float(valor)
            g.add((alimento_uri, predicado, Literal(valor_numerico, datatype=XSD.decimal)))
        except ValueError:
            # Caso não seja número válido
            g.add((alimento_uri, predicado, Literal(0.0, datatype=XSD.decimal)))

    # Grupo
    grupo_uri = URIRef(f"http://mo656/tbca/{normalizar_uri(grupos_alimentares[grupo_alimentar])}")
    g.add((alimento_uri, TBCA.perteneceAoGrupo, grupo_uri))
    g.add((grupo_uri, RDF.type, TBCA.GrupoAlimentar))
    g.add((grupo_uri, RDFS.label, Literal(grupos_alimentares[grupo_alimentar])))

    if primeira_iteracao:
        primeira_iteracao = False

# Salvar em arquivo Turtle
g.serialize(destination="tbca_props.ttl", format="turtle")

print("Arquivo tbca_props.ttl gerado com sucesso!")