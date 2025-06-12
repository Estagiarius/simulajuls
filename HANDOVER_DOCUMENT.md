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

## 3. Testes

*   **Testes Unitários dos Módulos:**
    *   É crucial executar os testes unitários para cada módulo de simulação para garantir sua corretude individual.
    *   Execute os testes usando `pytest` a partir da pasta `backend/`:
        ```bash
        # Exemplo para o módulo ácido-base
        pytest simulations/chemistry/test_acid_base_module.py

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
            *   Teste para cada `experiment_name` (`acid-base`, `projectile-launch`, `mendelian-genetics`).
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

Este documento deve servir como um bom ponto de partida para a continuação do desenvolvimento do Simulador de Experimentos Educativos.
```
