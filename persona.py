class Persona:
    def __init__(self, peso, altura, sexo, idade, nivel_atividade_fisica, objetivo, quantidade_refeicoes):
        self.peso = peso # em kg
        self.altura = altura # em metros
        self.sexo = sexo # masculino ou feminino
        self.idade = idade # em anos
        self.nivel_atividade_fisica = nivel_atividade_fisica # inativo, pouco ativo, ativo, muito ativo
        self.objetivo = objetivo # emagrecimento, ganho de massa muscular, manutenção
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
            return "eutrófico"
        elif 25 <= imc < 29.9:
            return "Sobrepeso"
        else:
            return "Obesidade"

    
    # Cálculo da Taxa Metabólica Basal (TMB) usando a fórmula de harris-benedict
    def calcular_taxa_metabolica_basal(self):
        if self.sexo == "masculino":
            tmb = 66.47 + (13.75 * self.peso) + (5.003 * self.altura * 100) - (6.755 * self.idade)
        else: # feminino
            tmb = 655.1 + (9.563 * self.peso) + (1.850 * self.altura * 100) - (4.676 * self.idade)
        return tmb

    # Cálculo do Gasto Energético Total (GET) 
    #dris 2023 - https://academy.dietbox.me/wp-content/uploads/2024/08/DRIs-.pdf
    '''
    1. Inativa > reflete um nível de TEE que cobre o metabolismo basal, o efeito térmico dos alimentos e um nível mínimo de atividade física necessário para a vida independente.
    2. Pouco ativa > reflete um nível de atividade física além do mínimo, envolvendo mais locomoção e algumas atividades ocupacionais e recreativas.
    3. Ativa > envolve ainda mais locomoção, atividades ocupacionais ou recreativas.
    4. Muito ativa > engloba não apenas as demandas da vida diária, mas também a prática vigorosa de atividades ocupacionais ou recreativas.
    '''
    def calcular_gasto_energetico_total(self):
        if self.sexo == "masculino":
            if self.nivel_atividade_fisica == "inativo":
                fator_atividade = 753.07 - (10.83 * self.idade) + (6.50 * self.altura * 100) + (14.10 * self.peso)
            elif self.nivel_atividade_fisica == "pouco ativo":
                fator_atividade = 581.47 - (10.83 * self.idade) + (8.30 * self.altura * 100) + (14.94 * self.peso)
            elif self.nivel_atividade_fisica == "ativo":
                fator_atividade = 1004.82 - (10.83 * self.idade) + (6.52 * self.altura * 100) + (15.91 * self.peso)
            else: # muito ativo
                fator_atividade = 517.88 - (10.83 * self.idade) + (15.61 * self.altura * 100) + (19.11 * self.peso)

        else: # feminino
            if self.nivel_atividade_fisica == "inativo":
                fator_atividade = 584.90 - (7.01 * self.idade) + (5.72 * self.altura * 100) + (11.71 * self.peso)
            elif self.nivel_atividade_fisica == "pouco ativo":
                fator_atividade = 575.77 - (7.01 * self.idade) + (6.60 * self.altura * 100) + (12.14 * self.peso)
            elif self.nivel_atividade_fisica == "ativo":
                fator_atividade = 710.25 - (7.01 * self.idade) + (6.54 * self.altura * 100) + (12.34 * self.peso)
            else: # muito ativo
                fator_atividade = 511.83 - (7.01 * self.idade) + (9.07 * self.altura * 100) + (12.56 * self.peso)
        eer = fator_atividade
        return eer

    def gerar_query_por_caloria(self, calorias_max, limite=5):

        filtro_alimentos = ""
        if self.classificar_imc() in ["Sobrepeso", "Obesidade"] and self.objetivo == "emagrecimento":
            calorias_max = calorias_max * 0.75
            filtro_alimentos = """
                FILTER NOT EXISTS { ?alimento tbca:Acucar_de_adicao_g ?a . FILTER(?a > 0) }
                FILTER NOT EXISTS { ?alimento tbca:Acidos_graxos_saturados_g ?s . FILTER(?s > 0) }
                FILTER NOT EXISTS { ?alimento tbca:Acidos_graxos_trans_g ?t . FILTER(?t > 0) }
                """

        query = f"""
        PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
        PREFIX taco: <http://mo656/taco/>
        PREFIX tbca: <http://mo656/tbca/>

        SELECT ?label ?energia_100g ?energia_calculada ?grupo_alimentar
        WHERE {{
            ?alimento rdfs:label ?label .

            {{
                ?alimento taco:Energia_kcal ?energia_100g .
                # MUDANÇA: Grupo_alimentar agora é opcional
                OPTIONAL {{ ?alimento taco:Grupo_alimentar ?grupo_alimentar . }}
            }}
            UNION
            {{
                ?alimento tbca:Energia_kcal ?energia_100g .
                # MUDANÇA: Grupo_alimentar agora é opcional
                OPTIONAL {{ ?alimento tbca:Grupo_alimentar ?grupo_alimentar . }}
                {filtro_alimentos}
            }}

            BIND((?energia_100g / 100) * 100 AS ?energia_calculada)
            FILTER(?energia_calculada <= {calorias_max})
        }}
        ORDER BY ?energia_calculada
        LIMIT {limite}
        """

        return query
    
    def definir_refeicoes(self):
        """
        Retorna queries SPARQL para cada refeição, filtrando alimentos por calorias.
        """
        if self.quantidade_refeicoes == 3:
            # café da manhã, almoço, jantar
            refeicoes = {
                "cafe_da_manha":    self.calcular_gasto_energetico_total() * 0.4,
                "almoco":           self.calcular_gasto_energetico_total() * 0.4,
                "jantar":           self.calcular_gasto_energetico_total() * 0.2,
            }
        elif self.quantidade_refeicoes == 4:
            # café da manhã, almoço, lanche da tarde, jantar
            refeicoes = {
                "cafe_da_manha":    self.calcular_gasto_energetico_total() * 0.3,
                "almoco":           self.calcular_gasto_energetico_total() * 0.4,
                "lanche_da_tarde":  self.calcular_gasto_energetico_total() * 0.1,
                "jantar":           self.calcular_gasto_energetico_total() * 0.2,
            }
        elif self.quantidade_refeicoes == 5:
            # café da manhã, lanche da manhã, almoço, lanche da tarde, jantar
            refeicoes = {
                "cafe_da_manha":    self.calcular_gasto_energetico_total() * 0.3,
                "lanche_da_manha":  self.calcular_gasto_energetico_total() * 0.1,
                "almoco":           self.calcular_gasto_energetico_total() * 0.4,
                "lanche_da_tarde":  self.calcular_gasto_energetico_total() * 0.1,
                "jantar":           self.calcular_gasto_energetico_total() * 0.1,
            }
        else: # 6 refeições
            # café da manhã, lanche da manhã, almoço, lanche da tarde, jantar, ceia
            refeicoes = {
                "cafe_da_manha":    self.calcular_gasto_energetico_total() * 0.25,
                "lanche_da_manha":  self.calcular_gasto_energetico_total() * 0.05,
                "almoco":           self.calcular_gasto_energetico_total() * 0.3,
                "lanche_da_tarde":  self.calcular_gasto_energetico_total() * 0.1,
                "jantar":           self.calcular_gasto_energetico_total() * 0.25,
                "ceia":             self.calcular_gasto_energetico_total() * 0.05,
            }
        queries = {}
        for refeicao, cal in refeicoes.items():
            queries[refeicao] = self.gerar_query_por_caloria(cal, limite=5)
        return queries
    
    # get dados
    def gerar_pergunta(self):
        return f"""Gere um plano alimentar para uma pessoa com as seguintes informações: 
        {self.peso}, 
        {self.idade}, 
        {self.altura},
        {self.sexo},  
        {self.nivel_atividade_fisica}
        {self.objetivo}
        {self.quantidade_refeicoes}
        """
