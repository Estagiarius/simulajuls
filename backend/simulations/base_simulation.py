from abc import ABC, abstractmethod
from pydantic import BaseModel
from typing import Type, Dict, Any

class BaseSimulationParams(BaseModel):
    # Modelo Pydantic base para os parâmetros de entrada de qualquer simulação.
    # Todas as classes de parâmetros para simulações específicas devem herdar desta.
    # Isso permite que a lógica central da API trate os parâmetros de forma genérica
    # e também que cada simulação defina seus próprios campos de entrada específicos.
    # Exemplo:
    # class MinhaSimulacaoParams(BaseSimulationParams):
    #     meu_parametro: int
    #     outro_parametro: str = "valor_padrao"
    """
    Classe base para parâmetros de simulação.
    Simulações específicas devem herdar desta classe e adicionar seus próprios campos.
    """
    pass

class BaseSimulationResult(BaseModel):
    # Modelo Pydantic base para os resultados de qualquer simulação.
    # Todas as classes de resultados para simulações específicas devem herdar desta.
    # O campo `parameters_used` é obrigatório e deve ser preenchido pela lógica da simulação
    # para registrar quais parâmetros foram efetivamente usados na execução.
    # Exemplo:
    # class MinhaSimulacaoResult(BaseSimulationResult):
    #     resultado_calculado: float
    #     mensagem: str
    """
    Classe base para resultados de simulação.
    Simulações específicas devem herdar desta classe.
    """
    parameters_used: Dict[str, Any] # Dicionário para armazenar os parâmetros que foram usados na simulação.


class SimulationModule(ABC):
    # Classe base abstrata (Interface) para todos os módulos de simulação.
    # Define um contrato que cada módulo de simulação específico (por exemplo, uma simulação de pêndulo,
    # uma simulação de reação química, etc.) deve seguir.
    # Isso permite que a API principal descubra e interaja com diferentes simulações
    # de uma maneira uniforme, sem precisar conhecer os detalhes de implementação de cada uma.
    #
    # Para criar uma nova simulação, você deve:
    # 1. Criar uma classe que herde de `SimulationModule`.
    # 2. Implementar todos os métodos abstratos definidos aqui.
    # 3. Definir classes de parâmetros (herdando de `BaseSimulationParams`) e resultados
    #    (herdando de `BaseSimulationResult`) específicas para a sua simulação.
    """
    Interface abstrata para um módulo de simulação.
    Cada nova simulação (ex: Reação Ácido-Base, Lançamento Oblíquo)
    deve implementar esta interface.
    """

    @abstractmethod
    def get_name(self) -> str:
        # Retorna um nome/identificador único em formato de string para a simulação.
        # Este nome é usado internamente, por exemplo, na URL da API e como chave no registro de simulações.
        # Deve ser conciso e em letras minúsculas, usando hífens para separar palavras (kebab-case).
        # Exemplo: "lancamento-projetil", "reacao-quimica-simples".
        """Retorna um nome curto/identificador para a simulação (ex: 'acid-base')."""
        pass

    @abstractmethod
    def get_display_name(self) -> str:
        # Retorna o nome de exibição da simulação, que será mostrado na interface do usuário.
        # Deve ser um nome amigável e descritivo.
        # Exemplo: "Lançamento de Projétil", "Reação Química Simples".
        """Retorna o nome de exibição amigável da simulação (ex: 'Reação Ácido-Base')."""
        pass

    @abstractmethod
    def get_category(self) -> str:
        # Retorna a categoria à qual a simulação pertence.
        # Usado para organizar as simulações na interface do usuário.
        # Exemplo: "Física", "Química", "Matemática".
        """Retorna a categoria da simulação (ex: 'Química', 'Física', 'Biologia')."""
        pass

    @abstractmethod
    def get_description(self) -> str:
        # Retorna uma breve descrição do que a simulação faz ou demonstra.
        # Esta descrição pode ser exibida na interface do usuário para ajudar a entender o propósito da simulação.
        """Retorna uma breve descrição da simulação."""
        pass

    @abstractmethod
    def get_parameter_schema(self) -> Type[BaseModel]:
        # Retorna o *tipo* da classe Pydantic (que herda de BaseSimulationParams)
        # que define os parâmetros de entrada necessários para esta simulação.
        # A API usará este schema para validar os dados de entrada fornecidos pelo usuário.
        # Exemplo: `return MinhaSimulacaoParams` (onde MinhaSimulacaoParams é uma classe que herda de BaseSimulationParams).
        """
        Retorna o *tipo* do modelo Pydantic que define os parâmetros de entrada
        desta simulação. Ex: return AcidBaseSimulationParams
        """
        pass

    @abstractmethod
    def get_result_schema(self) -> Type[BaseModel]:
        # Retorna o *tipo* da classe Pydantic (que herda de BaseSimulationResult)
        # que define a estrutura dos dados de resultado desta simulação.
        # A API usará este schema para serializar os dados de saída.
        # Exemplo: `return MinhaSimulacaoResult` (onde MinhaSimulacaoResult é uma classe que herda de BaseSimulationResult).
        """
        Retorna o *tipo* do modelo Pydantic que define a estrutura dos resultados
        desta simulação. Ex: return AcidBaseSimulationResult
        """
        pass

    @abstractmethod
    def run_simulation(self, params: BaseModel) -> BaseModel:
        # Método principal que executa a lógica da simulação.
        #
        # Parâmetros:
        #   params (BaseModel): Uma instância do modelo Pydantic (definido por `get_parameter_schema()`)
        #                       contendo os parâmetros de entrada para a simulação. A API garante
        #                       que `params` já foi validado contra o schema.
        #
        # Retorna:
        #   BaseModel: Uma instância do modelo Pydantic (definido por `get_result_schema()`)
        #              contendo os resultados da simulação. A implementação deste método
        #              é responsável por criar e popular este objeto de resultado, incluindo
        #              o campo `parameters_used` (herdado de `BaseSimulationResult`),
        #              que deve ser um dicionário dos parâmetros efetivamente utilizados.
        #
        # Exemplo de implementação:
        #   ```python
        #   def run_simulation(self, params: MinhaSimulacaoParams) -> MinhaSimulacaoResult:
        #       # ... lógica da simulação usando params.meu_parametro ...
        #       resultado_calculado = params.meu_parametro * 2
        #       return MinhaSimulacaoResult(
        #           parameters_used=params.model_dump(),
        #           resultado_calculado=resultado_calculado,
        #           mensagem="Simulação concluída."
        #       )
        #   ```
        """
        Executa a lógica da simulação.
        Recebe uma instância do modelo de parâmetros (validada pelo chamador
        usando o schema de get_parameter_schema()).
        Retorna uma instância do modelo de resultados (definido por get_result_schema()).
        A implementação deve incluir o preenchimento de 'parameters_used' no resultado.
        """
        pass
