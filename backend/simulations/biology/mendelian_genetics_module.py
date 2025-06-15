from typing import List, Optional, Type, Dict, Any
from collections import Counter
from fastapi import HTTPException
from pydantic import BaseModel # Required for Type hints like Type[BaseModel]

from backend.simulations.base_simulation import SimulationModule
from .models_mendelian_genetics import (
    MendelianCrossParams,
    GenotypeProportion,
    PhenotypeProportion,
    MendelianCrossResult
)

class MendelianGeneticsModule(SimulationModule):

    def get_name(self) -> str:
        return "mendelian-genetics"

    def get_display_name(self) -> str:
        return "Genética Mendeliana"

    def get_category(self) -> str:
        return "Biology"

    def get_description(self) -> str:
        return "Simula cruzamentos genéticos Mendelianos e calcula proporções genotípicas e fenotípicas."

    def get_parameter_schema(self) -> Type[MendelianCrossParams]:
        return MendelianCrossParams

    def get_result_schema(self) -> Type[MendelianCrossResult]:
        return MendelianCrossResult

    def run_simulation(self, params: MendelianCrossParams) -> MendelianCrossResult:
        # Logic moved from perform_mendelian_cross_simulation in main.py

        # Pydantic models in models_mendelian_genetics.py now handle several initial validations.
        # The explicit checks here for allele characters and their difference are now covered by
        # Pydantic validators in MendelianCrossParams.
        # However, the core logic of allele extraction and Punnett square generation remains.

        defined_dom_allele = params.dominant_allele.strip() # strip() is good practice, though Field might handle it.
        defined_rec_allele = params.recessive_allele.strip()

        # These initial validations are now largely handled by Pydantic model validators.
        # Re-checking them here would be redundant if Pydantic validation is guaranteed to run first.
        # For example, `dominant_allele` and `recessive_allele` length and their difference.
        # if not defined_dom_allele or not defined_rec_allele:
        #     raise HTTPException(status_code=400, detail="Caracteres para alelos dominante e recessivo não podem ser vazios.")
        # if len(defined_dom_allele) != 1 or len(defined_rec_allele) != 1:
        #     raise HTTPException(status_code=400, detail="Alelos dominante e recessivo devem ser caracteres únicos.")
        # if defined_dom_allele == defined_rec_allele: # BUG-004 in original, now in Pydantic model
        #      raise HTTPException(status_code=400, detail="Alelos dominante e recessivo definidos não podem ser o mesmo caractere.")

        dom_allele = defined_dom_allele
        rec_allele = defined_rec_allele

        # The Pydantic model now also validates that genotype characters match defined alleles.
        # The `validate_and_get_alleles` function can be simplified or its validation role reduced
        # if Pydantic handles all format and character set checks.
        # However, its role in splitting alleles is still useful.
        def validate_and_get_alleles(genotype_str: str, dA: str, rA: str) -> List[str]:
            # Basic format validation (length 2, isalpha) is now in Pydantic.
            # Matching characters against dA, rA is also in Pydantic.
            # This function primarily just splits the genotype string now.
            # if len(genotype_str) != 2: # Covered by Pydantic
            #     raise HTTPException(status_code=400, detail=f"Genótipo '{genotype_str}' inválido. Deve ter 2 alelos.")

            alleles_from_genotype = []
            for char_allele in genotype_str:
                # if char_allele == dA: # Covered by Pydantic
                #     alleles_from_genotype.append(dA)
                # elif char_allele == rA: # Covered by Pydantic
                #     alleles_from_genotype.append(rA)
                # else: # Covered by Pydantic
                #     raise HTTPException(status_code=400, detail=f"Alelo '{char_allele}' no genótipo '{genotype_str}' não corresponde...")
                alleles_from_genotype.append(char_allele) # Assume Pydantic validated characters
            return alleles_from_genotype

        p1_alleles_list = validate_and_get_alleles(params.parent1_genotype, dom_allele, rec_allele)
        p2_alleles_list = validate_and_get_alleles(params.parent2_genotype, dom_allele, rec_allele)

        punnett_square_genotypes: List[List[str]] = [["", ""], ["", ""]]
        prole_genotypes_list: List[str] = []

        for i in range(2):
            for j in range(2):
                allele1 = p1_alleles_list[i]
                allele2 = p2_alleles_list[j]

                if (allele1 == dom_allele and allele2 == rec_allele):
                    offspring_g = dom_allele + rec_allele
                elif (allele1 == rec_allele and allele2 == dom_allele):
                    offspring_g = dom_allele + rec_allele # BUG-001 & BUG-002 (Normalization)
                else:
                    offspring_g = allele1 + allele2

                punnett_square_genotypes[i][j] = offspring_g
                prole_genotypes_list.append(offspring_g)

        genotype_counts = Counter(prole_genotypes_list)
        total_offspring = len(prole_genotypes_list)
        offspring_genotype_proportions: List[GenotypeProportion] = []

        def sort_key_genotype(g_str):
            if g_str == dom_allele + dom_allele: return 0
            if g_str == dom_allele + rec_allele: return 1
            if g_str == rec_allele + rec_allele: return 2
            return 3

        sorted_genotypes_keys = sorted(genotype_counts.keys(), key=sort_key_genotype)

        for genotype_key in sorted_genotypes_keys:
            count = genotype_counts[genotype_key]
            offspring_genotype_proportions.append(GenotypeProportion(
                genotype=genotype_key, count=count, fraction=f"{count}/{total_offspring}",
                percentage=round((count / total_offspring) * 100, 2)
            ))

        phenotype_counts = Counter()
        for g_obj in offspring_genotype_proportions:
            genotype_str = g_obj.genotype
            if dom_allele in genotype_str: # BUG-003 (Phenotype determination) - this logic is correct
                phenotype_counts[params.dominant_phenotype_description] += g_obj.count
            else:
                phenotype_counts[params.recessive_phenotype_description] += g_obj.count

        offspring_phenotype_proportions: List[PhenotypeProportion] = []
        phenotype_order = {params.dominant_phenotype_description: 0, params.recessive_phenotype_description: 1}
        sorted_phenotypes_desc_keys = sorted(phenotype_counts.keys(), key=lambda p_desc: phenotype_order.get(p_desc, 99))

        for phenotype_d_key in sorted_phenotypes_desc_keys:
            count = phenotype_counts[phenotype_d_key]
            if count > 0:
                associated_genotypes_for_pheno = []
                if phenotype_d_key == params.dominant_phenotype_description:
                    associated_genotypes_for_pheno = [g for g in genotype_counts.keys() if dom_allele in g]
                else:
                    associated_genotypes_for_pheno = [g for g in genotype_counts.keys() if g == rec_allele + rec_allele]

                offspring_phenotype_proportions.append(PhenotypeProportion(
                    phenotype_description=phenotype_d_key, count=count, fraction=f"{count}/{total_offspring}",
                    percentage=round((count / total_offspring) * 100, 2),
                    associated_genotypes=sorted(list(set(associated_genotypes_for_pheno)), key=sort_key_genotype)
                ))

        # TASK-001 (model_copy for Pydantic V2)
        # The parameters_used should reflect the actual alleles used in simulation,
        # which are params.dominant_allele and params.recessive_allele after initial stripping.
        # No need for model_copy here if params are not modified internally in a way that needs to be reflected.
        # The original code did `updated_params = params.model_copy(update={"dominant_allele": dom_allele, "recessive_allele": rec_allele})`
        # This is useful if `strip()` modified them and you want the stripped version in parameters_used.
        # Since dom_allele and rec_allele are derived from params after strip(), this is good practice.
        updated_params = params.model_copy(deep=True) # Ensure a deep copy if there are nested models, though not strictly needed here.
        updated_params.dominant_allele = dom_allele
        updated_params.recessive_allele = rec_allele
        # The parent genotypes are taken as is.

        return MendelianCrossResult(
            parent1_alleles=p1_alleles_list,
            parent2_alleles=p2_alleles_list,
            punnett_square=punnett_square_genotypes,
            offspring_genotypes=offspring_genotype_proportions,
            offspring_phenotypes=offspring_phenotype_proportions,
            parameters_used=updated_params # Pass the potentially updated (stripped alleles) params
        )
