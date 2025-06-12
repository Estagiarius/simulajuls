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
