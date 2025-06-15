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

# Testes adicionados para Sprint 1

def test_h2so4_with_naoh_neutral():
    # H2SO4 (0.05M) vs NaOH (0.1M) - Volumes iguais para neutralização
    # Mols H+ = 0.05 * V * 2 = 0.1 * V
    # Mols OH- = 0.1 * V * 1 = 0.1 * V
    params = AcidBaseSimulationParams(
        acid_name="H2SO4", acid_concentration=0.05, acid_volume=50,
        base_name="NaOH", base_concentration=0.1, base_volume=50,
        indicator_name="Fenolftaleína"
    )
    result = module.run_simulation(params)
    assert result.final_ph == 7.0
    assert result.status == "Neutra"
    assert result.parameters_used["acid_name"] == "H2SO4"
    assert result.parameters_used["base_name"] == "NaOH"

def test_hcl_with_ca_oh2_neutral():
    # HCl (0.1M) vs Ca(OH)2 (0.05M) - Volumes iguais para neutralização
    # Mols H+ = 0.1 * V * 1 = 0.1 * V
    # Mols OH- = 0.05 * V * 2 = 0.1 * V
    params = AcidBaseSimulationParams(
        acid_name="HCl", acid_concentration=0.1, acid_volume=50,
        base_name="Ca(OH)2", base_concentration=0.05, base_volume=50,
        indicator_name="Azul de Bromotimol"
    )
    result = module.run_simulation(params)
    assert result.final_ph == 7.0
    assert result.status == "Neutra"
    assert result.indicator_color == "Verde" # Azul de bromotimol em pH 7 é verde
    assert result.parameters_used["base_name"] == "Ca(OH)2"

def test_h2so4_with_ca_oh2_acidic():
    # H2SO4 (0.1M, 10mL) vs Ca(OH)2 (0.05M, 10mL)
    # Mols H+ = 0.1 * 0.01L * 2 = 0.002 mols
    # Mols OH- = 0.05 * 0.01L * 2 = 0.001 mols
    # Excesso H+ = 0.001 mols em 20mL (0.02L)
    # [H+] = 0.001 / 0.02 = 0.05 M -> pH = -log10(0.05) = 1.30
    params = AcidBaseSimulationParams(
        acid_name="H₂SO₄", acid_concentration=0.1, acid_volume=10,
        base_name="Ca(OH)₂", base_concentration=0.05, base_volume=10,
        indicator_name="Alaranjado de Metila"
    )
    result = module.run_simulation(params)
    assert abs(result.final_ph - 1.30) < 0.01
    assert result.status == "Ácida"
    assert result.indicator_color == "Vermelho" # Alaranjado de metila em pH 1.30 é Vermelho
    assert result.parameters_used["acid_name"] == "H₂SO₄"
    assert result.parameters_used["base_name"] == "Ca(OH)₂"


def test_methyl_red_indicator_colors():
    # Vermelho de Metila: pH < 4.4 (Vermelho), 4.4 <= pH <= 6.2 (Laranja), pH > 6.2 (Amarelo)

    # Teste para Vermelho (pH < 4.4)
    # Ex: HCl 0.01M, 50ml; NaOH 0.01M, 10ml -> Excesso H+ = 0.01 * (0.05-0.01) = 0.0004 mol
    # Vol total = 60ml = 0.06L. [H+] = 0.0004 / 0.06 = 0.00667 M. pH = -log10(0.00667) = 2.18
    params_red = AcidBaseSimulationParams(acid_concentration=0.01, acid_volume=50, base_concentration=0.01, base_volume=10, indicator_name="Vermelho de Metila")
    result_red = module.run_simulation(params_red) # pH ~2.18
    assert result_red.final_ph < 4.4
    assert result_red.indicator_color == "Vermelho"

    # Teste para Laranja (4.4 <= pH <= 6.2)
    # Ex: HCl 0.001M, 50ml; NaOH 0.001M, 48ml -> Excesso H+ = 0.001 * (0.05-0.048) = 0.000002 mol
    # Vol total = 98ml = 0.098L. [H+] = 0.000002 / 0.098 = 2.04e-5 M. pH = -log10(2.04e-5) = 4.69
    params_orange = AcidBaseSimulationParams(acid_concentration=0.001, acid_volume=50, base_concentration=0.001, base_volume=48, indicator_name="Vermelho de Metila")
    result_orange = module.run_simulation(params_orange) # pH ~4.69
    assert 4.4 <= result_orange.final_ph <= 6.2
    assert result_orange.indicator_color == "Laranja"

    # Teste para Amarelo (pH > 6.2)
    # Ex: HCl 0.1M, 50ml; NaOH 0.1M, 50ml -> pH = 7.0
    params_yellow_neutral = AcidBaseSimulationParams(acid_concentration=0.1, acid_volume=50, base_concentration=0.1, base_volume=50, indicator_name="Vermelho de Metila")
    result_yellow_neutral = module.run_simulation(params_yellow_neutral) # pH 7.0
    assert result_yellow_neutral.final_ph > 6.2
    assert result_yellow_neutral.indicator_color == "Amarelo"

    params_yellow_basic = AcidBaseSimulationParams(acid_concentration=0.1, acid_volume=25, base_concentration=0.1, base_volume=50, indicator_name="Vermelho de Metila")
    result_yellow_basic = module.run_simulation(params_yellow_basic) # pH ~12.52
    assert result_yellow_basic.final_ph > 6.2
    assert result_yellow_basic.indicator_color == "Amarelo"

def test_methyl_orange_indicator_colors():
    # Alaranjado de Metila: pH < 3.1 (Vermelho), 3.1 <= pH <= 4.4 (Laranja), pH > 4.4 (Amarelo)

    # Teste para Vermelho (pH < 3.1)
    # Ex: HCl 0.01M, 50ml (nenhuma base) -> [H+] = 0.01M. pH = 2
    params_red = AcidBaseSimulationParams(acid_concentration=0.01, acid_volume=50, base_concentration=0.001, base_volume=0, indicator_name="Alaranjado de Metila") # base_volume 0 para simplificar
    result_red = module.run_simulation(params_red) # pH = 2
    assert result_red.final_ph < 3.1
    assert result_red.indicator_color == "Vermelho"

    # Teste para Laranja (3.1 <= pH <= 4.4)
    # Ex: HCl 0.001M, 50ml; NaOH 0.001M, 30ml -> Excesso H+ = 0.001 * (0.05-0.03) = 0.00002 mol
    # Vol total = 80ml = 0.08L. [H+] = 0.00002 / 0.08 = 0.00025 M. pH = -log10(0.00025) = 3.60
    params_orange = AcidBaseSimulationParams(acid_concentration=0.001, acid_volume=50, base_concentration=0.001, base_volume=30, indicator_name="Alaranjado de Metila")
    result_orange = module.run_simulation(params_orange) # pH ~3.60
    assert 3.1 <= result_orange.final_ph <= 4.4
    assert result_orange.indicator_color == "Laranja"

    # Teste para Amarelo (pH > 4.4)
    # Ex: HCl 0.001M, 50ml; NaOH 0.001M, 48ml -> pH ~4.69 (calculado anteriormente)
    params_yellow = AcidBaseSimulationParams(acid_concentration=0.001, acid_volume=50, base_concentration=0.001, base_volume=48, indicator_name="Alaranjado de Metila")
    result_yellow = module.run_simulation(params_yellow) # pH ~4.69
    assert result_yellow.final_ph > 4.4
    assert result_yellow.indicator_color == "Amarelo"

    params_yellow_neutral = AcidBaseSimulationParams(acid_concentration=0.1, acid_volume=50, base_concentration=0.1, base_volume=50, indicator_name="Alaranjado de Metila")
    result_yellow_neutral = module.run_simulation(params_yellow_neutral) # pH 7.0
    assert result_yellow_neutral.final_ph > 4.4
    assert result_yellow_neutral.indicator_color == "Amarelo"

# Testes adicionados para Sprint 2 (Ácidos/Bases Fracos)

KA_CH3COOH = 1.8e-5
KB_NH3 = 1.8e-5

# Testes para Ácidos Fracos Puros
def test_weak_acid_ch3cooh_pure():
    params = AcidBaseSimulationParams(
        acid_name="CH3COOH", acid_concentration=0.1, acid_volume=100,
        acid_ka=KA_CH3COOH,
        base_name="Nenhuma", base_concentration=0, base_volume=0
    )
    result = module.run_simulation(params)
    assert abs(result.final_ph - 2.88) < 0.01 # pH ~2.875
    assert result.status == "Ácida"
    assert result.is_weak_acid_calculation is True
    assert result.ka_used == KA_CH3COOH
    assert result.is_weak_base_calculation is False
    assert result.kb_used is None

def test_weak_acid_zero_concentration():
    params = AcidBaseSimulationParams(
        acid_name="CH3COOH", acid_concentration=0, acid_volume=100,
        acid_ka=KA_CH3COOH,
        base_name="Nenhuma", base_concentration=0, base_volume=0
    )
    result = module.run_simulation(params)
    assert result.final_ph == 7.0
    assert result.status == "Neutra (água pura)"
    assert result.is_weak_acid_calculation is False # Não houve cálculo fraco efetivo com conc 0

# Testes para Bases Fracas Puras
def test_weak_base_nh3_pure():
    params = AcidBaseSimulationParams(
        base_name="NH3", base_concentration=0.1, base_volume=100,
        base_kb=KB_NH3,
        acid_name="Nenhum", acid_concentration=0, acid_volume=0
    )
    result = module.run_simulation(params)
    assert abs(result.final_ph - 11.12) < 0.01 # pH ~11.125
    assert result.status == "Básica"
    assert result.is_weak_base_calculation is True
    assert result.kb_used == KB_NH3
    assert result.is_weak_acid_calculation is False

def test_weak_base_zero_concentration():
    params = AcidBaseSimulationParams(
        base_name="NH3", base_concentration=0, base_volume=100,
        base_kb=KB_NH3,
        acid_name="Nenhum", acid_concentration=0, acid_volume=0
    )
    result = module.run_simulation(params)
    assert result.final_ph == 7.0
    assert result.status == "Neutra (água pura)"
    assert result.is_weak_base_calculation is False

# Testes de Titulação: Ácido Fraco (CH3COOH) com Base Forte (NaOH)
def test_titration_ch3cooh_naoh_half_equivalence():
    params = AcidBaseSimulationParams(
        acid_name="CH3COOH", acid_concentration=0.1, acid_volume=50, acid_ka=KA_CH3COOH,
        base_name="NaOH", base_concentration=0.1, base_volume=25 # Metade do volume para equivalência
    )
    result = module.run_simulation(params)
    assert abs(result.final_ph - 4.74) < 0.01 # pH = pKa
    assert result.status == "Ácida (Tampão HA/A⁻)"
    assert result.is_weak_acid_calculation is True
    assert result.ka_used == KA_CH3COOH
    assert result.is_weak_base_calculation is False

def test_titration_ch3cooh_naoh_equivalence_point():
    params = AcidBaseSimulationParams(
        acid_name="CH3COOH", acid_concentration=0.1, acid_volume=50, acid_ka=KA_CH3COOH,
        base_name="NaOH", base_concentration=0.1, base_volume=50 # Ponto de equivalência
    )
    result = module.run_simulation(params)
    assert abs(result.final_ph - 8.72) < 0.01
    assert result.status == "Básica (Hidrólise de A⁻)"
    assert result.is_weak_acid_calculation is True
    assert result.ka_used == KA_CH3COOH

def test_titration_ch3cooh_naoh_after_equivalence():
    params = AcidBaseSimulationParams(
        acid_name="CH3COOH", acid_concentration=0.1, acid_volume=50, acid_ka=KA_CH3COOH,
        base_name="NaOH", base_concentration=0.1, base_volume=75 # Excesso de NaOH
    )
    result = module.run_simulation(params)
    # Mols CH3COOH = 0.005. Mols NaOH = 0.0075. Excesso NaOH = 0.0025 mol. Vol total = 125ml.
    # [OH-]excess = 0.0025 / 0.125 = 0.02M. pOH = 1.70. pH = 12.30.
    assert abs(result.final_ph - 12.30) < 0.01
    assert result.status == "Básica (Excesso de OH⁻)"
    assert result.is_weak_acid_calculation is True # Ka foi usado para determinar o comportamento até P.E.
    assert result.ka_used == KA_CH3COOH


# Testes de Titulação: Base Fraca (NH3) com Ácido Forte (HCl)
def test_titration_nh3_hcl_half_equivalence():
    params = AcidBaseSimulationParams(
        base_name="NH3", base_concentration=0.1, base_volume=50, base_kb=KB_NH3,
        acid_name="HCl", acid_concentration=0.1, acid_volume=25 # Metade do volume para equivalência
    )
    result = module.run_simulation(params)
    assert abs(result.final_ph - 9.26) < 0.01 # pOH = pKb=4.74, pH = 14-4.74 = 9.26
    assert result.status == "Básica (Tampão B/BH⁺)"
    assert result.is_weak_base_calculation is True
    assert result.kb_used == KB_NH3

def test_titration_nh3_hcl_equivalence_point():
    params = AcidBaseSimulationParams(
        base_name="NH3", base_concentration=0.1, base_volume=50, base_kb=KB_NH3,
        acid_name="HCl", acid_concentration=0.1, acid_volume=50 # Ponto de equivalência
    )
    result = module.run_simulation(params)
    assert abs(result.final_ph - 5.28) < 0.01
    assert result.status == "Ácida (Hidrólise de BH⁺)"
    assert result.is_weak_base_calculation is True
    assert result.kb_used == KB_NH3

def test_titration_nh3_hcl_after_equivalence():
    params = AcidBaseSimulationParams(
        base_name="NH3", base_concentration=0.1, base_volume=50, base_kb=KB_NH3,
        acid_name="HCl", acid_concentration=0.1, acid_volume=75 # Excesso de HCl
    )
    result = module.run_simulation(params)
    # Mols NH3 = 0.005. Mols HCl = 0.0075. Excesso HCl = 0.0025 mol. Vol total = 125ml.
    # [H+]excess = 0.0025 / 0.125 = 0.02M. pH = 1.70.
    assert abs(result.final_ph - 1.70) < 0.01
    assert result.status == "Ácida (Excesso de H⁺)"
    assert result.is_weak_base_calculation is True # Kb foi usado
    assert result.kb_used == KB_NH3

# Teste para Ácido Fraco vs Base Fraca
def test_weak_acid_weak_base_mixture():
    params = AcidBaseSimulationParams(
        acid_name="CH3COOH", acid_concentration=0.1, acid_volume=50, acid_ka=KA_CH3COOH,
        base_name="NH3", base_concentration=0.1, base_volume=50, base_kb=KB_NH3
    )
    result = module.run_simulation(params)
    assert result.final_ph == -1.0 # Indicativo de não calculado/erro
    assert "não é suportado" in result.message
    assert result.status == "Indeterminado (WA vs WB)"
    assert result.is_weak_acid_calculation is True
    assert result.is_weak_base_calculation is True
    assert result.ka_used == KA_CH3COOH
    assert result.kb_used == KB_NH3

# Teste para Ka inválido
def test_invalid_ka_value():
    with pytest.raises(HTTPException) as exc_info:
        AcidBaseSimulationParams(
            acid_name="CH3COOH", acid_concentration=0.1, acid_volume=50, acid_ka=-1.0,
            base_name="NaOH", base_concentration=0.1, base_volume=25
        )
    assert exc_info.value.status_code == 422

def test_run_simulation_with_invalid_ka():
    pass
