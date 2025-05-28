from fastapi.testclient import TestClient
from backend.main import app # Ajuste o import conforme a localização de 'app'
# from backend.main import AcidBaseSimulationParams, perform_acid_base_simulation # Para testes diretos da lógica
# from backend.main import ProjectileLaunchParams, perform_projectile_launch_simulation # Para testes diretos da lógica de lançamento
# from backend.main import MendelianCrossParams, perform_mendelian_cross_simulation # Para testes diretos da lógica de genética

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

# Testes para o endpoint de simulação de Lançamento Oblíquo
def test_projectile_simulation_default_params():
    response = client.post("/api/simulation/physics/projectile-launch/start", json={
        "initial_velocity": 20,
        "launch_angle": 45,
        # initial_height e gravity usarão defaults do modelo (0.0 e 9.81)
    })
    assert response.status_code == 200
    data = response.json()
    assert data["max_range"] > 0
    assert data["max_height"] > 0
    assert data["total_time"] > 0
    assert len(data["trajectory"]) > 1 # Deve ter pelo menos o ponto inicial e final
    assert data["parameters_used"]["initial_velocity"] == 20
    assert data["parameters_used"]["launch_angle"] == 45
    assert data["parameters_used"]["initial_height"] == 0.0
    assert data["parameters_used"]["gravity"] == 9.81

def test_projectile_simulation_with_initial_height():
    response = client.post("/api/simulation/physics/projectile-launch/start", json={
        "initial_velocity": 20,
        "launch_angle": 30,
        "initial_height": 10,
        "gravity": 10 # Usar g=10 para facilitar cálculos mentais se necessário
    })
    assert response.status_code == 200
    data = response.json()
    assert data["max_range"] > 0
    assert data["max_height"] > 10 # Deve ser maior que a altura inicial
    assert data["total_time"] > 0
    assert data["trajectory"][0]["y"] == 10 # Ponto inicial na altura inicial
    assert data["trajectory"][-1]["y"] == 0 # Ponto final no solo

def test_projectile_simulation_invalid_velocity():
    response = client.post("/api/simulation/physics/projectile-launch/start", json={
        "initial_velocity": 0, "launch_angle": 45
    })
    assert response.status_code == 400
    assert "Velocidade inicial deve ser positiva" in response.json().get("detail", "")

def test_projectile_simulation_invalid_angle_too_low():
    response = client.post("/api/simulation/physics/projectile-launch/start", json={
        "initial_velocity": 10, "launch_angle": 0 
    })
    assert response.status_code == 400
    assert "Ângulo de lançamento deve estar entre 0 e 90 graus (exclusive)" in response.json().get("detail", "")
    
def test_projectile_simulation_invalid_angle_too_high():
    response = client.post("/api/simulation/physics/projectile-launch/start", json={
        "initial_velocity": 10, "launch_angle": 90
    })
    assert response.status_code == 400
    assert "Ângulo de lançamento deve estar entre 0 e 90 graus (exclusive)" in response.json().get("detail", "")

def test_projectile_simulation_invalid_height():
    response = client.post("/api/simulation/physics/projectile-launch/start", json={
        "initial_velocity": 10, "launch_angle": 45, "initial_height": -1
    })
    assert response.status_code == 400
    assert "Altura inicial não pode ser negativa" in response.json().get("detail", "")

def test_projectile_simulation_invalid_gravity():
    response = client.post("/api/simulation/physics/projectile-launch/start", json={
        "initial_velocity": 10, "launch_angle": 45, "gravity": 0
    })
    assert response.status_code == 400
    assert "Gravidade deve ser positiva" in response.json().get("detail", "")

# Exemplo de teste direto da lógica (se a função estiver importável)
# from backend.main import perform_projectile_launch_simulation, ProjectileLaunchParams
# def test_direct_projectile_logic():
#     params = ProjectileLaunchParams(initial_velocity=10, launch_angle=30, initial_height=5, gravity=10)
#     result = perform_projectile_launch_simulation(params)
#     assert result.max_height > 5
#     # Adicionar mais asserções específicas baseadas em cálculos manuais se desejado

# Testes para o endpoint de simulação de Genética Mendeliana
def test_mendelian_cross_homozygous_dominant_x_recessive():
    response = client.post("/api/simulation/biology/mendelian-genetics/start", json={
        "parent1_genotype": "AA",
        "parent2_genotype": "aa",
        "dominant_allele": "A",
        "recessive_allele": "a",
        "dominant_phenotype_description": "Dominante",
        "recessive_phenotype_description": "Recessivo"
    })
    assert response.status_code == 200
    data = response.json()
    # Quadro de Punnett esperado: [['Aa', 'Aa'], ['Aa', 'Aa']]
    assert data["punnett_square"] == [["Aa", "Aa"], ["Aa", "Aa"]]
    # Genótipos: 100% Aa
    assert len(data["offspring_genotypes"]) == 1
    assert data["offspring_genotypes"][0]["genotype"] == "Aa"
    assert data["offspring_genotypes"][0]["percentage"] == 100.0
    # Fenótipos: 100% Dominante
    assert len(data["offspring_phenotypes"]) == 1
    assert data["offspring_phenotypes"][0]["phenotype_description"] == "Dominante"
    assert data["offspring_phenotypes"][0]["percentage"] == 100.0

def test_mendelian_cross_heterozygous_x_heterozygous():
    response = client.post("/api/simulation/biology/mendelian-genetics/start", json={
        "parent1_genotype": "Aa",
        "parent2_genotype": "Aa"
        # Usar defaults para alelos e fenótipos
    })
    assert response.status_code == 200
    data = response.json()
    # Quadro de Punnett esperado: [['AA', 'Aa'], ['Aa', 'aa']] (ou ordem diferente mas mesmos conteúdos)
    # A lógica de ordenação interna pode variar, então verificamos os componentes
    flat_punnett = [item for sublist in data["punnett_square"] for item in sublist]
    assert sorted(flat_punnett) == sorted(["AA", "Aa", "Aa", "aa"])
    
    # Genótipos: 25% AA, 50% Aa, 25% aa
    genotypes = {g["genotype"]: g["percentage"] for g in data["offspring_genotypes"]}
    assert genotypes.get("AA") == 25.0
    assert genotypes.get("Aa") == 50.0
    assert genotypes.get("aa") == 25.0
    
    # Fenótipos: 75% Dominante, 25% Recessivo (usando defaults "Fenótipo Dominante", "Fenótipo Recessivo")
    phenotypes = {p["phenotype_description"]: p["percentage"] for p in data["offspring_phenotypes"]}
    assert phenotypes.get("Fenótipo Dominante") == 75.0
    assert phenotypes.get("Fenótipo Recessivo") == 25.0

def test_mendelian_cross_heterozygous_x_recessive():
    response = client.post("/api/simulation/biology/mendelian-genetics/start", json={
        "parent1_genotype": "Aa",
        "parent2_genotype": "aa",
        "dominant_allele": "B", # Testar com outros alelos
        "recessive_allele": "b",
        "dominant_phenotype_description": "Preto",
        "recessive_phenotype_description": "Branco"
    })
    assert response.status_code == 200
    data = response.json()
    flat_punnett = sorted([item for sublist in data["punnett_square"] for item in sublist])
    # O backend normaliza 'Ba' para 'Bb' e 'bB' para 'Bb'
    # E 'aa' (se input) para 'bb' (se recessive_allele='b')
    # Então, para Aa x aa com B/b, esperamos Bb, Bb, bb, bb
    assert flat_punnett == sorted(["Bb", "Bb", "bb", "bb"]) 
    
    genotypes = {g["genotype"]: g["percentage"] for g in data["offspring_genotypes"]}
    assert genotypes.get("Bb") == 50.0 
    assert genotypes.get("bb") == 50.0
    
    phenotypes = {p["phenotype_description"]: p["percentage"] for p in data["offspring_phenotypes"]}
    assert phenotypes.get("Preto") == 50.0
    assert phenotypes.get("Branco") == 50.0

def test_mendelian_cross_invalid_genotype_length():
    response = client.post("/api/simulation/biology/mendelian-genetics/start", json={
        "parent1_genotype": "A", "parent2_genotype": "Aa"
    })
    assert response.status_code == 400
    assert "Genótipo 'A' inválido. Deve ter 2 alelos." in response.json().get("detail", "")

def test_mendelian_cross_invalid_genotype_char():
    response = client.post("/api/simulation/biology/mendelian-genetics/start", json={
        "parent1_genotype": "AX", "parent2_genotype": "Aa"
    })
    assert response.status_code == 400
    # A mensagem exata pode variar dependendo da implementação da validação de alelos
    assert "Alelo 'X' no genótipo 'AX' não corresponde aos alelos definidos" in response.json().get("detail", "")


def test_mendelian_cross_invalid_allele_definition_same():
    response = client.post("/api/simulation/biology/mendelian-genetics/start", json={
        "parent1_genotype": "Aa", "parent2_genotype": "Aa",
        "dominant_allele": "A", "recessive_allele": "A"
    })
    assert response.status_code == 400
    assert "Alelos dominante e recessivo devem ser caracteres únicos e diferentes." in response.json().get("detail", "")

def test_mendelian_cross_invalid_allele_definition_long():
    response = client.post("/api/simulation/biology/mendelian-genetics/start", json={
        "parent1_genotype": "Aa", "parent2_genotype": "Aa",
        "dominant_allele": "Ab", "recessive_allele": "a"
    })
    assert response.status_code == 400
    assert "Alelos dominante e recessivo devem ser caracteres únicos e diferentes." in response.json().get("detail", "")
