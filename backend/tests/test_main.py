from fastapi.testclient import TestClient
from backend.main import app # Ajuste o import conforme a localização de 'app'

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
