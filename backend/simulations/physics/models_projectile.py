from typing import List, Optional, Literal
from pydantic import BaseModel, Field, field_validator
from backend.simulations.base_simulation import BaseSimulationParams, BaseSimulationResult

# Allowed Unit Literals
ALLOWED_VELOCITY_UNITS = Literal["m/s", "km/h", "ft/s", "mph"]
ALLOWED_LENGTH_UNITS = Literal["m", "ft"]
ALLOWED_OUTPUT_TIME_UNITS = Literal["s", "min"]
ALLOWED_OUTPUT_LENGTH_UNITS = Literal["m", "km", "ft", "mi"]

class OutputUnitSelection(BaseModel):
    velocity_unit: Optional[ALLOWED_VELOCITY_UNITS] = Field(
        "m/s",
        description="Unidade para velocidades nos resultados (e.g., componentes da velocidade inicial)."
    )
    time_unit: Optional[ALLOWED_OUTPUT_TIME_UNITS] = Field(
        "s",
        description="Unidade para o tempo total de voo."
    )
    range_unit: Optional[ALLOWED_OUTPUT_LENGTH_UNITS] = Field(
        "m",
        description="Unidade para o alcance máximo."
    )
    height_unit: Optional[ALLOWED_OUTPUT_LENGTH_UNITS] = Field(
        "m",
        description="Unidade para a altura máxima."
    )

    @field_validator('velocity_unit')
    @classmethod
    def validate_velocity_unit(cls, value):
        if value not in cls.model_fields['velocity_unit'].annotation.__args__[0].__args__: # Accessing Literal values
            raise ValueError(f"Unidade de velocidade inválida: {value}. Permitidas: {cls.model_fields['velocity_unit'].annotation.__args__[0].__args__}")
        return value

    @field_validator('time_unit')
    @classmethod
    def validate_time_unit(cls, value):
        if value not in cls.model_fields['time_unit'].annotation.__args__[0].__args__:
            raise ValueError(f"Unidade de tempo inválida: {value}. Permitidas: {cls.model_fields['time_unit'].annotation.__args__[0].__args__}")
        return value

    @field_validator('range_unit')
    @classmethod
    def validate_range_unit(cls, value):
        if value not in cls.model_fields['range_unit'].annotation.__args__[0].__args__:
            raise ValueError(f"Unidade de alcance inválida: {value}. Permitidas: {cls.model_fields['range_unit'].annotation.__args__[0].__args__}")
        return value

    @field_validator('height_unit')
    @classmethod
    def validate_height_unit(cls, value):
        if value not in cls.model_fields['height_unit'].annotation.__args__[0].__args__:
            raise ValueError(f"Unidade de altura inválida: {value}. Permitidas: {cls.model_fields['height_unit'].annotation.__args__[0].__args__}")
        return value


class ProjectileLaunchParams(BaseSimulationParams):
    initial_velocity: float = Field(..., gt=0, description="Valor da velocidade inicial do projétil.")
    initial_velocity_unit: Optional[ALLOWED_VELOCITY_UNITS] = Field(
        "m/s",
        description="Unidade da velocidade inicial."
    )
    launch_angle: float = Field(..., ge=0, lt=90, description="Ângulo de lançamento em graus (0° é horizontal, <90°).")
    initial_height: Optional[float] = Field(0.0, ge=0, description="Valor da altura inicial do lançamento.")
    initial_height_unit: Optional[ALLOWED_LENGTH_UNITS] = Field(
        "m",
        description="Unidade da altura inicial."
    )
    gravity: Optional[float] = Field(9.81, gt=0, description="Aceleração devido à gravidade. Assume-se m/s^2 e é usada como tal internamente. A conversão de outras unidades de entrada não é diretamente suportada para este campo.")
    output_units: Optional[OutputUnitSelection] = Field(
        default_factory=OutputUnitSelection,
        description="Preferências de unidade para os resultados da simulação."
    )

    @field_validator('initial_velocity_unit')
    @classmethod
    def validate_initial_velocity_unit(cls, value):
        if value not in cls.model_fields['initial_velocity_unit'].annotation.__args__[0].__args__:
             raise ValueError(f"Unidade de velocidade inicial inválida: {value}. Permitidas: {cls.model_fields['initial_velocity_unit'].annotation.__args__[0].__args__}")
        return value

    @field_validator('initial_height_unit')
    @classmethod
    def validate_initial_height_unit(cls, value):
        if value not in cls.model_fields['initial_height_unit'].annotation.__args__[0].__args__:
            raise ValueError(f"Unidade de altura inicial inválida: {value}. Permitidas: {cls.model_fields['initial_height_unit'].annotation.__args__[0].__args__}")
        return value

class TrajectoryPoint(BaseModel):
    time: float = Field(..., description="Tempo em segundos (sempre em 's' nesta lista de trajetória).")
    x: float = Field(..., description="Posição horizontal (x). A unidade corresponderá a ProjectileLaunchResult.max_range_unit.")
    y: float = Field(..., description="Posição vertical (y). A unidade corresponderá a ProjectileLaunchResult.max_height_unit.")

class ProjectileLaunchResult(BaseSimulationResult):
    initial_velocity_x: float = Field(..., description="Componente X da velocidade inicial.")
    initial_velocity_x_unit: str = Field(..., description="Unidade da componente X da velocidade inicial.")
    initial_velocity_y: float = Field(..., description="Componente Y da velocidade inicial.")
    initial_velocity_y_unit: str = Field(..., description="Unidade da componente Y da velocidade inicial.")

    total_time: float = Field(..., description="Tempo total de voo.")
    total_time_unit: str = Field(..., description="Unidade do tempo total de voo.")

    max_range: float = Field(..., description="Alcance horizontal máximo.")
    max_range_unit: str = Field(..., description="Unidade do alcance horizontal máximo.")

    max_height: float = Field(..., description="Altura máxima atingida (relativa ao ponto y=0).")
    max_height_unit: str = Field(..., description="Unidade da altura máxima.")

    trajectory: List[TrajectoryPoint] = Field(..., description="Lista de pontos da trajetória. 'time' é sempre em segundos. 'x' e 'y' terão unidades correspondentes a 'max_range_unit' e 'max_height_unit' respectivamente.")

    parameters_used: ProjectileLaunchParams
    # A anotação 'type: ignore[assignment]' foi removida pois o Pydantic v2 geralmente lida bem
    # com a atribuição de um modelo Pydantic onde um Dict[str, Any] é esperado na classe base,
    # especialmente durante a serialização. Se problemas surgirem, pode ser reavaliado.

    class Config:
        # Pydantic V2 não requer mais `orm_mode = True`. `from_attributes = True` é o substituto se necessário para ORM.
        # Para este caso, a configuração padrão deve ser suficiente.
        pass
