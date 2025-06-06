from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import List, Optional
from fastapi.middleware.cors import CORSMiddleware
import math
from collections import Counter

# 1. Modelos Pydantic (Existente)
class Experiment(BaseModel):
    id: int
    name: str
    category: str
    description: str
    image_url: Optional[str] = None

# Inicializa o aplicativo FastAPI (Existente)
app = FastAPI()

# Adicionar middleware CORS (Existente)
origins = [
    "*",  # Permite todas as origens
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],  # Permite todos os métodos
    allow_headers=["*"],  # Permite todos os cabeçalhos
)

# 2. Dados Mock (Existente)
mock_experiments_data: List[Experiment] = [
    Experiment(id=1, name="Reação Ácido-Base", category="Química", description="Observe a neutralização de um ácido por uma base.", image_url="images/placeholder.png"),
    Experiment(id=2, name="Eletrólise da Água", category="Química", description="Decomponha a água em oxigênio e hidrogênio.", image_url="images/placeholder.png"),
    Experiment(id=3, name="Titulação", category="Química", description="Determine a concentração de uma solução.", image_url="images/placeholder.png"),
    Experiment(id=4, name="Lançamento Oblíquo", category="Física", description="Analise a trajetória de um projétil.", image_url="images/placeholder.png"),
    Experiment(id=5, name="Plano Inclinado", category="Física", description="Estude as forças em um corpo em um plano inclinado.", image_url="images/placeholder.png"),
    Experiment(id=6, name="Queda Livre", category="Física", description="Observe o movimento de um corpo sob a ação da gravidade.", image_url="images/placeholder.png"),
    Experiment(id=7, name="Fotossíntese", category="Biologia", description="Veja como as plantas produzem energia.", image_url="images/placeholder.png"),
    Experiment(id=8, name="Ciclo Celular", category="Biologia", description="Explore as fases da divisão celular.", image_url="images/placeholder.png"),
    Experiment(id=9, name="Genética Mendeliana", category="Biologia", description="Entenda as leis da hereditariedade.", image_url="images/placeholder.png"),
]

# Modelos Pydantic para Simulação Ácido-Base
class AcidBaseSimulationParams(BaseModel):
    acid_name: Optional[str] = "Ácido Forte Monoprótico"
    acid_concentration: float
    acid_volume: float  # em mL
    base_name: Optional[str] = "Base Forte Monohidroxílica"
    base_concentration: float
    base_volume: float  # em mL
    indicator_name: Optional[str] = None

class AcidBaseSimulationResult(BaseModel):
    final_ph: float
    final_poh: Optional[float] = None
    total_volume_ml: float
    mols_h_plus_initial: float
    mols_oh_minus_initial: float
    excess_reactant: Optional[str] = None
    status: str
    indicator_color: Optional[str] = None
    message: Optional[str] = None

# Função para realizar a simulação Ácido-Base
def perform_acid_base_simulation(params: AcidBaseSimulationParams) -> AcidBaseSimulationResult:
    acid_volume_l = params.acid_volume / 1000
    base_volume_l = params.base_volume / 1000
    mols_h_plus = params.acid_concentration * acid_volume_l
    mols_oh_minus = params.base_concentration * base_volume_l
    total_volume_l = acid_volume_l + base_volume_l
    total_volume_ml = total_volume_l * 1000
    final_ph: float; final_poh: Optional[float] = None; excess_reactant_val: Optional[str] = None; status_val: str; message_val: Optional[str] = None
    if abs(mols_h_plus - mols_oh_minus) < 1e-9:
        final_ph = 7.0; final_poh = 7.0; excess_reactant_val = "Nenhum"; status_val = "Neutra"; message_val = "Neutralização completa."
    elif mols_h_plus > mols_oh_minus:
        mols_h_plus_excess = mols_h_plus - mols_oh_minus
        concentration_h_plus_final = mols_h_plus_excess / total_volume_l
        if concentration_h_plus_final <= 0: final_ph = 14.0; message_val = "Concentração de H+ excesso resultou em valor não positivo."
        else: final_ph = -math.log10(concentration_h_plus_final)
        excess_reactant_val = "H+"; status_val = "Ácida"
        if final_ph < 0: final_ph = 0
        final_poh = 14.0 - final_ph
    else:
        mols_oh_minus_excess = mols_oh_minus - mols_h_plus
        concentration_oh_minus_final = mols_oh_minus_excess / total_volume_l
        if concentration_oh_minus_final <= 0: final_poh = 14.0; message_val = "Concentração de OH- excesso resultou em valor não positivo."
        else: final_poh = -math.log10(concentration_oh_minus_final)
        if final_poh < 0: final_poh = 0
        final_ph = 14.0 - final_poh
        excess_reactant_val = "OH-"; status_val = "Básica"
    final_ph = round(final_ph, 2)
    if final_poh is not None: final_poh = round(final_poh, 2)
    indicator_color_val: Optional[str] = None
    if params.indicator_name:
        indicator_name_lower = params.indicator_name.strip().lower()
        if indicator_name_lower == "fenolftaleína":
            if final_ph < 8.2: indicator_color_val = "Incolor"
            elif final_ph <= 10.0: indicator_color_val = "Rosa claro/Róseo"
            else: indicator_color_val = "Carmim/Magenta"
        elif indicator_name_lower == "azul de bromotimol":
            if final_ph < 6.0: indicator_color_val = "Amarelo"
            elif final_ph <= 7.6: indicator_color_val = "Verde"
            else: indicator_color_val = "Azul"
        else:
            indicator_color_val = "Indicador não reconhecido"
            message_val = (message_val + " " if message_val else "") + f"Indicador '{params.indicator_name}' não suportado."
    return AcidBaseSimulationResult(final_ph=final_ph, final_poh=final_poh, total_volume_ml=round(total_volume_ml, 2), mols_h_plus_initial=round(mols_h_plus, 9), mols_oh_minus_initial=round(mols_oh_minus, 9), excess_reactant=excess_reactant_val, status=status_val, indicator_color=indicator_color_val, message=message_val)

# Modelos Pydantic para Simulação de Lançamento Oblíquo
class ProjectileLaunchParams(BaseModel):
    initial_velocity: float
    launch_angle: float  # em graus
    initial_height: Optional[float] = 0.0
    gravity: Optional[float] = 9.81

class TrajectoryPoint(BaseModel):
    time: float
    x: float
    y: float

class ProjectileLaunchResult(BaseModel):
    initial_velocity_x: float
    initial_velocity_y: float
    total_time: float
    max_range: float
    max_height: float
    trajectory: List[TrajectoryPoint]
    parameters_used: ProjectileLaunchParams

# Função para realizar a simulação de Lançamento Oblíquo
def perform_projectile_launch_simulation(params: ProjectileLaunchParams) -> ProjectileLaunchResult:
    # Validação de Parâmetros de Entrada
    if params.initial_velocity <= 0: raise HTTPException(status_code=400, detail="Velocidade inicial deve ser positiva.")
    if not (0 < params.launch_angle < 90): raise HTTPException(status_code=400, detail="Ângulo de lançamento deve estar entre 0 e 90 graus (exclusive) para lançamento oblíquo.")
    if params.initial_height < 0: raise HTTPException(status_code=400, detail="Altura inicial não pode ser negativa.")
    if params.gravity <= 0: raise HTTPException(status_code=400, detail="Gravidade deve ser positiva.")

    # Parâmetros da simulação
    g = params.gravity
    v0 = params.initial_velocity
    angle_rad = math.radians(params.launch_angle)
    y0 = params.initial_height # Altura inicial

    # Componentes da velocidade inicial
    v0x = v0 * math.cos(angle_rad) # Velocidade inicial no eixo x
    v0y = v0 * math.sin(angle_rad) # Velocidade inicial no eixo y

    # Altura máxima atingida (em relação ao solo, y=0)
    # Fórmula: max_h = y0 + (v0y^2) / (2 * g)
    # Esta é a altura máxima se y0=0, mais a altura inicial.
    max_h_from_y0 = (v0y**2) / (2 * g) if v0y > 0 else 0
    max_h = y0 + max_h_from_y0

    # Tempo total de voo (até o projétil atingir y(t) = 0 novamente ou pela primeira vez se y0 > 0)
    # Resolvendo a equação quadrática para y(t) = y0 + v0y*t - 0.5*g*t^2 = 0
    # 0.5*g*t^2 - v0y*t - y0 = 0.  Usando Bhaskara: t = [-b +/- sqrt(b^2 - 4ac)] / 2a
    # a = 0.5g, b = -v0y, c = -y0
    discriminant = (-v0y)**2 - 4 * (0.5 * g) * (-y0) # delta = b^2 - 4ac

    if discriminant < 0:
        # Se o discriminante é negativo, significa que o projétil nunca atinge y=0 (se y0>0 e lançado para cima com pouca força)
        # ou algo está errado (não deveria ocorrer para y0=0).
        # Para este contexto, se y0 > 0 e nunca atinge y=0 (ex: lançado verticalmente para cima e não volta a y0),
        # o tempo de voo até o ponto mais alto pode ser considerado, ou pode ser um caso não coberto.
        # A lógica atual para total_t=0 e y0>0 abaixo trata a queda.
        # Se y0=0 e discriminante < 0, isso implicaria v0y=0 e g<0 ou algo assim, já validado.
        total_t = 0
    else:
        # t = (v0y +/- math.sqrt(discriminant)) / g
        # Tomamos a raiz positiva que resulta em t > 0 (tempo de impacto no solo).
        # Se y0=0, uma raiz é t=0 (instante inicial) e a outra é 2*v0y/g.
        # Se y0>0, apenas a raiz positiva da fórmula completa faz sentido para impacto.
        t_impact = (v0y + math.sqrt(discriminant)) / g
        total_t = t_impact if t_impact >= 0 else 0 # Garante que o tempo não seja negativo

    # Alcance horizontal máximo
    # Fórmula: max_r = v0x * total_time (distância percorrida no eixo x durante o tempo total de voo)
    max_r = v0x * total_t

    # Geração de pontos da trajetória
    trajectory_points: List[TrajectoryPoint] = []
    time_step = 0.05 # Intervalo de tempo para calcular pontos da trajetória
    current_time = 0.0

    # Caso 1: O tempo total de voo é maior que zero.
    # Isso cobre lançamentos de y0=0 ou de y0>0 que sobem e descem, ou descem diretamente.
    if total_t > 0:
        while current_time <= total_t:
            # Equações do movimento:
            # x(t) = v0x * t
            # y(t) = y0 + v0y * t - 0.5 * g * t^2
            x = v0x * current_time
            y = y0 + v0y * current_time - 0.5 * g * current_time**2

            # Garante que o projétil não vá "abaixo" do solo (y=0) nos cálculos.
            if y < 0: y = 0

            trajectory_points.append(TrajectoryPoint(time=round(current_time,3), x=round(x,3), y=round(y,3)))

            # Se o projétil atingiu o solo (y=0) e já passou um tempo mínimo (para não parar no t=0 se y0=0),
            # e ainda não é o ponto final exato de total_t, podemos encerrar se a precisão for suficiente.
            # No entanto, é mais robusto iterar até total_t e garantir que o último ponto esteja lá.
            if y == 0 and current_time > 1e-6 and current_time < total_t:
                # Este break pode ser útil se quisermos parar assim que y=0 for atingido,
                # mas a lógica de adicionar o último ponto em total_t é mais completa.
                pass # Mantido para reflexão, mas o loop continua até total_t

            # Evita loop infinito se time_step for muito pequeno ou total_t for enorme.
            # Adiciona uma margem ao total_t para garantir que o último ponto seja incluído.
            if current_time > total_t + time_step : break
            current_time += time_step

        # Garante que o último ponto (tempo total, y=0) esteja na trajetória,
        # especialmente se o time_step não coincidir exatamente com total_t.
        if not trajectory_points or abs(trajectory_points[-1].time - total_t) > 1e-4 or trajectory_points[-1].y != 0:
            x_final = v0x * total_t
            # Adiciona o ponto final apenas se ele não for redundante com o último ponto já calculado.
            if not trajectory_points or abs(trajectory_points[-1].time - total_t) > 1e-4:
                 trajectory_points.append(TrajectoryPoint(time=round(total_t,3), x=round(x_final,3), y=0.0))
            # Se o último ponto calculado está no tempo total_t mas y não é exatamente 0 devido a arredondamentos, corrige y.
            elif trajectory_points[-1].y != 0:
                trajectory_points[-1].y = 0.0

    # Caso 2: O tempo total de voo calculado foi zero (ou negativo e corrigido para zero).
    # Isso pode ocorrer se y0=0 e v0y=0 (parado no chão), ou se y0>0 e o discriminante foi negativo (não atinge y=0).
    # A lógica anterior para `total_t == 0 and y0 > 0` foi integrada acima no cálculo de `total_t`
    # e na geração de trajetória quando `total_t > 0` é satisfeito por `t_impact`.
    # Esta cláusula `else` agora cobre o caso onde o projétil está no chão (y0=0) e não tem velocidade vertical (v0y=0).
    # Se v0x > 0, ele desliza (não coberto aqui como trajetória 2D). Se v0x=0, fica parado.
    else: # total_t == 0 (e, pela lógica anterior, y0 deve ser 0 ou o projétil não se move verticalmente)
        trajectory_points.append(TrajectoryPoint(time=0.0, x=0.0, y=y0)) # Ponto inicial
        if y0 == 0 and v0 == 0: # Se começa no chão e sem velocidade, altura máxima é 0.
             max_h = 0.0
        # Se y0 > 0 mas total_t = 0, significa que não houve movimento vertical para cima
        # e não atingiu o solo por cálculo parabólico (ex: v0y=0 e y0>0, queda livre horizontal).
        # Este cenário específico de queda livre de y0 > 0 com v0y=0 é um caso onde
        # total_t (tempo até y=0) seria sqrt(2*y0/g). A lógica de cálculo de total_t já deve cobrir isso.
        # Se ainda assim total_t = 0 aqui, e y0 > 0, pode ser um caso extremo.
        # Se o objeto está em y0 > 0 e total_t = 0, ele não se moveu para o solo.
        # max_r seria 0. max_h seria y0.
        if y0 > 0 and v0y == 0: # Lançamento horizontal de altura y0
            # O tempo de queda é sqrt(2*y0/g), que já deveria ter sido total_t.
            # Se total_t é 0 aqui, é um estado inconsistente ou não coberto.
            # A lógica de trajetória acima (total_t > 0) deve lidar com isso.
            # Se estamos aqui, significa que o cálculo de total_t resultou em 0, mesmo com y0 > 0.
            # Isso pode acontecer se v0y é para cima mas insuficiente para voltar a y0.
            # Contudo, o cálculo de max_h já considera a altura máxima atingida.
            # E o `total_t` com Bhaskara já é o tempo para y=0.
            # Se total_t é 0, então o objeto não se moveu significativamente no tempo.
            pass

    return ProjectileLaunchResult(
        initial_velocity_x=round(v0x, 3),
        initial_velocity_y=round(v0y, 3),
        total_time=round(total_t, 3),
        max_range=round(max_r, 3),
        max_height=round(max_h, 3),
        trajectory=trajectory_points,
        parameters_used=params
    )

# Modelos Pydantic para Simulação de Genética Mendeliana
class MendelianCrossParams(BaseModel):
    parent1_genotype: str
    parent2_genotype: str
    dominant_allele: Optional[str] = 'A'
    recessive_allele: Optional[str] = 'a'
    dominant_phenotype_description: Optional[str] = "Fenótipo Dominante"
    recessive_phenotype_description: Optional[str] = "Fenótipo Recessivo"

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

class MendelianCrossResult(BaseModel):
    parent1_alleles: List[str]
    parent2_alleles: List[str]
    punnett_square: List[List[str]]
    offspring_genotypes: List[GenotypeProportion]
    offspring_phenotypes: List[PhenotypeProportion]
    parameters_used: MendelianCrossParams

# Função para realizar a simulação de Genética Mendeliana (CORRIGIDA e REFINADA)
def perform_mendelian_cross_simulation(params: MendelianCrossParams) -> MendelianCrossResult:
    # Validação inicial dos CARACTERES usados para definir os alelos dominante e recessivo.
    # Estes são os símbolos que o usuário escolhe, ex: 'A' e 'a'.
    defined_dom_allele = params.dominant_allele.strip()
    defined_rec_allele = params.recessive_allele.strip()

    # 1.1. Valida se os caracteres definidos não são vazios.
    if not defined_dom_allele or not defined_rec_allele:
        raise HTTPException(status_code=400, detail="Caracteres para alelos dominante e recessivo não podem ser vazios.")
    # 1.2. Valida se os caracteres definidos têm tamanho 1.
    if len(defined_dom_allele) != 1 or len(defined_rec_allele) != 1:
        raise HTTPException(status_code=400, detail="Alelos dominante e recessivo devem ser caracteres únicos.")

    # 1.3. Valida se os caracteres definidos para dominante e recessivo são, de fato, o mesmo símbolo.
    # Ex: Se o usuário define Dominante='A' e Recessivo='A', é um erro.
    # 'A' e 'a' são permitidos, pois são caracteres diferentes.
    if defined_dom_allele == defined_rec_allele: # BUG-004 Fixed: This now correctly checks for exact character match.
         raise HTTPException(status_code=400, detail="Alelos dominante e recessivo definidos não podem ser o mesmo caractere.")

    # A partir daqui, dom_allele e rec_allele são os caracteres (case-sensitive) que representam os alelos,
    # conforme definido pelo usuário.
    dom_allele = defined_dom_allele
    rec_allele = defined_rec_allele

    # Função aninhada para validar um genótipo string (ex: "Aa", "bb") e extrair seus dois alelos.
    # dA: caractere do alelo dominante definido (ex: 'A' ou 'B')
    # rA: caractere do alelo recessivo definido (ex: 'a' ou 'b')
    def validate_and_get_alleles(genotype_str: str, dA: str, rA: str) -> List[str]:
        # 2.1. Valida o tamanho do genótipo (deve ter 2 alelos).
        if len(genotype_str) != 2:
            raise HTTPException(status_code=400, detail=f"Genótipo '{genotype_str}' inválido. Deve ter 2 alelos.")

        alleles_from_genotype = []
        # 2.2. Valida cada caractere do genótipo contra os alelos definidos (case-sensitive).
        # BUG-003 Fixed: Validation is now strictly case-sensitive against dA and rA.
        for char_allele in genotype_str:
            if char_allele == dA:
                alleles_from_genotype.append(dA)
            elif char_allele == rA:
                alleles_from_genotype.append(rA)
            else:
                raise HTTPException(status_code=400, detail=f"Alelo '{char_allele}' no genótipo '{genotype_str}' não corresponde aos alelos definidos como '{dA}' (dominante) ou '{rA}' (recessivo). Verifique a sensibilidade a maiúsculas/minúsculas.")
        return alleles_from_genotype

    # Valida e obtém os alelos para cada progenitor.
    p1_alleles_list = validate_and_get_alleles(params.parent1_genotype, dom_allele, rec_allele)
    p2_alleles_list = validate_and_get_alleles(params.parent2_genotype, dom_allele, rec_allele)

    # Gerar Quadro de Punnett: combina os alelos de cada pai.
    # O quadro é uma matriz 2x2 representando os 4 possíveis genótipos da prole.
    punnett_square_genotypes: List[List[str]] = [["", ""], ["", ""]]
    prole_genotypes_list: List[str] = [] # Lista para facilitar contagem e cálculo de proporções

    for i in range(2): # Itera sobre os dois alelos do progenitor 1 (p1_alleles_list[0], p1_alleles_list[1])
        for j in range(2): # Itera sobre os dois alelos do progenitor 2 (p2_alleles_list[0], p2_alleles_list[1])
            allele1 = p1_alleles_list[i]
            allele2 = p2_alleles_list[j]

            # Normaliza a ordem do par de alelos para heterozigotos:
            # O alelo dominante (definido pelo usuário) vem primeiro. Ex: "Aa" e não "aA" (se A é dom).
            # BUG-001 & BUG-002 Fixed: Correctly normalizes heterozygous offspring.
            if (allele1 == dom_allele and allele2 == rec_allele):
                offspring_g = dom_allele + rec_allele
            elif (allele1 == rec_allele and allele2 == dom_allele):
                offspring_g = dom_allele + rec_allele
            else: # Genótipos homozigotos (ex: AA, aa, BB, bb)
                offspring_g = allele1 + allele2

            punnett_square_genotypes[i][j] = offspring_g
            prole_genotypes_list.append(offspring_g)

    # Calcula a frequência de cada genótipo na prole usando Counter.
    genotype_counts = Counter(prole_genotypes_list)
    total_offspring = len(prole_genotypes_list)
    offspring_genotype_proportions: List[GenotypeProportion] = []

    # Ordena os genótipos para exibição consistente (ex: AA, Aa, aa).
    def sort_key_genotype(g_str): # Função chave para ordenação canônica.
        if g_str == dom_allele + dom_allele: return 0 # Homozigoto dominante primeiro.
        if g_str == dom_allele + rec_allele: return 1 # Heterozigoto em seguida.
        if g_str == rec_allele + rec_allele: return 2 # Homozigoto recessivo por último.
        return 3 # Outros (não esperado em cruzamento simples).

    sorted_genotypes_keys = sorted(genotype_counts.keys(), key=sort_key_genotype)

    for genotype_key in sorted_genotypes_keys:
        count = genotype_counts[genotype_key]
        offspring_genotype_proportions.append(GenotypeProportion(
            genotype=genotype_key, count=count, fraction=f"{count}/{total_offspring}",
            percentage=round((count / total_offspring) * 100, 2)))

    # Calcula as proporções fenotípicas.
    phenotype_counts = Counter()
    for g_obj in offspring_genotype_proportions:
        genotype_str = g_obj.genotype
        # Se o alelo dominante estiver presente no genótipo, expressa o fenótipo dominante.
        if dom_allele in genotype_str:
            phenotype_counts[params.dominant_phenotype_description] += g_obj.count
        else: # Caso contrário (apenas alelos recessivos), expressa o fenótipo recessivo.
            phenotype_counts[params.recessive_phenotype_description] += g_obj.count

    offspring_phenotype_proportions: List[PhenotypeProportion] = []
    # Ordena os fenótipos para exibição (Dominante primeiro, depois Recessivo).
    phenotype_order = {params.dominant_phenotype_description: 0, params.recessive_phenotype_description: 1}
    sorted_phenotypes_desc_keys = sorted(phenotype_counts.keys(), key=lambda p_desc: phenotype_order.get(p_desc, 99))

    for phenotype_d_key in sorted_phenotypes_desc_keys:
        count = phenotype_counts[phenotype_d_key]
        if count > 0: # Adiciona apenas se o fenótipo estiver presente na prole.
            associated_genotypes_for_pheno = []
            if phenotype_d_key == params.dominant_phenotype_description:
                # Fenótipo dominante é expresso por genótipos homozigotos dominantes ou heterozigotos.
                associated_genotypes_for_pheno = [g for g in genotype_counts.keys() if dom_allele in g]
            else: # Fenótipo recessivo
                # Fenótipo recessivo é expresso apenas pelo genótipo homozigoto recessivo.
                associated_genotypes_for_pheno = [g for g in genotype_counts.keys() if g == rec_allele + rec_allele]

            offspring_phenotype_proportions.append(PhenotypeProportion(
                phenotype_description=phenotype_d_key, count=count, fraction=f"{count}/{total_offspring}",
                percentage=round((count / total_offspring) * 100, 2),
                associated_genotypes=sorted(list(set(associated_genotypes_for_pheno)), key=sort_key_genotype)))

    # TASK-001 Fixed: Usar model_copy para compatibilidade com Pydantic V2.
    # Preserva os genótipos originais dos pais nos parâmetros retornados,
    # mas os alelos dominante/recessivo refletem os caracteres validados e usados na simulação.
    updated_params = params.model_copy(update={
        "dominant_allele": dom_allele,
        "recessive_allele": rec_allele
        # parent1_genotype e parent2_genotype do 'params' original são mantidos.
    })

    return MendelianCrossResult(
        parent1_alleles=p1_alleles_list, parent2_alleles=p2_alleles_list,
        punnett_square=punnett_square_genotypes,
        offspring_genotypes=offspring_genotype_proportions,
        offspring_phenotypes=offspring_phenotype_proportions,
        parameters_used=updated_params)

# 3. Endpoints da API (Existentes e Novos)
@app.get("/api/experiments", response_model=List[Experiment])
async def get_experiments():
    return mock_experiments_data

@app.post("/api/simulation/chemistry/acid-base/start", response_model=AcidBaseSimulationResult)
async def start_acid_base_simulation(params: AcidBaseSimulationParams):
    if params.acid_concentration <= 0 or params.acid_volume <= 0 or params.base_concentration <= 0 or params.base_volume <= 0:
        raise HTTPException(status_code=400, detail="Concentrações e volumes devem ser positivos e maiores que zero.")
    return perform_acid_base_simulation(params)

@app.post("/api/simulation/physics/projectile-launch/start", response_model=ProjectileLaunchResult)
async def start_projectile_launch_simulation(params: ProjectileLaunchParams):
    return perform_projectile_launch_simulation(params)

@app.post("/api/simulation/biology/mendelian-genetics/start", response_model=MendelianCrossResult)
async def start_mendelian_cross_simulation(params: MendelianCrossParams):
    return perform_mendelian_cross_simulation(params)

# Endpoint raiz (Existente)
@app.get("/")
async def read_root():
    return {"message": "Bem-vindo ao Simulador de Experimentos Educativos API"}

# Modelo Pydantic placeholder para dados de simulação a serem salvos
class SimulationData(BaseModel):
    experiment_type: str
    params: dict
    results: dict

# Esqueleto do endpoint para salvar simulações
@app.post("/api/simulations/save", status_code=501)
async def save_simulation(simulation_data: SimulationData):
    return {"message": "Funcionalidade de salvar simulação ainda não implementada."}

# Esqueleto do endpoint para carregar uma simulação específica
@app.get("/api/simulations/{simulation_id}", status_code=501)
async def get_simulation(simulation_id: str):
    return {"message": f"Funcionalidade de carregar simulação com ID {simulation_id} ainda não implementada."}
