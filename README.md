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
    *   **Unidades de Entrada:**
        *   Velocidade Inicial: Pode ser fornecida em "m/s" (padrão), "km/h", "ft/s", ou "mph".
        *   Altura Inicial: Pode ser fornecida em "m" (padrão) ou "ft".
        *   Gravidade: Assume-se que está em m/s² para cálculos internos.
    *   **Unidades de Saída:** Os resultados da simulação (velocidade inicial x/y, tempo total, alcance máximo, altura máxima) podem ser exibidos nas seguintes unidades, conforme selecionado pelo usuário (padrão para m/s, s, m, m):
        *   Velocidade: "m/s", "km/h", "ft/s", "mph"
        *   Tempo: "s", "min"
        *   Distância (alcance/altura): "m", "km", "ft", "mi"
    *   **Geração de Trajetória:** A geração de pontos da trajetória é adaptativa para garantir uma visualização suave para lançamentos curtos e para evitar um número excessivo de pontos para lançamentos longos.
    *   Visualize a trajetória, alcance máximo, altura máxima e tempo total de voo, com unidades selecionadas.
    *   Acesse em: `http://localhost:5173/experiments/physics/projectile-launch`

3.  **Biologia: Genética Mendeliana (Cruzamento Monoíbrido)**
    *   Realize um cruzamento genético simples informando os genótipos dos pais para um gene com dois alelos.
    *   Observe o Quadro de Punnett resultante e as proporções genotípicas e fenotípicas da prole.
    *   Acesse em: `http://localhost:5173/experiments/biology/mendelian-genetics`

4.  **Química: Curva de Titulação Ácido-Base**
    *   Simula uma curva de titulação ácido-base, permitindo configurar um analito (ácido/base, forte/fraco com Ka/Kb) e um titulante (ácido/base forte).
    *   Permite definir concentrações, volumes, e o intervalo de adição do titulante.
    *   Visualiza a variação do pH em função do volume de titulante adicionado através de um gráfico SVG.
    *   Mostra os parâmetros utilizados na simulação e mensagens do backend.
    *   Acesse em: `http://localhost:5173/experiments/chemistry/acid-base-titration`

## Automated Execution (Recommended)

The `run_simulation.sh` script automates the setup and launch of both the backend and frontend components of the simulator. This is the recommended way to start the application.

To run the script, navigate to the project root directory in your terminal and execute:
```bash
./run_simulation.sh
```

**Note:** This script is primarily intended for Linux/macOS environments. Windows users may need to adapt the commands within the script or follow the manual steps outlined in the "Como Executar o Projeto Localmente" section. The script will:
1.  Set up and start the Python backend server.
2.  Set up and start the SvelteKit frontend development server.

Once the script is running, you should be able to access the simulator in your browser, typically at `http://localhost:5173`. The backend will be running on `http://localhost:8000`.

To stop the servers:
- Press `Ctrl+C` in the terminal where the script is running. This will stop the frontend development server.
- The backend server, which was started in the background, might continue running. You may need to stop it manually by finding its process ID (e.g., using `ps aux | grep uvicorn`) and then using `kill <PID>`, or more directly with `pkill -f uvicorn` (this will kill all processes matching 'uvicorn').

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
