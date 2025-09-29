from rdflib import Graph
from groq import Groq
from dotenv import load_dotenv
import os

load_dotenv()
GROQ_TOKEN = os.getenv('GROQ_TOKEN')

# Carrega grafo RDF já salvo
g = Graph()
g.parse("grafo_taco_teste.ttl", format="turtle")

# Configura Groq
client = Groq(api_key=GROQ_TOKEN)

grupo_alimentar = ["Cereais e derivados", "Verduras, hortaliças e derivados", "Frutas e derivados", "Gorduras e óleos", "Carnes e derivados", "Pescados e frutos do mar", "Leite e derivados", "Bebidas (alcoólicas e não alcoólicas)", "Ovos e derivados", "Produtos açucarados", "Miscelâneas", "Outros alimentos industrializados", "Alimentos preparados", "Leguminosas e derivados", "Nozes e sementes"]

def pergunta_para_sparql(pergunta, erro_feedback=None):
    """
    Usa LLM para traduzir pergunta em SPARQL, adaptando caso receba erro como feedback
    """
   
    schema = """
    @prefix ns1: <http://mo656/taco/> .
    @prefix rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#> .
    @prefix rdfs: <http://www.w3.org/2000/01/rdf-schema#> .
    @prefix xsd: <http://www.w3.org/2001/XMLSchema#> .

    <http://mo656/taco/%C3%B3leo_de_baba%C3%A7u> a ns1:Alimento ;
        rdfs:label "Óleo, de babaçu" ;
        ns1:Carboidrato_g 0.0 ;
        ns1:Cobre_mg 0.0 ;
        ns1:Colesterol_mg 0.0 ;
        ns1:Cálcio_mg 0.0 ;
        ns1:Energia_kcal 884.0 ;
        ns1:Ferro_mg 0.0 ;
        ns1:Fibra_alimentar_g 0.0 ;
        ns1:Fósforo_mg 0.0 ;
        ns1:Lipídeos_g 100.0 ;
        ns1:Magnésio_mg 0.0 ;
        ns1:Manganês_mg 0.0 ;
        ns1:Niacina_mg 0.0 ;
        ns1:Piridoxina_mg 0.0 ;
        ns1:Potássio_mg 0.0 ;
        ns1:Proteína_g 0.0 ;
        ns1:Retinol_mcg 0.0 ;
        ns1:Riboflavina_mg 0.0 ;
        ns1:Sódio_mg 0.0 ;
        ns1:Tiamina_mg 0.0 ;
        ns1:Vitamina_C_mg 0.0 ;
        ns1:Zinco_mg 0.0 ;
        ns1:perteneceAoGrupo ns1:gorduras_e_%C3%B3leos .
    """   
    prompt = f"""
Você é um gerador de consultas SPARQL para um grafo RDF de alimentos e nutrientes.

## Instruções Gerais
- estes são os grupos alimentares presentes no grafo: {grupo_alimentar}
- Gere consultas SPARQL baseadas na pergunta do usuário.
- Siga rigorosamente os padrões e propriedades do grafo RDF fornecido.
- Não invente propriedades, classes ou estruturas.
- Retorne SOMENTE a consulta SPARQL, sem explicações, markdown, sem '''sparql''', '''sql'''.

## Exemplos de perguntas

- "Quais alimentos são ricos em proteína?"
- "Qual o teor de ferro na banana?"
- "Liste os alimentos do grupo cereal."

# regras
- Sempre use prefixos conforme o grafo RDF.
- os alimentos devem ser buscados pelo nome exato conforme estão no grafo, sem variações.
- os alimentos estão em porção de 100g, sempre traga os valores para 100g.
- Se o usuário pedir uma porção diferente, ignore e traga os valores para 100g.
- Para perguntas como "quais alimentos são ricos em proteína", retorne alimentos que tenham mais de 10g de proteína por porção.
- Não faça cálculos ou binds de valores, traga os valores originais do grafo.
- não procure pela descrição do alimento, procure pelo nome do alimento. SIGA ESSA REGRA RIGOROSAMENTE.
- Use filtros para restringir resultados conforme a pergunta.
- considere que os alimentos tipicamente consumidos cozidos, como arroz, feijão, carnes e legumes devem ser buscados em sua forma cozida, ignorando a forma crua.
nao use rdfs labels, se atenha ao grafo.
- as consultas devem sempre retornar a descrição do alimento (rdfs:label) e não a URI.
## Ontologia simplificada
{schema}

## Regra de nomenclatura
- Não use nomes genéricos como arroz_cozido.

## Pergunta do usuário
"{pergunta}"
"""

    chat_completion = client.chat.completions.create(
        messages=[{"role": "user", "content": prompt}],
        model="llama-3.3-70b-versatile",
        temperature=0
    )

    resultado = chat_completion.choices[0].message.content.strip()
    return resultado

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
    erro_feedback = None

    
    sparql = pergunta_para_sparql(pergunta, erro_feedback)
    print("\n⚡ Query SPARQL gerada:\n", sparql)

    resultados = executar_sparql(sparql)
    print("\n📊 Resultados brutos:", resultados)

    contexto = "\n".join([str(r) for r in resultados])
    prompt = f"""
    Contexto extraído do grafo:
    {contexto}

    Pergunta do usuário: {pergunta}

    Consulta SPARQL usada: {sparql}
    - O usuário quer saber sobre alimentos e seus nutrientes.
    - Responda com base apenas no contexto extraído do grafo e a pergunta.
    - Responda somente com o conhecimento extraído do grafo.

    - os valores na consulta SPARQL são para 100g do alimento.
    - Se a pergunta envolver porções diferentes de 100g, faça os cálculos necessários para ajustar os valores.
    Interprete a resposta recebida do grafo e responda de forma clara e objetiva.
    Não traga explicações, apenas a resposta direta.
    Se a resposta for [] vazia, responda "NÃO SEI"
    Se a resposta não trouxer informações relevantes, responda "CONTEXTO INSUFICIENTE PARA RESPONDER A PERGUNTA"
    - interprete os resultados e responda de forma clara e objetiva. não espere que o resultado seja uma frase pronta.
    """

    chat_completion = client.chat.completions.create(
        messages=[{"role": "user", "content": prompt}],
        model="llama-3.3-70b-versatile",
        temperature=2
    )

    resposta = chat_completion.choices[0].message.content.strip()
    print("\n🤖 Resposta final:", resposta)
    return resposta


# 🔥 Teste
# responder("quais frutas são ricas em potássio?")
responder("quais aliemntos são ricos em proteína?")
