<script>
  import { fade } from 'svelte/transition';

  // Unit selection constants
  const VELOCITY_UNITS = [{ value: 'm/s', label: 'm/s' }, { value: 'km/h', label: 'km/h' }, { value: 'ft/s', label: 'ft/s' }, { value: 'mph', label: 'mph' }];
  const HEIGHT_UNITS = [{ value: 'm', label: 'm' }, { value: 'ft', label: 'ft' }];
  const DISTANCE_OUTPUT_UNITS = [{ value: 'm', label: 'm' }, { value: 'km', label: 'km' }, { value: 'ft', label: 'ft' }, { value: 'mi', label: 'mi' }];
  const VELOCITY_OUTPUT_UNITS = [{ value: 'm/s', label: 'm/s' }, { value: 'km/h', label: 'km/h' }, { value: 'ft/s', label: 'ft/s' }, { value: 'mph', label: 'mph' }];
  const TIME_OUTPUT_UNITS = [{ value: 's', label: 's' }, { value: 'min', label: 'min' }];

  // Selected unit state variables
  let initialVelocityUnit = 'm/s';
  let initialHeightUnit = 'm';
  let outputDistanceUnit = 'm';
  let outputVelocityUnit = 'm/s';
  let outputTimeUnit = 's';

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

    const payload = {
      initial_velocity: parseFloat(params.initial_velocity),
      launch_angle: parseFloat(params.launch_angle),
      initial_height: parseFloat(params.initial_height),
      gravity: parseFloat(params.gravity),
      initial_velocity_unit: initialVelocityUnit,
      initial_height_unit: initialHeightUnit,
      output_units: {
        velocity_unit: outputVelocityUnit,
        time_unit: outputTimeUnit,
        range_unit: outputDistanceUnit,
        height_unit: outputDistanceUnit
      }
    };

    console.log("Enviando para API Lançamento Oblíquo:", payload);

    try {
      const response = await fetch('http://localhost:8000/api/simulation/projectile-launch/start', {
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

  function getSvgViewBox(trajectory, maxRange, maxHeight, initialHeight) {
    if (!trajectory || trajectory.length === 0) {
      return "0 0 100 100";
    }
    const padding = 20;
    const viewWidth = (maxRange > 0 ? maxRange : 100) + 2 * padding;
    const effectiveMaxPhysicalY = Math.max(maxHeight, initialHeight);
    const viewHeight = (effectiveMaxPhysicalY > 0 ? effectiveMaxPhysicalY : 100) + 2 * padding;
    const minX = -padding;
    const minY = -padding;
    return `${minX} ${minY} ${viewWidth} ${viewHeight}`;
  }

  function svgAdjustedX(physicalX, trajectory) {
    return physicalX;
  }

  function svgAdjustedY(physicalY, trajectory, overallMaxHeight, physicalInitialHeight) {
    const padding = 20;
    const effectiveMaxPhysicalY = Math.max(overallMaxHeight, physicalInitialHeight);
    return (effectiveMaxPhysicalY + padding) - physicalY;
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
  <a href="/" class="fluent-link" use:fade>← Voltar para Seleção de Experimentos</a>

  <h1 style="font-size: var(--font-size-display); color: var(--color-text-primary); text-align: center; margin-bottom: var(--spacing-s);">{experimentDetails.name}</h1>
  <p class="description">{experimentDetails.description}</p>

  <section class="content-section">
    <form on:submit|preventDefault={startSimulation} class="simulation-form">
      <h2 style="text-align: center; margin-bottom: var(--spacing-l); color: var(--color-text-primary); font-size: var(--font-size-title); font-weight: var(--font-weight-semibold);">Configurar Parâmetros do Lançamento</h2>

      <div class="form-grid">
        <fieldset>
          <legend>Parâmetros Principais</legend>
          <label for="initial_velocity">Velocidade Inicial ({initialVelocityUnit}):</label>
          <input type="number" id="initial_velocity" bind:value={params.initial_velocity} class="fluent-input" min="0.1" step="0.1" required>
          <select bind:value={initialVelocityUnit} class="fluent-select unit-select">
            {#each VELOCITY_UNITS as unit (unit.value)}
              <option value={unit.value}>{unit.label}</option>
            {/each}
          </select>

          <label for="launch_angle">Ângulo de Lançamento (graus):</label>
          <input type="number" id="launch_angle" bind:value={params.launch_angle} class="fluent-input" min="1" max="89" step="1" required>
          <small>Valores entre 1 e 89 graus para lançamento oblíquo.</small>
        </fieldset>

        <fieldset>
          <legend>Parâmetros Adicionais (Opcionais)</legend>
          <label for="initial_height">Altura Inicial ({initialHeightUnit}):</label>
          <input type="number" id="initial_height" bind:value={params.initial_height} class="fluent-input" min="0" step="0.1">
          <select bind:value={initialHeightUnit} class="fluent-select unit-select">
            {#each HEIGHT_UNITS as unit (unit.value)}
              <option value={unit.value}>{unit.label}</option>
            {/each}
          </select>

          <label for="gravity">Aceleração da Gravidade (m/s²):</label>
          <input type="number" id="gravity" bind:value={params.gravity} class="fluent-input" min="0.1" step="0.01">
        </fieldset>
      </div>

      <fieldset>
        <legend>Unidades de Saída para Resultados</legend>
        <div class="form-grid">
          <div>
            <label for="output_distance_unit">Unidade para Distâncias (Resultados):</label>
            <select id="output_distance_unit" bind:value={outputDistanceUnit} class="fluent-select unit-select">
              {#each DISTANCE_OUTPUT_UNITS as unit (unit.value)}
                <option value={unit.value}>{unit.label}</option>
              {/each}
            </select>
          </div>
          <div>
            <label for="output_velocity_unit">Unidade para Velocidades (Resultados):</label>
            <select id="output_velocity_unit" bind:value={outputVelocityUnit} class="fluent-select unit-select">
              {#each VELOCITY_OUTPUT_UNITS as unit (unit.value)}
                <option value={unit.value}>{unit.label}</option>
              {/each}
            </select>
          </div>
          <div>
            <label for="output_time_unit">Unidade para Tempo (Resultados):</label>
            <select id="output_time_unit" bind:value={outputTimeUnit} class="fluent-select unit-select">
              {#each TIME_OUTPUT_UNITS as unit (unit.value)}
                <option value={unit.value}>{unit.label}</option>
              {/each}
            </select>
          </div>
        </div>
      </fieldset>

      <button type="submit" class="fluent-button" disabled={isLoading}>
        {#if isLoading}
          Calculando Trajetória...
        {:else}
          Simular Lançamento
        {/if}
      </button>
    </form>
  </section>

  {#if simulationResult}
    {#if simulationResult.max_range_unit && simulationResult.max_height_unit && simulationResult.total_time_unit && simulationResult.initial_velocity_x_unit && simulationResult.initial_velocity_y_unit && simulationResult.parameters_used && simulationResult.trajectory && simulationResult.trajectory.length > 0}
    <section class="content-section results-section" transition:fade={{ duration: 300 }}>
      <h2 style="text-align: center; margin-bottom: var(--spacing-l); color: var(--color-text-primary); font-size: var(--font-size-title); font-weight: var(--font-weight-semibold);">Resultados do Lançamento</h2>
      <div class="results-summary-grid">
        <div class="result-item">
          <strong>Alcance Máximo:</strong> {simulationResult.max_range.toFixed(2)} {simulationResult.max_range_unit}
        </div>
        <div class="result-item">
          <strong>Altura Máxima:</strong> {simulationResult.max_height.toFixed(2)} {simulationResult.max_height_unit}
        </div>
        <div class="result-item">
          <strong>Tempo Total de Voo:</strong> {simulationResult.total_time.toFixed(2)} {simulationResult.total_time_unit}
        </div>
        <div class="result-item">
          <strong>Velocidade Inicial X:</strong> {simulationResult.initial_velocity_x.toFixed(2)} {simulationResult.initial_velocity_x_unit}
        </div>
        <div class="result-item">
          <strong>Velocidade Inicial Y:</strong> {simulationResult.initial_velocity_y.toFixed(2)} {simulationResult.initial_velocity_y_unit}
        </div>
      </div>

      <h3 style="margin-top: var(--spacing-l); margin-bottom:var(--spacing-s); color: var(--color-text-primary); font-size: var(--font-size-subheader); font-weight: var(--font-weight-semibold);">Trajetória do Projétil:</h3>
      {#if simulationResult.trajectory && simulationResult.trajectory.length > 0}
        <div class="trajectory-container" role="img" aria-label="Gráfico da trajetória do projétil">
          <svg
            width="100%"
            height="300"
            viewBox="{getSvgViewBox(simulationResult.trajectory, simulationResult.max_range, simulationResult.max_height, simulationResult.parameters_used.initial_height)}"
            preserveAspectRatio="xMidYMin meet"
            style="border: 1px solid var(--color-neutral-stroke-default); background-color: var(--color-neutral-layer-2); border-radius: var(--border-radius-small);"
          >
            <line x1="0" y1="{svgAdjustedY(0, simulationResult.trajectory, simulationResult.max_height, simulationResult.parameters_used.initial_height)}"
                  x2="{svgAdjustedX(simulationResult.max_range, simulationResult.trajectory)}"
                  y2="{svgAdjustedY(0, simulationResult.trajectory, simulationResult.max_height, simulationResult.parameters_used.initial_height)}"
                  stroke="var(--color-neutral-stroke-default)" stroke-width="1"/>
            <line x1="{svgAdjustedX(0, simulationResult.trajectory)}" y1="0"
                  x2="{svgAdjustedX(0, simulationResult.trajectory)}"
                  y2="{svgAdjustedY(simulationResult.max_height, simulationResult.trajectory, simulationResult.max_height, simulationResult.parameters_used.initial_height) + 20}"
                  stroke="var(--color-neutral-stroke-default)" stroke-width="1"/>

            <polyline
              points="{formatTrajectoryForSvg(simulationResult.trajectory, simulationResult.max_height, simulationResult.parameters_used.initial_height)}"
              fill="none"
              stroke="var(--color-accent-primary)"
              stroke-width="2"
            />
            <circle cx="{svgAdjustedX(simulationResult.trajectory[0].x, simulationResult.trajectory)}"
                    cy="{svgAdjustedY(simulationResult.trajectory[0].y, simulationResult.trajectory, simulationResult.max_height, simulationResult.parameters_used.initial_height)}"
                    r="3" fill="var(--color-text-success)" />
            <circle cx="{svgAdjustedX(simulationResult.trajectory[simulationResult.trajectory.length - 1].x, simulationResult.trajectory)}"
                    cy="{svgAdjustedY(simulationResult.trajectory[simulationResult.trajectory.length - 1].y, simulationResult.trajectory, simulationResult.max_height, simulationResult.parameters_used.initial_height)}"
                    r="3" fill="var(--color-text-error)" />
          </svg>
        </div>
      {:else}
        <p>Dados da trajetória não disponíveis.</p>
      {/if}

      <h4 style="margin-top: var(--spacing-l); margin-bottom:var(--spacing-s); color: var(--color-text-primary); font-size: var(--font-size-subheader); font-weight: var(--font-weight-semibold);">Dados da Trajetória (amostra):</h4>
      <div class="trajectory-table-container">
        <table>
          <thead>
            <tr>
              <th>Tempo ({simulationResult.total_time_unit})</th>
              <th>X ({simulationResult.max_range_unit})</th>
              <th>Y ({simulationResult.max_range_unit})</th>
            </tr>
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
    {:else if simulationResult}
    <section class="content-section results-section" transition:fade={{ duration: 300 }}>
      <h2 style="text-align: center; margin-bottom: var(--spacing-l); color: var(--color-text-primary); font-size: var(--font-size-title); font-weight: var(--font-weight-semibold);">Resultados da Simulação (Dados Incompletos)</h2>
      <p class="fluent-alert-error">
        Os resultados da simulação foram recebidos, mas alguns dados necessários para a exibição completa estão ausentes (ex: unidades específicas como `max_range_unit`, `parameters_used` ou `trajectory`).
      </p>
      <p><strong>Dados recebidos:</strong></p>
      <pre class="raw-json-output">{JSON.stringify(simulationResult, null, 2)}</pre>

      <h4 style="margin-top: var(--spacing-l); margin-bottom:var(--spacing-s); color: var(--color-text-primary); font-size: var(--font-size-subheader); font-weight: var(--font-weight-semibold);">Sumário Básico (se disponível):</h4>
      <ul>
        {#if simulationResult.max_range !== undefined}
          <li>Alcance Máximo: {simulationResult.max_range.toFixed(2)} {simulationResult.max_range_unit || ''}</li>
        {/if}
        {#if simulationResult.max_height !== undefined}
          <li>Altura Máxima: {simulationResult.max_height.toFixed(2)} {simulationResult.max_height_unit || ''}</li>
        {/if}
        {#if simulationResult.total_time !== undefined}
          <li>Tempo Total de Voo: {simulationResult.total_time.toFixed(2)} {simulationResult.total_time_unit || ''}</li>
        {/if}
      </ul>
    </section>
    {/if}
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
    /* fieldset background should be transparent if its parent section is already layer-1 */
    margin-bottom: var(--spacing-l); /* Added margin for spacing between fieldsets */
  }

  legend {
    font-weight: var(--font-weight-semibold);
    color: var(--color-text-primary);
    padding: 0 var(--spacing-xs);
    margin-bottom: var(--spacing-s); /* Reduced from m to s */
    font-size: var(--font-size-subheader);
  }

  label {
    display: block;
    margin-bottom: var(--spacing-xs);
    font-weight: var(--font-weight-regular);
    color: var(--color-text-primary);
  }

  fieldset small {
    display: block;
    margin-top: var(--spacing-xs);
    margin-bottom: var(--spacing-s); /* Added margin for spacing */
    font-size: var(--font-size-caption);
    color: var(--color-text-secondary);
  }

  .unit-select { /* Specific class for unit selects if they need different margin than fluent-input */
    margin-top: var(--spacing-xs);
    margin-bottom: var(--spacing-s);
  }

  .results-summary-grid {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(220px, 1fr));
    gap: var(--spacing-m);
    margin-bottom: var(--spacing-l);
  }

  .results-summary-grid .result-item {
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

  .trajectory-container {
    width: 100%;
    max-width: 600px;
    margin: var(--spacing-l) auto;
    overflow: hidden;
  }

  .trajectory-table-container {
    margin-top: var(--spacing-m);
    max-height: 250px; /* Increased height a bit */
    overflow-y: auto;
    border: 1px solid var(--color-neutral-stroke-default);
    border-radius: var(--border-radius-medium);
    background-color: var(--color-neutral-layer-1);
  }

  table {
    width: 100%;
    border-collapse: collapse;
    font-size: var(--font-size-body);
  }
  table th, table td {
    text-align: left;
    padding: var(--spacing-s);
    border-bottom: 1px solid var(--color-neutral-stroke-default);
  }
  table th {
    background-color: var(--color-neutral-layer-2);
    color: var(--color-text-primary);
    font-weight: var(--font-weight-semibold);
    position: sticky;
    top: 0;
  }
  table td {
    color: var(--color-text-primary);
  }
  table tbody tr:last-child td {
    border-bottom: none;
  }
  table tbody tr:hover {
    background-color: var(--color-neutral-layer-2);
  }

  .raw-json-output {
    background-color: var(--color-neutral-layer-2);
    border: 1px solid var(--color-neutral-stroke-default);
    color: var(--color-text-secondary);
    padding: var(--spacing-m);
    border-radius: var(--border-radius-small);
    font-family: monospace;
    font-size: var(--font-size-caption);
    white-space: pre-wrap;
    word-break: break-all;
    max-height: 300px;
    overflow-y: auto;
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
