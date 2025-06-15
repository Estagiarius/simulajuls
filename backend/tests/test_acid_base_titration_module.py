import pytest
from fastapi import HTTPException
from backend.simulations.chemistry.acid_base_titration_module import AcidBaseTitrationModule
from backend.simulations.chemistry.models_acid_base import TitrationParams, TitrationDataPoint, AcidBaseSimulationParams # AcidBaseSimulationParams is implicitly used by TitrationParams

# Instanciar o módulo uma vez para ser usado nos testes
titration_module = AcidBaseTitrationModule()
KA_CH3COOH = 1.8e-5
KB_NH3 = 1.8e-5

# Helper para verificar um ponto específico na curva
def get_ph_at_volume(curve: list[TitrationDataPoint], volume: float, volume_tolerance: float = 1e-6) -> float | None:
    for point in curve:
        if abs(point.titrant_volume_added_ml - volume) < volume_tolerance:
            return point.ph
    return None

# Testes para Titulação Ácido Forte com Base Forte
def test_titration_strong_acid_strong_base():
    params = TitrationParams(
        # Titulado: HCl 0.1M, 50mL
        acid_name="HCl", acid_concentration=0.1, acid_volume=50,
        base_name=None, # Explicitamente nulo para titulado ácido
        base_concentration=0, base_volume=0, # Garantir que não haja base no titulado
        # Titulante: NaOH 0.1M
        titrant_is_acid=False,
        titrant_name="NaOH",
        titrant_concentration=0.1,
        # Parâmetros da titulação
        initial_titrant_volume_ml=0.0,
        final_titrant_volume_ml=100.0,
        volume_increment_ml=1.0
    )
    result = titration_module.run_simulation(params)

    assert len(result.titration_curve) > 0
    assert result.parameters_used["acid_name"] == "HCl"

    # pH inicial (HCl 0.1M)
    ph_initial = get_ph_at_volume(result.titration_curve, 0.0)
    assert ph_initial is not None and abs(ph_initial - 1.0) < 0.01

    # Ponto de equivalência (50mL NaOH)
    ph_equivalence = get_ph_at_volume(result.titration_curve, 50.0)
    assert ph_equivalence is not None and abs(ph_equivalence - 7.0) < 0.01

    # Após P.E. (ex: 75mL NaOH) -> Excesso 0.0025 mol OH- em 125mL -> [OH-]=0.02M -> pOH=1.7 -> pH=12.3
    ph_after_equivalence = get_ph_at_volume(result.titration_curve, 75.0)
    assert ph_after_equivalence is not None and abs(ph_after_equivalence - 12.30) < 0.01

    # Verificar que o último ponto é o final_titrant_volume_ml
    last_point_vol = result.titration_curve[-1].titrant_volume_added_ml
    # A verificação exata do último ponto depende da lógica de incremento e parada
    # Se o último incremento ultrapassar final_titrant_volume_ml, o último ponto será exatamente final_titrant_volume_ml
    assert abs(last_point_vol - params.final_titrant_volume_ml) < 1e-6


# Testes para Titulação Ácido Fraco (CH3COOH) com Base Forte (NaOH)
def test_titration_weak_acid_strong_base():
    params = TitrationParams(
        # Titulado: CH3COOH 0.1M, 50mL, Ka=1.8e-5
        acid_name="CH3COOH", acid_concentration=0.1, acid_volume=50, acid_ka=KA_CH3COOH,
        base_name=None, base_concentration=0, base_volume=0,
        # Titulante: NaOH 0.1M
        titrant_is_acid=False,
        titrant_name="NaOH",
        titrant_concentration=0.1,
        # Parâmetros da titulação
        initial_titrant_volume_ml=0.0,
        final_titrant_volume_ml=100.0,
        volume_increment_ml=1.0
    )
    result = titration_module.run_simulation(params)

    assert len(result.titration_curve) > 0
    assert result.parameters_used["acid_ka"] == KA_CH3COOH

    # pH inicial (CH3COOH 0.1M)
    ph_initial = get_ph_at_volume(result.titration_curve, 0.0)
    assert ph_initial is not None and abs(ph_initial - 2.88) < 0.01

    # Meio da titulação (25mL NaOH) -> pH = pKa
    ph_half_equivalence = get_ph_at_volume(result.titration_curve, 25.0)
    assert ph_half_equivalence is not None and abs(ph_half_equivalence - 4.74) < 0.01 # pKa = -log10(1.8e-5) = 4.7447

    # Ponto de equivalência (50mL NaOH) -> Hidrólise de A-
    ph_equivalence = get_ph_at_volume(result.titration_curve, 50.0)
    assert ph_equivalence is not None and abs(ph_equivalence - 8.72) < 0.01

    # Após P.E. (ex: 75mL NaOH) -> pH determinado pelo excesso de NaOH
    ph_after_equivalence = get_ph_at_volume(result.titration_curve, 75.0)
    assert ph_after_equivalence is not None and abs(ph_after_equivalence - 12.30) < 0.01


# Testes para Titulação Base Fraca (NH3) com Ácido Forte (HCl)
def test_titration_weak_base_strong_acid():
    params = TitrationParams(
        # Titulado: NH3 0.1M, 50mL, Kb=1.8e-5
        base_name="NH3", base_concentration=0.1, base_volume=50, base_kb=KB_NH3,
        acid_name=None, acid_concentration=0, acid_volume=0,
        # Titulante: HCl 0.1M
        titrant_is_acid=True,
        titrant_name="HCl",
        titrant_concentration=0.1,
        # Parâmetros da titulação
        initial_titrant_volume_ml=0.0,
        final_titrant_volume_ml=100.0,
        volume_increment_ml=1.0
    )
    result = titration_module.run_simulation(params)

    assert len(result.titration_curve) > 0
    assert result.parameters_used["base_kb"] == KB_NH3

    # pH inicial (NH3 0.1M)
    ph_initial = get_ph_at_volume(result.titration_curve, 0.0)
    assert ph_initial is not None and abs(ph_initial - 11.12) < 0.01

    # Meio da titulação (25mL HCl) -> pOH = pKb => pH = 14 - pKb
    ph_half_equivalence = get_ph_at_volume(result.titration_curve, 25.0)
    assert ph_half_equivalence is not None and abs(ph_half_equivalence - 9.26) < 0.01 # 14 - 4.7447 = 9.2553

    # Ponto de equivalência (50mL HCl) -> Hidrólise de BH+
    ph_equivalence = get_ph_at_volume(result.titration_curve, 50.0)
    assert ph_equivalence is not None and abs(ph_equivalence - 5.28) < 0.01

    # Após P.E. (ex: 75mL HCl) -> pH determinado pelo excesso de HCl
    # Excesso 0.0025 mol H+ em 125mL -> [H+]=0.02M -> pH=1.7
    ph_after_equivalence = get_ph_at_volume(result.titration_curve, 75.0)
    assert ph_after_equivalence is not None and abs(ph_after_equivalence - 1.70) < 0.01

# Testes de Validação de Parâmetros
def test_titration_invalid_volume_increment():
    with pytest.raises(HTTPException) as exc_info:
        params = TitrationParams(
            acid_name="HCl", acid_concentration=0.1, acid_volume=50,
            base_name=None, base_concentration=0, base_volume=0,
            titrant_is_acid=False, titrant_name="NaOH", titrant_concentration=0.1,
            initial_titrant_volume_ml=0.0, final_titrant_volume_ml=10.0, volume_increment_ml=0
        )
        titration_module.run_simulation(params)
    assert exc_info.value.status_code == 400
    assert "incremento de volume deve ser positivo" in exc_info.value.detail

def test_titration_final_volume_less_than_initial():
    with pytest.raises(HTTPException) as exc_info:
        params = TitrationParams(
            acid_name="HCl", acid_concentration=0.1, acid_volume=50,
            base_name=None, base_concentration=0, base_volume=0,
            titrant_is_acid=False, titrant_name="NaOH", titrant_concentration=0.1,
            initial_titrant_volume_ml=10.0, final_titrant_volume_ml=5.0, volume_increment_ml=1.0
        )
        titration_module.run_simulation(params)
    assert exc_info.value.status_code == 400
    assert "volume final do titulante deve ser maior ou igual" in exc_info.value.detail

def test_titration_too_many_points():
    with pytest.raises(HTTPException) as exc_info:
        params = TitrationParams(
            acid_name="HCl", acid_concentration=0.1, acid_volume=50,
            base_name=None, base_concentration=0, base_volume=0,
            titrant_is_acid=False, titrant_name="NaOH", titrant_concentration=0.1,
            initial_titrant_volume_ml=0.0, final_titrant_volume_ml=100.0, volume_increment_ml=0.01
        )
        # O limite é 2000. (100 - 0) / 0.01 + 1 = 10001 pontos.
        titration_module.run_simulation(params)
    assert exc_info.value.status_code == 400
    assert "excede o limite" in exc_info.value.detail

# Teste de Caso Limite: Um Único Ponto
def test_titration_single_point():
    params = TitrationParams(
        acid_name="HCl", acid_concentration=0.1, acid_volume=50,
        base_name=None, base_concentration=0, base_volume=0,
        titrant_is_acid=False, titrant_name="NaOH", titrant_concentration=0.1,
        initial_titrant_volume_ml=10.0, final_titrant_volume_ml=10.0, volume_increment_ml=1.0
    )
    result = titration_module.run_simulation(params)
    assert len(result.titration_curve) == 1
    assert abs(result.titration_curve[0].titrant_volume_added_ml - 10.0) < 1e-6
    # pH para HCl 0.1M 50mL + NaOH 0.1M 10mL:
    # Mols H+ = 0.005. Mols OH- = 0.001. Excesso H+ = 0.004. Vol total = 60mL.
    # [H+] = 0.004 / 0.06 = 0.0666... pH = 1.18
    assert abs(result.titration_curve[0].ph - 1.18) < 0.01
