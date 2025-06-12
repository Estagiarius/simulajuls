"""
Módulo de simulação para Reações Ácido-Base.

Este módulo implementa a lógica para simular a mistura de um ácido forte
monoprótico com uma base forte monohidroxílica. Ele calcula o pH e o pOH
finais da solução resultante, determina o reagente em excesso (se houver)
e o status da solução (ácida, básica ou neutra). Adicionalmente, se um
indicador de pH for especificado, sua cor na solução final é determinada.
"""
import math
from typing import Type, Dict, Any # Adicionado Dict, Any
from pydantic import BaseModel # BaseModel é usado no type hint de run_simulation
from fastapi import HTTPException # Para levantar erros dentro da lógica se necessário

from backend.simulations.base_simulation import SimulationModule, BaseSimulationParams, BaseSimulationResult # Corrigido o import para BaseSimulationParams
from backend.simulations.chemistry.models_acid_base import AcidBaseSimulationParams, AcidBaseSimulationResult

class AcidBaseModule(SimulationModule):
    # Implementa a interface SimulationModule para a simulação de Reação Ácido-Base.

    def get_name(self) -> str:
        # Retorna o nome identificador da simulação.
        return "acid-base"

    def get_display_name(self) -> str:
        # Retorna o nome de exibição da simulação.
        return "Reação Ácido-Base"

    def get_category(self) -> str:
        # Retorna a categoria da simulação.
        return "Química"

    def get_description(self) -> str:
        # Retorna uma breve descrição da simulação.
        return "Simula a reação entre um ácido e uma base, calculando o pH final e a cor do indicador."

    def get_parameter_schema(self) -> Type[AcidBaseSimulationParams]:
        # Retorna o tipo do modelo Pydantic para os parâmetros de entrada.
        return AcidBaseSimulationParams

    def get_result_schema(self) -> Type[AcidBaseSimulationResult]:
        # Retorna o tipo do modelo Pydantic para os resultados da simulação.
        return AcidBaseSimulationResult

    def run_simulation(self, params: AcidBaseSimulationParams) -> AcidBaseSimulationResult:
        # Executa a lógica da simulação de reação ácido-base.
        # Os parâmetros de entrada (params) já foram validados pelo Pydantic
        # conforme definido em AcidBaseSimulationParams, incluindo a verificação de que
        # concentrações e volumes são positivos (gt=0).

        # Converte volumes de mL para L para os cálculos.
        acid_volume_l = params.acid_volume / 1000
        base_volume_l = params.base_volume / 1000

        # Calcula o número inicial de mols de H+ e OH-.
        # Assume-se ácidos e bases fortes monopróticos/monohidroxílicos,
        # então [H+] = [Ácido] e [OH-] = [Base].
        mols_h_plus = params.acid_concentration * acid_volume_l
        mols_oh_minus = params.base_concentration * base_volume_l

        # Calcula o volume total da solução em litros e mililitros.
        total_volume_l = acid_volume_l + base_volume_l
        total_volume_ml = total_volume_l * 1000

        # Inicializa variáveis para os resultados.
        final_ph: float
        final_poh: Optional[float] = None
        excess_reactant_val: Optional[str] = None
        status_val: str
        message_val: Optional[str] = None

        # Lógica de neutralização e cálculo de pH/pOH:
        # Utiliza uma pequena tolerância (epsilon) para comparar igualdade entre floats,
        # devido a possíveis imprecisões de ponto flutuante.
        epsilon = 1e-9
        if abs(mols_h_plus - mols_oh_minus) < epsilon:
            # Caso 1: Neutralização completa (mols de H+ ≈ mols de OH-).
            final_ph = 7.0
            final_poh = 7.0
            excess_reactant_val = "Nenhum" # Nenhum reagente em excesso.
            status_val = "Neutra"
            message_val = "Neutralização completa. O ponto de equivalência foi atingido."
        elif mols_h_plus > mols_oh_minus:
            # Caso 2: Ácido em excesso.
            mols_h_plus_excess = mols_h_plus - mols_oh_minus
            # Verifica se o volume total é zero para evitar divisão por zero.
            # Esta verificação é uma salvaguarda, pois os volumes de entrada devem ser > 0.
            if total_volume_l == 0:
                raise HTTPException(status_code=400, detail="Volume total da solução não pode ser zero.")
            concentration_h_plus_final = mols_h_plus_excess / total_volume_l

            # Trata casos onde a concentração final de H+ é extremamente baixa ou não positiva.
            if concentration_h_plus_final <= 1e-15:
                final_ph = 14.0 # pH de uma solução com [H+] residual muito baixa tende a básico extremo (raro aqui).
                message_val = "A concentração de H+ em excesso resultou em um valor não positivo ou extremamente baixo. O pH foi ajustado."
            else:
                 final_ph = -math.log10(concentration_h_plus_final) # Cálculo do pH.

            excess_reactant_val = "H+" # H+ é o reagente em excesso.
            status_val = "Ácida"
            # Ajusta o pH para o intervalo comum de 0-14.
            if final_ph < 0: final_ph = 0.0
            if final_ph > 14: final_ph = 14.0
            final_poh = 14.0 - final_ph # Cálculo do pOH.
        else: # mols_oh_minus > mols_h_plus
            # Caso 3: Base em excesso.
            mols_oh_minus_excess = mols_oh_minus - mols_h_plus
            if total_volume_l == 0:
                raise HTTPException(status_code=400, detail="Volume total da solução não pode ser zero.")
            concentration_oh_minus_final = mols_oh_minus_excess / total_volume_l

            # Trata casos onde a concentração final de OH- é extremamente baixa ou não positiva.
            if concentration_oh_minus_final <= 1e-15:
                final_poh = 14.0 # pOH de uma solução com [OH-] residual muito baixa.
                message_val = "A concentração de OH- em excesso resultou em um valor não positivo ou extremamente baixo. O pOH foi ajustado."
            else:
                final_poh = -math.log10(concentration_oh_minus_final) # Cálculo do pOH.

            # Ajusta o pOH para o intervalo comum de 0-14.
            if final_poh < 0: final_poh = 0.0
            if final_poh > 14: final_poh = 14.0
            final_ph = 14.0 - final_poh # Cálculo do pH.
            excess_reactant_val = "OH-" # OH- é o reagente em excesso.
            status_val = "Básica"

        # Arredonda os valores de pH e pOH para duas casas decimais.
        final_ph = round(final_ph, 2)
        if final_poh is not None:
            final_poh = round(final_poh, 2)

        # Determinação da cor do indicador de pH, se um for especificado.
        indicator_color_val: Optional[str] = "N/A" # Valor padrão se nenhum indicador ou não reconhecido.
        if params.indicator_name:
            indicator_name_lower = params.indicator_name.lower().strip() # Normaliza o nome do indicador.
            if indicator_name_lower == "fenolftaleína":
                if final_ph < 8.2: indicator_color_val = "Incolor"
                elif final_ph <= 10.0: indicator_color_val = "Rosa claro/Róseo" # Faixa de viragem
                else: indicator_color_val = "Carmim/Magenta"
            elif indicator_name_lower == "azul de bromotimol":
                if final_ph < 6.0: indicator_color_val = "Amarelo"
                elif final_ph <= 7.6: indicator_color_val = "Verde" # Faixa de viragem
                else: indicator_color_val = "Azul"
            else:
                # Se o indicador não for reconhecido, define uma mensagem apropriada.
                indicator_color_val = "Indicador não reconhecido"
                unsupported_indicator_message = f"Indicador '{params.indicator_name}' não é suportado ou reconhecido."
                if message_val:
                    message_val += f" {unsupported_indicator_message}"
                else:
                    message_val = unsupported_indicator_message
        else:
            indicator_color_val = "Nenhum indicador utilizado"


        # Retorna o objeto de resultado da simulação.
        return AcidBaseSimulationResult(
            final_ph=final_ph,
            final_poh=final_poh,
            total_volume_ml=round(total_volume_ml, 3), # Volume total arredondado.
            mols_h_plus_initial=round(mols_h_plus, 9), # Mols iniciais com precisão.
            mols_oh_minus_initial=round(mols_oh_minus, 9),
            excess_reactant=excess_reactant_val,
            status=status_val,
            indicator_color=indicator_color_val,
            message=message_val,
            parameters_used=params.model_dump() # Inclui os parâmetros de entrada usados na simulação.
        )
