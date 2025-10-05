Para executar a solução completa, siga os passos abaixo na ordem correta. Certifique-se de que os arquivos de dados (taco_tratada.xlsx e output.json) estão nos caminhos especificados dentro dos scripts.
Gerar os Grafos Individuais
- Execute o script kg_taco.py para processar a planilha Excel e gerar o grafo RDF da TACO (taco.ttl).
- Execute o script kg_tbca.py para processar o arquivo JSON e gerar o grafo RDF da TBCA (tbca.ttl), já conformado ao esquema de nutrientes desejado.
Unificar os Grafos
- Execute o script grafo_unificado.py para carregar os dois grafos (taco.ttl e tbca.ttl) em um único grafo. Este script também adiciona os links de equivalência (skos:exactMatch) entre os grupos alimentares dos dois conjuntos de dados, criando o arquivo final grafo_unificado.ttl.
Configurar e Executar a Aplicação Principal
Definir a Persona: No arquivo llm.py, edite ou crie uma instância da classe Persona com o perfil desejado (peso, altura, objetivo, etc.).
- Executar a Consulta com LLM: Execute o arquivo llm.py. O fluxo será o seguinte:
O script irá carregar o grafo_unificado.ttl.
A instância da Persona calculará as necessidades calóricas e gerará as queries SPARQL para cada refeição.
A função responder executará essas queries sobre o grafo.
Os resultados serão formatados e enviados em um prompt para a LLM (via API da Groq).
A resposta final da LLM, contendo o plano alimentar, será impressa no terminal.
