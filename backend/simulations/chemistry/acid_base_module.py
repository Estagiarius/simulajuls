import math
from typing import Type, Dict, Any # Adicionado Dict, Any
from pydantic import BaseModel # BaseModel é usado no type hint de run_simulation
from fastapi import HTTPException # Para levantar erros dentro da lógica se necessário

from backend.simulations.base_simulation import SimulationModule, BaseSimulationParams, BaseSimulationResult # Corrigido o import para BaseSimulationParams
from backend.simulations.chemistry.models_acid_base import AcidBaseSimulationParams, AcidBaseSimulationResult

class AcidBaseModule(SimulationModule):

    def get_name(self) -> str:
        return "acid-base"

    def get_display_name(self) -> str:
        return "Reação Ácido-Base"

    def get_category(self) -> str:
        return "Química"

    def get_description(self) -> str:
        return "Simula a reação entre um ácido e uma base, calculando o pH final e a cor do indicador."

    def get_parameter_schema(self) -> Type[AcidBaseSimulationParams]: # Especifica o tipo exato
        return AcidBaseSimulationParams

    def get_result_schema(self) -> Type[AcidBaseSimulationResult]: # Especifica o tipo exato
        return AcidBaseSimulationResult

    def run_simulation(self, params: AcidBaseSimulationParams) -> AcidBaseSimulationResult:
        # A validação de que params é do tipo AcidBaseSimulationParams
        # será feita pelo endpoint genérico antes de chamar este método.
        # No entanto, uma checagem de robustez pode ser mantida se desejado.
        if not isinstance(params, AcidBaseSimulationParams):
            # Este erro idealmente não deveria ser alcançado se o dispatcher funciona bem.
            raise TypeError("Parâmetros fornecidos não são do tipo AcidBaseSimulationParams.")

        # Validação de inputs que estava no endpoint original (pode ser mantida aqui ou no schema com Field)
        if params.acid_concentration <= 0 or params.acid_volume <= 0 or \
           params.base_concentration <= 0 or params.base_volume <= 0:
            # Esta validação também é feita pelo Field(gt=0) no modelo Pydantic,
            # mas uma checagem explícita aqui é uma garantia adicional.
            raise HTTPException(status_code=400, detail="Concentrações e volumes devem ser positivos.")

        # Lógica movida de perform_acid_base_simulation de main.py
        acid_volume_l = params.acid_volume / 1000
        base_volume_l = params.base_volume / 1000

        mols_h_plus = params.acid_concentration * acid_volume_l
        mols_oh_minus = params.base_concentration * base_volume_l

        total_volume_l = acid_volume_l + base_volume_l
        total_volume_ml = total_volume_l * 1000

        final_ph: float
        final_poh: Optional[float] = None # type: ignore
        # A diretiva # type: ignore é usada aqui porque o Pydantic pode, em alguns cenários de validação estrita de tipos,
        # não inferir corretamente que final_poh será atribuído um float antes de ser usado, dependendo do fluxo.
        # No entanto, a lógica garante que ele seja um float ou None.
        excess_reactant_val: Optional[str] = None
        status_val: str
        message_val: Optional[str] = None

        # Considerar neutralização com uma pequena tolerância para igualdade de floats
        if abs(mols_h_plus - mols_oh_minus) < 1e-9:
            final_ph = 7.0
            final_poh = 7.0
            excess_reactant_val = "Nenhum"
            status_val = "Neutra"
            message_val = "Neutralização completa."
        elif mols_h_plus > mols_oh_minus:
            mols_h_plus_excess = mols_h_plus - mols_oh_minus
            # Evitar divisão por zero se total_volume_l for zero (improvável com validações de volume)
            if total_volume_l == 0: raise HTTPException(status_code=400, detail="Volume total não pode ser zero.")
            concentration_h_plus_final = mols_h_plus_excess / total_volume_l

            if concentration_h_plus_final <= 1e-15: # Praticamente zero ou negativo
                final_ph = 14.0
                message_val = "Concentração de H+ excesso resultou em valor não positivo ou muito baixo, pH ajustado."
            else:
                 final_ph = -math.log10(concentration_h_plus_final)

            excess_reactant_val = "H+"
            status_val = "Ácida"
            if final_ph < 0: final_ph = 0.0 # pH não deve ser negativo
            if final_ph > 14: final_ph = 14.0 # Nem acima de 14 (para ácidos/bases fortes)
            final_poh = 14.0 - final_ph
        else: # mols_OH_minus > mols_H_plus
            mols_oh_minus_excess = mols_oh_minus - mols_h_plus
            if total_volume_l == 0: raise HTTPException(status_code=400, detail="Volume total não pode ser zero.")
            concentration_oh_minus_final = mols_oh_minus_excess / total_volume_l

            if concentration_oh_minus_final <= 1e-15:
                final_poh = 14.0
                message_val = "Concentração de OH- excesso resultou em valor não positivo ou muito baixo, pOH ajustado."
            else:
                final_poh = -math.log10(concentration_oh_minus_final)

            if final_poh < 0: final_poh = 0.0 # pOH não deve ser negativo
            if final_poh > 14: final_poh = 14.0
            final_ph = 14.0 - final_poh
            excess_reactant_val = "OH-"
            status_val = "Básica"

        final_ph = round(final_ph, 2)
        if final_poh is not None:
            final_poh = round(final_poh, 2)

        indicator_color_val: Optional[str] = None
        if params.indicator_name:
            indicator_name_lower = params.indicator_name.lower().strip() # Adicionado .strip()
            if indicator_name_lower == "fenolftaleína":
                if final_ph < 8.2: indicator_color_val = "Incolor"
                elif final_ph <= 10.0: indicator_color_val = "Rosa claro/Róseo"
                else: indicator_color_val = "Carmim/Magenta"
            elif indicator_name_lower == "azul de bromotimol":
                if final_ph < 6.0: indicator_color_val = "Amarelo"
                elif final_ph <= 7.6: indicator_color_val = "Verde"
                else: indicator_color_val = "Azul"
            else:
                indicator_color_val = "Indicador não reconhecido"
                if message_val:
                    message_val += f" Indicador '{params.indicator_name}' não suportado."
                else:
                    message_val = f"Indicador '{params.indicator_name}' não suportado."

        return AcidBaseSimulationResult(
            final_ph=final_ph,
            final_poh=final_poh,
            total_volume_ml=round(total_volume_ml, 3), # Ajustado para 3 casas decimais como no exemplo
            mols_h_plus_initial=round(mols_h_plus, 9),
            mols_oh_minus_initial=round(mols_oh_minus, 9),
            excess_reactant=excess_reactant_val,
            status=status_val,
            indicator_color=indicator_color_val,
            message=message_val,
            parameters_used=params.model_dump() # Importante para a classe base
        )
