from abc import ABC, abstractmethod
from pydantic import BaseModel
from typing import Type, Dict, Any

class BaseSimulationParams(BaseModel):
    """
    Classe base para parâmetros de simulação.
    Simulações específicas devem herdar desta classe e adicionar seus próprios campos.
    """
    pass

class BaseSimulationResult(BaseModel):
    """
    Classe base para resultados de simulação.
    Simulações específicas devem herdar desta classe.
    """
    parameters_used: Dict[str, Any]


class SimulationModule(ABC):
    """
    Interface abstrata para um módulo de simulação.
    Cada nova simulação (ex: Reação Ácido-Base, Lançamento Oblíquo)
    deve implementar esta interface.
    """

    @abstractmethod
    def get_name(self) -> str:
        """Retorna um nome curto/identificador para a simulação (ex: 'acid-base')."""
        pass

    @abstractmethod
    def get_display_name(self) -> str:
        """Retorna o nome de exibição amigável da simulação (ex: 'Reação Ácido-Base')."""
        pass

    @abstractmethod
    def get_category(self) -> str:
        """Retorna a categoria da simulação (ex: 'Química', 'Física', 'Biologia')."""
        pass

    @abstractmethod
    def get_description(self) -> str:
        """Retorna uma breve descrição da simulação."""
        pass

    @abstractmethod
    def get_parameter_schema(self) -> Type[BaseModel]:
        """
        Retorna o *tipo* do modelo Pydantic que define os parâmetros de entrada
        desta simulação. Ex: return AcidBaseSimulationParams
        """
        pass

    @abstractmethod
    def get_result_schema(self) -> Type[BaseModel]:
        """
        Retorna o *tipo* do modelo Pydantic que define a estrutura dos resultados
        desta simulação. Ex: return AcidBaseSimulationResult
        """
        pass

    @abstractmethod
    def run_simulation(self, params: BaseModel) -> BaseModel:
        """
        Executa a lógica da simulação.
        Recebe uma instância do modelo de parâmetros (validada pelo chamador
        usando o schema de get_parameter_schema()).
        Retorna uma instância do modelo de resultados (definido por get_result_schema()).
        A implementação deve incluir o preenchimento de 'parameters_used' no resultado.
        """
        pass
