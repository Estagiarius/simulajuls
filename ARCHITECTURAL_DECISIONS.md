# Decisões Arquiteturais e Impacto da Refatoração (Backend API)

Este documento detalha as razões por trás das significativas refatorações realizadas no backend da API do "Simulador de Experimentos Educativos" e compara a nova arquitetura com o estado anterior do código.

## Contexto da Refatoração

O código original em `backend/main.py` apresentava desafios potenciais para a manutenibilidade e escalabilidade do projeto a longo prazo:

1.  **Lógica de Simulação Centralizada:** Toda a lógica para cada simulação (ácido-base, lançamento oblíquo, genética) residia diretamente em `main.py`. Com a adição de novos experimentos, este arquivo se tornaria progressivamente maior e mais complexo.
2.  **Modelos Pydantic Misturados/Duplicados:** Definições de modelos de dados (parâmetros e resultados) para as simulações estavam concentradas em `main.py`. No caso do módulo ácido-base, havia duplicidade de modelos, gerando potencial para inconsistências.
3.  **Endpoints de API Específicos por Simulação:** A adição de novas simulações exigiria a criação manual de novos endpoints em `main.py`, aumentando o acoplamento entre a camada de API e as implementações de simulação.
4.  **Listagem Estática de Experimentos:** A relação de experimentos disponíveis era codificada (hardcoded), necessitando edição manual a cada novo experimento.

A refatoração teve como objetivo principal endereçar esses pontos, implementando uma arquitetura mais **modular, organizada e escalável**.

## Visão Geral das Alterações Implementadas

*   **Modularização das Simulações:**
    *   Cada simulação foi encapsulada em seu próprio "módulo" Python dentro da pasta `backend/simulations/`. Cada módulo contém sua lógica específica (em um arquivo `*_module.py`) e seus modelos de dados Pydantic (`models_*.py`).
    *   Foi introduzida uma classe base abstrata `SimulationModule` (`backend/simulations/base_simulation.py`) para definir uma interface padrão para todos os módulos de simulação.
*   **API Genérica e Dinâmica:**
    *   O arquivo `main.py` foi refatorado para descobrir dinamicamente os módulos de simulação no momento da inicialização.
    *   Um único endpoint genérico, `/api/simulation/{experiment_name}/start`, foi implementado para executar qualquer simulação, identificada pelo `experiment_name`.
    *   O endpoint `/api/experiments` agora lista os experimentos de forma dinâmica, consultando os metadados dos módulos descobertos.
*   **Funcionalidade Centralizada de Salvar/Carregar:** A capacidade de salvar e carregar o estado das simulações foi adicionada de forma centralizada em `main.py`, utilizando arquivos JSON para persistência.

## Análise Comparativa: Prós e Contras

### Lados Positivos das Alterações (Nova Arquitetura)

1.  **Melhor Organização e Manutenibilidade:**
    *   O código é mais fácil de navegar e compreender, com responsabilidades claramente delimitadas.
    *   Modificações ou correções em uma simulação específica são isoladas em seu respectivo módulo, minimizando o risco de efeitos colaterais em outras partes do sistema.
    *   O arquivo `main.py` tornou-se significativamente mais enxuto, focando no roteamento da API e em funcionalidades transversais.
2.  **Maior Escalabilidade e Extensibilidade:**
    *   Adicionar novos experimentos é simplificado: requer apenas a criação de um novo módulo seguindo o padrão `SimulationModule`. A API irá automaticamente descobrir e integrar o novo experimento sem necessidade de alterações em `main.py` para listagem ou execução.
3.  **Redução de Acoplamento:**
    *   A lógica central da API está menos dependente das implementações detalhadas de cada simulação.
4.  **Reusabilidade Potencial:**
    *   Módulos de simulação autocontidos podem, teoricamente, ser reutilizados em outros contextos ou projetos.
5.  **Testabilidade Aprimorada:**
    *   Módulos menores e com responsabilidade única são inerentemente mais fáceis de testar unitariamente de forma isolada, como demonstrado pela criação dos arquivos `test_*_module.py`.
6.  **Clareza na Definição de Dados:**
    *   Cada simulação possui seus modelos de parâmetros e resultados explicitamente definidos em seus arquivos `models_*.py`, melhorando a clareza e a robustez da validação de dados com Pydantic.

### Lados Negativos das Alterações (ou Pontos de Atenção)

1.  **Complexidade Inicial da Arquitetura:**
    *   A introdução de uma camada de abstração (com `SimulationModule`), a descoberta dinâmica de módulos e o endpoint genérico podem apresentar uma complexidade conceitual maior inicialmente, comparada a uma abordagem monolítica com toda a lógica em um único arquivo.
2.  **Curva de Aprendizado para Novos Contribuidores:**
    *   Desenvolvedores que se juntem ao projeto precisarão primeiro entender a arquitetura modular (o padrão `SimulationModule`, a estrutura de diretórios para simulações) antes de adicionar novos experimentos. No entanto, essa estruturação visa facilitar contribuições consistentes e de qualidade a longo prazo.
3.  **Overhead para Projetos Muito Pequenos (Argumentável):**
    *   Para um projeto que permanecesse estritamente com um número muito limitado de experimentos (e.g., 2 ou 3), a arquitetura modular poderia ser considerada um excesso de engenharia. Contudo, o escopo do "Simulador de Experimentos Educativos" (Química, Física, Biologia) sugere um potencial de crescimento que se beneficia diretamente da escalabilidade proporcionada.
4.  **Descoberta Dinâmica e Erros de Importação:**
    *   Se um módulo de simulação contiver erros que impeçam sua importação (e.g., erros de sintaxe), ele não será carregado e, consequentemente, não aparecerá na lista de experimentos. Embora a função `discover_simulation_modules` implementada inclua tratamento básico de exceções para logar esses erros no console, eles podem ser menos visíveis do que erros em um arquivo monolítico.

## Conclusão

A refatoração implementada representa uma decisão estratégica para estabelecer uma fundação de software mais robusta e preparada para o crescimento futuro do "Simulador de Experimentos Educativos". Os benefícios em termos de organização, manutenibilidade, testabilidade e, fundamentalmente, escalabilidade, são considerados preponderantes sobre a complexidade inicial introduzida. Esta abordagem visa prevenir que o projeto se torne difícil de gerenciar à medida que evolui, alinhando-se com boas práticas de engenharia de software. O `HANDOVER_DOCUMENT.md` também foi criado para auxiliar na transição e compreensão desta arquitetura.

---

## AD-001: Unit Handling in Physics Simulation (Projectile Module)

*   **Status:** Decidido e Implementado
*   **Context:**
    *   O módulo de simulação de lançamento de projéteis inicialmente utilizava unidades SI (metros, segundos, m/s) para todas as entradas e saídas.
    *   Havia a necessidade de melhorar a experiência do usuário, permitindo que fornecessem dados de entrada em unidades mais familiares (e.g., km/h, pés) e visualizassem os resultados também em unidades de sua escolha.
*   **Decision:**
    1.  **Backend Calculations in SI:** Todos os cálculos físicos dentro do `projectile_module.py` continuarão a ser realizados estritamente em unidades SI (metros para comprimento, segundos para tempo, m/s para velocidade). Isso garante a consistência e simplicidade da lógica de simulação principal.
    2.  **API Accepts and Returns Specified Units:** A API (via modelos Pydantic em `models_projectile.py`) será modificada para:
        *   Aceitar unidades opcionais para parâmetros de entrada (e.g., `initial_velocity_unit`, `initial_height_unit`). Se não fornecidas, assumem-se unidades SI padrão.
        *   Aceitar um objeto `output_units` que especifica as unidades desejadas para os resultados da simulação (velocidade, tempo, alcance, altura).
    3.  **Conversion at API Boundary:** A conversão de unidades de entrada para SI ocorrerá no início do método `run_simulation` em `projectile_module.py`. A conversão dos resultados de SI para as unidades de saída selecionadas ocorrerá no final deste método, antes de retornar os dados.
    4.  **Centralized Conversion Logic:** Funções de conversão de unidades serão implementadas em um novo arquivo dedicado, `backend/simulations/physics/unit_conversion.py`.
*   **Rationale:**
    *   **Clean Core Logic:** Mantém a lógica de simulação física principal livre de complexidades de conversão de unidades, operando sempre em um sistema consistente (SI).
    *   **User Flexibility:** Oferece uma experiência de usuário significativamente melhorada, permitindo o uso de unidades comuns.
    *   **Centralized Conversion:** Agrupa toda a lógica de conversão de unidades em um local, facilitando a manutenção e a adição de novas unidades no futuro.
    *   **Clear API Contract:** Os modelos Pydantic definem claramente quais unidades são suportadas.
*   **Alternatives Considered:**
    *   **Frontend Conversion Only:** O frontend seria responsável por todas as conversões de e para SI. Rejeitado porque o backend deve validar e entender as unidades de entrada para garantir a corretude da simulação (e.g., se um limite de parâmetro depende da unidade). Além disso, forçaria todos os clientes da API a reimplementar a lógica de conversão.
    *   **Backend Stores and Calculates in Multiple Units:** A lógica de simulação lidaria internamente com múltiplas unidades. Rejeitado por aumentar drasticamente a complexidade da física principal e o risco de erros.

## AD-002: Trajectory Point Generation Strategy (Projectile Module)

*   **Status:** Decidido e Implementado
*   **Context:**
    *   A estratégia original de geração de pontos para a trajetória do projétil usava um `time_step` fixo (0.05s).
    *   Isso poderia levar a um número muito pequeno de pontos para simulações de curta duração (resultando em gráficos "quadrados" ou pouco suaves) ou a um número excessivo de pontos para simulações de longa duração (impactando a performance de transferência de dados e renderização no frontend).
*   **Decision:**
    1.  Implementar uma estratégia de `time_step` adaptativo no `projectile_module.py`.
    2.  **Minimum Points:** Se o tempo total de voo (`total_t`) dividido pelo `time_step` padrão (0.05s) resultar em menos que um número mínimo desejado de intervalos (definido como `min_desired_points = 20`), o `time_step` será recalculado como `total_t / min_desired_points` para garantir aproximadamente 20 intervalos (21 pontos).
    3.  **Maximum Points:** Se o tempo total de voo (`total_t`) dividido pelo `time_step` (seja o padrão ou o ajustado pelo critério de pontos mínimos) resultar em mais que um limite máximo de intervalos (definido como `max_points_limit = 2000`), o `time_step` será recalculado como `total_t / max_points_limit` para garantir aproximadamente 2000 intervalos (2001 pontos).
    4.  **Default Step:** Se nenhum dos critérios acima for atendido, o `time_step` padrão de 0.05s é utilizado.
*   **Rationale:**
    *   **Visual Consistency:** Garante uma experiência de visualização mais consistente, com curvas suaves para voos curtos.
    *   **Frontend Performance:** Evita o envio e a tentativa de renderização de um número excessivo de pontos da trajetória para voos longos, o que poderia degradar a performance do frontend.
    *   **Backend Control:** Mantém a lógica de geração de dados no backend, que tem pleno conhecimento da simulação.
*   **Alternatives Considered:**
    *   **Frontend Sampling/Interpolation:** O backend sempre envia um número fixo (grande) de pontos, e o frontend decide quais exibir ou como interpolar. Rejeitado por potencialmente enviar dados desnecessários e colocar mais carga no frontend.
    *   **User-Defined Precision for Trajectory:** Permitir que o usuário escolha o número de pontos ou o `time_step`. Rejeitado por adicionar complexidade desnecessária à interface do usuário para este nível de funcionalidade; a adaptação automática foi preferida.
