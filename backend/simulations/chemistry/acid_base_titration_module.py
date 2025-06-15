from typing import Type, List, Optional
from fastapi import HTTPException

from backend.simulations.base_simulation import SimulationModule
from backend.simulations.chemistry.models_acid_base import TitrationParams, TitrationResult, TitrationDataPoint, AcidBaseSimulationParams
from backend.simulations.chemistry.acid_base_module import AcidBaseModule

class AcidBaseTitrationModule(SimulationModule):

    def __init__(self):
        super().__init__()
        self.acid_base_calculator = AcidBaseModule()

    def get_name(self) -> str:
        return "acid-base-titration"

    def get_display_name(self) -> str:
        return "Curva de Titulação Ácido-Base"

    def get_category(self) -> str:
        return "Chemistry"

    def get_description(self) -> str:
        return "Simula uma curva de titulação ácido-base, mostrando a variação do pH com a adição de um titulante."

    def get_parameter_schema(self) -> Type[TitrationParams]:
        return TitrationParams

    def get_result_schema(self) -> Type[TitrationResult]:
        return TitrationResult

    def run_simulation(self, params: TitrationParams) -> TitrationResult:
        if not isinstance(params, TitrationParams):
            raise TypeError("Parâmetros fornecidos não são do tipo TitrationParams.")

        if params.final_titrant_volume_ml < params.initial_titrant_volume_ml:
            raise HTTPException(status_code=400, detail="O volume final do titulante deve ser maior ou igual ao volume inicial.")
        if params.volume_increment_ml <= 0:
            raise HTTPException(status_code=400, detail="O incremento de volume deve ser positivo.")

        max_points = 2000
        num_expected_points = 0
        if params.volume_increment_ml > 1e-9: # Evitar divisão por zero
            num_expected_points = abs(params.final_titrant_volume_ml - params.initial_titrant_volume_ml) / params.volume_increment_ml

        # Adicionar 1 para incluir o ponto inicial, se o intervalo não for zero
        if abs(params.final_titrant_volume_ml - params.initial_titrant_volume_ml) > 1e-9 :
             num_expected_points +=1
        else: # Caso initial_volume == final_volume, apenas 1 ponto
             num_expected_points = 1


        if num_expected_points > max_points:
            raise HTTPException(status_code=400, detail=f"Número de pontos ({int(num_expected_points)}) excede o limite de {max_points}. Aumente o incremento ou reduza o intervalo.")

        titration_curve_data: List[TitrationDataPoint] = []
        current_titrant_vol_ml = params.initial_titrant_volume_ml

        iteration_count = 0
        # Usar max_points como um limite seguro para iterações, num_expected_points já foi validado
        # O loop deve, em teoria, terminar com base na condição de volume.
        # A condição de parada do loop é `current_titrant_vol_ml > params.final_titrant_volume_ml`
        # mas com uma pequena tolerância para float.

        while iteration_count < num_expected_points + 5 and iteration_count < max_points + 10 : # Adiciona uma margem pequena
            actual_volume_to_simulate = current_titrant_vol_ml
            if actual_volume_to_simulate > params.final_titrant_volume_ml:
                actual_volume_to_simulate = params.final_titrant_volume_ml

            point_params_dict = {}

            if params.titrant_is_acid:
                point_params_dict = {
                    "acid_name": params.titrant_name,
                    "acid_concentration": params.titrant_concentration,
                    "acid_volume": actual_volume_to_simulate,
                    "acid_ka": None, # Titulante forte

                    "base_name": params.base_name,
                    "base_concentration": params.base_concentration,
                    "base_volume": params.base_volume,
                    "base_kb": params.base_kb,
                    "indicator_name": None
                }
            else:
                point_params_dict = {
                    "acid_name": params.acid_name,
                    "acid_concentration": params.acid_concentration,
                    "acid_volume": params.acid_volume,
                    "acid_ka": params.acid_ka,

                    "base_name": params.titrant_name,
                    "base_concentration": params.titrant_concentration,
                    "base_volume": actual_volume_to_simulate,
                    "base_kb": None, # Titulante forte
                    "indicator_name": None
                }

            try:
                current_point_simulation_params = AcidBaseSimulationParams.model_validate(point_params_dict)
            except Exception as e:
                 raise HTTPException(status_code=400, detail=f"Erro ao criar parâmetros para o ponto de titulação (vol={actual_volume_to_simulate:.2f}mL): {e}")

            current_ph = -1.0 # Default para caso de erro no cálculo do pH
            try:
                ph_result = self.acid_base_calculator.run_simulation(current_point_simulation_params)
                current_ph = ph_result.final_ph
                # Se ph_result.message existir e current_ph for -1.0, essa info pode ser útil, mas não é adicionada por ponto
            except HTTPException as e:
                raise HTTPException(status_code=400,
                                    detail=f"Erro ao calcular pH no volume {actual_volume_to_simulate:.2f}mL do titulante: {e.detail}")
            except Exception as e:
                raise HTTPException(status_code=500,
                                    detail=f"Erro inesperado ao calcular pH no volume {actual_volume_to_simulate:.2f}mL do titulante: {str(e)}")

            titration_curve_data.append(
                TitrationDataPoint(titrant_volume_added_ml=round(actual_volume_to_simulate, 3), ph=current_ph)
            )

            if actual_volume_to_simulate >= params.final_titrant_volume_ml:
                break

            current_titrant_vol_ml += params.volume_increment_ml
            iteration_count += 1
            if iteration_count >= max_points +10: # Salvaguarda contra loop infinito
                 # Log ou mensagem de que o loop foi interrompido pela salvaguarda
                 break

        return TitrationResult(
            titration_curve=titration_curve_data,
            parameters_used=params.model_dump(),
            message=f"Curva de titulação gerada com {len(titration_curve_data)} pontos." if titration_curve_data else "Nenhum ponto gerado para a curva.",
            equivalence_points_ml=None
        )
