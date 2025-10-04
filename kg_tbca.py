import json
import unicodedata
import re
from rdflib import Graph, Namespace, Literal, RDF, RDFS, XSD, OWL

# ==============================================================================
# --- 1. FUNÇÃO DE PADRONIZAÇÃO (sem alterações) ---
# ==============================================================================
def padronizar_nome(texto_original, tipo='propriedade'):
    if not isinstance(texto_original, str): return ""
    texto_sem_acentos = ''.join(c for c in unicodedata.normalize('NFD', texto_original)
                                if unicodedata.category(c) != 'Mn')
    palavras = re.findall(r'[a-zA-Z0-9]+', texto_sem_acentos)
    if not palavras: return ""
    palavras_capitalizadas = [palavra.capitalize() for palavra in palavras]
    nome_upper_camel = "".join(palavras_capitalizadas)
    if tipo in ['classe', 'individuo']: return nome_upper_camel
    elif tipo == 'propriedade': return nome_upper_camel[0].lower() + nome_upper_camel[1:]
    else: return nome_upper_camel

# ==============================================================================
# --- 2. SETUP DO GRAFO E CARREGAMENTO DE DADOS ---
# ==============================================================================
try:
    with open("C:\\Users\\Jacson\\Desktop\\websemantica\\mo656-kg-llm-nutri\\output.json", "r", encoding="utf-8") as f:
        data = json.load(f)
except FileNotFoundError:
    print("ERRO: Arquivo 'output.json' não encontrado. Verifique o nome e o caminho.")
    exit()

TBCA = Namespace("http://mo656/tbca/")

g = Graph()
g.bind("tbca", TBCA); g.bind("rdf", RDF); g.bind("rdfs", RDFS); g.bind("xsd", XSD); g.bind("owl", OWL)

g.add((TBCA.Alimento, RDF.type, OWL.Class)); g.add((TBCA.Alimento, RDFS.label, Literal("Alimento")))
g.add((TBCA.GrupoAlimentar, RDF.type, OWL.Class)); g.add((TBCA.GrupoAlimentar, RDFS.label, Literal("Grupo Alimentar")))
g.add((TBCA.pertenceAoGrupo, RDF.type, OWL.ObjectProperty)); g.add((TBCA.pertenceAoGrupo, RDFS.label, Literal("Pertence ao Grupo")))

nutrientes_taco_desejados = {
    "umidadeG", "energiaKcal", "proteinaG", "lipideosG", "colesterolMg",
    "carboidratoG", "fibraAlimentarG", "cinzasG", "calcioMg", "magnesioMg",
    "manganesMg", "fosforoMg", "ferroMg", "sodioMg", "potassioMg",
    "cobreMg", "zincoMg", "retinolMcg", "tiaminaMg", "riboflavinaMg",
    "piridoxinaMg", "niacinaMg", "vitaminaCMg"
}

grupos_definidos = set()
propriedades_definidas = set()

# ==============================================================================
# --- 3. CONSTRUÇÃO DO GRAFO A PARTIR DO JSON (COM FILTRO) ---
# ==============================================================================
print("Iniciando a construção do grafo TBCA (com esquema TACO) a partir do JSON...")

for alimento in data:
    nome_alimento_original = alimento["name"]
    grupo_alimento_original = alimento["group"]
    
    print(f"Processando: {nome_alimento_original}")

    alimento_padronizado = padronizar_nome(nome_alimento_original, tipo='individuo')
    alimento_uri = TBCA[alimento_padronizado]

    g.add((alimento_uri, RDF.type, TBCA.Alimento))
    g.add((alimento_uri, RDFS.label, Literal(nome_alimento_original, lang='pt')))

    for n in alimento["nutritional_values"]:
        componente = n["component"]
        unidade = n["unity"]
        valor = n["value"]

        nome_propriedade = padronizar_nome(f"{componente} {unidade}", tipo='propriedade')

        if nome_propriedade in nutrientes_taco_desejados:
            propriedade_uri = TBCA[nome_propriedade]
            
            if propriedade_uri not in propriedades_definidas:
                g.add((propriedade_uri, RDF.type, OWL.DatatypeProperty))
                g.add((propriedade_uri, RDFS.label, Literal(f"{componente} ({unidade})")))
                propriedades_definidas.add(propriedade_uri)

            if valor in ["-", "NA", "tr"]: valor = "0.0"

            try:
                valor_numerico = float(str(valor).replace(',', '.'))
                g.add((alimento_uri, propriedade_uri, Literal(valor_numerico, datatype=XSD.decimal)))
            except (ValueError, TypeError): pass

    grupo_padronizado = padronizar_nome(grupo_alimento_original, tipo='classe')
    grupo_uri = TBCA[grupo_padronizado]
    
    g.add((alimento_uri, TBCA.pertenceAoGrupo, grupo_uri))

    if grupo_uri not in grupos_definidos:
        g.add((grupo_uri, RDF.type, TBCA.GrupoAlimentar))
        g.add((grupo_uri, RDFS.label, Literal(grupo_alimento_original, lang='pt')))
        grupos_definidos.add(grupo_uri)

# ==============================================================================
# --- 4. SALVAR O GRAFO ---
# ==============================================================================
output_file = "C:\\Users\\Jacson\\Desktop\\websemantica\\mo656-kg-llm-nutri\\tbca1.ttl"
g.serialize(destination=output_file, format="turtle")

print(f"\nArquivo '{output_file}' (com esquema TACO) gerado com sucesso!")