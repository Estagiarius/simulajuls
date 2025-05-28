from fastapi import FastAPI, HTTPException # Adicionado HTTPException
from pydantic import BaseModel
from typing import List, Optional
from fastapi.middleware.cors import CORSMiddleware
import math # Adicionar import para math.log10

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

# Função para realizar a simulação
def perform_acid_base_simulation(params: AcidBaseSimulationParams) -> AcidBaseSimulationResult:
    # Converter volumes para Litros para cálculo de mols
    acid_volume_l = params.acid_volume / 1000
    base_volume_l = params.base_volume / 1000

    mols_h_plus = params.acid_concentration * acid_volume_l
    mols_oh_minus = params.base_concentration * base_volume_l

    total_volume_l = acid_volume_l + base_volume_l
    total_volume_ml = total_volume_l * 1000

    final_ph: float
    final_poh: Optional[float] = None
    excess_reactant_val: Optional[str] = None
    status_val: str
    message_val: Optional[str] = None

    if abs(mols_h_plus - mols_oh_minus) < 1e-9:  # Considerar neutralização com uma pequena tolerância
        final_ph = 7.0
        final_poh = 7.0
        excess_reactant_val = "Nenhum"
        status_val = "Neutra"
        message_val = "Neutralização completa."
    elif mols_h_plus > mols_oh_minus:
        mols_h_plus_excess = mols_h_plus - mols_oh_minus
        concentration_h_plus_final = mols_h_plus_excess / total_volume_l
        if concentration_h_plus_final <= 0: # Evitar log de zero ou negativo
             final_ph = 14.0 # Ou algum valor indicando erro ou alta basicidade
             message_val = "Concentração de H+ excesso resultou em valor não positivo."
        else:
             final_ph = -math.log10(concentration_h_plus_final)
        excess_reactant_val = "H+"
        status_val = "Ácida"
        if final_ph < 0: final_ph = 0 # pH não deve ser negativo
        final_poh = 14.0 - final_ph
    else: # mols_OH_minus > mols_H_plus
        mols_oh_minus_excess = mols_oh_minus - mols_h_plus
        concentration_oh_minus_final = mols_oh_minus_excess / total_volume_l
        if concentration_oh_minus_final <= 0: # Evitar log de zero ou negativo
            final_poh = 14.0 # Ou algum valor indicando erro ou alta acidez
            message_val = "Concentração de OH- excesso resultou em valor não positivo."
        else:
            final_poh = -math.log10(concentration_oh_minus_final)
        
        if final_poh < 0: final_poh = 0 # pOH não deve ser negativo
        final_ph = 14.0 - final_poh
        excess_reactant_val = "OH-"
        status_val = "Básica"
        
    # Arredondar pH e pOH para 2 casas decimais
    final_ph = round(final_ph, 2)
    if final_poh is not None:
        final_poh = round(final_poh, 2)

    indicator_color_val: Optional[str] = None
    if params.indicator_name:
        # Normalizar o nome do indicador para minúsculas para comparação case-insensitive
        indicator_name_lower = params.indicator_name.strip().lower()
        if indicator_name_lower == "fenolftaleína":
            if final_ph < 8.2:
                indicator_color_val = "Incolor"
            elif final_ph <= 10.0: 
                indicator_color_val = "Rosa claro/Róseo"
            else: # pH > 10.0
                indicator_color_val = "Carmim/Magenta"
        elif indicator_name_lower == "azul de bromotimol":
            if final_ph < 6.0:
                indicator_color_val = "Amarelo"
            elif final_ph <= 7.6:
                indicator_color_val = "Verde"
            else: # pH > 7.6
                indicator_color_val = "Azul"
        else:
            indicator_color_val = "Indicador não reconhecido"
            message_val = (message_val + " " if message_val else "") + f"Indicador '{params.indicator_name}' não suportado."


    return AcidBaseSimulationResult(
        final_ph=final_ph,
        final_poh=final_poh,
        total_volume_ml=round(total_volume_ml, 2),
        mols_h_plus_initial=round(mols_h_plus, 9), 
        mols_oh_minus_initial=round(mols_oh_minus, 9),
        excess_reactant=excess_reactant_val,
        status=status_val,
        indicator_color=indicator_color_val,
        message=message_val
    )

# 3. Endpoints da API (Existentes e Novos)
@app.get("/api/experiments", response_model=List[Experiment])
async def get_experiments():
    return mock_experiments_data

@app.post("/api/simulation/chemistry/acid-base/start", response_model=AcidBaseSimulationResult)
async def start_acid_base_simulation(params: AcidBaseSimulationParams):
    if params.acid_concentration <= 0 or params.acid_volume <= 0 or params.base_concentration <= 0 or params.base_volume <= 0:
        raise HTTPException(status_code=400, detail="Concentrações e volumes devem ser positivos e maiores que zero.")
        
    return perform_acid_base_simulation(params)

# Endpoint raiz (Existente)
@app.get("/")
async def read_root():
    return {"message": "Bem-vindo ao Simulador de Experimentos Educativos API"}

# Modelo Pydantic placeholder para dados de simulação a serem salvos (NOVO)
class SimulationData(BaseModel):
    experiment_type: str # ex: "acid-base", "projectile-motion"
    params: dict
    results: dict

# Esqueleto do endpoint para salvar simulações (NOVO)
@app.post("/api/simulations/save", status_code=501)
async def save_simulation(simulation_data: SimulationData):
    # A lógica de salvar em um banco de dados ou arquivo viria aqui.
    # Por enquanto, apenas retornamos que não está implementado.
    return {"message": "Funcionalidade de salvar simulação ainda não implementada."}

# Esqueleto do endpoint para carregar uma simulação específica (NOVO)
@app.get("/api/simulations/{simulation_id}", status_code=501)
async def get_simulation(simulation_id: str): # Usar str para IDs que podem não ser numéricos
    # A lógica de buscar em um banco de dados ou arquivo viria aqui.
    # Por enquanto, apenas retornamos que não está implementado.
    return {"message": f"Funcionalidade de carregar simulação com ID {simulation_id} ainda não implementada."}
