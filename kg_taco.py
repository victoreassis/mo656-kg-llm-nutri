import pandas as pd
from rdflib import Graph, Literal, RDF, RDFS, Namespace, URIRef, XSD, OWL
import os
import unicodedata
import re

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

if not os.path.exists("taco.ttl"):
    print("Arquivo de grafo não encontrado. Iniciando a criação...")

    file_path = "taco_tratada.xlsx"
    
    try:
        # Lendo o Excel e usando a primeira linha como cabeçalho (padrão)
        print(f"Lendo o arquivo Excel de: {file_path}")
        df = pd.read_excel(file_path)
    except FileNotFoundError:
        print(f"ERRO: Arquivo não encontrado em {file_path}")
        exit()

    # Padronização dinâmica dos Nomes das Colunas
    colunas_para_renomear = {}
    lista_nutrientes_padronizados = []
    
    for coluna_original in df.columns:
        if coluna_original == df.columns[0]:
            colunas_para_renomear[coluna_original] = "nome"
        else:
            coluna_padronizada = padronizar_nome(coluna_original, tipo='propriedade')
            colunas_para_renomear[coluna_original] = coluna_padronizada
            lista_nutrientes_padronizados.append(coluna_padronizada)
            
    df.rename(columns=colunas_para_renomear, inplace=True)
    
    print("Colunas do DataFrame padronizadas com sucesso!")
    print("Nomes das colunas agora:", list(df.columns))

    # Setup do Grafo e Namespaces
    g = Graph()
    TACO = Namespace("http://mo656/taco/")
    g.bind("taco", TACO); g.bind("rdfs", RDFS); g.bind("rdf", RDF); g.bind("owl", OWL)

    # Definição da Ontologia
    g.add((TACO.Alimento, RDF.type, OWL.Class)); g.add((TACO.Alimento, RDFS.label, Literal("Alimento")))
    g.add((TACO.GrupoAlimentar, RDF.type, OWL.Class)); g.add((TACO.GrupoAlimentar, RDFS.label, Literal("Grupo Alimentar")))
    g.add((TACO.pertenceAoGrupo, RDF.type, OWL.ObjectProperty)); g.add((TACO.pertenceAoGrupo, RDFS.label, Literal("Pertence ao Grupo")))

    for nutriente_nome in lista_nutrientes_padronizados:
        propriedade_uri = TACO[nutriente_nome]
        g.add((propriedade_uri, RDF.type, OWL.DatatypeProperty))
        g.add((propriedade_uri, RDFS.label, Literal(nutriente_nome)))

    grupo_atual_uri = None
    print("\nIniciando processamento das linhas da planilha...")
    for index, row in df.iterrows():
        nome_original = row['nome']
        if pd.isna(nome_original): continue

        if pd.isna(row.iloc[1]): # Checa a segunda coluna para ver se é grupo
            grupo_label = nome_original
            grupo_padronizado = padronizar_nome(grupo_label, tipo='classe')
            grupo_atual_uri = TACO[grupo_padronizado]
            g.add((grupo_atual_uri, RDF.type, TACO.GrupoAlimentar))
            g.add((grupo_atual_uri, RDFS.label, Literal(grupo_label, lang='pt')))
            print(f"\n--- Processando Grupo: {grupo_label} ---")
        else:
            if grupo_atual_uri is None:
                print(f"AVISO: Alimento '{nome_original}' encontrado sem um grupo. Pulando.")
                continue
            print(f"  - Processando Alimento: {nome_original}")
            alimento_padronizado = padronizar_nome(nome_original, tipo='individuo')
            alimento_uri = TACO[alimento_padronizado]
            g.add((alimento_uri, RDF.type, TACO.Alimento))
            g.add((alimento_uri, RDFS.label, Literal(nome_original, lang='pt')))
            g.add((alimento_uri, TACO.pertenceAoGrupo, grupo_atual_uri))
            
            for nutriente_coluna in lista_nutrientes_padronizados:
                valor = row[nutriente_coluna]
                if pd.notna(valor):
                    try:
                        valor_numerico = float(str(valor).replace(',', '.'))
                        g.add((alimento_uri, TACO[nutriente_coluna], Literal(valor_numerico, datatype=XSD.decimal)))
                    except (ValueError, TypeError): pass

    print("\nSerializando o grafo para o arquivo 'grafo_taco_final.ttl'...")
    g.serialize(destination="taco.ttl", format="turtle")
    print("Grafo criado com sucesso!")

else:
    print("O arquivo 'taco.ttl' já existe. Nenhuma ação foi tomada.")

# Carregar grafo salvo
g = Graph()
g.parse("taco.ttl", format="turtle")

