from typing import Optional, Dict, Any, List # Adicionado List
from pydantic import BaseModel, Field
from backend.simulations.base_simulation import BaseSimulationParams, BaseSimulationResult

class AcidBaseSimulationParams(BaseSimulationParams):
    acid_name: Optional[str] = Field(default="Ácido Forte", description="Nome do ácido (ex: HCl, H₂SO₄, CH₃COOH)")
    acid_concentration: float = Field(gt=0, description="Concentração molar do ácido (mol/L)")
    acid_volume: float = Field(gt=0, description="Volume de ácido a ser usado (mL)")
    acid_ka: Optional[float] = Field(default=None, gt=0, description="Constante de ionização do ácido (Ka) para ácidos fracos")

    base_name: Optional[str] = Field(default="Base Forte", description="Nome da base (ex: NaOH, Ca(OH)₂, NH₃)")
    base_concentration: float = Field(gt=0, description="Concentração molar da base (mol/L)")
    base_volume: float = Field(gt=0, description="Volume de base a ser adicionado (mL)")
    base_kb: Optional[float] = Field(default=None, gt=0, description="Constante de ionização da base (Kb) para bases fracas")

    indicator_name: Optional[str] = Field(default=None, description="Nome do indicador de pH (ex: Fenolftaleína, Vermelho de Metila)")

class AcidBaseSimulationResult(BaseSimulationResult):
    final_ph: float = Field(description="pH final da solução")
    final_poh: Optional[float] = Field(default=None, description="pOH final da solução, se aplicável")
    total_volume_ml: float = Field(description="Volume total da solução em mL")
    mols_h_plus_initial: float = Field(description="Mols de H+ efetivos iniciais após considerar a estequiometria")
    mols_oh_minus_initial: float = Field(description="Mols de OH- efetivos iniciais após considerar a estequiometria")
    excess_reactant: Optional[str] = Field(default=None, description="Reagente em excesso (H+, OH- ou Nenhum)")
    status: str = Field(description="Status da solução (Ácida, Neutra, Básica)")
    indicator_color: Optional[str] = Field(default=None, description="Cor resultante do indicador")
    message: Optional[str] = Field(default=None, description="Mensagem adicional sobre a simulação")
    is_weak_acid_calculation: Optional[bool] = Field(default=None, description="Indica se o cálculo envolveu um ácido fraco")
    is_weak_base_calculation: Optional[bool] = Field(default=None, description="Indica se o cálculo envolveu uma base fraca")
    ka_used: Optional[float] = Field(default=None, description="Valor de Ka utilizado no cálculo, se aplicável")
    kb_used: Optional[float] = Field(default=None, description="Valor de Kb utilizado no cálculo, se aplicável")

# Modelos para Simulação de Curva de Titulação

class TitrationParams(AcidBaseSimulationParams): # Herda do titulado
    # Titulado já definido em AcidBaseSimulationParams:
    # acid_name, acid_concentration, acid_volume, acid_ka
    # base_name, base_concentration, base_volume, base_kb
    # indicator_name (pode não ser usado diretamente na curva, mas herdado)

    # Propriedades do Titulante
    titrant_is_acid: bool = Field(description="Define se o titulante é um ácido (True) ou uma base (False).")
    titrant_name: str = Field(default="NaOH", description="Nome do titulante (ex: NaOH, HCl). Focar em titulantes fortes inicialmente.")
    titrant_concentration: float = Field(gt=0, description="Concentração molar do titulante (mol/L).")

    # Parâmetros da Titulação
    initial_titrant_volume_ml: float = Field(default=0.0, ge=0, description="Volume inicial de titulante a ser considerado (mL).")
    final_titrant_volume_ml: float = Field(gt=0, description="Volume final de titulante a ser adicionado (mL).")
    volume_increment_ml: float = Field(gt=0, description="Volume de cada incremento de titulante (mL).")

    # Sobrescrever indicator_name para não ser obrigatório ou ter um default diferente se não for usado
    indicator_name: Optional[str] = Field(default=None, description="Indicador de pH (opcional para curva de titulação).")


class TitrationDataPoint(BaseModel):
    titrant_volume_added_ml: float = Field(description="Volume total de titulante adicionado acumulado naquele ponto (mL).")
    ph: float = Field(description="pH calculado da solução naquele ponto.")


class TitrationResult(BaseSimulationResult):
    # parameters_used já está em BaseSimulationResult, mas será do tipo TitrationParams
    titration_curve: List[TitrationDataPoint] = Field(description="Lista de pontos de dados (volume adicionado, pH) para plotar a curva.")
    # Para o futuro, mas bom de prever no modelo:
    equivalence_points_ml: Optional[List[float]] = Field(default=None, description="Lista opcional de volumes de titulante (mL) onde os pontos de equivalência foram detectados.")

    # Garantir que o parameters_used seja explicitamente TitrationParams no schema gerado, se possível,
    # ou que a documentação gerada seja clara. Pydantic deve lidar com isso na serialização.
    # Se precisarmos ser explícitos para OpenAPI:
    # parameters_used: TitrationParams # Substituiria o Dict[str, Any] da classe base.
    # Por enquanto, vamos confiar na herança e na passagem correta do dict.
