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

    const payload = {
      ...params,
      indicator_name: params.indicator_name === "Nenhum" ? null : params.indicator_name
    };

    console.log("Enviando para API:", payload);

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

  function getPhColor(ph) {
    if (ph < 3) return '#d32f2f';
    if (ph < 5) return '#ef5350';
    if (ph < 7) return '#ffc107';
    if (ph === 7) return '#4caf50';
    if (ph < 9) return '#64b5f6';
    if (ph < 11) return '#1976d2';
    return '#303f9f';
  }

  function getIndicatorDisplayColor(colorName) {
    if (!colorName) return 'transparent';
    const colorMap = {
      "incolor": "transparent",
      "rosa claro/róseo": "pink",
      "carmim/magenta": "magenta",
      "amarelo": "yellow",
      "verde": "green",
      "azul": "blue",
      "indicador não reconhecido": "grey",
      "nenhum": "transparent"
    };
    return colorMap[colorName.toLowerCase()] || 'grey';
  }

  function calculatePhIndicatorPosition(ph) {
    const clampedPh = Math.max(0, Math.min(14, ph));
    return (clampedPh / 14) * 100;
  }

</script>

<svelte:head>
  <title>{experimentDetails.name} - Simulador</title>
</svelte:head>

<main class="container">
  <a href="/" class="fluent-link" use:fade>← Voltar para Seleção de Experimentos</a>

  <h1>{experimentDetails.name}</h1>
  <p class="description">{experimentDetails.description}</p>

  <section class="content-section">
    <form on:submit|preventDefault={startSimulation} class="simulation-form">
      <h2 style="text-align: center; margin-bottom: var(--spacing-l); color: var(--color-text-primary); font-size: var(--font-size-title); font-weight: var(--font-weight-semibold);">Configurar Parâmetros da Simulação</h2>

      <div class="form-grid">
        <fieldset>
        <legend>Ácido</legend>
        <label for="acid_concentration">Concentração do Ácido (mol/L):</label>
        <input type="number" id="acid_concentration" bind:value={params.acid_concentration} class="fluent-input" min="0.001" step="0.001" required>

        <label for="acid_volume">Volume do Ácido (mL):</label>
        <input type="number" id="acid_volume" bind:value={params.acid_volume} class="fluent-input" min="1" step="1" required>
      </fieldset>

      <fieldset>
        <legend>Base</legend>
        <label for="base_concentration">Concentração da Base (mol/L):</label>
        <input type="number" id="base_concentration" bind:value={params.base_concentration} class="fluent-input" min="0.001" step="0.001" required>

        <label for="base_volume">Volume da Base (mL):</label>
        <input type="number" id="base_volume" bind:value={params.base_volume} class="fluent-input" min="1" step="1" required>
      </fieldset>
    </div>

    <fieldset class="indicator-fieldset">
      <legend>Indicador</legend>
      <label for="indicator_name">Selecione o Indicador:</label>
      <select id="indicator_name" bind:value={params.indicator_name} class="fluent-select">
        {#each indicatorOptions as option}
          <option value={option === "Nenhum" ? null : option}>{option}</option>
        {/each}
      </select>
    </fieldset>

    <button type="submit" class="fluent-button" disabled={isLoading}>
      {#if isLoading}
        Simulando...
      {:else}
        Iniciar Simulação
      {/if}
    </button>
  </form>
  </section>

  {#if simulationResult}
    <section class="content-section results-section" transition:fade={{ duration: 300 }}>
      <h2 style="text-align: center; margin-bottom: var(--spacing-l); color: var(--color-text-primary); font-size: var(--font-size-title); font-weight: var(--font-weight-semibold);">Resultados da Simulação</h2>
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

      <h4 style="margin-top: var(--spacing-l); margin-bottom: var(--spacing-s); color: var(--color-text-primary); font-size: var(--font-size-subheader); font-weight: var(--font-weight-semibold);">Escala de pH:</h4>
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
    <p class="fluent-alert-error" use:fade>Erro: {error}</p>
  {/if}

</main>

<style>
  .container {
    max-width: 900px;
    margin: var(--spacing-xl) auto;
    padding: 0;
    background-color: var(--color-neutral-background);
    box-shadow: none;
    border-radius: 0;
  }

  .content-section {
    background-color: var(--color-neutral-layer-1);
    box-shadow: var(--shadow-depth-8);
    border-radius: var(--border-radius-large);
    padding: var(--spacing-l);
    margin-bottom: var(--spacing-xl);
  }

  h1 {
    text-align: center;
    margin-bottom: var(--spacing-s);
    font-size: var(--font-size-display);
    color: var(--color-text-primary);
  }

  .description {
    text-align: center;
    margin-bottom: var(--spacing-l);
    color: var(--color-text-secondary);
  }

  .form-grid {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(280px, 1fr));
    gap: var(--spacing-m);
    margin-bottom: var(--spacing-l);
  }

  fieldset {
    border: 1px solid var(--color-neutral-stroke-default);
    border-radius: var(--border-radius-medium);
    padding: var(--spacing-l);
    background-color: var(--color-neutral-layer-1);
  }

  legend {
    font-weight: var(--font-weight-semibold);
    color: var(--color-text-primary);
    padding: 0 var(--spacing-xs);
    margin-bottom: var(--spacing-m);
    font-size: var(--font-size-subheader);
  }

  label {
    display: block;
    margin-bottom: var(--spacing-xs);
    font-weight: var(--font-weight-regular);
    color: var(--color-text-primary);
  }

  .indicator-fieldset {
    margin-bottom: var(--spacing-l);
  }

  .results-grid {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
    gap: var(--spacing-m);
    margin-bottom: var(--spacing-l);
  }

  .result-item {
    background-color: var(--color-neutral-layer-2);
    padding: var(--spacing-m);
    border-radius: var(--border-radius-medium);
    border: 1px solid var(--color-neutral-stroke-default);
    font-size: var(--font-size-body);
  }

  .result-item strong {
    color: var(--color-text-primary);
    font-weight: var(--font-weight-semibold);
  }

  .ph-value {
    font-weight: var(--font-weight-bold);
    font-size: var(--font-size-title);
  }

  .indicator-color-display {
    display: flex;
    align-items: center;
    gap: var(--spacing-s);
    margin-top: var(--spacing-xs);
  }

  .color-box {
    display: inline-block;
    width: 20px;
    height: 20px;
    border: 1px solid var(--color-neutral-stroke-strong);
    border-radius: var(--border-radius-small);
  }

  .result-message {
    grid-column: 1 / -1;
  }

  .ph-scale-container {
    margin-top: var(--spacing-l);
    padding: var(--spacing-m);
    border: 1px solid var(--color-neutral-stroke-default);
    border-radius: var(--border-radius-medium);
  }

  .ph-bar {
    width: 100%;
    height: 25px;
    background: linear-gradient(to right, red, orange, yellow, lightgreen, green, lightblue, blue, purple);
    border-radius: var(--border-radius-small);
    position: relative;
    margin-bottom: var(--spacing-s);
  }

  .ph-indicator {
    position: absolute;
    top: -5px;
    transform: translateX(-50%);
    background-color: var(--color-accent-primary);
    border: 1px solid var(--color-neutral-stroke-strong);
    border-radius: var(--border-radius-small);
    padding: var(--spacing-xs);
    font-size: var(--font-size-caption);
    white-space: nowrap;
    box-shadow: var(--shadow-depth-4);
  }
  .ph-indicator span {
      color: var(--color-text-on-accent);
  }

  .ph-labels {
    display: flex;
    justify-content: space-between;
    font-size: var(--font-size-caption);
    color: var(--color-text-secondary);
  }

  html[data-theme="dark"] .ph-value {
    color: var(--color-text-primary) !important; /* Override inline style for dark mode */
  }

  /* Fluent CSS Definitions Start */
  .fluent-link {
    color: var(--color-accent-primary);
    text-decoration: none;
  }
  .fluent-link:hover {
    color: var(--color-accent-primary-hover);
    text-decoration: underline;
  }

  .fluent-input, .fluent-select {
    background-color: var(--color-neutral-layer-1);
    border: 1px solid var(--color-neutral-stroke-default);
    color: var(--color-text-primary);
    padding: var(--spacing-s) var(--spacing-m);
    border-radius: var(--border-radius-medium);
    width: 100%;
    box-sizing: border-box;
  }
  .fluent-input:focus, .fluent-select:focus {
    outline: 2px solid transparent;
    outline-offset: 2px;
    border-color: var(--color-accent-primary);
    box-shadow: 0 0 0 1px var(--color-accent-primary);
  }
  .fluent-input::placeholder {
    color: var(--color-text-secondary);
    opacity: 0.7;
  }
  .fluent-select {
    -webkit-appearance: none;
    -moz-appearance: none;
    appearance: none;
    background-image: url('data:image/svg+xml;charset=US-ASCII,%3Csvg%20xmlns%3D%22http%3A%2F%2Fwww.w3.org%2F2000%2Fsvg%22%20width%3D%2220%22%20height%3D%2220%22%20viewBox%3D%220%200%2020%2020%22%3E%3Cpath%20fill%3D%22%23605e5c%22%20d%3D%22M5.516%207.548c.436-.446%201.143-.48%201.584-.038L10%2010.092l2.899-2.582c.442-.394%201.148-.394%201.59%200%20.442.394.442%201.034%200%201.428l-3.704%203.3c-.442.394-1.148.394-1.59%200L5.516%208.976c-.436-.446-.402-1.143.038-1.584z%22%2F%3E%3C%2Fsvg%3E');
    background-repeat: no-repeat;
    background-position: right var(--spacing-m) center;
    background-size: 1em;
  }

  .fluent-button {
    background-color: var(--color-accent-primary);
    color: var(--color-text-on-accent);
    border: 1px solid transparent;
    padding: var(--spacing-s) var(--spacing-m);
    border-radius: var(--border-radius-small);
    cursor: pointer;
    font-family: var(--font-family-base);
    font-size: var(--font-size-body);
    font-weight: var(--font-weight-semibold);
    text-align: center;
    transition: background-color 0.2s ease-in-out, box-shadow 0.2s ease-in-out;
    min-width: 120px;
  }
  .fluent-button:hover:not(:disabled) {
    background-color: var(--color-accent-primary-hover);
    box-shadow: var(--shadow-depth-2);
  }
  .fluent-button:active:not(:disabled) {
    background-color: var(--color-accent-primary-active);
    box-shadow: none;
  }
  .fluent-button:disabled {
    background-color: var(--color-neutral-stroke-default);
    color: var(--color-text-disabled);
    cursor: not-allowed;
    box-shadow: none;
  }

  .fluent-alert-error {
    background-color: color-mix(in srgb, var(--color-text-error) 10%, var(--color-neutral-layer-1));
    color: var(--color-text-error);
    border: 1px solid var(--color-text-error);
    padding: var(--spacing-m);
    border-radius: var(--border-radius-medium);
    margin-top: var(--spacing-m);
  }
  /* Fluent CSS Definitions End */
</style>
