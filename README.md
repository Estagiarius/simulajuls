# simulajuls
1. Especificação de Requisitos de Software (SRS) 

Especificação de Requisitos de Software 

Versão 1.0 

Introdução 

Este documento especifica os requisitos para o "Simulador de Experimentos Educativos", um software destinado a auxiliar professores e alunos nas áreas de química, física e biologia. 

1. Requisitos Funcionais 

1.1 O sistema deve permitir a seleção de experimentos pré-definidos em química, física e biologia. 

1.2 Deve ser possível configurar parâmetros específicos para cada simulação. 

1.3 O software deve apresentar os resultados da simulação em formatos gráficos e numéricos. 

1.4 Usuários devem poder salvar e carregar simulações anteriores. 

1.5 O sistema deve permitir a exportação de dados para formatos CSV e PDF. 

2. Requisitos Não Funcionais 

2.1 Usabilidade: O software deve ser fácil de navegar, com uma interface limpa e instruções claras. 

2.2 Desempenho: Simulações devem ser processadas em menos de 2 segundos para cenários de baixa complexidade. 

2.3 Confiabilidade: O sistema deve garantir uma taxa de falhas inferior a 1% durante simulações. 

2.4 Segurança: Dados de simulações salvas devem ser protegidos por criptografia. 

3. Restrições e Suposições 

3.1 Restrições: O software será compatível apenas com sistemas operacionais Windows e MacOS. 

3.2 Suposições: Assume-se que os usuários têm acesso a uma conexão de internet estável para utilizar recursos online. 

2. Documento de Design de Interface do Usuário (UI Design Document) 

Documento de Design de Interface do Usuário 

Versão 1.0 

Introdução 

Este documento descreve o design da interface do usuário para o "Simulador de Experimentos Educativos". 

Layout e Design 

O aplicativo terá três telas principais: 

     

    Tela de Seleção de Experimentos: Lista categorizada de experimentos com breves descrições e imagens ilustrativas. 
     

    Tela de Configuração e Simulação: Área central para a simulação com painéis laterais para configuração de parâmetros. 
     

    Tela de Resultados: Visualização gráfica e numérica dos resultados, com opções de exportação. 
     

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

     Linguagem: Python
     Framework: Django para backend, React para frontend.
     Controle de Versão: Git com GitHub.
     

5. Documento de API 

Documento de API 

Versão 1.0 

Introdução 

A API do "Simulador de Experimentos Educativos" permite a interação com os dados de simulação. 

Endpoints 

     

    GET /api/experiments: Recupera a lista de experimentos disponíveis. 
         Parâmetros: Nenhum
         Resposta: JSON com detalhes dos experimentos.
         
     

    POST /api/simulation/start: Inicia uma nova simulação. 
         Parâmetros: experiment_id, parameters
         Resposta: JSON com status e ID da simulação.
         
     

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
     
