import importlib
import inspect
import os
from typing import List, Optional, Dict, Any, Type

from fastapi import FastAPI, HTTPException, Request
from pydantic import BaseModel, ValidationError

# Base simulation class for type hinting and discovery logic
from backend.simulations.base_simulation import SimulationModule, BaseSimulationParams, BaseSimulationResult

# CORS Middleware
from fastapi.middleware.cors import CORSMiddleware

# Additional imports for saving/loading simulations
import uuid
import json
from pathlib import Path

# --- Pydantic Models ---
# Define os modelos de dados Pydantic que serão usados para validação e serialização de dados nas requisições e respostas da API.

class Experiment(BaseModel):
    # Modelo Pydantic para representar um experimento.
    # Usado para listar os experimentos disponíveis na interface do usuário.
    id: str
    name: str
    category: str
    description: str
    image_url: Optional[str] = "/images/placeholder.png"

class SimulationData(BaseModel):
    # Modelo Pydantic para os dados de uma simulação específica que são salvos ou carregados.
    # Contém o tipo de experimento, os parâmetros de entrada e os resultados da simulação.
    experiment_type: str
    params: Dict[str, Any]
    results: Dict[str, Any]

# --- FastAPI App Initialization ---
# Cria uma instância da aplicação FastAPI.
app = FastAPI()

# CORS Setup
# Configuração do Cross-Origin Resource Sharing (CORS).
# Permite que a interface do usuário (frontend) acesse a API a partir de diferentes origens (domínios).
origins = ["*"]  # Permite todas as origens, ideal para desenvolvimento mas pode ser restrito em produção.
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# --- Saved Simulations Directory Setup ---
# Configura o diretório onde os dados das simulações salvas serão armazenados.
# O diretório 'saved_simulations' é criado dentro do diretório 'backend'.
# Path(__file__).parent refere-se ao diretório do arquivo atual (main.py),
# e / "saved_simulations" concatena para formar o caminho completo.
# mkdir(parents=True, exist_ok=True) cria o diretório se não existir;
# parents=True permite criar diretórios pai necessários, e exist_ok=True não gera erro se o diretório já existir.
SAVED_SIMULATIONS_DIR = Path(__file__).parent / "saved_simulations"
SAVED_SIMULATIONS_DIR.mkdir(parents=True, exist_ok=True)


# --- Dynamic Module Discovery and Registry ---
# Esta seção é responsável por encontrar e registrar dinamicamente os módulos de simulação.
# Isso permite adicionar novas simulações ao sistema sem modificar o código principal da API.

def discover_simulation_modules() -> Dict[str, SimulationModule]:
    # Descobre e carrega módulos de simulação de dentro do pacote 'backend.simulations'.
    # Retorna um dicionário mapeando nomes de experimentos para suas instâncias de módulo.
    discovered_modules_map: Dict[str, SimulationModule] = {}
    base_package_path = "backend.simulations"  # Caminho base para importação dos módulos de simulação.
    package_dir = os.path.join(os.path.dirname(__file__), "simulations") # Caminho do diretório físico dos pacotes de simulações.

    if not os.path.exists(package_dir):
        # Emite um aviso se o diretório de simulações não for encontrado.
        print(f"Aviso: O diretório do pacote de simulações {package_dir} não existe.")
        return discovered_modules_map

    # Itera sobre cada subdiretório (categoria) dentro do diretório 'simulations'.
    for category_name in os.listdir(package_dir):
        category_path = os.path.join(package_dir, category_name)
        # Verifica se é um diretório e não é um diretório especial (como '__pycache__').
        if os.path.isdir(category_path) and not category_name.startswith("__"):
            # Itera sobre cada arquivo no diretório da categoria.
            for module_file_name in os.listdir(category_path):
                # Procura por arquivos que terminam com '_module.py', convenção para módulos de simulação.
                if module_file_name.endswith("_module.py"):
                    # Constrói o nome completo do módulo para importação (ex: backend.simulations.fisica.movimento_module).
                    module_name_import = f"{base_package_path}.{category_name}.{module_file_name[:-3]}"
                    try:
                        # Importa dinamicamente o módulo.
                        module_import = importlib.import_module(module_name_import)
                        # Inspeciona o módulo importado para encontrar classes.
                        for name, cls in inspect.getmembers(module_import, inspect.isclass):
                            # Verifica se a classe é uma subclasse de SimulationModule,
                            # não é a própria SimulationModule, e pertence ao módulo que acabamos de importar.
                            if issubclass(cls, SimulationModule) and \
                               cls is not SimulationModule and \
                               cls.__module__ == module_name_import:
                                try:
                                    # Cria uma instância da classe do módulo de simulação.
                                    instance = cls()
                                    # Adiciona a instância ao mapa de módulos descobertos, usando o nome do experimento como chave.
                                    discovered_modules_map[instance.get_name()] = instance
                                except Exception as e:
                                    print(f"Erro ao instanciar o módulo {cls.__name__} de {module_name_import}: {e}")
                    except ImportError as e:
                        print(f"Erro ao importar o módulo {module_name_import}: {e}")
                    except Exception as e:
                        print(f"Erro geral ao processar o arquivo do módulo {module_name_import}: {e}")

    if not discovered_modules_map:
        # Emite um aviso se nenhum módulo de simulação for encontrado.
        print("Aviso: Nenhum módulo de simulação foi descoberto.")
    else:
        # Imprime os nomes dos módulos de simulação descobertos.
        print(f"Módulos de simulação descobertos: {list(discovered_modules_map.keys())}")
    return discovered_modules_map

# Registra os módulos de simulação descobertos globalmente para serem usados pela API.
simulation_modules_registry: Dict[str, SimulationModule] = discover_simulation_modules()

# --- API Endpoints ---
# Define os endpoints da API que serão usados pela interface do usuário para interagir com as simulações.

@app.get("/api/experiments", response_model=List[Experiment])
async def get_experiments():
    # Endpoint para listar todos os experimentos (simulações) disponíveis.
    # Retorna uma lista de objetos Experiment, cada um descrevendo uma simulação.
    # Não requer parâmetros.
    # Resposta:
    #   - 200 OK: Retorna uma lista de informações sobre os experimentos.
    #       - id (str): Identificador único do experimento.
    #       - name (str): Nome de exibição do experimento.
    #       - category (str): Categoria do experimento (ex: Física, Química).
    #       - description (str): Breve descrição do experimento.
    #       - image_url (Optional[str]): URL para uma imagem representativa do experimento.
    experiments_data = []
    for mod_name, mod_instance in simulation_modules_registry.items():
        experiments_data.append(
            Experiment(
                id=mod_instance.get_name(),
                name=mod_instance.get_display_name(),
                category=mod_instance.get_category(),
                description=mod_instance.get_description()
            )
        )
    return experiments_data

@app.post("/api/simulation/{experiment_name}/start")
async def start_generic_simulation(experiment_name: str, request: Request):
    # Endpoint para iniciar uma nova simulação para um determinado experimento.
    # Parâmetros:
    #   - experiment_name (str): O nome do experimento a ser iniciado (parte da URL).
    #   - request (Request): O corpo da requisição HTTP, esperado em formato JSON,
    #                        contendo os parâmetros específicos para a simulação.
    # Resposta:
    #   - 200 OK: Retorna os resultados da simulação, conforme definido pelo módulo de simulação específico.
    #   - 404 Not Found: Se o experiment_name não corresponder a nenhum módulo de simulação registrado.
    #   - 400 Bad Request: Se o payload da requisição não for um JSON válido ou se houver erro no processamento dos parâmetros.
    #   - 422 Unprocessable Entity: Se os parâmetros fornecidos no payload JSON não passarem na validação do modelo Pydantic do experimento.
    module_instance = simulation_modules_registry.get(experiment_name)
    if not module_instance:
        # Se o módulo não for encontrado no registro, retorna um erro 404.
        raise HTTPException(status_code=404, detail=f"Experimento '{experiment_name}' não encontrado.")

    # Obtém o esquema Pydantic para os parâmetros esperados por este módulo de simulação.
    ParameterModel: Type[BaseSimulationParams] = module_instance.get_parameter_schema()

    try:
        # Tenta parsear o corpo da requisição como JSON.
        payload_json = await request.json()
    except Exception as e:
        # Se o payload não for JSON válido, retorna um erro 400.
        raise HTTPException(status_code=400, detail=f"Payload JSON inválido: {e}")

    try:
        # Valida o JSON recebido contra o modelo Pydantic de parâmetros do módulo.
        params_object = ParameterModel.model_validate(payload_json)
    except ValidationError as e:
        # Se a validação falhar, retorna um erro 422 com os detalhes da validação.
        raise HTTPException(status_code=422, detail=e.errors())
    except Exception as e:
        # Outros erros durante o processamento dos parâmetros.
        raise HTTPException(status_code=400, detail=f"Erro ao processar parâmetros: {e}")

    # Executa a simulação com os parâmetros validados e retorna o resultado.
    return module_instance.run_simulation(params_object)

@app.post("/api/simulations/save", status_code=201)
async def save_simulation(simulation_data: SimulationData):
    # Endpoint para salvar o estado de uma simulação (parâmetros e resultados).
    # Parâmetros:
    #   - simulation_data (SimulationData): Corpo da requisição JSON contendo os dados da simulação a serem salvos.
    #     Espera um objeto com `experiment_type`, `params` e `results`.
    # Resposta:
    #   - 201 Created: Retorna uma mensagem de sucesso e o ID da simulação salva.
    #     - message (str): "Simulação salva com sucesso".
    #     - simulation_id (str): O UUID gerado para esta simulação salva.
    #   - 500 Internal Server Error: Se houver um erro ao escrever o arquivo no servidor.
    simulation_id = str(uuid.uuid4())  # Gera um ID único para a simulação.
    file_path = SAVED_SIMULATIONS_DIR / f"{simulation_id}.json"  # Define o caminho do arquivo para salvar a simulação.

    data_to_save = simulation_data.model_dump()  # Converte o modelo Pydantic para um dicionário.
    data_to_save["simulation_id"] = simulation_id # Adiciona o ID da simulação aos dados a serem salvos.

    try:
        # Abre o arquivo no modo de escrita ('w') e salva os dados da simulação em formato JSON.
        with open(file_path, "w") as f:
            json.dump(data_to_save, f, indent=4)  # indent=4 para formatação legível do JSON.
    except IOError as e:
        # Se ocorrer um erro de E/S (ex: permissão negada, disco cheio), retorna um erro 500.
        raise HTTPException(status_code=500, detail=f"Falha ao salvar os dados da simulação: {e}")

    return {"message": "Simulação salva com sucesso", "simulation_id": simulation_id}

@app.get("/api/simulations/{simulation_id}", response_model=Dict[str, Any])
async def get_simulation(simulation_id: str):
    # Endpoint para carregar os dados de uma simulação previamente salva.
    # Parâmetros:
    #   - simulation_id (str): O UUID da simulação a ser carregada (parte da URL).
    # Resposta:
    #   - 200 OK: Retorna os dados da simulação salva em formato JSON.
    #   - 400 Bad Request: Se o `simulation_id` fornecido não tiver um formato UUID válido.
    #   - 404 Not Found: Se nenhum arquivo de simulação corresponder ao `simulation_id` fornecido.
    #   - 500 Internal Server Error: Se houver um erro ao ler o arquivo ou se o arquivo estiver corrompido (JSON inválido).

    # Valida o formato do simulation_id para prevenir ataques de travessia de diretório e garantir que é um UUID.
    # Uma verificação simples: UUIDs têm uma estrutura fixa. Uma verificação mais robusta pode usar regex.
    try:
        uuid.UUID(simulation_id, version=4)
    except ValueError:
        # Se o ID não for um UUID v4 válido, retorna erro 400.
        raise HTTPException(status_code=400, detail="Formato de simulation_id inválido.")

    file_path = SAVED_SIMULATIONS_DIR / f"{simulation_id}.json" # Constrói o caminho para o arquivo da simulação.

    if not file_path.is_file():
        # Verifica se o arquivo da simulação realmente existe.
        # É uma boa prática garantir que a resolução do caminho esteja dentro do diretório pretendido,
        # embora as operações Path() sejam geralmente mais seguras do que manipulações de string brutas.
        # Para segurança adicional, pode-se verificar `file_path.resolve().parent == SAVED_SIMULATIONS_DIR.resolve()`.
        raise HTTPException(status_code=404, detail="Simulação não encontrada.")

    try:
        # Abre o arquivo da simulação em modo de leitura ('r').
        with open(file_path, "r") as f:
            saved_data = json.load(f) # Carrega os dados do arquivo JSON.
        return saved_data
    except IOError:
        # Erro de E/S pode ser um problema de permissão ou outro problema do sistema de arquivos.
        print(f"IOError ao ler o arquivo da simulação: {file_path}") # Log para o administrador do servidor.
        raise HTTPException(status_code=500, detail="Não foi possível ler o arquivo da simulação.")
    except json.JSONDecodeError:
        # Indica que o arquivo está corrompido ou não é um JSON válido.
        print(f"JSONDecodeError para o arquivo da simulação: {file_path}") # Log para o administrador do servidor.
        raise HTTPException(status_code=500, detail="Erro ao decodificar os dados da simulação do arquivo.")
    except Exception as e:
        # Captura todos os outros erros inesperados.
        print(f"Erro inesperado ao carregar a simulação {simulation_id}: {e}") # Log para o administrador do servidor.
        raise HTTPException(status_code=500, detail="Ocorreu um erro inesperado ao carregar a simulação.")

# Root endpoint
@app.get("/")
async def read_root():
    # Endpoint raiz da API.
    # Retorna uma mensagem de boas-vindas.
    # Não requer parâmetros.
    # Resposta:
    #   - 200 OK: Retorna um objeto JSON com uma mensagem.
    #     - message (str): "Bem-vindo ao Simulador de Experimentos Educativos API"
    return {"message": "Bem-vindo ao Simulador de Experimentos Educativos API"}
