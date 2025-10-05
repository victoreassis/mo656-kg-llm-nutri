import unicodedata
import re
from rdflib import Graph, Namespace, OWL, SKOS

# ==============================================================================
# --- 1. FUNÇÃO DE PADRONIZAÇÃO ---
# ==============================================================================
def padronizar_nome(texto_original, tipo='classe'):
    """
    Limpa e padroniza uma string para ser um nome de Classe, Propriedade ou Indivíduo.
    """
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
# --- 2. CARREGAR E UNIR OS GRAFOS ---
# ==============================================================================
print("Iniciando a união dos grafos taco.ttl e tbca.ttl...")

taco_file = "taco.ttl"
tbca_file = "tbca.ttl"
output_file = "grafo_unificado.ttl"


g_unificado = Graph()

try:
    print(f"Carregando {taco_file}...")
    g_unificado.parse(taco_file, format="turtle")

    print(f"Carregando {tbca_file}...")
    g_unificado.parse(tbca_file, format="turtle")
    
    print("Grafos carregados com sucesso.")
except FileNotFoundError as e:
    print(f"ERRO: Arquivo não encontrado. Verifique se os arquivos .ttl existem nos caminhos corretos.")
    print(e)
    exit()

# ==============================================================================
# --- 3. DEFINIR NAMESPACES E CRIAR LINKS DE EQUIVALÊNCIA ---
# ==============================================================================
TACO = Namespace("http://mo656/taco/")
TBCA = Namespace("http://mo656/tbca/")
g_unificado.bind("taco", TACO)
g_unificado.bind("tbca", TBCA)
g_unificado.bind("owl", OWL)
g_unificado.bind("skos", SKOS)

grupos_alimentares_labels = [
    "Cereais e derivados", "Verduras, hortaliças e derivados", "Frutas e derivados", 
    "Gorduras e óleos", "Carnes e derivados", "Pescados e frutos do mar", 
    "Leite e derivados", "Bebidas (alcoólicas e não alcoólicas)", "Ovos e derivados", 
    "Produtos açucarados", "Miscelâneas", "Outros alimentos industrializados", 
    "Alimentos preparados", "Leguminosas e derivados", "Nozes e sementes",
    "Alimentos para fins especiais"
]

print("\nAdicionando links de equivalência (skos:exactMatch) entre os grupos...")
for grupo_label in grupos_alimentares_labels:

    grupo_padronizado = padronizar_nome(grupo_label, tipo='classe')
    

    uri_grupo_taco = TACO[grupo_padronizado]
    uri_grupo_tbca = TBCA[grupo_padronizado]
    

    g_unificado.add((uri_grupo_taco, SKOS.exactMatch, uri_grupo_tbca))    

    g_unificado.add((uri_grupo_tbca, SKOS.exactMatch, uri_grupo_taco))

    print(f"  - Link criado para: {grupo_padronizado}")

# ==============================================================================
# --- 4. SALVAR O GRAFO UNIFICADO ---
# ==============================================================================
print(f"\nSerializando o grafo unificado para '{output_file}'...")
g_unificado.serialize(destination=output_file, format="turtle")
print("Grafo unificado gerado com sucesso!")