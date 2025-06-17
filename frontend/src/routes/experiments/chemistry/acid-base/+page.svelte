<script>
  import { fade } from 'svelte/transition'; // Usar transições padrão

  // Detalhes do experimento (poderiam vir de uma API no futuro)
  const experimentDetails = {
    name: "Reação Ácido-Base",
    description: "Simule a reação entre um ácido e uma base, observe a mudança de pH e a cor do indicador."
  };

  // Parâmetros da Simulação
  let params = {
    acid_concentration: 0.1, // mol/L
    acid_volume: 50, // mL
    base_concentration: 0.1, // mol/L
    base_volume: 25, // mL
    indicator_name: "Fenolftaleína" // Default value, can be null if "Nenhum" is selected
  };

  // Opções para o indicador
  const indicatorOptions = ["Nenhum", "Fenolftaleína", "Azul de Bromotimol"];

  // Variáveis para armazenar resultado e estado
  let simulationResult = null;
  let isLoading = false;
  let error = null;

  async function startSimulation() {
    isLoading = true;
    error = null;
    simulationResult = null;

    // Ajustar o indicator_name para null se "Nenhum" for selecionado
    const payload = {
      ...params,
      indicator_name: params.indicator_name === "Nenhum" ? null : params.indicator_name
    };

    console.log("Enviando para API:", payload); // Log para depuração

    try {
      const response = await fetch('http://localhost:8000/api/simulation/acid-base/start', {
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
      console.log("Resultado da simulação:", simulationResult);

    } catch (e) {
      console.error("Falha ao iniciar simulação:", e);
      error = e.message || "Ocorreu um erro desconhecido ao contatar a API.";
    } finally {
      isLoading = false;
    }
  }

  // NOVAS FUNÇÕES AUXILIARES:
  function getPhColor(ph) {
    if (ph < 3) return '#d32f2f'; // Vermelho forte
    if (ph < 5) return '#ef5350'; // Vermelho claro
    if (ph < 7) return '#ffc107'; // Laranja/Amarelo
    if (ph === 7) return '#4caf50'; // Verde
    if (ph < 9) return '#64b5f6'; // Azul claro
    if (ph < 11) return '#1976d2'; // Azul
    return '#303f9f'; // Azul escuro/Roxo
  }

  function getIndicatorDisplayColor(colorName) {
    if (!colorName) return 'transparent';
    const colorMap = {
      "incolor": "transparent", // ou um cinza bem claro para indicar a presença
      "rosa claro/róseo": "pink",
      "carmim/magenta": "magenta",
      "amarelo": "yellow",
      "verde": "green",
      "azul": "blue",
      "indicador não reconhecido": "grey",
      "nenhum": "transparent"
    };
    return colorMap[colorName.toLowerCase()] || 'grey'; // Retorna cinza se a cor não for mapeada
  }

  function calculatePhIndicatorPosition(ph) {
    // Converte pH (0-14) para uma porcentagem (0-100) para posicionamento na barra.
    // Garante que o valor esteja entre 0 e 14 antes de calcular.
    const clampedPh = Math.max(0, Math.min(14, ph));
    return (clampedPh / 14) * 100;
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
    <h2>Configurar Parâmetros da Simulação</h2>

    <div class="form-grid">
      <fieldset>
        <legend>Ácido</legend>
        <label for="acid_concentration">Concentração do Ácido (mol/L):</label>
        <input type="number" id="acid_concentration" bind:value={params.acid_concentration} min="0.001" step="0.001" required>

        <label for="acid_volume">Volume do Ácido (mL):</label>
        <input type="number" id="acid_volume" bind:value={params.acid_volume} min="1" step="1" required>
      </fieldset>

      <fieldset>
        <legend>Base</legend>
        <label for="base_concentration">Concentração da Base (mol/L):</label>
        <input type="number" id="base_concentration" bind:value={params.base_concentration} min="0.001" step="0.001" required>

        <label for="base_volume">Volume da Base (mL):</label>
        <input type="number" id="base_volume" bind:value={params.base_volume} min="1" step="1" required>
      </fieldset>
    </div>

    <fieldset class="indicator-fieldset">
      <legend>Indicador</legend>
      <label for="indicator_name">Selecione o Indicador:</label>
      <select id="indicator_name" bind:value={params.indicator_name}>
        {#each indicatorOptions as option}
          <option value={option === "Nenhum" ? null : option}>{option}</option>
        {/each}
      </select>
    </fieldset>

    <button type="submit" class="submit-button" disabled={isLoading}>
      {#if isLoading}
        Simulando...
      {:else}
        Iniciar Simulação
      {/if}
    </button>
  </form>

  {#if simulationResult}
    <section class="results-section" transition:fade={{ duration: 300 }}>
      <h2>Resultados da Simulação</h2>
      <div class="results-grid">
        <div class="result-item">
          <strong>pH Final:</strong>
          <span class="ph-value" style="color: {getPhColor(simulationResult.final_ph)}">
            {simulationResult.final_ph.toFixed(2)}
          </span>
        </div>
        <div class="result-item">
          <strong>Status:</strong> {simulationResult.status}
        </div>

        {#if simulationResult.indicator_name || (simulationResult.indicator_color && simulationResult.indicator_color !== 'Indicador não reconhecido' && simulationResult.indicator_color !== 'Nenhum')}
          <div class="result-item">
            <strong>Indicador ({simulationResult.indicator_name || params.indicator_name || 'Não especificado'}):</strong>
            <div class="indicator-color-display">
              <span class="color-box" style="background-color: {getIndicatorDisplayColor(simulationResult.indicator_color)};"></span>
              {simulationResult.indicator_color || 'N/A'}
            </div>
          </div>
        {/if}

        <div class="result-item">
          <strong>Volume Total:</strong> {simulationResult.total_volume_ml.toFixed(2)} mL
        </div>
        <div class="result-item">
          <strong>Mols H+ Iniciais:</strong> {simulationResult.mols_h_plus_initial.toExponential(3)}
        </div>
        <div class="result-item">
          <strong>Mols OH- Iniciais:</strong> {simulationResult.mols_oh_minus_initial.toExponential(3)}
        </div>

        {#if simulationResult.excess_reactant && simulationResult.excess_reactant !== "Nenhum"}
          <div class="result-item">
            <strong>Reagente em Excesso:</strong> {simulationResult.excess_reactant}
          </div>
        {/if}

        {#if simulationResult.message}
          <div class="result-item result-message">
            <strong>Mensagem:</strong> {simulationResult.message}
          </div>
        {/if}
      </div>

      <!-- Representação Gráfica Simples: Barra de pH -->
      <h4>Escala de pH:</h4>
      <div class="ph-scale-container">
        <div class="ph-bar">
          <div class="ph-indicator" style="left: {calculatePhIndicatorPosition(simulationResult.final_ph)}%;">
            <span>pH {simulationResult.final_ph.toFixed(2)}</span>
          </div>
        </div>
        <div class="ph-labels">
          <span>0 (Ácido)</span>
          <span>7 (Neutro)</span>
          <span>14 (Básico)</span>
        </div>
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
    background-color: #f4f7f6; /* Um tom ligeiramente diferente para distinguir da home */
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
    color: #2980b9; /* Azul do plano de UI */
    text-decoration: none;
  }
  .back-link:hover {
    text-decoration: underline;
  }

  h1 {
    color: #2c3e50;
    text-align: center;
    margin-bottom: 10px;
  }

  .description {
    text-align: center;
    margin-bottom: 30px;
    color: #555;
  }

  .simulation-form h2 {
    margin-bottom: 20px;
    text-align: center;
    color: #34495e;
  }

  .form-grid {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(280px, 1fr));
    gap: 20px;
    margin-bottom: 20px;
  }

  fieldset {
    border: 1px solid #ddd;
    border-radius: 6px;
    padding: 20px;
    background-color: #fdfdfd;
  }

  legend {
    font-weight: bold;
    color: #2980b9; /* Azul do plano de UI */
    padding: 0 10px;
  }

  label {
    display: block;
    margin-bottom: 8px;
    font-weight: 500;
    color: #444;
  }

  input[type="number"],
  select {
    width: 100%;
    padding: 10px;
    margin-bottom: 15px;
    border: 1px solid #ccc;
    border-radius: 4px;
    box-sizing: border-box;
    font-size: 1em;
  }
  input[type="number"]:focus,
  select:focus {
    border-color: #2980b9; /* Azul do plano de UI */
    outline: none;
    box-shadow: 0 0 0 2px rgba(41, 128, 185, 0.2);
  }

  .indicator-fieldset {
    margin-bottom: 25px;
  }

  .submit-button {
    display: block;
    width: 100%;
    padding: 12px 20px;
    background-color: #ADD8E6; /* Azul claro interativo */
    color: #333; /* Texto mais escuro para contraste */
    font-size: 1.1em;
    font-weight: bold;
    border: none;
    border-radius: 4px;
    cursor: pointer;
    transition: background-color 0.2s ease;
  }
  .submit-button:hover:not(:disabled) {
    background-color: #9BC9E0; /* Um pouco mais escuro no hover */
  }
  .submit-button:disabled {
    background-color: #ccc;
    cursor: not-allowed;
  }

  .results-section {
    margin-top: 30px;
    padding: 20px;
    background-color: #e9f5ff; /* Fundo azul bem claro para resultados */
    border: 1px solid #ADD8E6; /* Borda azul claro */
    border-radius: 6px;
  }
  .results-section h2 {
    margin-top: 0;
    margin-bottom: 20px;
    color: #2980b9;
    text-align: center;
  }

  .results-grid {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
    gap: 15px;
    margin-bottom: 20px;
  }

  .result-item {
    background-color: #fff;
    padding: 10px 15px;
    border-radius: 4px;
    border: 1px solid #d0e0eb;
    font-size: 0.95em;
  }

  .result-item strong {
    color: #34495e;
  }

  .ph-value {
    font-weight: bold;
    font-size: 1.2em;
  }

  .indicator-color-display {
    display: flex;
    align-items: center;
    gap: 8px;
    margin-top: 5px;
  }

  .color-box {
    display: inline-block;
    width: 20px;
    height: 20px;
    border: 1px solid #ccc;
    border-radius: 3px;
  }

  .result-message {
    grid-column: 1 / -1; /* Faz a mensagem ocupar a largura total */
    background-color: #fff9c4; /* Amarelo bem claro para mensagens */
    border-color: #fbc02d;
  }

  /* Estilos para a Barra de pH */
  .ph-scale-container {
    margin-top: 10px;
    padding: 10px;
    border: 1px solid #ccc;
    border-radius: 4px;
  }

  .ph-bar {
    width: 100%;
    height: 25px;
    background: linear-gradient(to right, red, orange, yellow, lightgreen, green, lightblue, blue, purple);
    border-radius: 5px;
    position: relative;
    margin-bottom: 5px;
  }

  .ph-indicator {
    position: absolute;
    top: -5px; /* Para ficar um pouco acima da barra */
    transform: translateX(-50%); /* Centraliza o indicador */
    background-color: white;
    border: 2px solid black;
    border-radius: 4px;
    padding: 2px 5px;
    font-size: 0.8em;
    white-space: nowrap;
    box-shadow: 0 1px 3px rgba(0,0,0,0.2);
  }
  .ph-indicator span {
      color: black;
  }

  .ph-labels {
    display: flex;
    justify-content: space-between;
    font-size: 0.8em;
    color: #555;
  }

  .error-message {
    color: #FFA500; /* Laranja para alertas */
    background-color: #fff3e0;
    border: 1px solid #FFA500;
    padding: 10px;
    border-radius: 4px;
    margin-top: 20px;
  }
</style>
