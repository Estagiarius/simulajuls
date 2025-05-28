from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import List, Optional
from fastapi.middleware.cors import CORSMiddleware
import math
from collections import Counter # Adicionar para contagem de genótipos/fenótipos

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
    if params.initial_velocity <= 0: raise HTTPException(status_code=400, detail="Velocidade inicial deve ser positiva.")
    if not (0 < params.launch_angle < 90): raise HTTPException(status_code=400, detail="Ângulo de lançamento deve estar entre 0 e 90 graus (exclusive) para lançamento oblíquo.")
    if params.initial_height < 0: raise HTTPException(status_code=400, detail="Altura inicial não pode ser negativa.")
    if params.gravity <= 0: raise HTTPException(status_code=400, detail="Gravidade deve ser positiva.")
    g = params.gravity; v0 = params.initial_velocity; angle_rad = math.radians(params.launch_angle); y0 = params.initial_height
    v0x = v0 * math.cos(angle_rad); v0y = v0 * math.sin(angle_rad)
    max_h = y0 + (v0y**2) / (2 * g)
    discriminant = v0y**2 - 4 * (0.5 * g) * (-y0)
    if discriminant < 0: total_t = 0 
    else: total_t = (v0y + math.sqrt(discriminant)) / g
    if total_t < 0: total_t = 0
    max_r = v0x * total_t
    trajectory_points: List[TrajectoryPoint] = []; time_step = 0.05; current_time = 0.0
    if total_t == 0 and y0 > 0: 
        time_to_fall_y0 = 0
        if v0y <=0: 
            if y0 > 0 : time_to_fall_y0 = (math.sqrt(v0y**2 + 2*g*y0) - v0y) / g if g > 0 else 0
            current_t_fall = 0.0
            while current_t_fall <= time_to_fall_y0:
                x = v0x * current_t_fall; y = y0 + v0y * current_t_fall - 0.5 * g * current_t_fall**2
                if y < 0: y = 0 
                trajectory_points.append(TrajectoryPoint(time=round(current_t_fall,3), x=round(x,3), y=round(y,3)))
                if y == 0 and current_t_fall > 1e-6 : break 
                if current_t_fall > time_to_fall_y0 + time_step : break 
                current_t_fall += time_step
            if not any(p.time == round(time_to_fall_y0,3) and p.y == 0 for p in trajectory_points) and y0 > 0 and time_to_fall_y0 > 0:
                 x = v0x * time_to_fall_y0; y = 0
                 trajectory_points.append(TrajectoryPoint(time=round(time_to_fall_y0,3), x=round(x,3), y=round(y,3)))
            total_t = time_to_fall_y0 
    elif total_t > 0:
        while current_time <= total_t:
            x = v0x * current_time; y = y0 + v0y * current_time - 0.5 * g * current_time**2
            if y < 0: y = 0 
            trajectory_points.append(TrajectoryPoint(time=round(current_time,3), x=round(x,3), y=round(y,3)))
            if current_time > total_t + time_step : break 
            current_time += time_step
        if not trajectory_points or abs(trajectory_points[-1].time - total_t) > 1e-4 or trajectory_points[-1].y != 0 :
            x_final = v0x * total_t
            if not trajectory_points or abs(trajectory_points[-1].time - total_t) > 1e-4 :
                 trajectory_points.append(TrajectoryPoint(time=round(total_t,3), x=round(x_final,3), y=0.0))
            elif trajectory_points[-1].y != 0: trajectory_points[-1].y = 0.0
    else: 
        trajectory_points.append(TrajectoryPoint(time=0.0, x=0.0, y=0.0))
        if v0 == 0 : max_h = 0.0
    return ProjectileLaunchResult(initial_velocity_x=round(v0x, 3), initial_velocity_y=round(v0y, 3), total_time=round(total_t, 3), max_range=round(max_r, 3), max_height=round(max_h, 3), trajectory=trajectory_points, parameters_used=params)

# Modelos Pydantic para Simulação de Genética Mendeliana
class MendelianCrossParams(BaseModel):
    parent1_genotype: str
    parent2_genotype: str
    dominant_allele: Optional[str] = 'A'
    recessive_allele: Optional[str] = 'a'
    dominant_phenotype_description: Optional[str] = "Fenótipo Dominante"
    recessive_phenotype_description: Optional[str] = "Fenótipo Recessivo"

class PunnettSquareCell(BaseModel): 
    parent1_allele: str
    parent2_allele: str
    offspring_genotype: str

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

# Função para realizar a simulação de Genética Mendeliana
def perform_mendelian_cross_simulation(params: MendelianCrossParams) -> MendelianCrossResult:
    dom_allele = params.dominant_allele.upper()
    rec_allele = params.recessive_allele.lower()
    if len(dom_allele) != 1 or len(rec_allele) != 1 or dom_allele == rec_allele:
        raise HTTPException(status_code=400, detail="Alelos dominante e recessivo devem ser caracteres únicos e diferentes.")
    def validate_and_normalize_genotype(genotype: str, dA: str, rA: str) -> str:
        if len(genotype) != 2: raise HTTPException(status_code=400, detail=f"Genótipo '{genotype}' inválido. Deve ter 2 alelos.")
        normalized_alleles = []
        for allele_char in genotype:
            if allele_char.upper() == dA: normalized_alleles.append(dA)
            elif allele_char.lower() == rA: normalized_alleles.append(rA)
            else: raise HTTPException(status_code=400, detail=f"Alelo '{allele_char}' no genótipo '{genotype}' não corresponde aos alelos definidos ({dA}, {rA}).")
        if normalized_alleles[0] == rA and normalized_alleles[1] == dA: return dA + rA
        return "".join(normalized_alleles)
    p1_genotype = validate_and_normalize_genotype(params.parent1_genotype, dom_allele, rec_allele)
    p2_genotype = validate_and_normalize_genotype(params.parent2_genotype, dom_allele, rec_allele)
    p1_alleles = [p1_genotype[0], p1_genotype[1]]
    p2_alleles = [p2_genotype[0], p2_genotype[1]]
    punnett_square_genotypes: List[List[str]] = [["", ""], ["", ""]]
    prole_genotypes_list: List[str] = []
    for i in range(2):
        for j in range(2):
            allele_pair = sorted([p1_alleles[i], p2_alleles[j]], key=lambda x: x == rec_allele)
            offspring_g = "".join(allele_pair)
            punnett_square_genotypes[i][j] = offspring_g
            prole_genotypes_list.append(offspring_g)
    genotype_counts = Counter(prole_genotypes_list)
    total_offspring = len(prole_genotypes_list)
    offspring_genotype_proportions: List[GenotypeProportion] = []
    for genotype, count in sorted(genotype_counts.items()):
        offspring_genotype_proportions.append(GenotypeProportion(genotype=genotype, count=count, fraction=f"{count}/{total_offspring}", percentage=round((count / total_offspring) * 100, 2)))
    phenotype_map = {params.dominant_phenotype_description: [], params.recessive_phenotype_description: []}
    if dom_allele+dom_allele not in phenotype_map[params.dominant_phenotype_description]: phenotype_map[params.dominant_phenotype_description].append(dom_allele+dom_allele)
    if dom_allele+rec_allele not in phenotype_map[params.dominant_phenotype_description]: phenotype_map[params.dominant_phenotype_description].append(dom_allele+rec_allele)
    if rec_allele+dom_allele not in phenotype_map[params.dominant_phenotype_description] and dom_allele+rec_allele != rec_allele+dom_allele : phenotype_map[params.dominant_phenotype_description].append(rec_allele+dom_allele)
    if rec_allele+rec_allele not in phenotype_map[params.recessive_phenotype_description]: phenotype_map[params.recessive_phenotype_description].append(rec_allele+rec_allele)
    phenotype_counts = Counter()
    for g_obj in offspring_genotype_proportions:
        genotype_str = g_obj.genotype
        if dom_allele in genotype_str: phenotype_counts[params.dominant_phenotype_description] += g_obj.count
        else: phenotype_counts[params.recessive_phenotype_description] += g_obj.count
    offspring_phenotype_proportions: List[PhenotypeProportion] = []
    for phenotype_desc, count in sorted(phenotype_counts.items()):
        if count > 0:
            associated_genotypes_for_pheno = []
            if phenotype_desc == params.dominant_phenotype_description: associated_genotypes_for_pheno = [g for g in genotype_counts.keys() if dom_allele in g]
            else: associated_genotypes_for_pheno = [g for g in genotype_counts.keys() if dom_allele not in g]
            offspring_phenotype_proportions.append(PhenotypeProportion(phenotype_description=phenotype_desc, count=count, fraction=f"{count}/{total_offspring}", percentage=round((count / total_offspring) * 100, 2), associated_genotypes=sorted(list(set(associated_genotypes_for_pheno)))))
    updated_params = params.copy(update={"parent1_genotype": p1_genotype, "parent2_genotype": p2_genotype, "dominant_allele": dom_allele, "recessive_allele": rec_allele})
    return MendelianCrossResult(parent1_alleles=p1_alleles, parent2_alleles=p2_alleles, punnett_square=punnett_square_genotypes, offspring_genotypes=offspring_genotype_proportions, offspring_phenotypes=offspring_phenotype_proportions, parameters_used=updated_params)

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

# Endpoint da API para Simulação de Genética Mendeliana (Adicionar este)
@app.post("/api/simulation/biology/mendelian-genetics/start", response_model=MendelianCrossResult)
async def start_mendelian_cross_simulation(params: MendelianCrossParams):
    return perform_mendelian_cross_simulation(params)

# Endpoint raiz (Existente)
@app.get("/")
async def read_root():
    return {"message": "Bem-vindo ao Simulador de Experimentos Educativos API"}

# Modelo Pydantic placeholder para dados de simulação a serem salvos
class SimulationData(BaseModel):
    experiment_type: str # ex: "acid-base", "projectile-motion", "mendelian-genetics"
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
