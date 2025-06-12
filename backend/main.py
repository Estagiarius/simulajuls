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

class Experiment(BaseModel):
    id: str
    name: str
    category: str
    description: str
    image_url: Optional[str] = "/images/placeholder.png"

class SimulationData(BaseModel):
    experiment_type: str
    params: Dict[str, Any]
    results: Dict[str, Any]

# --- FastAPI App Initialization ---
# app = FastAPI()

# CORS Setup
# origins = ["*"]
# app.add_middleware(
#     CORSMiddleware,
#     allow_origins=origins,
#     allow_credentials=True,
#     allow_methods=["*"],
#     allow_headers=["*"],
# )

# --- Saved Simulations Directory Setup ---
SAVED_SIMULATIONS_DIR = Path(__file__).parent / "saved_simulations"
SAVED_SIMULATIONS_DIR.mkdir(parents=True, exist_ok=True)


# --- Dynamic Module Discovery and Registry ---

def discover_simulation_modules() -> Dict[str, SimulationModule]:
    discovered_modules_map: Dict[str, SimulationModule] = {}
    base_package_path = "simulations"
    package_dir = os.path.join(os.path.dirname(__file__), "simulations")

    if not os.path.exists(package_dir):
        print(f"Warning: Simulation package directory {package_dir} does not exist.")
        return discovered_modules_map

    for category_name in os.listdir(package_dir):
        category_path = os.path.join(package_dir, category_name)
        if os.path.isdir(category_path) and not category_name.startswith("__"):
            for module_file_name in os.listdir(category_path):
                if module_file_name.endswith("_module.py"):
                    module_name_import = f"{base_package_path}.{category_name}.{module_file_name[:-3]}"
                    try:
                        module_import = importlib.import_module(module_name_import)
                        for name, cls in inspect.getmembers(module_import, inspect.isclass):
                            if issubclass(cls, SimulationModule) and \
                               cls is not SimulationModule and \
                               cls.__module__ == module_name_import:
                                try:
                                    instance = cls()
                                    discovered_modules_map[instance.get_name()] = instance
                                except Exception as e:
                                    print(f"Error instantiating module {cls.__name__} from {module_name_import}: {e}")
                    except ImportError as e:
                        print(f"Error importing module {module_name_import}: {e}")
                    except Exception as e:
                        print(f"General error processing module file {module_name_import}: {e}")

    if not discovered_modules_map:
        print("Warning: No simulation modules were discovered.")
    else:
        print(f"Discovered simulation modules: {list(discovered_modules_map.keys())}")
    return discovered_modules_map

simulation_modules_registry: Dict[str, SimulationModule] = discover_simulation_modules()

# --- API Endpoints ---

# @app.get("/api/experiments", response_model=List[Experiment])
# async def get_experiments():
#     experiments_data = []
#     for mod_name, mod_instance in simulation_modules_registry.items():
#         experiments_data.append(
#             Experiment(
#                 id=mod_instance.get_name(),
#                 name=mod_instance.get_display_name(),
#                 category=mod_instance.get_category(),
#                 description=mod_instance.get_description()
#             )
#         )
#     return experiments_data

# @app.post("/api/simulation/{experiment_name}/start")
# async def start_generic_simulation(experiment_name: str, request: Request):
#     module_instance = simulation_modules_registry.get(experiment_name)
#     if not module_instance:
#         raise HTTPException(status_code=404, detail=f"Experiment '{experiment_name}' not found.")

#     ParameterModel: Type[BaseSimulationParams] = module_instance.get_parameter_schema()

#     try:
#         payload_json = await request.json()
#     except Exception as e:
#         raise HTTPException(status_code=400, detail=f"Invalid JSON payload: {e}")

#     try:
#         params_object = ParameterModel.model_validate(payload_json)
#     except ValidationError as e:
#         raise HTTPException(status_code=422, detail=e.errors())
#     except Exception as e:
#         raise HTTPException(status_code=400, detail=f"Error processing parameters: {e}")

#     return module_instance.run_simulation(params_object)

# @app.post("/api/simulations/save", status_code=201)
# async def save_simulation(simulation_data: SimulationData):
#     simulation_id = str(uuid.uuid4())
#     file_path = SAVED_SIMULATIONS_DIR / f"{simulation_id}.json"

#     data_to_save = simulation_data.model_dump()
#     data_to_save["simulation_id"] = simulation_id

#     try:
#         with open(file_path, "w") as f:
#             json.dump(data_to_save, f, indent=4)
#     except IOError as e:
#         raise HTTPException(status_code=500, detail=f"Failed to save simulation data: {e}")

#     return {"message": "Simulation saved successfully", "simulation_id": simulation_id}

# @app.get("/api/simulations/{simulation_id}", response_model=Dict[str, Any])
# async def get_simulation(simulation_id: str):
#     # Validate simulation_id format to prevent directory traversal if it's part of a path
#     # A simple check: UUIDs have a fixed structure. A more robust check might involve regex.
#     try:
#         uuid.UUID(simulation_id, version=4)
#     except ValueError:
#         raise HTTPException(status_code=400, detail="Invalid simulation_id format.")

#     file_path = SAVED_SIMULATIONS_DIR / f"{simulation_id}.json"

#     if not file_path.is_file():
#         # It's good practice to ensure the path resolution is within the intended directory,
#         # though Path() operations are generally safer than raw string manipulations.
#         # For added security, one might check `file_path.resolve().parent == SAVED_SIMULATIONS_DIR.resolve()`.
#         raise HTTPException(status_code=404, detail="Simulation not found.")

#     try:
#         with open(file_path, "r") as f:
#             saved_data = json.load(f)
#         return saved_data
#     except IOError:
#         # This could be a permissions issue or other file system problem.
#         print(f"IOError reading simulation file: {file_path}") # Log for server admin
#         raise HTTPException(status_code=500, detail="Could not read simulation data from file.")
#     except json.JSONDecodeError:
#         # This indicates the file is corrupted or not valid JSON.
#         print(f"JSONDecodeError for simulation file: {file_path}") # Log for server admin
#         raise HTTPException(status_code=500, detail="Error decoding simulation data from file.")
#     except Exception as e:
#         # Catch-all for other unexpected errors.
#         print(f"Unexpected error loading simulation {simulation_id}: {e}") # Log for server admin
#         raise HTTPException(status_code=500, detail="An unexpected error occurred while loading the simulation.")

# # Root endpoint
# @app.get("/")
# async def read_root():
#     return {"message": "Bem-vindo ao Simulador de Experimentos Educativos API"}

if __name__ == "__main__":
    print(simulation_modules_registry)
