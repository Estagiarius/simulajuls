import pytest
from fastapi import HTTPException # Para testar exceções esperadas
from backend.simulations.chemistry.acid_base_module import AcidBaseModule
from backend.simulations.chemistry.models_acid_base import AcidBaseSimulationParams

# Instanciar o módulo uma vez para ser usado nos testes
module = AcidBaseModule()

def test_acid_base_neutral_simulation():
    params = AcidBaseSimulationParams(
        acid_concentration=0.1, acid_volume=50,
        base_concentration=0.1, base_volume=50,
        indicator_name="Fenolftaleína"
    )
    result = module.run_simulation(params)
    assert result.final_ph == 7.0
    assert result.status == "Neutra"
    assert result.indicator_color == "Incolor"
    assert result.parameters_used["acid_concentration"] == 0.1

def test_acid_base_acidic_simulation():
    params = AcidBaseSimulationParams(
        acid_concentration=0.1, acid_volume=50,
        base_concentration=0.1, base_volume=25,
        indicator_name="Azul de Bromotimol"
    )
    result = module.run_simulation(params)
    assert result.final_ph < 7.0
    assert result.status == "Ácida"
    assert result.indicator_color == "Amarelo"
    # pH esperado para 0.0025 mol H+ em 75ml -> [H+] = 0.0025 / 0.075 = 0.0333... M -> pH ~ 1.48
    # Errata no comentário do prompt original: 0.005 mol H+ iniciais, 0.0025 mol OH- -> 0.0025 mol H+ em excesso
    assert abs(result.final_ph - 1.48) < 0.01 # Comparar com tolerância

def test_acid_base_basic_simulation():
    params = AcidBaseSimulationParams(
        acid_concentration=0.1, acid_volume=25,
        base_concentration=0.1, base_volume=50,
        indicator_name="Fenolftaleína"
    )
    result = module.run_simulation(params)
    assert result.final_ph > 7.0
    assert result.status == "Básica"
    # pH esperado para 0.0025 mol OH- em 75ml -> [OH-] = 0.0025 / 0.075 = 0.0333... M -> pOH ~ 1.48 -> pH ~ 12.52
    assert abs(result.final_ph - 12.52) < 0.01
    assert result.indicator_color in ["Rosa claro/Róseo", "Carmim/Magenta"] # pH > 8.2

def test_acid_base_bromothymol_blue_various_ph():
    # Teste ácido
    params_acid = AcidBaseSimulationParams(acid_concentration=0.1, acid_volume=60, base_concentration=0.1, base_volume=10, indicator_name="Azul de Bromotimol")
    result_acid = module.run_simulation(params_acid)
    assert result_acid.indicator_color == "Amarelo" # pH < 6.0

    # Teste neutro/levemente básico para verde
    params_neutral = AcidBaseSimulationParams(acid_concentration=0.1, acid_volume=50, base_concentration=0.1, base_volume=50, indicator_name="Azul de Bromotimol")
    result_neutral = module.run_simulation(params_neutral)
    assert result_neutral.indicator_color == "Verde" # pH 6.0 - 7.6

    # Teste básico para azul
    params_basic = AcidBaseSimulationParams(acid_concentration=0.1, acid_volume=10, base_concentration=0.1, base_volume=60, indicator_name="Azul de Bromotimol")
    result_basic = module.run_simulation(params_basic)
    assert result_basic.indicator_color == "Azul" # pH > 7.6

def test_acid_base_invalid_input_concentration():
    with pytest.raises(HTTPException) as exc_info:
        params = AcidBaseSimulationParams(
            acid_concentration=0, acid_volume=50, # Concentração inválida
            base_concentration=0.1, base_volume=50
        )
        # A validação do Pydantic Field(gt=0) deve pegar isso antes do run_simulation,
        # mas se o run_simulation for chamado com um objeto já criado com valor 0,
        # a checagem interna do run_simulation deve pegar.
        # Para este teste, assumimos que o objeto params pode ser criado com 0,
        # e testamos a lógica interna do run_simulation.
        # Se os Fields gt=0 são estritamente aplicados na criação do AcidBaseSimulationParams,
        # este teste precisaria ser adaptado para testar a validação do Pydantic.
        # No entanto, a duplicata de validação no run_simulation é o que está sendo testado aqui.
        module.run_simulation(params)
    assert exc_info.value.status_code == 400
    assert "Concentrações e volumes devem ser positivos" in exc_info.value.detail

def test_acid_base_invalid_input_volume():
    with pytest.raises(HTTPException) as exc_info:
        params = AcidBaseSimulationParams(
            acid_concentration=0.1, acid_volume=50,
            base_concentration=0.1, base_volume=0 # Volume inválido
        )
        module.run_simulation(params)
    assert exc_info.value.status_code == 400
    assert "Concentrações e volumes devem ser positivos" in exc_info.value.detail

def test_acid_base_no_indicator():
    params = AcidBaseSimulationParams(
        acid_concentration=0.1, acid_volume=50,
        base_concentration=0.1, base_volume=25,
        indicator_name=None # Sem indicador
    )
    result = module.run_simulation(params)
    assert result.indicator_color is None

def test_acid_base_unknown_indicator():
    params = AcidBaseSimulationParams(
        acid_concentration=0.1, acid_volume=50,
        base_concentration=0.1, base_volume=25,
        indicator_name="Vermelho Desconhecido"
    )
    result = module.run_simulation(params)
    assert result.indicator_color == "Indicador não reconhecido"
