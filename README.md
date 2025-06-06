# Simulador de Experimentos Educativos

Bem-vindo ao Simulador de Experimentos Educativos! Este projeto visa fornecer uma plataforma interativa para simular experimentos de Química, Física e Biologia, auxiliando no processo de ensino-aprendizagem.

## Visão Geral

O simulador permite aos usuários selecionar um experimento pré-definido, configurar seus parâmetros e observar os resultados da simulação tanto numericamente quanto (em alguns casos) visualmente.

## Tecnologias Utilizadas

*   **Backend:** Python com [FastAPI](https://fastapi.tiangolo.com/)
*   **Frontend:** JavaScript com [Svelte](https://svelte.dev/) (usando SvelteKit)
*   **Linguagem de Simulação:** Python (no backend)
*   **Testes de Backend:** Pytest

## Simulações Disponíveis

Atualmente, as seguintes simulações estão implementadas:

1.  **Química: Reação Ácido-Base**
    *   Configure as concentrações e volumes de um ácido e uma base (fortes e monopróticos/monohidroxílicos) e veja o pH resultante.
    *   Observe a mudança de cor com indicadores como Fenolftaleína ou Azul de Bromotimol.
    *   Acesse em: `http://localhost:5173/experiments/chemistry/acid-base` (após iniciar os servidores)

2.  **Física: Lançamento Oblíquo**
    *   Defina a velocidade inicial, ângulo de lançamento, altura inicial (opcional) e gravidade (opcional) de um projétil.
    *   Visualize a trajetória, alcance máximo, altura máxima e tempo total de voo.
    *   Acesse em: `http://localhost:5173/experiments/physics/projectile-launch`

3.  **Biologia: Genética Mendeliana (Cruzamento Monoíbrido)**
    *   Realize um cruzamento genético simples informando os genótipos dos pais para um gene com dois alelos.
    *   Observe o Quadro de Punnett resultante e as proporções genotípicas e fenotípicas da prole.
    *   Acesse em: `http://localhost:5173/experiments/biology/mendelian-genetics`

## Como Executar o Projeto Localmente

Você precisará ter Python (3.7+) e Node.js (com npm, pnpm ou yarn) instalados.

**1. Backend (FastAPI):**

   a. Abra um terminal na raiz do projeto.

   b. (Recomendado) Crie e ative um ambiente virtual Python na pasta `backend/`:
      ```bash
      python3 -m venv backend/venv
      source backend/venv/bin/activate  # Linux/macOS
      # backend\venv\Scripts\activate    # Windows
      ```

   c. Instale as dependências Python (FastAPI, Uvicorn):
      ```bash
      # Se um requirements.txt existisse em backend/, você usaria:
      # pip install -r backend/requirements.txt
      # Por enquanto, instale manualmente se não estiverem globais:
      pip install fastapi uvicorn pydantic
      ```
      *Nota: Durante o desenvolvimento com o agente AI, as dependências foram instaladas globalmente como workaround para limitações do ambiente do agente. Em um setup local padrão, o uso de ambiente virtual e `requirements.txt` é preferível.*

   d. Inicie o servidor FastAPI:
      ```bash
      python -m uvicorn backend.main:app --reload --port 8000
      ```
      O backend estará rodando em `http://localhost:8000`.

**2. Frontend (SvelteKit):**

   a. Abra um segundo terminal.

   b. Navegue até a pasta `frontend/`:
      ```bash
      cd frontend
      ```

   c. Instale as dependências do Node.js:
      ```bash
      npm install
      # ou pnpm install / yarn install
      ```
      *Nota: Esta etapa pode falhar no ambiente do agente AI devido a restrições. Em um setup local, ela é necessária.*

   d. Inicie o servidor de desenvolvimento SvelteKit:
      ```bash
      npm run dev
      ```
      O frontend estará geralmente acessível em `http://localhost:5173`.

**3. Acessando o Simulador:**

   Após iniciar ambos os servidores, abra seu navegador e acesse `http://localhost:5173`. Você deverá ver a tela de seleção de experimentos.

## Testes

*   **Backend:** Os testes de unidade para o backend são escritos com Pytest. Para executá-los (com o ambiente virtual ativado e `pytest` instalado via `pip install pytest`):
    ```bash
    python -m pytest backend/tests/test_main.py
    ```

*   **Frontend:** Arquivos de placeholder para testes de frontend (`*.test.js`) foram criados dentro das pastas de cada componente/rota. Eles contêm exemplos de como os testes poderiam ser escritos usando Vitest e Svelte Testing Library. A execução real desses testes requer a configuração de um ambiente de teste JavaScript.

## Próximos Passos (Sugestões)

*   Implementar a persistência de simulações salvas (Requisito Funcional 1.4).
*   Expandir com mais experimentos em cada área.
*   Melhorar as visualizações gráficas.
*   Adicionar autenticação de usuário, se necessário.
*   Configurar um ambiente de teste completo para o frontend.


```

Elementos de Design 

     

    Paleta de Cores: Azul claro (#ADD8E6) para elementos interativos, verde claro (#90EE90) para feedback positivo e laranja (#FFA500) para alertas. 
     

    Tipografia: Fonte sans-serif 'Roboto' para leitura fácil e confortável. 
     

Experiência do Usuário (UX) 

     

    Simplicidade: Minimizar o número de cliques para iniciar uma simulação. 
     

    Feedback Visual: Mostrar mudanças imediatas quando os parâmetros são ajustados. 
     

    Foco: Limitar distrações, com um design limpo e organizado. 
     

3. Plano de Testes 

Plano de Testes 

Versão 1.0 

Estratégia de Testes 

Serão realizados testes de unidade, integração, sistema e aceitação. Utilizaremos frameworks como JUnit para testes de unidade e Selenium para testes de interface do usuário. 

Casos de Teste 

     

    Teste de Unidade: Testar funções matemáticas e algoritmos de simulação. 
     

    Teste de Integração: Verificar a comunicação entre os módulos de simulação e interface. 
     

    Teste de Sistema: Executar simulações completas para validar funcionalidades e desempenho. 
     

    Teste de Aceitação: Realizar sessões com professores para assegurar que o software atende às suas necessidades. 
     

Testes de Usabilidade 

     Serão conduzidas sessões de teste com professores e alunos para coletar feedback sobre a interface.
     

4. Plano de Implementação 

Plano de Implementação 

Versão 1.0 

Cronograma 

     Sprint 1 (1 mês): Design da arquitetura, desenvolvimento da tela de seleção de experimentos.
     Sprint 2 (1 mês): Implementação do módulo de simulação de química.
     Sprint 3 (1 mês): Desenvolvimento dos módulos de física e biologia.
     Sprint 4 (2 semanas): Testes de integração e correção de bugs.
     Sprint 5 (1 semana): Preparação para o lançamento.
     

Tecnologias e Ferramentas 


     Controle de Versão: Git com GitHub.
     


         
     

Autenticação 

     Utiliza token de autenticação JWT.
     

6. Manual do Usuário 

Manual do Usuário 

Versão 1.0 

Introdução 

Bem-vindo ao "Simulador de Experimentos Educativos". Este manual ajudará você a utilizar todas as funcionalidades do software. 

Configuração Inicial 

     Baixe e instale o software a partir do site oficial.
     Abra o aplicativo e faça login com suas credenciais.
     

Guias de Uso 

     Iniciar Simulação: Selecione um experimento, configure os parâmetros e clique em "Iniciar".
     Salvar Simulação: Após a execução, clique em "Salvar" para armazenar os resultados.
     Exportar Dados: Na tela de resultados, selecione "Exportar" e escolha o formato desejado.
     

Resolução de Problemas 

     Simulação não inicia: Verifique a conexão com a internet e tente novamente.
     Erro ao exportar dados: Assegure-se de que o software tem permissão para escrever no diretório escolhido.
     

7. Plano de Gerenciamento de Configuração 

Plano de Gerenciamento de Configuração 

Versão 1.0 

Controle de Versão 

     Sistema: Git
     Convenções: Branch principal 'main', branches de funcionalidades nomeadas como 'feature/nome-da-funcionalidade'.
     

Integração Contínua 

     Ferramenta: GitHub Actions
     Processo: Executa testes de unidade e integração em cada push para 'main'.
     

Gestão de Mudanças 

     Processo: Cada mudança deve ser documentada em um 'pull request' com revisão por pares.
     

8. Relatório de Avaliação de Riscos 

Relatório de Avaliação de Riscos 

Versão 1.0 

Identificação de Riscos 

     Atraso no Desenvolvimento: Dependência de bibliotecas de terceiros.
     Problemas de Usabilidade: Interface complexa para usuários com TDAH.
     

Análise de Impacto e Probabilidade 

     Atraso no Desenvolvimento: Impacto alto, probabilidade média.
     Problemas de Usabilidade: Impacto médio, probabilidade alta.
     

Planos de Mitigação e Contingência 

     

    Atraso no Desenvolvimento: Avaliar e testar bibliotecas antes da integração, ter um plano de desenvolvimento alternativo. 
     

    Problemas de Usabilidade: Realizar testes de usabilidade com usuários-alvo e iterar o design conforme necessário. 
    
