# seu_arquivo_principal.py (VERSÃO CORRIGIDA)

from rdflib import Graph
from groq import Groq
from dotenv import load_dotenv
import os
from persona import Persona # Importa a classe do outro arquivo

# --- SETUP INICIAL ---
load_dotenv()
# GROQ_TOKEN = os.getenv("GROQ_API_KEY") # Forma mais segura de carregar a chave
GROQ_TOKEN = "gsk_your_groq_api_token_here"
client = Groq(api_key=GROQ_TOKEN)

# Carrega o grafo unificado
g = Graph()
g.parse("C:\\Users\\Jacson\\Desktop\\websemantica\\mo656-kg-llm-nutri\\grafo_unificado.ttl", format="turtle")

# --- FUNÇÕES AUXILIARES ---
def executar_sparql(query):
    try:
        results = g.query(query)
        # MELHORIA: Retorna uma lista de dicionários, mais fácil de usar
        return [dict(row.items()) for row in results]
    except Exception as e:
        print(f"ERRO na query SPARQL: {e}")
        return []

def formatar_contexto_refeicoes(refeicoes_dict: dict) -> str:
    contexto_formatado = ""
    for refeicao, resultados in refeicoes_dict.items():
        titulo_refeicao = refeicao.replace("_", " ").title()
        contexto_formatado += f"### Opções para {titulo_refeicao}\n"
        if not resultados:
            contexto_formatado += "- Nenhuma opção de alimento encontrada.\n\n"
            continue
        contexto_formatado += "| Alimento | Calorias (por 100g) | Fonte |\n"
        contexto_formatado += "|---|---|---|\n"
        for item in resultados:
            # CORREÇÃO: Acessando os dados pelo nome da variável
            label = item.get('label', 'N/A')
            energia = item.get('energiaKcal', 'N/A')
            fonte = item.get('fonte', 'N/A')
            contexto_formatado += f"| {label} | {energia} | {fonte} |\n"
        contexto_formatado += "\n"
    return contexto_formatado

def responder(pergunta, queries_refeicoes):
    print("🔎 Pergunta para a LLM:", pergunta)
    
    refeicoes_resultados = {}
    for refeicao, query in queries_refeicoes.items():
        refeicoes_resultados[refeicao] = executar_sparql(query)

    if not any(refeicoes_resultados.values()):
        resposta_final = "NÃO SEI. Não foi possível encontrar alimentos no grafo que atendam aos critérios."
        print(f"\n🤖 Resposta final (sem LLM): {resposta_final}")
        return resposta_final

    contexto_formatado = formatar_contexto_refeicoes(refeicoes_resultados)
    
    prompt = f"""
    ## PERSONA
    Você é uma nutricionista virtual que cria planos alimentares personalizados com base em dados das tabelas TACO e TBCA, com foco na culinária brasileira.

    ## CONTEXTO - ALIMENTOS DISPONÍVEIS
    A seguir uma lista de alimentos pré-selecionados, separados por refeição. Os valores calóricos são por 100g.

    {contexto_formatado}
    ## TAREFA E PERGUNTA DO USUÁRIO
    Com base estritamente nos alimentos do CONTEXTO, responda à pergunta do usuário:
    "{pergunta}"

    ## REGRAS E FORMATO DA RESPOSTA
    1. Crie um plano alimentar completo.
    2. Siga rigorosamente as calorias totais para cada refeição. 
    - Você DEVE calcular a porção em gramas de cada alimento para atingir o objetivo calórico.
    - Você DEVE diminuir a quantidade Gramas, dos alimentos para que as calorias se adequem à re
    3. Use apenas os alimentos do CONTEXTO.
    4. Não invente valores nutricionais.
    5. Formato: Apresente a dieta de forma clara. Para cada refeição, liste os alimentos, a porção em gramas e as calorias da porção. Exemplo:
    **Café da Manhã (Total Aprox: 300 kcal)**
    - Pão Francês: 70g (Aprox. 202 kcal)
    - Queijo Minas Frescal: 30g (Aprox. 75 kcal)
    6. Seja direta. Apenas o plano alimentar.
    7. Se o contexto for insuficiente, informe isso claramente.
    """
    print(f"\nPrompt final enviado para a LLM:\n{prompt}")
    
    chat_completion = client.chat.completions.create(
        messages=[{"role": "user", "content": prompt}],
        model="llama-3.3-70b-versatile",
        temperature=0
    )
    resposta = chat_completion.choices[0].message.content.strip()
    print("\n🤖 Resposta final:", resposta)
    return resposta


# 1. Criar a persona (usando os dados do seu exemplo de erro)
personaA = Persona(peso=75, altura=1.65, sexo="feminino", idade=30, 
                    nivel_atividade_fisica="pouco ativo", objetivo="emagrecimento", 
                    quantidade_refeicoes=4)

# 2. Gerar o dicionário de queries SPARQL a partir da persona
queries_para_llm = personaA.definir_refeicoes()

# 3. Gerar a pergunta (prompt) para a LLM
pergunta_para_llm = personaA.gerar_pergunta()

# 4. Chamar a função principal que executa tudo
resposta_da_dieta = responder(pergunta_para_llm, queries_para_llm)
