import math
from typing import Type, Dict, Any, Optional # Adicionado Optional
from pydantic import BaseModel
from fastapi import HTTPException

from backend.simulations.base_simulation import SimulationModule
from backend.simulations.chemistry.models_acid_base import AcidBaseSimulationParams, AcidBaseSimulationResult

class AcidBaseModule(SimulationModule):

    def get_name(self) -> str:
        return "acid-base"

    def get_display_name(self) -> str:
        return "Reação Ácido-Base"

    def get_category(self) -> str:
        return "Chemistry"

    def get_description(self) -> str:
        return "Simula a reação entre ácidos e bases (fortes, incluindo H₂SO₄ e Ca(OH)₂), calculando o pH final e a cor de vários indicadores."

    def get_parameter_schema(self) -> Type[AcidBaseSimulationParams]:
        return AcidBaseSimulationParams

    def get_result_schema(self) -> Type[AcidBaseSimulationResult]:
        return AcidBaseSimulationResult

    def run_simulation(self, params: AcidBaseSimulationParams) -> AcidBaseSimulationResult:
        if not isinstance(params, AcidBaseSimulationParams):
            raise TypeError("Parâmetros fornecidos não são do tipo AcidBaseSimulationParams.")

        if params.acid_concentration <= 0 or params.acid_volume <= 0 or \
           params.base_concentration <= 0 or params.base_volume <= 0:
            raise HTTPException(status_code=400, detail="Concentrações e volumes devem ser positivos.")

        acid_volume_l = params.acid_volume / 1000
        base_volume_l = params.base_volume / 1000

        # Ajuste para estequiometria
        mols_h_plus_factor = 1.0
        # Normalizar o nome do ácido para comparação
        normalized_acid_name = params.acid_name.lower().strip() if params.acid_name else ""
        if "h2so4" in normalized_acid_name or "h₂so₄" in normalized_acid_name: # Considerar h2so4 ou h₂so₄
            mols_h_plus_factor = 2.0

        mols_oh_minus_factor = 1.0
        # Normalizar o nome da base para comparação
        normalized_base_name = params.base_name.lower().strip() if params.base_name else ""
        if "ca(oh)2" in normalized_base_name or "ca(oh)₂" in normalized_base_name: # Considerar ca(oh)2 ou ca(oh)₂
            mols_oh_minus_factor = 2.0

        mols_h_plus = params.acid_concentration * acid_volume_l * mols_h_plus_factor
        mols_oh_minus = params.base_concentration * base_volume_l * mols_oh_minus_factor

        total_volume_l = acid_volume_l + base_volume_l
        total_volume_ml = total_volume_l * 1000

        final_ph: float
        final_poh: Optional[float] = None
        excess_reactant_val: Optional[str] = None
        status_val: str
        message_val: Optional[str] = None

        if abs(mols_h_plus - mols_oh_minus) < 1e-9: # Neutralização
            final_ph = 7.0
            final_poh = 7.0
            excess_reactant_val = "Nenhum"
            status_val = "Neutra"
            message_val = "Neutralização completa."
        elif mols_h_plus > mols_oh_minus: # Excesso de ácido
            mols_h_plus_excess = mols_h_plus - mols_oh_minus
            if total_volume_l == 0: raise HTTPException(status_code=400, detail="Volume total não pode ser zero.")
            concentration_h_plus_final = mols_h_plus_excess / total_volume_l
            if concentration_h_plus_final <= 1e-15:
                final_ph = 14.0
                message_val = "Concentração de H+ excesso resultou em valor não positivo ou muito baixo, pH ajustado."
            else:
                 final_ph = -math.log10(concentration_h_plus_final)
            excess_reactant_val = "H+"
            status_val = "Ácida"
            if final_ph < 0: final_ph = 0.0
            if final_ph > 14: final_ph = 14.0
            final_poh = 14.0 - final_ph
        else: # Excesso de base
            mols_oh_minus_excess = mols_oh_minus - mols_h_plus
            if total_volume_l == 0: raise HTTPException(status_code=400, detail="Volume total não pode ser zero.")
            concentration_oh_minus_final = mols_oh_minus_excess / total_volume_l
            if concentration_oh_minus_final <= 1e-15:
                final_poh = 14.0
                message_val = "Concentração de OH- excesso resultou em valor não positivo ou muito baixo, pOH ajustado."
            else:
                final_poh = -math.log10(concentration_oh_minus_final)
            if final_poh < 0: final_poh = 0.0
            if final_poh > 14: final_poh = 14.0
            final_ph = 14.0 - final_poh
            excess_reactant_val = "OH-"
            status_val = "Básica"

        final_ph = round(final_ph, 2)
        if final_poh is not None:
            final_poh = round(final_poh, 2)

        indicator_color_val: Optional[str] = None
        if params.indicator_name:
            indicator_name_lower = params.indicator_name.lower().strip()
            if indicator_name_lower == "fenolftaleína":
                if final_ph < 8.2: indicator_color_val = "Incolor"
                elif final_ph <= 10.0: indicator_color_val = "Rosa claro/Róseo"
                else: indicator_color_val = "Carmim/Magenta"
            elif indicator_name_lower == "azul de bromotimol":
                if final_ph < 6.0: indicator_color_val = "Amarelo"
                elif final_ph <= 7.6: indicator_color_val = "Verde"
                else: indicator_color_val = "Azul"
            elif indicator_name_lower == "vermelho de metila": # Novo indicador
                if final_ph < 4.4: indicator_color_val = "Vermelho"
                elif final_ph <= 6.2: indicator_color_val = "Laranja"
                else: indicator_color_val = "Amarelo"
            elif indicator_name_lower == "alaranjado de metila": # Novo indicador
                if final_ph < 3.1: indicator_color_val = "Vermelho"
                elif final_ph <= 4.4: indicator_color_val = "Laranja"
                else: indicator_color_val = "Amarelo"
            else:
                indicator_color_val = "Indicador não reconhecido"
                current_message = f"Indicador '{params.indicator_name}' não suportado."
                message_val = f"{message_val} {current_message}".strip() if message_val else current_message

        # Atualizar descrição do módulo dinamicamente (se necessário, embora geralmente estático)
        # self.get_description.__func__.__doc__ = "Simula a reação entre ácidos e bases (fortes, incluindo H₂SO₄ e Ca(OH)₂), calculando o pH final e a cor de vários indicadores."
        # A linha acima não é a forma padrão de atualizar metadados de um método se a descrição é para ser estática.
        # A docstring da função get_description já foi alterada manualmente no código fornecido.

        return AcidBaseSimulationResult(
            final_ph=final_ph,
            final_poh=final_poh,
            total_volume_ml=round(total_volume_ml, 3),
            mols_h_plus_initial=round(mols_h_plus, 9), # Estes são os mols efetivos
            mols_oh_minus_initial=round(mols_oh_minus, 9), # Estes são os mols efetivos
            excess_reactant=excess_reactant_val,
            status=status_val,
            indicator_color=indicator_color_val,
            message=message_val,
            parameters_used=params.model_dump()
        )
