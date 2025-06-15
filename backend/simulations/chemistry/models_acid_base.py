from typing import Optional, Dict, Any # Adicionado Dict, Any
from pydantic import BaseModel, Field # Field pode ser usado para validação se necessário
from backend.simulations.base_simulation import BaseSimulationParams, BaseSimulationResult

class AcidBaseSimulationParams(BaseSimulationParams):
    acid_name: Optional[str] = Field(default="Ácido Forte", description="Nome do ácido (ex: HCl, H₂SO₄)")
    acid_concentration: float = Field(gt=0, description="Concentração molar do ácido (mol/L)")
    acid_volume: float = Field(gt=0, description="Volume de ácido a ser usado (mL)")
    base_name: Optional[str] = Field(default="Base Forte", description="Nome da base (ex: NaOH, Ca(OH)₂)")
    base_concentration: float = Field(gt=0, description="Concentração molar da base (mol/L)")
    base_volume: float = Field(gt=0, description="Volume de base a ser adicionado (mL)")
    indicator_name: Optional[str] = Field(default=None, description="Nome do indicador de pH (ex: Fenolftaleína, Vermelho de Metila)")

class AcidBaseSimulationResult(BaseSimulationResult):
    # parameters_used: Dict[str, Any] já está em BaseSimulationResult
    # Se quiséssemos ser mais específicos aqui, poderíamos sobrescrever, mas não é estritamente necessário
    # para a herança funcionar, desde que o que é passado para o construtor de BaseSimulationResult
    # seja um dict. A implementação do módulo cuidará de passar o dict correto.
    # No entanto, para clareza no schema do resultado específico, podemos definir:
    # parameters_used: AcidBaseSimulationParams # Isso daria erro se AcidBaseSimulationParams não estivesse totalmente definido ainda.
    # Vamos manter o Dict[str, Any] da classe base e garantir que o módulo preencha corretamente.

    final_ph: float = Field(description="pH final da solução")
    final_poh: Optional[float] = Field(default=None, description="pOH final da solução, se aplicável")
    total_volume_ml: float = Field(description="Volume total da solução em mL")
    mols_h_plus_initial: float = Field(description="Mols de H+ efetivos iniciais após considerar a estequiometria")
    mols_oh_minus_initial: float = Field(description="Mols de OH- efetivos iniciais após considerar a estequiometria")
    excess_reactant: Optional[str] = Field(default=None, description="Reagente em excesso (H+, OH- ou Nenhum)")
    status: str = Field(description="Status da solução (Ácida, Neutra, Básica)")
    indicator_color: Optional[str] = Field(default=None, description="Cor resultante do indicador")
    message: Optional[str] = Field(default=None, description="Mensagem adicional sobre a simulação")
