from rdflib import Graph
from groq import Groq
from dotenv import load_dotenv
import os
from persona import Persona

# Criar uma persona
personaA = Persona(55, 1.61, "feminino", 22, "pouco ativo", "emagrecimento", 3)

print("Persona A:")

print(personaA.objetivo)

# Calcular IMC
imc = personaA.calcular_imc()
print(f"IMC: {imc:.2f}")

# Classificar IMC
classificacao = personaA.classificar_imc()
print(f"Classificação: {classificacao}")

# Calcular TMB
tmb = personaA.calcular_taxa_metabolica_basal()
print(f"TMB: {tmb:.2f}")

# Calcular GET
get = personaA.calcular_gasto_energetico_total()
print(f"GET: {get:.2f}")

print(f"Número de refeições diárias: {personaA.quantidade_refeicoes}")

# Gerar queries para refeições
queries_refeicoes = personaA.definir_refeicoes()
for refeicao, query in queries_refeicoes.items():
    print(f"\nQuery para {refeicao}:\n{query}")


load_dotenv()
GROQ_TOKEN = "gsk_your_groq_api_token_here"

# Carrega grafo RDF já salvo
g = Graph()
g.parse("C:\\Users\\Jacson\\Desktop\\websemantica\\mo656-kg-llm-nutri\\grafo_taco_tbca.ttl", format="turtle")

# Configura Groq
client = Groq(api_key=GROQ_TOKEN)

grupo_alimentar = ["Cereais e derivados", "Verduras, hortaliças e derivados", "Frutas e derivados", "Gorduras e óleos", "Carnes e derivados", "Pescados e frutos do mar", "Leite e derivados", "Bebidas (alcoólicas e não alcoólicas)", "Ovos e derivados", "Produtos açucarados", "Miscelâneas", "Outros alimentos industrializados", "Alimentos preparados", "Leguminosas e derivados", "Nozes e sementes"]

def executar_sparql(query):
    """
    Executa a query no grafo RDF e retorna resultados
    """
    try:
        results = g.query(query)
        return list(results)
    except Exception as e:
        return [("Erro", str(e))]

def responder(pergunta):
    """
    Pipeline: pergunta -> SPARQL -> resultado -> resposta em linguagem natural
    Tenta adaptar a consulta SPARQL caso ocorra erro, enviando o erro como feedback para a LLM.
    """
    print("🔎 Pergunta:", pergunta)
    refeicoes = {}
    sparql = {}
    for refeicao, query in queries_refeicoes.items():
        refeicoes[refeicao] = executar_sparql(query)
        sparql[refeicao] = query
        print("\n⚡ Query SPARQL gerada:\n", query)

    
    prompt = f"""
    Contexto extraído do grafo:
    {refeicoes}

    Pergunta do usuário: {pergunta}

    Consulta SPARQL usada: {sparql}

    - O usuário quer saber sobre alimentos e seus nutrientes.
    - Responda somente com o conhecimento extraído do grafo.
    - Os valores na consulta SPARQL são para 100g do alimento.
    - Se a pergunta envolver porções diferentes de 100g, faça os cálculos necessários para ajustar os valores.
    - Interprete a resposta recebida do grafo e responda de forma clara e objetiva, não espere que o resultado seja uma frase pronta.
    - Não traga explicações, apenas a resposta direta.
    - Se o contexto extraído do grafo for igual a "[]", responda "NÃO SEI".
    """

    print(f"\nPrompt final: {prompt}")

    chat_completion = client.chat.completions.create(
        messages=[{"role": "user", "content": prompt}],
        model="llama-3.3-70b-versatile",
        temperature=0
    )

    resposta = chat_completion.choices[0].message.content.strip()
    print("\n🤖 Resposta final:", resposta)
    return resposta

responder(personaA.gerar_pergunta())

# 🔥 Teste
# responder("quais frutas são ricas em potássio?")
# responder("quais alimentos são ricos em proteína?")
# responder("quantas calorias no Azeite, de oliva, extra virgem?")
# print("\n".join([str(r) for r in []]))
# responder("quantas calorias tem a vitela?")
# responder("quais os nutrientes do azeite?")
# responder("quais os nutrientes da vitela?")

# erro_feedback = None
# sparql = pergunta_para_sparql("quais os nutrientes do azeite?", erro_feedback)
# print(sparql)

# Pergunta direta para a LLM sem KG
# print(client.chat.completions.create(
#     messages=[{"role": "user", "content": "quais frutas são ricas em potássio?"}],
#     model="llama-3.3-70b-versatile",
#     temperature=2
# ).choices[0].message.content.strip())

# Criar as queries SPARQL
# Elabore um cardápio de dieta de emagrecimento para uma mulher adulta, com peso 70,8kg, altura de 1,61 m, idade 22 anos, nível de atividade física leve.
# Informe qual é a perda de peso calculada por mês, a partir da dieta calculada, e em quanto tempo essa mulher alcançaria um IMC considerado adequado


