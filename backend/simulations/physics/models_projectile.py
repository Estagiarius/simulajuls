from typing import List, Optional, Any, Dict
from pydantic import BaseModel, Field
from backend.simulations.base_simulation import BaseSimulationParams, BaseSimulationResult

class ProjectileLaunchParams(BaseSimulationParams):
    # Parâmetros para uma simulação de lançamento de projétil.
    # Considera o lançamento oblíquo de um projétil em um campo gravitacional uniforme,
    # desconsiderando a resistência do ar.
    initial_velocity: float = Field(..., gt=0, description="Velocidade inicial com que o projétil é lançado (em m/s). Deve ser maior que zero.")
    launch_angle: float = Field(..., ge=0, lt=90, description="Ângulo de lançamento do projétil em relação à horizontal (em graus). Deve estar entre 0 (lançamento horizontal) e 90 (lançamento vertical para cima), não incluindo 90 para este modelo de trajetória oblíqua.")
    initial_height: Optional[float] = Field(0.0, ge=0, description="Altura inicial de onde o projétil é lançado (em metros), em relação ao nível do solo (y=0). Deve ser maior ou igual a zero.")
    gravity: Optional[float] = Field(9.81, gt=0, description="Aceleração devido à gravidade (em m/s²). Por padrão, é 9.81 m/s². Deve ser maior que zero.")

class TrajectoryPoint(BaseModel):
    # Representa um ponto específico na trajetória do projétil.
    time: float = Field(..., description="Instante de tempo (em segundos) desde o lançamento.")
    x: float = Field(..., description="Posição horizontal (coordenada x) do projétil (em metros) no instante de tempo 'time'.")
    y: float = Field(..., description="Posição vertical (coordenada y) do projétil (em metros) no instante de tempo 'time', em relação ao nível do solo.")

class ProjectileLaunchResult(BaseSimulationResult):
    # Resultados de uma simulação de lançamento de projétil.
    # O campo `parameters_used` é herdado de BaseSimulationResult e será preenchido
    # com uma cópia dos ProjectileLaunchParams que foram usados para esta execução.
    initial_velocity_x: float = Field(..., description="Componente horizontal (Vx) da velocidade inicial (em m/s).")
    initial_velocity_y: float = Field(..., description="Componente vertical (Vy) da velocidade inicial (em m/s).")
    total_time: float = Field(..., description="Tempo total de voo do projétil (em segundos) até atingir o solo (y=0 ou altura inicial, dependendo do cenário).")
    max_range: float = Field(..., description="Alcance horizontal máximo (distância x) atingido pelo projétil (em metros) quando ele retorna à altura de referência (geralmente y=0 ou altura inicial).")
    max_height: float = Field(..., description="Altura máxima (ponto mais alto da trajetória, coordenada y) atingida pelo projétil (em metros) em relação ao nível do solo.")
    trajectory: List[TrajectoryPoint] = Field(..., description="Lista de objetos TrajectoryPoint que descrevem a trajetória do projétil em intervalos de tempo discretos.")
    parameters_used: ProjectileLaunchParams # type: ignore[assignment] # Parâmetros de entrada que foram utilizados para esta simulação específica.
    # Pydantic V2 lida com a atribuição de um modelo Pydantic a um campo Dict[str, Any] na classe base
    # através da serialização do modelo (ex: model_dump()).

    class Config:
        # Configurações do modelo Pydantic.
        # A atribuição de um modelo Pydantic (ProjectileLaunchParams) a um campo
        # que na classe base é Dict[str, Any] (parameters_used) é geralmente bem tratada
        # pelo Pydantic V2, que pode serializar o modelo para um dicionário quando necessário.
        # Em versões mais antigas do Pydantic ou para tipagem mais estrita, poderia ser necessário
        # um model_validator ou um serializador customizado na BaseSimulationResult,
        # ou garantir que parameters_used seja sempre explicitamente um dicionário.
        pass
