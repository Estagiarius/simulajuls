<script>
  import { fade } from 'svelte/transition';

  const experimentDetails = {
    name: "Lançamento Oblíquo",
    description: "Simule o lançamento de um projétil, definindo velocidade inicial, ângulo e outros parâmetros. Observe a trajetória, alcance e altura máxima."
  };

  let params = {
    initial_velocity: 20, // m/s
    launch_angle: 45, // graus
    initial_height: 0, // m
    gravity: 9.81 // m/s^2
  };

  let simulationResult = null;
  let isLoading = false;
  let error = null;

  async function startSimulation() {
    isLoading = true;
    error = null;
    simulationResult = null;
    
    // Garantir que os tipos de dados estão corretos antes de enviar
    const payload = {
      initial_velocity: parseFloat(params.initial_velocity),
      launch_angle: parseFloat(params.launch_angle),
      initial_height: parseFloat(params.initial_height),
      gravity: parseFloat(params.gravity)
    };

    console.log("Enviando para API Lançamento Oblíquo:", payload);

    try {
      const response = await fetch('http://localhost:8000/api/simulation/physics/projectile-launch/start', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(payload),
      });

      if (!response.ok) {
        const errorData = await response.json().catch(() => ({ detail: response.statusText }));
        throw new Error(errorData.detail || `Erro HTTP: ${response.status}`);
      }

      simulationResult = await response.json();
      console.log("Resultado da simulação de Lançamento Oblíquo:", simulationResult);

    } catch (e) {
      console.error("Falha ao iniciar simulação de Lançamento Oblíquo:", e);
      error = e.message || "Ocorreu um erro desconhecido ao contatar a API de física.";
    } finally {
      isLoading = false;
    }
  }

  // NOVAS FUNÇÕES AUXILIARES PARA O SVG E TABELA:
  function getSvgViewBox(trajectory, maxRange, maxHeight, initialHeight) {
    if (!trajectory || trajectory.length === 0) {
      return "0 0 100 100"; // Default viewBox
    }
    const padding = 20; 
    const viewWidth = maxRange > 0 ? maxRange + 2*padding : 100 + 2*padding; 
    const viewHeight = Math.max(maxHeight, initialHeight) > 0 ? Math.max(maxHeight, initialHeight) + 2*padding : 100 + 2*padding;
    return `${-padding} ${-padding} ${viewWidth} ${viewHeight}`;
  }

  function svgAdjustedX(physicalX, trajectory) {
    return physicalX; 
  }

  function svgAdjustedY(physicalY, trajectory, overallMaxHeight, physicalInitialHeight) {
    const padding = 20; 
    // const viewHeight = Math.max(overallMaxHeight, physicalInitialHeight) + 2 * padding; // Not directly used here but part of viewBox logic
    return (Math.max(overallMaxHeight, physicalInitialHeight) + padding) - physicalY; // Using the version from Turn 40 prompt
  }

  function formatTrajectoryForSvg(trajectory, overallMaxHeight, physicalInitialHeight) {
    if (!trajectory) return "";
    return trajectory
      .map(p => `${svgAdjustedX(p.x, trajectory)},${svgAdjustedY(p.y, trajectory, overallMaxHeight, physicalInitialHeight)}`)
      .join(" ");
  }

  function getTrajectorySample(trajectory, count = 10) {
    if (!trajectory || trajectory.length === 0) return [];
    if (trajectory.length <= count) return trajectory;
    
    const sample = [];
    const step = Math.floor(trajectory.length / (count -1)); 
    for (let i = 0; i < count -1 ; i++) {
      sample.push(trajectory[i * step]);
    }
    sample.push(trajectory[trajectory.length - 1]); 
    return sample;
  }

</script>

<svelte:head>
  <title>{experimentDetails.name} - Simulador</title>
</svelte:head>

<main class="container">
  <a href="/" class="back-link" use:fade>← Voltar para Seleção de Experimentos</a>
  
  <h1>{experimentDetails.name}</h1>
  <p class="description">{experimentDetails.description}</p>

  <form on:submit|preventDefault={startSimulation} class="simulation-form">
    <h2>Configurar Parâmetros do Lançamento</h2>

    <div class="form-grid">
      <fieldset>
        <legend>Parâmetros Principais</legend>
        <label for="initial_velocity">Velocidade Inicial (m/s):</label>
        <input type="number" id="initial_velocity" bind:value={params.initial_velocity} min="0.1" step="0.1" required>
        
        <label for="launch_angle">Ângulo de Lançamento (graus):</label>
        <input type="number" id="launch_angle" bind:value={params.launch_angle} min="1" max="89" step="1" required>
        <small>Valores entre 1 e 89 graus para lançamento oblíquo.</small>
      </fieldset>

      <fieldset>
        <legend>Parâmetros Adicionais (Opcionais)</legend>
        <label for="initial_height">Altura Inicial (m):</label>
        <input type="number" id="initial_height" bind:value={params.initial_height} min="0" step="0.1">
        
        <label for="gravity">Aceleração da Gravidade (m/s²):</label>
        <input type="number" id="gravity" bind:value={params.gravity} min="0.1" step="0.01">
      </fieldset>
    </div>
    
    <button type="submit" class="submit-button" disabled={isLoading}>
      {#if isLoading}
        Calculando Trajetória...
      {:else}
        Simular Lançamento
      {/if}
    </button>
  </form>

  {#if simulationResult}
    <section class="results-section" transition:fade={{ duration: 300 }}>
      <h2>Resultados do Lançamento</h2>
      <div class="results-summary-grid">
        <div class="result-item">
          <strong>Alcance Máximo:</strong> {simulationResult.max_range.toFixed(2)} m
        </div>
        <div class="result-item">
          <strong>Altura Máxima:</strong> {simulationResult.max_height.toFixed(2)} m
        </div>
        <div class="result-item">
          <strong>Tempo Total de Voo:</strong> {simulationResult.total_time.toFixed(2)} s
        </div>
        <div class="result-item">
          <strong>Velocidade Inicial X:</strong> {simulationResult.initial_velocity_x.toFixed(2)} m/s
        </div>
        <div class="result-item">
          <strong>Velocidade Inicial Y:</strong> {simulationResult.initial_velocity_y.toFixed(2)} m/s
        </div>
      </div>

      <h3>Trajetória do Projétil:</h3>
      {#if simulationResult.trajectory && simulationResult.trajectory.length > 0}
        <div class="trajectory-container" role="img" aria-label="Gráfico da trajetória do projétil">
          <svg 
            width="100%" 
            height="300" 
            viewBox="{getSvgViewBox(simulationResult.trajectory, simulationResult.max_range, simulationResult.max_height, simulationResult.parameters_used.initial_height)}" 
            preserveAspectRatio="xMidYMin meet" <!-- Kept xMidYMin meet as implemented -->
            style="border: 1px solid #ccc; background-color: #f0f8ff;"
          >
            <!-- Eixos (simplificado) - Using version from Turn 40 prompt -->
            <line x1="0" y1="{svgAdjustedY(0, simulationResult.trajectory, simulationResult.max_height, simulationResult.parameters_used.initial_height)}" 
                  x2="{svgAdjustedX(simulationResult.max_range, simulationResult.trajectory)}" 
                  y2="{svgAdjustedY(0, simulationResult.trajectory, simulationResult.max_height, simulationResult.parameters_used.initial_height)}" 
                  stroke="#aaa" stroke-width="1"/>
            <line x1="{svgAdjustedX(0, simulationResult.trajectory)}" y1="0" 
                  x2="{svgAdjustedX(0, simulationResult.trajectory)}" 
                  y2="{svgAdjustedY(simulationResult.max_height, simulationResult.trajectory, simulationResult.max_height, simulationResult.parameters_used.initial_height) + 20}"  /* +20 para dar espaço */
                  stroke="#aaa" stroke-width="1"/>

            <!-- Trajetória -->
            <polyline
              points="{formatTrajectoryForSvg(simulationResult.trajectory, simulationResult.max_height, simulationResult.parameters_used.initial_height)}"
              fill="none"
              stroke="#2980b9" /* Azul do plano de UI */
              stroke-width="2"
            />
            <!-- Ponto inicial -->
            <circle cx="{svgAdjustedX(simulationResult.trajectory[0].x, simulationResult.trajectory)}" 
                    cy="{svgAdjustedY(simulationResult.trajectory[0].y, simulationResult.trajectory, simulationResult.max_height, simulationResult.parameters_used.initial_height)}" 
                    r="3" fill="green" />
            <!-- Ponto final -->
            <circle cx="{svgAdjustedX(simulationResult.trajectory[simulationResult.trajectory.length - 1].x, simulationResult.trajectory)}" 
                    cy="{svgAdjustedY(simulationResult.trajectory[simulationResult.trajectory.length - 1].y, simulationResult.trajectory, simulationResult.max_height, simulationResult.parameters_used.initial_height)}" 
                    r="3" fill="red" />
          </svg>
        </div>
      {:else}
        <p>Dados da trajetória não disponíveis.</p>
      {/if}
      
      <h4>Dados da Trajetória (amostra):</h4>
      <div class="trajectory-table-container">
        <table>
          <thead>
            <tr><th>Tempo (s)</th><th>X (m)</th><th>Y (m)</th></tr>
          </thead>
          <tbody>
            {#each getTrajectorySample(simulationResult.trajectory) as point}
              <tr>
                <td>{point.time.toFixed(2)}</td>
                <td>{point.x.toFixed(2)}</td>
                <td>{point.y.toFixed(2)}</td>
              </tr>
            {/each}
          </tbody>
        </table>
      </div>
    </section>
  {/if}

  {#if error}
    <p class="error-message" use:fade>Erro: {error}</p>
  {/if}

</main>

<style>
  :global(body) {
    font-family: 'Roboto', sans-serif;
    background-color: #f4f7f6;
    color: #333;
    line-height: 1.6;
  }
  .container {
    max-width: 800px;
    margin: 20px auto;
    padding: 20px;
    background-color: #fff;
    border-radius: 8px;
    box-shadow: 0 2px 10px rgba(0,0,0,0.05);
  }
  .back-link {
    display: inline-block;
    margin-bottom: 20px;
    color: #2980b9;
    text-decoration: none;
  }
  .back-link:hover { text-decoration: underline; }
  h1 { color: #2c3e50; text-align: center; margin-bottom: 10px; }
  .description { text-align: center; margin-bottom: 30px; color: #555; }
  .simulation-form h2 { margin-bottom: 20px; text-align: center; color: #34495e; }
  .form-grid { display: grid; grid-template-columns: repeat(auto-fit, minmax(280px, 1fr)); gap: 20px; margin-bottom: 20px; }
  fieldset { border: 1px solid #ddd; border-radius: 6px; padding: 20px; background-color: #fdfdfd; }
  legend { font-weight: bold; color: #2980b9; padding: 0 10px; }
  label { display: block; margin-bottom: 8px; font-weight: 500; color: #444; }
  input[type="number"] {
    width: 100%; padding: 10px; margin-bottom: 5px;
    border: 1px solid #ccc; border-radius: 4px; box-sizing: border-box; font-size: 1em;
  }
  input[type="number"]:focus {
    border-color: #2980b9; outline: none; box-shadow: 0 0 0 2px rgba(41, 128, 185, 0.2);
  }
  fieldset small {
    display: block;
    margin-bottom: 10px;
    font-size: 0.85em;
    color: #666;
  }
  .submit-button {
    display: block; width: 100%; padding: 12px 20px; background-color: #ADD8E6;
    color: #333; font-size: 1.1em; font-weight: bold; border: none;
    border-radius: 4px; cursor: pointer; transition: background-color 0.2s ease;
  }
  .submit-button:hover:not(:disabled) { background-color: #9BC9E0; }
  .submit-button:disabled { background-color: #ccc; cursor: not-allowed; }
  
  .results-section {
    margin-top: 30px; padding: 20px; background-color: #e9f5ff;
    border: 1px solid #ADD8E6; border-radius: 6px;
  }
  .results-section h2 { margin-top: 0; margin-bottom:15px; color: #2980b9; text-align:center; }
  .results-section h3 { margin-top: 20px; margin-bottom:10px; color: #34495e; }
  .results-section h4 { margin-top: 20px; margin-bottom:5px; color: #34495e; font-size: 1em; font-weight:bold; }
  
  .error-message {
    color: #FFA500; background-color: #fff3e0; border: 1px solid #FFA500;
    padding: 10px; border-radius: 4px; margin-top: 20px;
  }

  /* NOVOS ESTILOS */
  .results-summary-grid {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(220px, 1fr));
    gap: 10px;
    margin-bottom: 20px;
  }

  .results-summary-grid .result-item { /* Estilo para os itens de sumário */
    background-color: #f9f9f9;
    padding: 10px;
    border-radius: 4px;
    border: 1px solid #eee;
    font-size: 0.9em;
  }

  .trajectory-container {
    width: 100%;
    max-width: 600px; /* Limita a largura do SVG para não ficar gigante */
    margin: 20px auto;
    overflow: hidden; /* Para cantos arredondados do SVG se houver */
  }

  .trajectory-container svg {
    display: block; /* Remove espaço extra abaixo do SVG */
    border-radius: 4px;
  }

  .trajectory-table-container {
    margin-top: 15px;
    max-height: 200px; /* Altura máxima para a tabela, com scroll se necessário */
    overflow-y: auto;
    border: 1px solid #ddd;
    border-radius: 4px;
  }

  table {
    width: 100%;
    border-collapse: collapse;
    font-size: 0.9em;
  }
  th, td {
    text-align: left;
    padding: 8px 10px;
    border-bottom: 1px solid #eee;
  }
  th {
    background-color: #f0f0f0;
    position: sticky; /* Cabeçalho fixo ao rolar */
    top: 0;
  }
  tbody tr:last-child td {
    border-bottom: none;
  }
  tbody tr:hover {
    background-color: #f5f5f5;
  }
</style>
