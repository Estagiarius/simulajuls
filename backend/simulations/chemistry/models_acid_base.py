from typing import Optional, Dict, Any # Adicionado Dict, Any
from pydantic import BaseModel, Field # Field pode ser usado para validação se necessário
from backend.simulations.base_simulation import BaseSimulationParams, BaseSimulationResult

class AcidBaseSimulationParams(BaseSimulationParams):
    # Parâmetros para uma simulação de titulação ácido-base.
    # Assume ácidos e bases fortes monopróticos/monohidroxílicos para simplificação dos cálculos de pH.
    acid_name: Optional[str] = Field(default="Ácido Forte Monoprótico", description="Nome do ácido utilizado na simulação (informativo). Ex: 'HCl', 'Ácido Clorídrico'.")
    acid_concentration: float = Field(gt=0, description="Concentração molar (mol/L) da solução ácida. Deve ser maior que zero.")
    acid_volume: float = Field(gt=0, description="Volume (em mL) da solução ácida a ser titulada. Deve ser maior que zero.")
    base_name: Optional[str] = Field(default="Base Forte Monohidroxílica", description="Nome da base utilizada na simulação (informativo). Ex: 'NaOH', 'Hidróxido de Sódio'.")
    base_concentration: float = Field(gt=0, description="Concentração molar (mol/L) da solução básica (titulante). Deve ser maior que zero.")
    base_volume: float = Field(gt=0, description="Volume (em mL) da solução básica adicionado à solução ácida. Deve ser maior que zero.")
    indicator_name: Optional[str] = Field(default=None, description="Nome do indicador de pH utilizado (opcional). Ex: 'Fenolftaleína', 'Alaranjado de Metila'.")

class AcidBaseSimulationResult(BaseSimulationResult):
    # Resultados de uma simulação de titulação ácido-base.
    # O campo `parameters_used` é herdado de BaseSimulationResult e será preenchido
    # com uma cópia dos AcidBaseSimulationParams que foram usados para esta execução.

    final_ph: float = Field(description="Valor do pH final da solução após a mistura do ácido e da base.")
    final_poh: Optional[float] = Field(default=None, description="Valor do pOH final da solução. Calculado se a solução for neutra ou básica.")
    total_volume_ml: float = Field(description="Volume total da solução resultante (em mL) após a mistura.")
    mols_h_plus_initial: float = Field(description="Quantidade inicial de mols de íons H+ (provenientes do ácido).")
    mols_oh_minus_initial: float = Field(description="Quantidade inicial de mols de íons OH- (provenientes da base).")
    excess_reactant: Optional[str] = Field(default=None, description="Identifica qual reagente (H+ ou OH-) está em excesso após a neutralização, ou 'Nenhum' se for estequiométrico.")
    status: str = Field(description="Status da solução final, indicando se é 'Ácida', 'Neutra' ou 'Básica'.")
    indicator_color: Optional[str] = Field(default=None, description="Cor esperada para o indicador de pH selecionado no pH final da solução. 'N/A' se nenhum indicador for usado ou se o pH estiver fora da faixa do indicador.")
    message: Optional[str] = Field(default=None, description="Uma mensagem adicional fornecendo contexto ou informações sobre o resultado da simulação (ex: ponto de equivalência atingido).")
