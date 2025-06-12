"""
Módulo de simulação para Genética Mendeliana.

Este módulo implementa a lógica para simular cruzamentos Mendelianos simples
(monoibridismo), permitindo aos usuários definir os genótipos dos progenitores,
os alelos dominante e recessivo, e descrições para os fenótipos.
A simulação calcula e retorna os alelos segregados, o Quadrado de Punnett,
e as proporções genotípicas e fenotípicas da prole.
"""
from typing import List, Optional, Type, Dict, Any
from collections import Counter
from fastapi import HTTPException
from pydantic import BaseModel # Necessário para dicas de tipo como Type[BaseModel]

from backend.simulations.base_simulation import SimulationModule
from .models_mendelian_genetics import (
    MendelianCrossParams,
    GenotypeProportion,
    PhenotypeProportion,
    MendelianCrossResult
)

class MendelianGeneticsModule(SimulationModule):
    # Implementa a interface SimulationModule para a simulação de Genética Mendeliana.

    def get_name(self) -> str:
        # Retorna o nome identificador da simulação.
        return "mendelian-genetics"

    def get_display_name(self) -> str:
        # Retorna o nome de exibição da simulação.
        return "Genética Mendeliana"

    def get_category(self) -> str:
        # Retorna a categoria da simulação.
        return "Biologia"

    def get_description(self) -> str:
        # Retorna uma breve descrição da simulação.
        return "Simula cruzamentos genéticos Mendelianos e calcula proporções genotípicas e fenotípicas."

    def get_parameter_schema(self) -> Type[MendelianCrossParams]:
        # Retorna o tipo do modelo Pydantic para os parâmetros de entrada.
        return MendelianCrossParams

    def get_result_schema(self) -> Type[MendelianCrossResult]:
        # Retorna o tipo do modelo Pydantic para os resultados da simulação.
        return MendelianCrossResult

    def run_simulation(self, params: MendelianCrossParams) -> MendelianCrossResult:
        # Executa a lógica da simulação de cruzamento Mendeliano.
        # Os parâmetros de entrada já foram validados pelo Pydantic (MendelianCrossParams).

        # Remove espaços em branco dos alelos definidos, embora o Field já possa cuidar disso.
        # É uma boa prática garantir que não haja espaços residuais.
        defined_dom_allele = params.dominant_allele.strip()
        defined_rec_allele = params.recessive_allele.strip()

        # As validações iniciais sobre os alelos (comprimento, diferença entre dominante e recessivo)
        # são agora tratadas pelos validadores do modelo Pydantic em MendelianCrossParams.
        # Portanto, verificações explícitas aqui seriam redundantes.

        dom_allele = defined_dom_allele
        rec_allele = defined_rec_allele

        # Função auxiliar para obter os alelos de uma string de genótipo.
        # A validação do formato do genótipo (comprimento 2, alfabético) e
        # a correspondência dos caracteres com os alelos definidos (dom_allele, rec_allele)
        # já são realizadas pelos validadores Pydantic no modelo MendelianCrossParams.
        # Esta função agora foca principalmente em dividir a string do genótipo em seus alelos constituintes.
        def get_alleles_from_genotype_str(genotype_str: str) -> List[str]:
            # Simplesmente divide a string do genótipo em uma lista de caracteres (alelos).
            # Ex: "Aa" -> ["A", "a"]
            # Pressupõe-se que as validações de formato e caracteres já ocorreram.
            return list(genotype_str)

        # Obtém as listas de alelos para cada progenitor.
        p1_alleles_list = get_alleles_from_genotype_str(params.parent1_genotype)
        p2_alleles_list = get_alleles_from_genotype_str(params.parent2_genotype)

        # Inicializa o Quadrado de Punnett (matriz 2x2) e a lista de genótipos da prole.
        punnett_square_genotypes: List[List[str]] = [["", ""], ["", ""]]
        prole_genotypes_list: List[str] = []

        # Preenche o Quadrado de Punnett e a lista de genótipos da prole.
        # Itera sobre os alelos de cada progenitor para formar os genótipos dos descendentes.
        for i in range(2): # Para cada alelo do progenitor 1
            for j in range(2): # Para cada alelo do progenitor 2
                allele1 = p1_alleles_list[i]
                allele2 = p2_alleles_list[j]

                # Normaliza a ordem dos alelos no genótipo do descendente: dominante primeiro.
                # Ex: "aA" torna-se "Aa". Isso é importante para a contagem correta dos genótipos.
                if (allele1 == dom_allele and allele2 == rec_allele):
                    offspring_g = dom_allele + rec_allele
                elif (allele1 == rec_allele and allele2 == dom_allele):
                    offspring_g = dom_allele + rec_allele # Alelo dominante primeiro
                else: # Ambos alelos são iguais (AA ou aa)
                    offspring_g = allele1 + allele2

                punnett_square_genotypes[i][j] = offspring_g # Adiciona ao Quadrado de Punnett
                prole_genotypes_list.append(offspring_g)   # Adiciona à lista de genótipos da prole

        # Calcula as proporções genotípicas.
        genotype_counts = Counter(prole_genotypes_list) # Conta a ocorrência de cada genótipo.
        total_offspring = len(prole_genotypes_list)     # Total de combinações (normalmente 4).
        offspring_genotype_proportions: List[GenotypeProportion] = []

        # Função de chave para ordenar os genótipos (Homozigoto Dominante, Heterozigoto, Homozigoto Recessivo).
        def sort_key_genotype(g_str: str) -> int:
            if g_str == dom_allele + dom_allele: return 0 # Ex: AA
            if g_str == dom_allele + rec_allele: return 1 # Ex: Aa
            if g_str == rec_allele + rec_allele: return 2 # Ex: aa
            return 3 # Outros (não esperado em cruzamento simples)

        # Obtém as chaves dos genótipos (ex: 'AA', 'Aa', 'aa') e ordena.
        sorted_genotypes_keys = sorted(genotype_counts.keys(), key=sort_key_genotype)

        # Cria os objetos GenotypeProportion para cada genótipo.
        for genotype_key in sorted_genotypes_keys:
            count = genotype_counts[genotype_key]
            offspring_genotype_proportions.append(GenotypeProportion(
                genotype=genotype_key,
                count=count,
                fraction=f"{count}/{total_offspring}",
                percentage=round((count / total_offspring) * 100, 2)
            ))

        # Calcula as proporções fenotípicas.
        phenotype_counts = Counter() # Contador para os fenótipos.
        # Itera sobre as proporções genotípicas já calculadas.
        for g_obj in offspring_genotype_proportions:
            genotype_str = g_obj.genotype
            # Determina o fenótipo com base na presença do alelo dominante.
            if dom_allele in genotype_str: # Se o alelo dominante está presente (AA ou Aa)
                phenotype_counts[params.dominant_phenotype_description] += g_obj.count
            else: # Caso contrário, é homozigoto recessivo (aa)
                phenotype_counts[params.recessive_phenotype_description] += g_obj.count

        offspring_phenotype_proportions: List[PhenotypeProportion] = []
        # Define a ordem de exibição dos fenótipos (Dominante primeiro, depois Recessivo).
        phenotype_order = {params.dominant_phenotype_description: 0, params.recessive_phenotype_description: 1}
        sorted_phenotypes_desc_keys = sorted(phenotype_counts.keys(), key=lambda p_desc: phenotype_order.get(p_desc, 99))

        # Cria os objetos PhenotypeProportion para cada fenótipo.
        for phenotype_d_key in sorted_phenotypes_desc_keys:
            count = phenotype_counts[phenotype_d_key]
            if count > 0: # Processa apenas se o fenótipo estiver presente na prole.
                associated_genotypes_for_pheno = []
                # Identifica os genótipos associados a este fenótipo.
                if phenotype_d_key == params.dominant_phenotype_description:
                    # Genótipos que expressam o fenótipo dominante (contêm o alelo dominante).
                    associated_genotypes_for_pheno = [g for g in genotype_counts.keys() if dom_allele in g]
                else: # Fenótipo recessivo
                    # Genótipos que expressam o fenótipo recessivo (apenas homozigoto recessivo).
                    associated_genotypes_for_pheno = [g for g in genotype_counts.keys() if g == rec_allele + rec_allele]

                offspring_phenotype_proportions.append(PhenotypeProportion(
                    phenotype_description=phenotype_d_key,
                    count=count,
                    fraction=f"{count}/{total_offspring}",
                    percentage=round((count / total_offspring) * 100, 2),
                    associated_genotypes=sorted(list(set(associated_genotypes_for_pheno)), key=sort_key_genotype) # Ordena os genótipos associados.
                ))

        # Prepara os parâmetros usados para incluir na resposta.
        # É importante registrar os alelos dominante e recessivo após o strip(),
        # para refletir os valores efetivamente usados na simulação.
        updated_params = params.model_copy(deep=True) # Cria uma cópia profunda para evitar modificar o objeto original inesperadamente.
        updated_params.dominant_allele = dom_allele
        updated_params.recessive_allele = rec_allele
        # Os genótipos dos pais são mantidos como foram fornecidos.

        # Retorna o objeto de resultado da simulação.
        return MendelianCrossResult(
            parent1_alleles=p1_alleles_list, # Alelos segregados do progenitor 1.
            parent2_alleles=p2_alleles_list,
            punnett_square=punnett_square_genotypes,
            offspring_genotypes=offspring_genotype_proportions,
            offspring_phenotypes=offspring_phenotype_proportions,
            parameters_used=updated_params # Parâmetros de entrada efetivamente usados, com alelos após strip().
        )
