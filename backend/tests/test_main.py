from fastapi.testclient import TestClient
from backend.main import app # Ajuste o import conforme a localização de 'app'
# from backend.main import AcidBaseSimulationParams, perform_acid_base_simulation # Para testes diretos da lógica

client = TestClient(app)

def test_read_root():
    response = client.get("/")
    assert response.status_code == 200
    assert response.json() == {"message": "Bem-vindo ao Simulador de Experimentos Educativos API"}

def test_get_experiments():
    response = client.get("/api/experiments")
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    # Verifica se há pelo menos um experimento (ajuste se o mock data puder estar vazio)
    assert len(data) > 0 
    # Verifica a estrutura do primeiro experimento (ajuste conforme seus modelos Pydantic)
    if len(data) > 0:
        experiment = data[0]
        assert "id" in experiment
        assert "name" in experiment
        assert "category" in experiment
        assert "description" in experiment
        # image_url é opcional, então não precisa estar presente em todos

# Exemplo de teste para verificar um experimento específico, se necessário
# def test_get_specific_experiment_details():
#     response = client.get("/api/experiments")
#     assert response.status_code == 200
#     data = response.json()
#     assert any(exp['name'] == "Reação Ácido-Base" and exp['category'] == "Química" for exp in data)

# Testes para o endpoint de simulação ácido-base
def test_simulation_acidic_result():
    response = client.post("/api/simulation/chemistry/acid-base/start", json={
        "acid_concentration": 0.1, "acid_volume": 50,
        "base_concentration": 0.1, "base_volume": 25,
        "indicator_name": "Fenolftaleína"
    })
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "Ácida"
    assert data["indicator_color"] == "Incolor" # pH esperado < 8.2
    assert data["final_ph"] < 7.0

def test_simulation_basic_result():
    response = client.post("/api/simulation/chemistry/acid-base/start", json={
        "acid_concentration": 0.1, "acid_volume": 25,
        "base_concentration": 0.1, "base_volume": 50,
        "indicator_name": "Fenolftaleína"
    })
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "Básica"
    # Para Fenolftaleína, pH > 8.2 (aproximadamente) deve dar cor.
    # O pH exato para 0.1M/25ml ácido vs 0.1M/50ml base será bem básico.
    assert data["indicator_color"] in ["Rosa claro/Róseo", "Carmim/Magenta"] 
    assert data["final_ph"] > 7.0

def test_simulation_neutral_result():
    response = client.post("/api/simulation/chemistry/acid-base/start", json={
        "acid_concentration": 0.1, "acid_volume": 50,
        "base_concentration": 0.1, "base_volume": 50,
        "indicator_name": "Azul de Bromotimol"
    })
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "Neutra"
    assert data["final_ph"] == 7.0
    assert data["indicator_color"] == "Verde" # Azul de Bromotimol é verde em pH 6.0-7.6

def test_simulation_bromothymol_blue_acidic():
    response = client.post("/api/simulation/chemistry/acid-base/start", json={
        "acid_concentration": 0.2, "acid_volume": 50, # Mais ácido
        "base_concentration": 0.1, "base_volume": 50,
        "indicator_name": "Azul de Bromotimol"
    })
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "Ácida"
    assert data["indicator_color"] == "Amarelo" # pH < 6.0

def test_simulation_bromothymol_blue_basic():
    response = client.post("/api/simulation/chemistry/acid-base/start", json={
        "acid_concentration": 0.1, "acid_volume": 50,
        "base_concentration": 0.2, "base_volume": 50, # Mais base
        "indicator_name": "Azul de Bromotimol"
    })
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "Básica"
    assert data["indicator_color"] == "Azul" # pH > 7.6

def test_simulation_invalid_input_negative_concentration():
    response = client.post("/api/simulation/chemistry/acid-base/start", json={
        "acid_concentration": -0.1, "acid_volume": 50,
        "base_concentration": 0.1, "base_volume": 50
    })
    assert response.status_code == 400 # Esperando erro de validação do endpoint
    # A mensagem de erro pode vir do HTTPException que adicionamos no endpoint
    assert "Concentrações e volumes devem ser positivos" in response.json().get("detail", "")

def test_simulation_invalid_input_zero_volume():
    response = client.post("/api/simulation/chemistry/acid-base/start", json={
        "acid_concentration": 0.1, "acid_volume": 0,
        "base_concentration": 0.1, "base_volume": 50
    })
    assert response.status_code == 400
    assert "Concentrações e volumes devem ser positivos" in response.json().get("detail", "")

# Teste direto da lógica (opcional, mas recomendado)
# from backend.main import perform_acid_base_simulation, AcidBaseSimulationParams

# def test_direct_simulation_logic_neutral():
#     params = AcidBaseSimulationParams(
#         acid_concentration=0.1, acid_volume=50,
#         base_concentration=0.1, base_volume=50,
#         indicator_name="Fenolftaleína"
#     )
#     result = perform_acid_base_simulation(params)
#     assert result.final_ph == 7.0
#     assert result.status == "Neutra"
#     assert result.indicator_color == "Incolor" # Fenolftaleína em pH 7 é incolor
