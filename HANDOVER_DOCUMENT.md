# Documento de Revisão e Próximos Passos - Simulador de Experimentos Educativos API

## 1. Visão Geral da Arquitetura Atual

O backend do Simulador de Experimentos Educativos é construído usando FastAPI (Python) e segue uma arquitetura modular para as simulações.

*   **API Principal (`backend/main.py`):**
    *   Define os endpoints da API FastAPI.
    *   Gerencia a descoberta dinâmica de módulos de simulação.
    *   Fornece um endpoint genérico (`/api/simulation/{experiment_name}/start`) para executar qualquer simulação descoberta.
    *   Inclui endpoints para listar experimentos (`/api/experiments`), salvar (`/api/simulations/save`) e carregar (`/api/simulations/{simulation_id}`) dados de simulação.
    *   Simulações salvas são armazenadas como arquivos JSON no diretório `backend/saved_simulations/`.

*   **Módulos de Simulação (`backend/simulations/`):**
    *   Cada simulação é encapsulada em seu próprio módulo (ex: `acid_base_module.py`).
    *   Os módulos herdam de `SimulationModule` (definido em `backend/simulations/base_simulation.py`), que impõe uma interface comum para metadados (nome, descrição, categoria) e execução.
    *   Parâmetros e modelos de resultado para cada simulação são definidos usando Pydantic em arquivos `models_*.py` correspondentes (ex: `models_acid_base.py`).
    *   Atualmente, existem três módulos de simulação refatorados:
        *   Química: Reação Ácido-Base
        *   Física: Lançamento Oblíquo
        *   Biologia: Genética Mendeliana

*   **Testes Unitários:**
    *   Cada módulo de simulação possui um arquivo de teste unitário correspondente (ex: `test_acid_base_module.py`) na mesma pasta, utilizando `pytest`.

## 2. Configuração do Ambiente e Execução

Para executar e testar a aplicação:

1.  **Ambiente Python:**
    *   Certifique-se de ter Python 3.8+ instalado.
    *   Recomenda-se criar um ambiente virtual:
        ```bash
        cd backend
        python -m venv venv
        source venv/bin/activate  # ou venv\Scripts\activate no Windows
        ```
2.  **Instalar Dependências:**
    *   Com o ambiente virtual ativado, instale as dependências necessárias:
        ```bash
        pip install fastapi uvicorn pydantic pytest
        ```
3.  **Iniciar o Servidor Backend:**
    *   Navegue até a pasta `backend/` (se ainda não estiver lá).
    *   Execute o servidor FastAPI com Uvicorn:
        ```bash
        uvicorn main:app --reload --port 8000
        ```
    *   A API estará acessível em `http://localhost:8000`. Você pode ver a documentação interativa da API (Swagger UI) em `http://localhost:8000/docs`.

## 3. Detalhes dos Módulos de Simulação Implementados

Esta seção detalha aspectos específicos de módulos que receberam atualizações recentes significativas.

### 3.1 Química: Reação Ácido-Base (`acid_base_module.py`)
*   **Frontend:** `frontend/src/routes/experiments/chemistry/acid-base/+page.svelte`
*   **Descrição:** Simula a reação entre um ácido e uma base (fortes e monopróticos/monohidroxílicos) e calcula o pH resultante. Permite a seleção de indicadores visuais.

### 3.2 Física: Lançamento Oblíquo (`projectile_module.py`)

O módulo de lançamento oblíquo foi aprimorado com as seguintes funcionalidades:

#### Novas Funcionalidades

*   **Conversão de Unidades:**
    *   **Descrição:** Permite que os usuários forneçam dados de entrada (velocidade inicial, altura inicial) em diferentes unidades e selecionem as unidades para os resultados da simulação.
    *   **Impacto no Backend:**
        *   `models_projectile.py`: Atualizado com novos campos para unidades de entrada (`initial_velocity_unit`, `initial_height_unit`) e um modelo `OutputUnitSelection` para especificar unidades de saída. Validadores foram adicionados para garantir que apenas unidades permitidas sejam usadas.
        *   `unit_conversion.py`: Um novo arquivo foi criado contendo funções para converter valores entre unidades (e.g., m/s para km/h, ft para m) e a unidade base SI (m/s, m, s).
        *   `projectile_module.py`: A lógica principal em `run_simulation` foi modificada para:
            1.  Converter todos os parâmetros de entrada para unidades SI (metros, segundos, m/s) usando as funções de `unit_conversion.py`.
            2.  Realizar todos os cálculos de física interna exclusivamente com unidades SI.
            3.  Converter os resultados finais (alcance, altura máxima, tempo de voo, componentes da velocidade, pontos da trajetória) para as unidades de saída selecionadas pelo usuário antes de retornar a resposta.
    *   **Requisitos para Frontend:**
        *   A UI (`frontend/src/routes/experiments/physics/projectile-launch/+page.svelte`) permite que os usuários selecionem a unidade para os campos de entrada relevantes (velocidade inicial, altura inicial).
        *   A UI permite que os usuários selecionem as unidades desejadas para os principais resultados numéricos.
        *   As chamadas de API para `/api/simulation/projectile-launch/start` incluem os novos campos de unidade no payload.
        *   Os resultados exibidos na UI indicam claramente as unidades correspondentes.

*   **Geração Adaptativa de Pontos de Trajetória:**
    *   **Descrição:** O método de geração de pontos para a trajetória do projétil agora usa um passo de tempo (`time_step`) adaptativo.
    *   **Impacto no Backend (`projectile_module.py`):**
        *   Se o tempo total de voo for muito curto, o `time_step` é reduzido para garantir um número mínimo de pontos (atualmente 20 intervalos, resultando em 21 pontos) para uma plotagem suave.
        *   Se o tempo total de voo for muito longo (resultando em mais de 2000 pontos com o `time_step` padrão de 0.05s), o `time_step` é aumentado para limitar o número total de pontos (atualmente 2000 intervalos, resultando em 2001 pontos), otimizando a performance.
        *   Para durações de voo intermediárias, o `time_step` padrão de 0.05s é mantido.
    *   **Impacto no Frontend:**
        *   A plotagem da trajetória no frontend (`frontend/src/routes/experiments/physics/projectile-launch/+page.svelte`) beneficia-se dessa mudança, mostrando curvas mais suaves para lançamentos de baixa energia e evitando sobrecarga de dados para lançamentos de alta energia.

#### Testes Específicos do Módulo

*   Os testes unitários em `backend/simulations/physics/test_projectile_module.py` foram significativamente expandidos para cobrir:
    *   Casos de teste com diferentes unidades de entrada (e.g., velocidade em km/h, altura em ft) e verificação dos resultados em SI.
    *   Casos de teste para conversão de unidades de saída (e.g., solicitar resultados em km, ft, min).
    *   Testes específicos para a lógica de geração adaptativa da trajetória, verificando o número de pontos gerados para cenários de baixa energia, alta energia (limitado) e casos padrão.
    *   Os testes existentes foram atualizados para incluir os novos parâmetros de unidade.

### 3.3 Biologia: Genética Mendeliana (`mendelian_genetics_module.py`)
*   **Frontend:** `frontend/src/routes/experiments/biology/mendelian-genetics/+page.svelte`
*   **Descrição:** Permite aos usuários realizar cruzamentos genéticos simples (monoíbridos) e visualizar os resultados em um quadro de Punnett, juntamente com as proporções genotípicas e fenotípicas.

### 3.4 Química: Curva de Titulação Ácido-Base (`acid_base_titration_module.py`)
*   **Frontend:** `frontend/src/routes/experiments/chemistry/acid-base-titration/+page.svelte`
*   **Descrição:** Simula uma titulação ácido-base. Os usuários podem definir as propriedades do analito (ácido ou base, incluindo concentração, volume e, opcionalmente, Ka/Kb para ácidos/bases fracas) e do titulante (ácido ou base forte, com nome e concentração). Também se configura o processo de titulação (volume inicial, volume final e incremento de volume).
*   **Funcionalidades Frontend:**
    *   Interface de usuário para entrada de todos os parâmetros necessários.
    *   Comunicação com o endpoint `/api/simulation/acid-base-titration/start`.
    *   Visualização da curva de titulação (pH vs. volume de titulante) usando um gráfico SVG customizado.
    *   Exibição clara da mensagem de status da simulação e um resumo dos parâmetros utilizados.
    *   Inclui validações básicas no lado do cliente para melhorar a experiência do usuário (por exemplo, verificar se o volume final é maior que o inicial).

## 4. Testes

*   **Testes Unitários dos Módulos:**
    *   É crucial executar os testes unitários para cada módulo de simulação para garantir sua corretude individual.
    *   Execute os testes usando `pytest` a partir da pasta `backend/`:
        ```bash
        # Exemplo para o módulo ácido-base
        pytest simulations/chemistry/test_acid_base_module.py
        pytest simulations/chemistry/test_acid_base_titration_module.py

        # Exemplo para o módulo de lançamento oblíquo
        pytest simulations/physics/test_projectile_module.py

        # Exemplo para o módulo de genética mendeliana
        pytest simulations/biology/test_mendelian_genetics_module.py

        # Ou para rodar todos os testes no diretório de simulações
        pytest simulations/
        ```
    *   **Nota:** Durante o desenvolvimento assistido por IA, houve instabilidade na ferramenta de execução de testes, impedindo a confirmação automatizada da passagem desses testes. É **altamente recomendável** executá-los manualmente para verificar a integridade dos módulos.

*   **Testes de Integração da API (Manuais):**
    *   Use uma ferramenta como `curl` ou Postman para testar os endpoints da API:
        *   **`GET /api/experiments`**: Verifica se a lista de experimentos é retornada corretamente.
        *   **`POST /api/simulation/{experiment_name}/start`**:
            *   Teste para cada `experiment_name` (`acid-base`, `projectile-launch`, `mendelian-genetics`, `acid-base-titration`).
            *   Envie um JSON válido no corpo da requisição com os parâmetros esperados pelo respectivo módulo. Verifique se os resultados são calculados corretamente.
            *   Exemplo de payload para `acid-base`:
                ```json
                {
                    "acid_concentration": 0.1,
                    "acid_volume": 50,
                    "base_concentration": 0.1,
                    "base_volume": 50,
                    "indicator_name": "Fenolftaleína"
                }
                ```
            *   Exemplo de payload para `acid-base-titration`:
                ```json
                {
                    "analyte_is_acid": true,
                    "acid_name": "HCl",
                    "acid_concentration": 0.1,
                    "acid_volume": 50,
                    "acid_ka": null,
                    "base_name": null,
                    "base_concentration": null,
                    "base_volume": null,
                    "base_kb": null,
                    "titrant_is_acid": false,
                    "titrant_name": "NaOH",
                    "titrant_concentration": 0.1,
                    "initial_titrant_volume_ml": 0.0,
                    "final_titrant_volume_ml": 100.0,
                    "volume_increment_ml": 1.0
                }
                ```
        *   **`POST /api/simulations/save`**:
            *   Envie um payload no formato:
                ```json
                {
                    "experiment_type": "acid-base",
                    "params": {"acid_concentration": 0.1, "acid_volume": 50, ...},
                    "results": {"final_ph": 7.0, ...}
                }
                ```
            *   Verifique se um ID de simulação é retornado e um arquivo JSON é criado em `backend/saved_simulations/`.
        *   **`GET /api/simulations/{simulation_id}`**:
            *   Use um ID de uma simulação salva para verificar se os dados são retornados corretamente.

## 4. Pontos de Atenção e Próximas Implementações

*   **Criptografia de Simulações Salvas (RNF2.4):**
    *   Os dados em `backend/saved_simulations/` são atualmente armazenados em JSON puro.
    *   Implementar criptografia (ex: usando a biblioteca `cryptography`) para proteger esses dados. Isso envolverá a modificação dos endpoints de salvar e carregar para criptografar/descriptografar os dados. Gerenciamento seguro de chaves será essencial.

*   **Desenvolvimento do Frontend:**
    *   A API backend está pronta para ser consumida. Interfaces de usuário (frontend Svelte) foram desenvolvidas para interagir com esta API.
    *   **Experimentos com Frontend Implementado:**
        *   **Reação Ácido-Base Simples:** `frontend/src/routes/experiments/chemistry/acid-base/+page.svelte`
        *   **Lançamento Oblíquo:** `frontend/src/routes/experiments/physics/projectile-launch/+page.svelte` (com funcionalidades avançadas de unidades e plotagem SVG da trajetória).
        *   **Genética Mendeliana:** `frontend/src/routes/experiments/biology/mendelian-genetics/+page.svelte`
        *   **Curva de Titulação Ácido-Base:**
            *   Localização: `frontend/src/routes/experiments/chemistry/acid-base-titration/+page.svelte`.
            *   Descrição: Permite aos usuários configurar um analito (ácido ou base, especificando concentração, volume, e opcionalmente Ka/Kb para espécies fracas) e um titulante (ácido ou base forte, com nome, concentração). Os usuários também definem o processo de titulação (volume inicial, volume final e incremento de volume do titulante).
            *   Funcionalidades: A interface envia esses parâmetros para o endpoint backend `/api/simulation/acid-base-titration/start`. Exibe a curva de titulação (pH vs. volume de titulante) resultante usando um gráfico SVG customizado. Também apresenta uma mensagem de status da simulação e um resumo dos parâmetros utilizados.
            *   Backend Consumido: Utiliza o módulo de simulação `acid_base_titration_module.py` existente no backend.
    *   O desenvolvimento de interfaces para outros módulos de simulação ou novas simulações pode seguir o padrão estabelecido.

*   **Novos Experimentos:**
    *   Adicionar mais simulações seguindo o padrão `SimulationModule` no backend:
        1.  Crie uma nova subpasta em `backend/simulations/<categoria>/`.
        2.  Defina `models_<experimento>.py` com os modelos Pydantic para parâmetros e resultados.
        3.  Implemente `<experimento>_module.py` herdando de `SimulationModule`.
        4.  Adicione testes unitários em `test_<experimento>_module.py`.
        *   O novo experimento será descoberto automaticamente pela API.

*   **Tratamento de Erros e Logging:**
    *   Expandir o tratamento de erros na API.
    *   Implementar logging estruturado para monitoramento e depuração.

*   **Persistência de Dados Avançada:**
    *   Para um cenário de produção ou com muitos usuários, substituir o armazenamento de simulações em arquivos JSON por um banco de dados (SQL ou NoSQL) pode ser necessário para melhor desempenho, concorrência e gerenciamento.

*   **Segurança da API:**
    *   Se a API for exposta publicamente ou usada em um ambiente multiusuário, implementar mecanismos de autenticação e autorização (ex: OAuth2 com tokens JWT) será crucial.

*   **Refinamento do `run_simulation.sh`:**
    *   O script `run_simulation.sh` atualmente foca em iniciar o ambiente de desenvolvimento. Pode ser estendido para:
        *   Executar todos os testes unitários.
        *   Executar simulações específicas via linha de comando, imprimindo os resultados (útil para depuração rápida).

*   **Documentação da API:**
    *   Embora o FastAPI forneça documentação automática via Swagger UI (`/docs`) e ReDoc (`/redoc`), manter um documento de API separado (como o `Documento de API` original do projeto) atualizado com detalhes e exemplos pode ser útil.

## 5. Revisão dos Arquivos Chave (Conceitual)

*   **`backend/main.py`:**
    *   A lógica de roteamento foi significativamente simplificada com o endpoint de simulação genérico.
    *   A descoberta de módulos na inicialização é eficiente.
    *   Os endpoints de salvar/carregar usam manipulação de arquivos JSON; a transição para um banco de dados ou adição de criptografia afetará principalmente esta parte.
    *   O tratamento de erros para validação de payload e operações de arquivo parece adequado para o estágio atual.

*   **`backend/simulations/base_simulation.py`:**
    *   A interface `SimulationModule` e os modelos base `BaseSimulationParams`, `BaseSimulationResult` fornecem uma boa espinha dorsal para a padronização e extensibilidade dos módulos de simulação.

*   **Módulos de Simulação (ex: `acid_base_module.py`, `models_acid_base.py`):**
    *   A separação da lógica do módulo e seus modelos Pydantic está clara.
    *   O uso de Pydantic para validação de parâmetros nos modelos é uma boa prática.
    *   A lógica de simulação está contida dentro do método `run_simulation`.

## 4. Detalhes dos Módulos de Simulação Implementados

Esta seção detalha aspectos específicos de módulos que receberam atualizações recentes significativas.

### 4.1 Física: Lançamento Oblíquo (`projectile_module.py`)

O módulo de lançamento oblíquo foi aprimorado com as seguintes funcionalidades:

#### Novas Funcionalidades

*   **Conversão de Unidades:**
    *   **Descrição:** Permite que os usuários forneçam dados de entrada (velocidade inicial, altura inicial) em diferentes unidades e selecionem as unidades para os resultados da simulação.
    *   **Impacto no Backend:**
        *   `models_projectile.py`: Atualizado com novos campos para unidades de entrada (`initial_velocity_unit`, `initial_height_unit`) e um modelo `OutputUnitSelection` para especificar unidades de saída. Validadores foram adicionados para garantir que apenas unidades permitidas sejam usadas.
        *   `unit_conversion.py`: Um novo arquivo foi criado contendo funções para converter valores entre unidades (e.g., m/s para km/h, ft para m) e a unidade base SI (m/s, m, s).
        *   `projectile_module.py`: A lógica principal em `run_simulation` foi modificada para:
            1.  Converter todos os parâmetros de entrada para unidades SI (metros, segundos, m/s) usando as funções de `unit_conversion.py`.
            2.  Realizar todos os cálculos de física interna exclusivamente com unidades SI.
            3.  Converter os resultados finais (alcance, altura máxima, tempo de voo, componentes da velocidade, pontos da trajetória) para as unidades de saída selecionadas pelo usuário antes de retornar a resposta.
    *   **Requisitos para Frontend:**
        *   A UI deve permitir que os usuários selecionem a unidade para os campos de entrada relevantes (velocidade inicial, altura inicial).
        *   A UI deve permitir que os usuários selecionem as unidades desejadas para os principais resultados numéricos.
        *   As chamadas de API para `/api/simulation/projectile-launch/start` devem incluir os novos campos de unidade no payload.
        *   Os resultados exibidos na UI devem indicar claramente as unidades correspondentes.

*   **Geração Adaptativa de Pontos de Trajetória:**
    *   **Descrição:** O método de geração de pontos para a trajetória do projétil agora usa um passo de tempo (`time_step`) adaptativo.
    *   **Impacto no Backend (`projectile_module.py`):**
        *   Se o tempo total de voo for muito curto, o `time_step` é reduzido para garantir um número mínimo de pontos (atualmente 20 intervalos, resultando em 21 pontos) para uma plotagem suave.
        *   Se o tempo total de voo for muito longo (resultando em mais de 2000 pontos com o `time_step` padrão de 0.05s), o `time_step` é aumentado para limitar o número total de pontos (atualmente 2000 intervalos, resultando em 2001 pontos), otimizando a performance.
        *   Para durações de voo intermediárias, o `time_step` padrão de 0.05s é mantido.
    *   **Impacto no Frontend:**
        *   A plotagem da trajetória deve se beneficiar dessa mudança, mostrando curvas mais suaves para lançamentos de baixa energia e evitando sobrecarga de dados para lançamentos de alta energia. Nenhuma alteração direta na lógica de plotagem do frontend é esperada, além de lidar com o número variável de pontos.

#### Testes Específicos do Módulo

*   Os testes unitários em `backend/simulations/physics/test_projectile_module.py` foram significativamente expandidos para cobrir:
    *   Casos de teste com diferentes unidades de entrada (e.g., velocidade em km/h, altura em ft) e verificação dos resultados em SI.
    *   Casos de teste para conversão de unidades de saída (e.g., solicitar resultados em km, ft, min).
    *   Testes específicos para a lógica de geração adaptativa da trajetória, verificando o número de pontos gerados para cenários de baixa energia, alta energia (limitado) e casos padrão.
    *   Os testes existentes foram atualizados para incluir os novos parâmetros de unidade.

## 5. Pontos de Atenção e Próximas Implementações (Renumerado)

*   **Criptografia de Simulações Salvas (RNF2.4):**
    *   Os dados em `backend/saved_simulations/` são atualmente armazenados em JSON puro.
    *   Implementar criptografia (ex: usando a biblioteca `cryptography`) para proteger esses dados. Isso envolverá a modificação dos endpoints de salvar e carregar para criptografar/descriptografar os dados. Gerenciamento seguro de chaves será essencial.

*   **Desenvolvimento do Frontend:**
    *   A API backend está pronta para ser consumida. O próximo grande passo é desenvolver a interface do usuário (frontend React/Svelte conforme planejado) que interaja com esta API.

*   **Novos Experimentos:**
    *   Adicionar mais simulações seguindo o padrão `SimulationModule`:
        1.  Crie uma nova subpasta em `backend/simulations/<categoria>/`.
        2.  Defina `models_<experimento>.py` com os modelos Pydantic para parâmetros e resultados.
        3.  Implemente `<experimento>_module.py` herdando de `SimulationModule`.
        4.  Adicione testes unitários em `test_<experimento>_module.py`.
        *   O novo experimento será descoberto automaticamente pela API.

*   **Tratamento de Erros e Logging:**
    *   Expandir o tratamento de erros na API.
    *   Implementar logging estruturado para monitoramento e depuração.

*   **Persistência de Dados Avançada:**
    *   Para um cenário de produção ou com muitos usuários, substituir o armazenamento de simulações em arquivos JSON por um banco de dados (SQL ou NoSQL) pode ser necessário para melhor desempenho, concorrência e gerenciamento.

*   **Segurança da API:**
    *   Se a API for exposta publicamente ou usada em um ambiente multiusuário, implementar mecanismos de autenticação e autorização (ex: OAuth2 com tokens JWT) será crucial.

*   **Refinamento do `run_simulation.sh`:**
    *   O script `run_simulation.sh` atualmente foca em iniciar o ambiente de desenvolvimento. Pode ser estendido para:
        *   Executar todos os testes unitários.
        *   Executar simulações específicas via linha de comando, imprimindo os resultados (útil para depuração rápida).

*   **Documentação da API:**
    *   Embora o FastAPI forneça documentação automática via Swagger UI (`/docs`) e ReDoc (`/redoc`), manter um documento de API separado (como o `Documento de API` original do projeto) atualizado com detalhes e exemplos pode ser útil.

## 6. Revisão dos Arquivos Chave (Conceitual) (Renumerado)

*   **`backend/main.py`:**
    *   A lógica de roteamento foi significativamente simplificada com o endpoint de simulação genérico.
    *   A descoberta de módulos na inicialização é eficiente.
    *   Os endpoints de salvar/carregar usam manipulação de arquivos JSON; a transição para um banco de dados ou adição de criptografia afetará principalmente esta parte.
    *   O tratamento de erros para validação de payload e operações de arquivo parece adequado para o estágio atual.

*   **`backend/simulations/base_simulation.py`:**
    *   A interface `SimulationModule` e os modelos base `BaseSimulationParams`, `BaseSimulationResult` fornecem uma boa espinha dorsal para a padronização e extensibilidade dos módulos de simulação.

*   **Módulos de Simulação (ex: `acid_base_module.py`, `models_acid_base.py`):**
    *   A separação da lógica do módulo e seus modelos Pydantic está clara.
    *   O uso de Pydantic para validação de parâmetros nos modelos é uma boa prática.
    *   A lógica de simulação está contida dentro do método `run_simulation`.

Este documento deve servir como um bom ponto de partida para a continuação do desenvolvimento do Simulador de Experimentos Educativos.
```
