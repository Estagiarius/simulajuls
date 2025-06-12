from typing import List, Optional, Any, Dict
from pydantic import BaseModel, Field
from backend.simulations.base_simulation import BaseSimulationParams, BaseSimulationResult

class ProjectileLaunchParams(BaseSimulationParams):
    initial_velocity: float = Field(..., gt=0, description="Velocidade inicial do projétil (m/s)")
    launch_angle: float = Field(..., ge=0, lt=90, description="Ângulo de lançamento em graus (0-90, não inclusivo de 90 para oblíquo)")
    initial_height: Optional[float] = Field(0.0, ge=0, description="Altura inicial do lançamento (m)")
    gravity: Optional[float] = Field(9.81, gt=0, description="Aceleração devido à gravidade (m/s^2)")

class TrajectoryPoint(BaseModel):
    time: float = Field(..., description="Tempo em segundos")
    x: float = Field(..., description="Posição horizontal (x) em metros")
    y: float = Field(..., description="Posição vertical (y) em metros")

class ProjectileLaunchResult(BaseSimulationResult):
    initial_velocity_x: float = Field(..., description="Componente X da velocidade inicial (m/s)")
    initial_velocity_y: float = Field(..., description="Componente Y da velocidade inicial (m/s)")
    total_time: float = Field(..., description="Tempo total de voo (s)")
    max_range: float = Field(..., description="Alcance horizontal máximo (m)")
    max_height: float = Field(..., description="Altura máxima atingida (m)")
    trajectory: List[TrajectoryPoint] = Field(..., description="Lista de pontos da trajetória")
    parameters_used: ProjectileLaunchParams # type: ignore[assignment]
    # Pydantic V2 handles model assignment to Dict[str, Any] in the base class.
    # parameters_used: Dict[str, Any] # This would also be valid as per BaseSimulationResult

    class Config:
        # Ensure that Pydantic can handle the ProjectileLaunchParams type for parameters_used
        # when converting to dict for the BaseSimulationResult if necessary.
        # This is generally handled well in Pydantic V2 by default.
        # For older Pydantic or stricter typing, a model_validator or serializer might be used
        # in BaseSimulationResult, or ensure parameters_used is always a dict.
        # However, the current setup where BaseSimulationResult expects Dict[str, Any]
        # and we assign a Pydantic model instance to parameters_used in the child class
        # typically works because Pydantic model instances are dict-like and can be
        # serialized to dictionaries (e.g. via model_dump()).
        pass
