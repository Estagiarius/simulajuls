from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field, field_validator, model_validator
from backend.simulations.base_simulation import BaseSimulationParams, BaseSimulationResult

class MendelianCrossParams(BaseSimulationParams):
    # Parâmetros para uma simulação de cruzamento Mendeliano simples (monoibridismo).
    parent1_genotype: str = Field(..., description="Genótipo do progenitor 1 (ex: 'AA', 'Aa', 'aa'). Representa os dois alelos do primeiro progenitor para uma característica específica.")
    parent2_genotype: str = Field(..., description="Genótipo do progenitor 2 (ex: 'AA', 'Aa', 'aa'). Representa os dois alelos do segundo progenitor para a mesma característica.")
    dominant_allele: str = Field('A', min_length=1, max_length=1, description="Caractere que representa o alelo dominante (ex: 'A'). Este alelo se manifesta no fenótipo mesmo em heterozigose.")
    recessive_allele: str = Field('a', min_length=1, max_length=1, description="Caractere que representa o alelo recessivo (ex: 'a'). Este alelo só se manifesta no fenótipo em homozigose recessiva.")
    dominant_phenotype_description: Optional[str] = Field("Fenótipo Dominante", description="Descrição textual do fenótipo expresso pelo alelo dominante (ex: 'Amarelo').")
    recessive_phenotype_description: Optional[str] = Field("Fenótipo Recessivo", description="Descrição textual do fenótipo expresso pelo alelo recessivo em homozigose (ex: 'Verde').")

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
        # Validador a nível de modelo para garantir que os alelos dominante e recessivo sejam diferentes.
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
        # Validador a nível de modelo para garantir que os genótipos dos pais usem apenas os alelos definidos.
        valid_chars = {self.dominant_allele, self.recessive_allele}
        for char_allele in self.parent1_genotype:
            if char_allele not in valid_chars:
                raise ValueError(f"Alelo '{char_allele}' no genótipo '{self.parent1_genotype}' não corresponde aos alelos definidos ('{self.dominant_allele}' ou '{self.recessive_allele}').")
        for char_allele in self.parent2_genotype:
            if char_allele not in valid_chars:
                raise ValueError(f"Alelo '{char_allele}' no genótipo '{self.parent2_genotype}' não corresponde aos alelos definidos ('{self.dominant_allele}' ou '{self.recessive_allele}').")
        return self


class GenotypeProportion(BaseModel):
    # Representa a proporção de um genótipo específico na prole.
    genotype: str = Field(..., description="O genótipo da prole (ex: 'AA', 'Aa', 'aa').")
    count: int = Field(..., description="Número de descendentes com este genótipo no Quadrado de Punnett (total de 4 combinações).")
    fraction: str = Field(..., description="Fração da prole com este genótipo (ex: '1/4', '1/2').")
    percentage: float = Field(..., description="Porcentagem da prole com este genótipo (ex: 25.0, 50.0).")

class PhenotypeProportion(BaseModel):
    # Representa a proporção de um fenótipo específico na prole.
    phenotype_description: str = Field(..., description="Descrição do fenótipo (ex: 'Amarelo', 'Verde').")
    count: int = Field(..., description="Número de descendentes com este fenótipo no Quadrado de Punnett (total de 4 combinações).")
    fraction: str = Field(..., description="Fração da prole com este fenótipo (ex: '3/4', '1/4').")
    percentage: float = Field(..., description="Porcentagem da prole com este fenótipo (ex: 75.0, 25.0).")
    associated_genotypes: List[str] = Field(..., description="Lista de genótipos que resultam neste fenótipo (ex: ['AA', 'Aa'] para fenótipo dominante).")

class MendelianCrossResult(BaseSimulationResult):
    # Resultados de uma simulação de cruzamento Mendeliano.
    parent1_alleles: List[str] = Field(..., description="Lista dos alelos segregados do progenitor 1 (ex: ['A', 'a']).")
    parent2_alleles: List[str] = Field(..., description="Lista dos alelos segregados do progenitor 2 (ex: ['A', 'A']).")
    punnett_square: List[List[str]] = Field(..., description="Matriz (2x2) representando o Quadrado de Punnett, mostrando as combinações de genótipos da prole.")
    offspring_genotypes: List[GenotypeProportion] = Field(..., description="Lista das proporções de cada genótipo na prole.")
    offspring_phenotypes: List[PhenotypeProportion] = Field(..., description="Lista das proporções de cada fenótipo na prole.")
    parameters_used: MendelianCrossParams # type: ignore[assignment] # Parâmetros de entrada que foram utilizados para esta simulação específica.
    # Conforme BaseSimulationResult, parameters_used é Dict[str, Any].
    # Pydantic v2 lida com a atribuição de uma instância de modelo chamando model_dump() se necessário.
    # If strict typing without Pydantic's implicit conversion is required, this could be:
    # parameters_used: Dict[str, Any]
    # And in the module: parameters_used=updated_params.model_dump()
    # Por enquanto, a atribuição direta é aceitável com Pydantic v2.

    class Config:
        # Para Pydantic V2, isso geralmente não é necessário para este tipo de atribuição.
        # Se surgirem problemas, ou para V1, `arbitrary_types_allowed = True` poderia ter sido usado,
        # mas a melhor abordagem é garantir que os tipos sejam compatíveis ou explicitamente convertidos.
        pass
