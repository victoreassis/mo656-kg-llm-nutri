# persona.py (VERSÃO COM ORDENAÇÃO INTELIGENTE)

class Persona:
    # ... (todo o início da sua classe, __init__, calcular_imc, etc., continua igual)
    # (código omitido por brevidade)
    def __init__(self, peso, altura, sexo, idade, nivel_atividade_fisica, objetivo, quantidade_refeicoes):
        self.peso = peso; self.altura = altura; self.sexo = sexo; self.idade = idade
        self.nivel_atividade_fisica = nivel_atividade_fisica; self.objetivo = objetivo
        self.quantidade_refeicoes = quantidade_refeicoes
    def calcular_imc(self): return self.peso / (self.altura ** 2)
    def classificar_imc(self):   
        imc = self.calcular_imc()
        if imc < 18.5: return "Abaixo do peso"
        elif 18.5 <= imc < 24.9: return "eutrófico"
        elif 25 <= imc < 29.9: return "Sobrepeso"
        else: return "Obesidade"
    def calcular_gasto_energetico_total(self):
        if self.sexo == "masculino":
            if self.nivel_atividade_fisica == "inativo": fator_atividade = 753.07-(10.83*self.idade)+(6.50*self.altura*100)+(14.10*self.peso)
            elif self.nivel_atividade_fisica == "pouco ativo": fator_atividade = 581.47-(10.83*self.idade)+(8.30*self.altura*100)+(14.94*self.peso)
            elif self.nivel_atividade_fisica == "ativo": fator_atividade = 1004.82-(10.83*self.idade)+(6.52*self.altura*100)+(15.91*self.peso)
            else: fator_atividade = 517.88-(10.83*self.idade)+(15.61*self.altura*100)+(19.11*self.peso)
        else:
            if self.nivel_atividade_fisica == "inativo": fator_atividade = 584.90-(7.01*self.idade)+(5.72*self.altura*100)+(11.71*self.peso)
            elif self.nivel_atividade_fisica == "pouco ativo": fator_atividade = 575.77-(7.01*self.idade)+(6.60*self.altura*100)+(12.14*self.peso)
            elif self.nivel_atividade_fisica == "ativo": fator_atividade = 710.25-(7.01*self.idade)+(6.54*self.altura*100)+(12.34*self.peso)
            else: fator_atividade = 511.83-(7.01*self.idade)+(9.07*self.altura*100)+(12.56*self.peso)
        return fator_atividade
    def _definir_distribuicao_calorica(self):
        get = self.calcular_gasto_energetico_total()
        if self.quantidade_refeicoes == 3: return {"cafe_da_manha": get * 0.30, "almoco": get * 0.40, "jantar": get * 0.30}
        elif self.quantidade_refeicoes == 4: return {"cafe_da_manha": get * 0.20, "almoco": get * 0.35, "lanche_da_tarde": get * 0.15, "jantar": get * 0.30}
        elif self.quantidade_refeicoes == 5: return {"cafe_da_manha": get * 0.20, "lanche_da_manha": get * 0.10, "almoco": get * 0.30, "lanche_da_tarde": get * 0.15, "jantar": get * 0.25}
        else: return {"cafe_da_manha": get * 0.20, "lanche_da_manha": get * 0.10, "almoco": get * 0.30, "lanche_da_tarde": get * 0.10, "jantar": get * 0.25, "ceia": get * 0.05}

    def gerar_query_refeicao(self, nome_refeicao: str, calorias_refeicao: float, limite: int = 30, filtro_saude: str = ""):
        grupos_por_refeicao = {
            "cafe_da_manha": ["Cereais e derivados", "Frutas e derivados", "Leite e derivados", "Ovos e derivados", "Nozes e sementes"],
            "lanche_da_manha": ["Frutas e derivados", "Nozes e sementes", "Leite e derivados"],
            "almoco": ["Cereais e derivados", "Leguminosas e derivados", "Carnes e derivados", "Pescados e frutos do mar", "Verduras, hortaliças e derivados", "Alimentos preparados"],
            "lanche_da_tarde": ["Frutas e derivados", "Cereais e derivados", "Leite e derivados", "Nozes e sementes"],
            "jantar": ["Cereais e derivados", "Leguminosas e derivados", "Carnes e derivados", "Pescados e frutos do mar", "Verduras, hortaliças e derivados", "Alimentos preparados", "Ovos e derivados"],
            "ceia": ["Frutas e derivados", "Leite e derivados"]
        }
        grupos_selecionados = grupos_por_refeicao.get(nome_refeicao, [])
        filtro_grupos_values = "VALUES ?grupoLabel { " + " ".join(f'"{g}"' for g in grupos_selecionados) + " }"
        
        # A query agora não tem NENHUM filtro ou ordenação por calorias.
        query = f"""
            PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
            PREFIX taco: <http://mo656/taco/>
            PREFIX tbca: <http://mo656/tbca/>

            SELECT ?label ?energiaKcal ?fonte ?grupoLabel
            WHERE {{
                {filtro_grupos_values}
                {{
                    ?alimento a taco:Alimento ; 
                        rdfs:label ?label ; 
                        taco:energiaKcal ?energiaKcal ; 
                        taco:pertenceAoGrupo ?grupoURI.
                    ?grupoURI rdfs:label ?grupoLabel.
                    BIND("taco" AS ?fonte)
                }}
                UNION
                {{
                    ?alimento a tbca:Alimento ; rdfs:label ?label ; tbca:energiaKcal ?energiaKcal ; tbca:pertenceAoGrupo ?grupoURI.
                    ?grupoURI rdfs:label ?grupoLabel.
                    BIND("tbca" AS ?fonte)
                }}
                {filtro_saude}
            }}
            ORDER BY ASC(?fonte) RAND()
            LIMIT {limite}
        """
        print(query)
        return query


    def definir_refeicoes(self):
        refeicoes = self._definir_distribuicao_calorica()
        filtro_saude = ""
        if self.classificar_imc() in ["Sobrepeso", "Obesidade"] and self.objetivo == "emagrecimento":
            filtro_saude = """
                FILTER NOT EXISTS {{ ?alimento tbca:acucarDeAdicaoG ?a . FILTER(?a > 0) }}
                FILTER NOT EXISTS {{ ?alimento tbca:acidosGraxosSaturadosG ?s . FILTER(?s > 5) }}
                FILTER NOT EXISTS {{ ?alimento tbca:acidosGraxosTransG ?t . FILTER(?t > 0) }}
            """
        queries = {}
        for refeicao, cal in refeicoes.items():
            # A chamada agora passa 'cal', as calorias totais da refeição
            queries[refeicao] = self.gerar_query_refeicao(refeicao, cal, limite=30, filtro_saude=filtro_saude)
        return queries
    
    def gerar_pergunta(self):
        # ... (este método já está correto, sem alterações)
        refeicoes_map = {"cafe_da_manha": "Café da Manhã", "lanche_da_manha": "Lanche da Manhã", "almoco": "Almoço", "lanche_da_tarde": "Lanche da Tarde", "jantar": "Jantar", "ceia": "Ceia"}
        refeicoes_dict = self._definir_distribuicao_calorica()
        refeicoes_str = ", ".join([f"{refeicoes_map[nome]} com aproximadamente {int(cal)} kcal" for nome, cal in refeicoes_dict.items()])
        return f"""Gere um plano alimentar para uma pessoa com as seguintes informações: {self.peso} kg, {self.idade} anos, {self.altura} m, sexo {self.sexo}, nível de atividade física {self.nivel_atividade_fisica} e objetivo de {self.objetivo}. A dieta deve ter {self.quantidade_refeicoes} refeições: {refeicoes_str}."""