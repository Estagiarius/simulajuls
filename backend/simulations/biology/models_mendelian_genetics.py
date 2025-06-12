from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field, field_validator, model_validator
from backend.simulations.base_simulation import BaseSimulationParams, BaseSimulationResult

class MendelianCrossParams(BaseSimulationParams):
    parent1_genotype: str = Field(..., description="Genótipo do progenitor 1 (ex: 'AA', 'Aa', 'aa')")
    parent2_genotype: str = Field(..., description="Genótipo do progenitor 2 (ex: 'AA', 'Aa', 'aa')")
    dominant_allele: str = Field('A', min_length=1, max_length=1, description="Caractere do alelo dominante (ex: 'A')")
    recessive_allele: str = Field('a', min_length=1, max_length=1, description="Caractere do alelo recessivo (ex: 'a')")
    dominant_phenotype_description: Optional[str] = Field("Fenótipo Dominante", description="Descrição do fenótipo dominante")
    recessive_phenotype_description: Optional[str] = Field("Fenótipo Recessivo", description="Descrição do fenótipo recessivo")

    @field_validator('parent1_genotype', 'parent2_genotype')
    @classmethod
    def validate_genotype_format(cls, v: str) -> str:
        if not v.isalpha() or len(v) != 2:
            raise ValueError(f"Genótipo '{v}' inválido. Deve conter exatamente 2 caracteres alfabéticos.")
        # Further validation (e.g., ensuring alleles match dominant/recessive definitions)
        # will be done inside the simulation logic, as it requires context of other fields.
        return v

    @model_validator(mode='after')
    def check_alleles_differ(self) -> 'MendelianCrossParams':
        if self.dominant_allele == self.recessive_allele:
            raise ValueError("Alelos dominante e recessivo definidos não podem ser o mesmo caractere.")
        # Check if genotype alleles are composed of the defined dominant/recessive alleles
        # This is complex here as it requires parsing genotypes based on allele definitions.
        # The simulation logic in perform_mendelian_cross_simulation already handles this robustly.
        # Adding partial validation here could be redundant or conflict.
        # For now, basic format is validated by field_validator, specific allele matching is in the module.
        return self

    @model_validator(mode='after')
    def check_genotypes_match_alleles(self) -> 'MendelianCrossParams':
        valid_chars = {self.dominant_allele, self.recessive_allele}
        for char_allele in self.parent1_genotype:
            if char_allele not in valid_chars:
                raise ValueError(f"Alelo '{char_allele}' no genótipo '{self.parent1_genotype}' não corresponde aos alelos definidos ('{self.dominant_allele}' ou '{self.recessive_allele}').")
        for char_allele in self.parent2_genotype:
            if char_allele not in valid_chars:
                raise ValueError(f"Alelo '{char_allele}' no genótipo '{self.parent2_genotype}' não corresponde aos alelos definidos ('{self.dominant_allele}' ou '{self.recessive_allele}').")
        return self


class GenotypeProportion(BaseModel):
    genotype: str
    count: int
    fraction: str
    percentage: float

class PhenotypeProportion(BaseModel):
    phenotype_description: str
    count: int
    fraction: str
    percentage: float
    associated_genotypes: List[str]

class MendelianCrossResult(BaseSimulationResult):
    parent1_alleles: List[str]
    parent2_alleles: List[str]
    punnett_square: List[List[str]]
    offspring_genotypes: List[GenotypeProportion]
    offspring_phenotypes: List[PhenotypeProportion]
    parameters_used: MendelianCrossParams # type: ignore[assignment]
    # As per BaseSimulationResult, parameters_used is Dict[str, Any].
    # Pydantic v2 handles the assignment of a model instance by calling model_dump() if needed.
    # If strict typing without Pydantic's implicit conversion is required, this could be:
    # parameters_used: Dict[str, Any]
    # And in the module: parameters_used=updated_params.model_dump()
    # For now, direct assignment is fine with Pydantic v2.

    class Config:
        # For Pydantic V2, this is often not needed for this kind of assignment.
        # If issues arise, or for V1, `arbitrary_types_allowed = True` might have been used,
        # but the better approach is to ensure the types are compatible or explicitly converted.
        pass
