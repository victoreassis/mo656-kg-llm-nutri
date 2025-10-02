from rdflib import Graph
from groq import Groq
from dotenv import load_dotenv
import os

load_dotenv()
GROQ_TOKEN = os.getenv('GROQ_TOKEN')

# Carrega grafo RDF já salvo
#g = Graph()
#g.parse("grafo_taco_tbca.ttl", format="turtle")

# Configura Groq
client = Groq(api_key=GROQ_TOKEN)

grupo_alimentar = ["Cereais e derivados", "Verduras, hortaliças e derivados", "Frutas e derivados", "Gorduras e óleos", "Carnes e derivados", "Pescados e frutos do mar", "Leite e derivados", "Bebidas (alcoólicas e não alcoólicas)", "Ovos e derivados", "Produtos açucarados", "Miscelâneas", "Outros alimentos industrializados", "Alimentos preparados", "Leguminosas e derivados", "Nozes e sementes"]

def pergunta_para_sparql(pergunta, erro_feedback=None):
    """
    Usa LLM para traduzir pergunta em SPARQL, adaptando caso receba erro como feedback
    """
   
    schema = """
    @prefix rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#> .
    @prefix rdfs: <http://www.w3.org/2000/01/rdf-schema#> .
    @prefix skos: <http://www.w3.org/2004/02/skos/core#> .
    @prefix taco: <http://mo656/taco/> .
    @prefix tbca: <http://mo656/tbca/> .
    @prefix xsd: <http://www.w3.org/2001/XMLSchema#> .

    <http://mo656/taco/%C3%B3leo_de_baba%C3%A7u> a taco:Alimento ;
        rdfs:label "Óleo, de babaçu" ;
        taco:Carboidrato_g 0.0 ;
        taco:Cinzas_g 0.0 ;
        taco:Cobre_mg 0.0 ;
        taco:Colesterol_mg 0.0 ;
        taco:Cálcio_mg 0.0 ;
        taco:Energia_kcal 884.0 ;
        taco:Ferro_mg 0.0 ;
        taco:Fibra_alimentar_g 0.0 ;
        taco:Fósforo_mg 0.0 ;
        taco:Lipídeos_g 100.0 ;
        taco:Magnésio_mg 0.0 ;
        taco:Manganês_mg 0.0 ;
        taco:Niacina_mg 0.0 ;
        taco:Piridoxina_mg 0.0 ;
        taco:Potássio_mg 0.0 ;
        taco:Proteína_g 0.0 ;
        taco:Retinol_mcg 0.0 ;
        taco:Riboflavina_mg 0.0 ;
        taco:Sódio_mg 0.0 ;
        taco:Tiamina_mg 0.0 ;
        taco:Umidade 0.0 ;
        taco:Vitamina_C_mg 0.0 ;
        taco:Zinco_mg 0.0 ;
        taco:perteneceAoGrupo taco:gorduras_e_%C3%B3leos .

    tbca:abacate_polpa_in_natura_brasil a tbca:Alimento ;
        rdfs:label "Abacate, polpa, in natura, Brasil" ;
        tbca:Acidos_graxos_monoinsaturados_g 3.18 ;
        tbca:Acidos_graxos_poliinsaturados_g 1.04 ;
        tbca:Acidos_graxos_saturados_g 1.7 ;
        tbca:Acidos_graxos_trans_g 0.0 ;
        tbca:Acucar_de_adicao_g 0.0 ;
        tbca:Alcool_g 0.0 ;
        tbca:Alfa_tocoferol_%28Vitamina_E%29_mg 0.02 ;
        tbca:Calcio_mg 7.16 ;
        tbca:Carboidrato_disponivel_g 1.81 ;
        tbca:Carboidrato_total_g 5.84 ;
        tbca:Cinzas_g 0.47 ;
        tbca:Cobre_mg 0.12 ;
        tbca:Colesterol_mg 0.0 ;
        tbca:Energia_kJ 312.0 ;
        tbca:Energia_kcal 76.0 ;
        tbca:Equivalente_de_folato_mcg 41.5 ;
        tbca:Ferro_mg 0.18 ;
        tbca:Fibra_alimentar_g 4.03 ;
        tbca:Fosforo_mg 18.5 ;
        tbca:Gordura_de_adicao_g 0.0 ;
        tbca:Lipidios_g 6.21 ;
        tbca:Magnesio_mg 17.0 ;
        tbca:Niacina_mg 0.0 ;
        tbca:Potassio_mg 174.0 ;
        tbca:Proteina_animal_g 0.0 ;
        tbca:Proteina_g 1.15 ;
        tbca:Proteina_vegetal_g 1.15 ;
        tbca:Riboflavina_mg 0.04 ;
        tbca:Sal_de_adicao_g 0.0 ;
        tbca:Selenio_mcg 0.2 ;
        tbca:Sodio_mg 0.0 ;
        tbca:Tiamina_mg 0.0 ;
        tbca:Umidade_g 86.3 ;
        tbca:Vitamina_A_%28RAE%29_mcg 3.11 ;
        tbca:Vitamina_A_%28RE%29_mcg 6.21 ;
        tbca:Vitamina_B12_mcg 0.0 ;
        tbca:Vitamina_B6_mg 0.0 ;
        tbca:Vitamina_C_mg 7.32 ;
        tbca:Vitamina_D_mcg 0.0 ;
        tbca:Zinco_mg 0.23 ;
        tbca:perteneceAoGrupo tbca:frutas_e_derivados .
    """
   
    prompt = f"""
Você é um gerador de consultas SPARQL para um grafo RDF de alimentos e nutrientes.

## Exemplos de perguntas

- "Quais alimentos são ricos em proteína?"
- "Qual o teor de ferro na banana?"
- "Liste os alimentos do grupo cereal."

## Regras

- Estes são os grupos alimentares presentes no grafo: {grupo_alimentar}
- Gere consultas SPARQL baseadas na pergunta do usuário.
- Siga rigorosamente os padrões e propriedades do grafo RDF fornecido.
- Não invente propriedades, classes ou estruturas.
- Quando a pergunta envolver nutrientes informe o nutriente na resposta.
- Entender caloria como a propriedade Energia_kcal.
- Retorne SOMENTE a consulta SPARQL, sem explicações, markdown, sem '''sparql''', '''sql'''.
- Sempre use prefixos conforme o grafo RDF.
- Os alimentos estão em porção de 100g, sempre traga os valores para 100g.
- Se o usuário pedir uma porção diferente, ignore e traga os valores para 100g.
- Para perguntas como "quais alimentos são ricos em proteína", retorne alimentos que tenham mais de 10g de proteína por porção.
- Para perguntas como "quais alimentos são ricos em potássio", retorne alimentos que tenham mais de 400g de potássio por porção.
- Não faça cálculos ou binds de valores, traga os valores originais do grafo.
- Aplicar filtro de expressão regular para encontrar APENAS o ínicio do nome alimento.
- O filter é SEMPRE o último componente do WHERE em SPARQL.
- Adicionar o grupo alimentar como componente do WHERE APENAS quando extritamente mencionada.
- Use filtros para restringir resultados conforme a pergunta.
- Considere que os alimentos tipicamente consumidos cozidos, como arroz, feijão, carnes e legumes devem ser buscados em sua forma cozida, ignorando a forma crua.
- As consultas devem SEMPRE selecionar o nome do alimento, i.e, (?label).
- Tentar encontrar o alimento no namespace TACO e TBCA.

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
        temperature=0.5
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

    prompt = f"""
    Contexto extraído do grafo:
    {resultados}

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

class Persona:
    def __init__(self, peso, altura, sexo, idade, nivel_atividade_fisica, restricao_alimentar, objetivo, quantidade_refeicoes):
        self.peso = peso # em kg
        self.altura = altura # em metros
        self.sexo = sexo # masculino ou feminino
        self.idade = idade # em anos
        self.nivel_atividade_fisica = nivel_atividade_fisica # ex: sedentário, leve, moderado, intenso
        self.restricao_alimentar = restricao_alimentar # ex: nenhuma, vegetariana, vegana, intolerância à lactose, doença celíaca
        self.objetivo = objetivo # ex: emagrecimento, ganho de massa muscular, manutenção
        self.quantidade_refeicoes = quantidade_refeicoes # por dia
    
    # Cálculo do IMC
    def calcular_imc(self):
        imc = self.peso / (self.altura ** 2)
        return imc
    
    # Classificação do IMC
    def classificar_imc(self):  
        imc = self.calcular_imc()
        if imc < 18.5:
            return "Abaixo do peso"
        elif 18.5 <= imc < 24.9:
            return "Peso normal"
        elif 25 <= imc < 29.9:
            return "Sobrepeso"
        else:
            return "Obesidade"
        
    def calcular_taxa_metabolica_basal(self):
        if self.sexo == "masculino":
            tmb = 88.36 + (13.4 * self.peso) + (4.8 * (self.altura * 100)) - (5.7 * self.idade)
        else:
            tmb = 447.6 + (9.2 * self.peso) + (3.1 * (self.altura * 100)) - (4.3 * self.idade)
        return tmb
    
    def calcular_gasto_calorico_total(self):
        tmb = self.calcular_taxa_metabolica_basal()
        if self.nivel_atividade_fisica == "sedentário":
            fator_atividade = 1.2
        elif self.nivel_atividade_fisica == "leve":
            fator_atividade = 1.375
        elif self.nivel_atividade_fisica == "moderado":
            fator_atividade = 1.55
        else: # intenso
            fator_atividade = 1.725
        gct = tmb * fator_atividade
        return gct
    
    def definir_almoco(self):
        if self.objetivo == "emagrecimento":
            calorias_almoco = self.calcular_gasto_calorico_total() * 0.3
        elif self.objetivo == "ganho de massa muscular":
            calorias_almoco = self.calcular_gasto_calorico_total() * 0.4
        else: # manutenção
            calorias_almoco = self.calcular_gasto_calorico_total() * 0.35
        
        # TODO: Retornar uma query SPARQL para alimentos da refeição

        return calorias_almoco
    
    def definir_jantar(self):
        if self.objetivo == "emagrecimento":
            calorias_jantar = self.calcular_gasto_calorico_total() * 0.2
        elif self.objetivo == "ganho de massa muscular":
            calorias_jantar = self.calcular_gasto_calorico_total() * 0.3
        else: # manutenção
            calorias_jantar = self.calcular_gasto_calorico_total() * 0.25
        
        # TODO: Retornar uma query SPARQL para alimentos da refeição

        return calorias_jantar
    
    def definir_lanches(self):
        if self.objetivo == "emagrecimento":
            calorias_lanches = self.calcular_gasto_calorico_total() * 0.1
        elif self.objetivo == "ganho de massa muscular":
            calorias_lanches = self.calcular_gasto_calorico_total() * 0.1
        else: # manutenção
            calorias_lanches = self.calcular_gasto_calorico_total() * 0.1

        # TODO: Retornar uma query SPARQL para alimentos da refeição

        return calorias_lanches
    
    def definir_refeicoes(self):
        # valor calorico total (%)
        # cafe da manha = 25 
        # lanche da manha = 5
        # almoco = 30
        # lanche da tarde = 10
        # jantar = 25
        # ceia = 5

        return self
    
# Exemplo de uso
personaA = Persona(
    70.8, 1.61, "feminino", 22, "leve", "nenhuma", "emagrecimento", 5
)

print(personaA.definir_almoco())

personaB = Persona(
    70.8, 1.61, "feminino", 22, "leve", "nenhuma", "ganho de massa muscular", 5
)

print(personaB.definir_almoco())


