from fastapi import FastAPI
from pydantic import BaseModel
from typing import List, Optional
from fastapi.middleware.cors import CORSMiddleware # Importar

# 1. Modelos Pydantic
class Experiment(BaseModel):
    id: int
    name: str
    category: str
    description: str
    image_url: Optional[str] = None

# Inicializa o aplicativo FastAPI
app = FastAPI()

# Adicionar middleware CORS
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

# 2. Dados Mock (Exemplo)
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

# 3. Endpoint da API
@app.get("/api/experiments", response_model=List[Experiment])
async def get_experiments():
    return mock_experiments_data

@app.get("/")
async def read_root():
    return {"message": "Bem-vindo ao Simulador de Experimentos Educativos API"}
