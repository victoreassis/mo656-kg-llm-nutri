import pandas as pd
from rdflib import Graph, Literal, RDF, RDFS, Namespace, URIRef, XSD
import os
import urllib.parse

from groq import Groq

if not os.path.exists("grafo_taco.ttl"):

    def criar_uri_segura(nome, ns):
        nome_limpo = nome.replace(" ", "_").replace(",", "").replace("-", "_").lower()
        nome_limpo = nome_limpo.replace("(", "").replace(")", "").replace("/", "_").replace("á", "a").replace("é", "e").replace("í", "i").replace("ó", "o").replace("ú", "u").replace("ç", "c").replace("ã", "a").replace("õ", "o").replace("â", "a").replace("ê", "e").replace("ô", "o")
        return URIRef(ns[urllib.parse.quote(nome_limpo)])

    # Carregar planilha
    file_path = "C:\\Users\\Jacson\\Desktop\\websemantica\\mo656-kg-llm-nutri\\taco_tratada.xlsx"
    df = pd.read_excel(file_path)

    # Criar grafo
    g = Graph()

    # Namespaces
    TACO = Namespace("http://mo656/taco/")
    g.bind("taco", TACO)
    # relacionamentos
    g.add((TACO.perteneceAoGrupo, RDF.type, RDF.Property))
    #grupos alimentares
    grupo_alimentar = ["Cereais e derivados", "Verduras, hortaliças e derivados", "Frutas e derivados", "Gorduras e óleos", "Carnes e derivados", "Pescados e frutos do mar", "Leite e derivados", "Bebidas (alcoólicas e não alcoólicas)", "Ovos e derivados", "Produtos açucarados", "Miscelâneas", "Outros alimentos industrializados", "Alimentos preparados", "Leguminosas e derivados", "Nozes e sementes"]

    nutrientes = ["Umidade", "Cinzas_g" , "Energia_kcal", "Proteína_g", "Lipídeos_g", "Colesterol_mg", "Carboidrato_g", "Fibra_alimentar_g", "Cálcio_mg", "Magnésio_mg", "Manganês_mg", "Fósforo_mg", "Ferro_mg", "Sódio_mg", "Potássio_mg", "Cobre_mg", "Zinco_mg", "Retinol_mcg", "Tiamina_mg", "Riboflavina_mg", "Piridoxina_mg", "Niacina_mg", "Vitamina_C_mg"]

    # nutrientes como propriedades
    for nutriente in nutrientes:
        prop = TACO[nutriente]
        g.add((prop, RDF.type, RDF.Property))

    for i in range(len(df)):
        linha = df.iloc[i, 0]
        if linha in grupo_alimentar:
            grupo_uri = criar_uri_segura(linha, TACO)
            g.add((grupo_uri, RDF.type, TACO.GrupoAlimentar))
            g.add((grupo_uri, RDFS.label, Literal(linha)))

        # Adicionar alimentos 
        elif pd.notna(linha): 
                    
            alimento_uri = criar_uri_segura(linha, TACO)
            g.add((alimento_uri, RDF.type, TACO.Alimento))
            g.add((alimento_uri, RDFS.label, Literal(linha)))

            if grupo_uri:
                g.add((alimento_uri, TACO.perteneceAoGrupo, grupo_uri))

            # Adicionar nutrientes ao alimento
            for j in range(len(df.columns)):
                nutriente = df.columns[j]
                    
                if nutriente in nutrientes:
                    valor = df.iloc[i, j]
                    try:
                        valor = float(valor)
                        g.add((alimento_uri, TACO[nutriente], Literal(valor, datatype=XSD.decimal)))
                    except (ValueError, TypeError):
                        print(f"Valor inválido para {linha} - {nutriente}: {df.iloc[i, j]}")


    g.serialize("grafo_taco.ttl", format="turtle")

# Carregar grafo salvo
g = Graph()
g.parse("C:\\Users\\Jacson\\Desktop\\websemantica\\mo656-kg-llm-nutri\\grafo_taco.ttl", format="turtle")


#consultar grafo com SPARQL
consulta = """ PREFIX ns1: <http://mo656/taco/>
PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
PREFIX xsd: <http://www.w3.org/2001/XMLSchema#>

SELECT ?alimento ?potassio
WHERE {
    ?alimento ns1:perteneceAoGrupo ns1:frutas_e_derivados .
    ?alimento ns1:Potássio_mg ?potassio .
    FILTER (?potassio > 400)
}
"""

resultado = g.query(consulta)
print("Resultados da consulta:")
for row in resultado:
    print(f"Alimento: {row.alimento}, Potássio (mg): {row.potassio}")

exit(0)
