import pytest
from backend.simulations.biology.mendelian_genetics_module import MendelianGeneticsModule
from backend.simulations.biology.models_mendelian_genetics import (
    MendelianCrossParams,
    GenotypeProportion,
    PhenotypeProportion,
    MendelianCrossResult
)
# No HTTPException import needed if we're testing Pydantic validation errors (ValueError)
# and the module's internal logic doesn't raise new HTTPErrors for these cases.

module = MendelianGeneticsModule()

def find_genotype_proportion(result: MendelianCrossResult, genotype: str) -> Optional[GenotypeProportion]:
    for gp in result.offspring_genotypes:
        if gp.genotype == genotype:
            return gp
    return None

def find_phenotype_proportion(result: MendelianCrossResult, description: str) -> Optional[PhenotypeProportion]:
    for pp in result.offspring_phenotypes:
        if pp.phenotype_description == description:
            return pp
    return None

# Test 1: Cruzamento Clássico (Aa x Aa)
def test_classic_monohybrid_cross_Aa_x_Aa():
    params = MendelianCrossParams(parent1_genotype="Aa", parent2_genotype="Aa", dominant_allele="A", recessive_allele="a")
    result = module.run_simulation(params)

    assert result is not None
    # Expected Punnett Square:
    #     A   a
    # A  AA  Aa
    # a  Aa  aa
    assert result.punnett_square == [["AA", "Aa"], ["Aa", "aa"]]

    # Genotypic proportions
    gp_AA = find_genotype_proportion(result, "AA")
    gp_Aa = find_genotype_proportion(result, "Aa")
    gp_aa = find_genotype_proportion(result, "aa")

    assert gp_AA and gp_AA.count == 1 and gp_AA.percentage == 25.0
    assert gp_Aa and gp_Aa.count == 2 and gp_Aa.percentage == 50.0
    assert gp_aa and gp_aa.count == 1 and gp_aa.percentage == 25.0
    assert len(result.offspring_genotypes) == 3

    # Phenotypic proportions
    pp_dominant = find_phenotype_proportion(result, "Fenótipo Dominante")
    pp_recessive = find_phenotype_proportion(result, "Fenótipo Recessivo")

    assert pp_dominant and pp_dominant.count == 3 and pp_dominant.percentage == 75.0
    assert pp_dominant.associated_genotypes == ["AA", "Aa"] # Assuming sorted
    assert pp_recessive and pp_recessive.count == 1 and pp_recessive.percentage == 25.0
    assert pp_recessive.associated_genotypes == ["aa"]
    assert len(result.offspring_phenotypes) == 2
    assert result.parameters_used == params # Check if stripped params are there if applicable.

# Test 2: Cruzamento Homozigoto Dominante x Homozigoto Recessivo (AA x aa)
def test_homozygous_dominant_x_recessive_AA_x_aa():
    params = MendelianCrossParams(parent1_genotype="AA", parent2_genotype="aa", dominant_allele="A", recessive_allele="a")
    result = module.run_simulation(params)

    assert result.punnett_square == [["Aa", "Aa"], ["Aa", "Aa"]]
    gp_Aa = find_genotype_proportion(result, "Aa")
    assert gp_Aa and gp_Aa.count == 4 and gp_Aa.percentage == 100.0
    assert len(result.offspring_genotypes) == 1

    pp_dominant = find_phenotype_proportion(result, "Fenótipo Dominante")
    assert pp_dominant and pp_dominant.count == 4 and pp_dominant.percentage == 100.0
    assert pp_dominant.associated_genotypes == ["Aa"]
    assert len(result.offspring_phenotypes) == 1
    assert result.parameters_used == params

# Test 3: Cruzamento Heterozigoto x Homozigoto Recessivo (Aa x aa)
def test_heterozygous_x_recessive_Aa_x_aa():
    params = MendelianCrossParams(parent1_genotype="Aa", parent2_genotype="aa", dominant_allele="A", recessive_allele="a")
    result = module.run_simulation(params)

    assert result.punnett_square == [["Aa", "Aa"], ["aa", "aa"]] # A from Aa with a, a from Aa with a

    gp_Aa = find_genotype_proportion(result, "Aa")
    gp_aa = find_genotype_proportion(result, "aa")
    assert gp_Aa and gp_Aa.count == 2 and gp_Aa.percentage == 50.0
    assert gp_aa and gp_aa.count == 2 and gp_aa.percentage == 50.0
    assert len(result.offspring_genotypes) == 2

    pp_dominant = find_phenotype_proportion(result, "Fenótipo Dominante")
    pp_recessive = find_phenotype_proportion(result, "Fenótipo Recessivo")
    assert pp_dominant and pp_dominant.count == 2 and pp_dominant.percentage == 50.0
    assert pp_dominant.associated_genotypes == ["Aa"]
    assert pp_recessive and pp_recessive.count == 2 and pp_recessive.percentage == 50.0
    assert pp_recessive.associated_genotypes == ["aa"]
    assert len(result.offspring_phenotypes) == 2
    assert result.parameters_used == params

# Test 4: Validação de Entrada (Pydantic)
def test_input_validation_pydantic():
    # Invalid genotype length/format
    with pytest.raises(ValueError, match="Genótipo 'A' inválido. Deve conter exatamente 2 caracteres alfabéticos."):
        MendelianCrossParams(parent1_genotype="A", parent2_genotype="Aa", dominant_allele="A", recessive_allele="a")
    with pytest.raises(ValueError, match="Genótipo 'Aaa' inválido. Deve conter exatamente 2 caracteres alfabéticos."):
        MendelianCrossParams(parent1_genotype="Aaa", parent2_genotype="Aa", dominant_allele="A", recessive_allele="a")
    with pytest.raises(ValueError, match="Genótipo 'A1' inválido. Deve conter exatamente 2 caracteres alfabéticos."):
        MendelianCrossParams(parent1_genotype="A1", parent2_genotype="Aa", dominant_allele="A", recessive_allele="a")

    # Alleles are the same
    with pytest.raises(ValueError, match="Alelos dominante e recessivo definidos não podem ser o mesmo caractere."):
        MendelianCrossParams(parent1_genotype="Aa", parent2_genotype="Aa", dominant_allele="A", recessive_allele="A")

    # Genotype characters not matching defined alleles
    with pytest.raises(ValueError, match="Alelo 'b' no genótipo 'Ab' não corresponde aos alelos definidos .*"):
        MendelianCrossParams(parent1_genotype="Ab", parent2_genotype="Aa", dominant_allele="A", recessive_allele="a")
    with pytest.raises(ValueError, match="Alelo 'B' no genótipo 'aB' não corresponde aos alelos definidos .*"):
        MendelianCrossParams(parent1_genotype="aa", parent2_genotype="aB", dominant_allele="a", recessive_allele="c") # dom='a', rec='c'

    # Invalid allele definition (e.g. not single char) - Pydantic Field validation
    with pytest.raises(ValueError, match="String should have at most 1 character"): # Pydantic's max_length message
        MendelianCrossParams(parent1_genotype="Aa", parent2_genotype="Aa", dominant_allele="AA", recessive_allele="a")
    with pytest.raises(ValueError, match="String should have at least 1 character"): # Pydantic's min_length message
        MendelianCrossParams(parent1_genotype="Aa", parent2_genotype="Aa", dominant_allele="", recessive_allele="a")

# Test 5: Alelos Diferentes (ex: Bb x Bb)
def test_different_alleles_Bb_x_Bb():
    dom_desc = "Pelagem Preta"
    rec_desc = "Pelagem Branca"
    params = MendelianCrossParams(
        parent1_genotype="Bb", parent2_genotype="Bb",
        dominant_allele="B", recessive_allele="b",
        dominant_phenotype_description=dom_desc, recessive_phenotype_description=rec_desc
    )
    result = module.run_simulation(params)

    assert result.punnett_square == [["BB", "Bb"], ["Bb", "bb"]]
    gp_BB = find_genotype_proportion(result, "BB")
    gp_Bb = find_genotype_proportion(result, "Bb")
    gp_bb = find_genotype_proportion(result, "bb")

    assert gp_BB and gp_BB.count == 1 and gp_BB.percentage == 25.0
    assert gp_Bb and gp_Bb.count == 2 and gp_Bb.percentage == 50.0
    assert gp_bb and gp_bb.count == 1 and gp_bb.percentage == 25.0

    pp_dominant = find_phenotype_proportion(result, dom_desc)
    pp_recessive = find_phenotype_proportion(result, rec_desc)
    assert pp_dominant and pp_dominant.count == 3 and pp_dominant.percentage == 75.0
    assert pp_dominant.associated_genotypes == ["BB", "Bb"]
    assert pp_recessive and pp_recessive.count == 1 and pp_recessive.percentage == 25.0
    assert pp_recessive.associated_genotypes == ["bb"]
    assert result.parameters_used.dominant_phenotype_description == dom_desc
    assert result.parameters_used.recessive_phenotype_description == rec_desc


# Test 6: Normalização de Genótipo da Prole (e aceitação de genótipo de pai 'aA')
def test_offspring_normalization_and_parent_input_aA():
    # Pydantic model for MendelianCrossParams validates that parent genotypes consist of defined alleles.
    # So, "aA" is valid if dominant_allele="A" and recessive_allele="a".
    params = MendelianCrossParams(parent1_genotype="aA", parent2_genotype="aA", dominant_allele="A", recessive_allele="a")
    result = module.run_simulation(params)

    # Parent alleles should be extracted correctly: ['a', 'A'] for both
    assert result.parent1_alleles == ['a', 'A']
    assert result.parent2_alleles == ['a', 'A']

    # Punnett square should show normalized offspring genotypes
    #     a   A
    # a  aa  Aa  (A is dominant, so Aa, not aA)
    # A  Aa  AA
    # The order of alleles in the Punnett square depends on the loop in run_simulation.
    # p1_alleles_list[i] and p2_alleles_list[j]
    # If parent1_alleles is ['a', 'A'] and parent2_alleles is ['a', 'A']
    # i=0, j=0: 'a', 'a' -> "aa"
    # i=0, j=1: 'a', 'A' -> "Aa" (normalized)
    # i=1, j=0: 'A', 'a' -> "Aa" (normalized)
    # i=1, j=1: 'A', 'A' -> "AA"
    expected_punnett = [
        ["aa", "Aa"],  # row for parent1_allele 'a'
        ["Aa", "AA"]   # row for parent1_allele 'A'
    ]
    assert result.punnett_square == expected_punnett, f"Punnett square mismatch. Got {result.punnett_square}"

    gp_AA = find_genotype_proportion(result, "AA")
    gp_Aa = find_genotype_proportion(result, "Aa")
    gp_aa = find_genotype_proportion(result, "aa")

    assert gp_AA and gp_AA.percentage == 25.0
    assert gp_Aa and gp_Aa.percentage == 50.0
    assert gp_aa and gp_aa.percentage == 25.0

# Test 7: parameters_used no resultado
def test_parameters_used_content():
    params_in = MendelianCrossParams(
        parent1_genotype=" Gg ", # Test stripping if model does it, current model does not strip genotypes
        parent2_genotype="gg",
        dominant_allele="G",
        recessive_allele="g",
        dominant_phenotype_description="Verde ", # Test stripping of descriptions
        recessive_phenotype_description=" Amarelo "
    )
    # The current Pydantic model for MendelianCrossParams does not strip these fields by default.
    # The module's run_simulation method does strip dominant_allele and recessive_allele from params.
    # Let's test with non-stripped inputs to see what parameters_used reflects.

    result = module.run_simulation(params_in)

    # The module updates params internally for dom/rec_allele based on stripped values.
    # So parameters_used should reflect these stripped values.
    # Genotypes and phenotype descriptions are used as is from the input `params_in` object for logic,
    # but the `updated_params.model_copy(update={...})` in the module only updates dom/rec alleles.

    # The `updated_params` in the module is created from `params.model_copy(deep=True)`
    # and then `dominant_allele` and `recessive_allele` fields are updated on this copy.
    # So, `result.parameters_used` should be identical to `params_in` for genotype and phenotype descriptions,
    # and match the stripped versions for dominant/recessive alleles.

    assert result.parameters_used.parent1_genotype == " Gg " # Not stripped by model or module logic for this field
    assert result.parameters_used.parent2_genotype == "gg"
    assert result.parameters_used.dominant_allele == "G" # Stripped by module logic before being put in updated_params
    assert result.parameters_used.recessive_allele == "g" # Stripped
    assert result.parameters_used.dominant_phenotype_description == "Verde " # Not stripped by model or module logic
    assert result.parameters_used.recessive_phenotype_description == " Amarelo "

    # If the model itself did stripping for all relevant fields via a validator, that would be cleaner.
    # For now, this test verifies current behavior.
    # Example: If MendelianCrossParams had a validator that stripped parentX_genotype:
    # params_validated = MendelianCrossParams(...)
    # assert params_validated.parent1_genotype == "Gg" (stripped)
    # And then result.parameters_used would also show "Gg".
    # Current model validators only check format, not strip these specific fields.

# Test with all recessive parents
def test_all_recessive_parents_aa_x_aa():
    params = MendelianCrossParams(parent1_genotype="aa", parent2_genotype="aa", dominant_allele="A", recessive_allele="a")
    result = module.run_simulation(params)

    assert result.punnett_square == [["aa", "aa"], ["aa", "aa"]]
    gp_aa = find_genotype_proportion(result, "aa")
    assert gp_aa and gp_aa.count == 4 and gp_aa.percentage == 100.0
    assert len(result.offspring_genotypes) == 1

    pp_recessive = find_phenotype_proportion(result, "Fenótipo Recessivo")
    assert pp_recessive and pp_recessive.count == 4 and pp_recessive.percentage == 100.0
    assert pp_recessive.associated_genotypes == ["aa"]
    assert len(result.offspring_phenotypes) == 1
    assert result.parameters_used == params

# Test with one parent homozygous dominant, other heterozygous (AA x Aa)
def test_homozygous_dominant_x_heterozygous_AA_x_Aa():
    params = MendelianCrossParams(parent1_genotype="AA", parent2_genotype="Aa", dominant_allele="A", recessive_allele="a")
    result = module.run_simulation(params)

    # Punnett:
    #     A   a
    # A  AA  Aa
    # A  AA  Aa
    assert result.punnett_square == [["AA", "Aa"], ["AA", "Aa"]]

    gp_AA = find_genotype_proportion(result, "AA")
    gp_Aa = find_genotype_proportion(result, "Aa")
    assert gp_AA and gp_AA.count == 2 and gp_AA.percentage == 50.0
    assert gp_Aa and gp_Aa.count == 2 and gp_Aa.percentage == 50.0
    assert len(result.offspring_genotypes) == 2

    pp_dominant = find_phenotype_proportion(result, "Fenótipo Dominante")
    assert pp_dominant and pp_dominant.count == 4 and pp_dominant.percentage == 100.0
    assert pp_dominant.associated_genotypes == ["AA", "Aa"] # Assuming sorted
    assert len(result.offspring_phenotypes) == 1
    assert result.parameters_used == params
