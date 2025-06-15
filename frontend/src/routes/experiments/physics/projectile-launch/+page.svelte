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

    // Garantir que os tipos de dados estão corretos antes de enviar
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
        height_unit: outputDistanceUnit // Assuming height_unit uses the same selection as range_unit
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

  // Calcula o atributo viewBox para o SVG, para enquadrar corretamente a trajetória.
  // O viewBox define a "janela" de visualização das coordenadas internas do SVG.
  // Formato: "minX minY width height"
  function getSvgViewBox(trajectory, maxRange, maxHeight, initialHeight) {
    if (!trajectory || trajectory.length === 0) {
      return "0 0 100 100"; // ViewBox padrão se não houver trajetória
    }
    const padding = 20; // Espaçamento visual ao redor da trajetória dentro do SVG

    // Largura visual: alcance máximo + padding em ambos os lados.
    // Se maxRange for 0, usa um valor padrão para evitar largura 0.
    const viewWidth = (maxRange > 0 ? maxRange : 100) + 2 * padding;
    // Altura visual: altura máxima (considerando altura inicial se for maior que o pico da trajetória)
    // + padding em cima e embaixo.
    const effectiveMaxPhysicalY = Math.max(maxHeight, initialHeight);
    const viewHeight = (effectiveMaxPhysicalY > 0 ? effectiveMaxPhysicalY : 100) + 2 * padding;

    // minX do viewBox: começa um 'padding' à esquerda da origem física (x=0).
    const minX = -padding;
    // minY do viewBox: No SVG, o eixo Y cresce para baixo.
    // Esta implementação de viewBox, junto com svgAdjustedY, faz com que:
    // - O ponto (0,0) físico (origem do lançamento) seja mapeado para (0, altura_máxima_efetiva + padding) no sistema de coordenadas do SVG.
    // - O eixo Y físico positivo (para cima) corresponda ao eixo Y SVG negativo (para cima).
    // min-y define o valor Y no topo do viewBox. Para que o ponto mais alto da trajetória (maxHeight)
    // fique visível com padding, e o "chão" (y=0 físico) também tenha padding abaixo dele,
    // e considerando que svgAdjustedY inverte as coordenadas Y,
    // o minY do viewBox é -padding.
    const minY = -padding;

    return `${minX} ${minY} ${viewWidth} ${viewHeight}`;
  }

  // Ajusta a coordenada X física para o sistema de coordenadas do SVG.
  // Nesta implementação, o minX do viewBox é -padding.
  // As coordenadas X da trajetória são usadas diretamente como coordenadas X no SVG,
  // assumindo que a origem (x=0) da física corresponde a x=0 no sistema de coordenadas do viewBox.
  // O padding lateral é gerenciado pelo tamanho e minX do viewBox.
  function svgAdjustedX(physicalX, trajectory) {
    return physicalX;
  }

  // Ajusta e INVERTE a coordenada Y física para o sistema de coordenadas do SVG.
  // physicalY: coordenada no sistema físico (y=0 é o solo, cresce para cima).
  // overallMaxHeight: altura máxima atingida pela trajetória, medida a partir do solo (y=0 físico).
  // physicalInitialHeight: altura inicial do lançamento (y0 físico).
  // O SVG tem y=0 no topo da sua área de desenho e o eixo Y cresce para baixo.
  // Esta função mapeia o Y físico para que o gráfico pareça correto (Y crescendo para cima) dentro do viewBox SVG.
  function svgAdjustedY(physicalY, trajectory, overallMaxHeight, physicalInitialHeight) {
    const padding = 20;
    // Determina a maior altura física relevante (pico da trajetória ou altura inicial).
    const effectiveMaxPhysicalY = Math.max(overallMaxHeight, physicalInitialHeight);
    // A coordenada Y no SVG é calculada para que:
    // 1. O eixo Y físico seja invertido (valores Y físicos maiores ficam "mais para cima" no SVG).
    // 2. Haja um 'padding' no topo do gráfico.
    // O cálculo (effectiveMaxPhysicalY + padding) - physicalY faz essa inversão e posicionamento.
    // - (effectiveMaxPhysicalY + padding) define uma linha de referência "acima" do ponto mais alto.
    // - Subtrair physicalY inverte o eixo:
    //   - Se physicalY = 0 (solo), Ysvg = effectiveMaxPhysicalY + padding (base do gráfico no SVG).
    //   - Se physicalY = effectiveMaxPhysicalY (ponto mais alto), Ysvg = padding (topo do gráfico no SVG).
    // Isso funciona em conjunto com o viewBox que tem minY = -padding.
    return (effectiveMaxPhysicalY + padding) - physicalY;
  }

  // Formata a lista de pontos da trajetória (objetos {x, y})
  // em uma string única de coordenadas, conforme esperado pelo atributo `points`
  // da tag `<polyline>` do SVG (ex: "x1,y1 x2,y2 x3,y3 ...").
  function formatTrajectoryForSvg(trajectory, overallMaxHeight, physicalInitialHeight) {
    if (!trajectory) return "";
    return trajectory
      .map(p => `${svgAdjustedX(p.x, trajectory)},${svgAdjustedY(p.y, trajectory, overallMaxHeight, physicalInitialHeight)}`)
      .join(" ");
  }

  // Retorna uma amostra dos pontos da trajetória para exibição em tabela.
  // Se a trajetória tiver muitos pontos, a tabela pode ficar muito longa.
  // Esta função seleciona aproximadamente 'count' pontos, incluindo o primeiro e o último.
  function getTrajectorySample(trajectory, count = 10) {
    if (!trajectory || trajectory.length === 0) return []; // Retorna vazio se não houver trajetória
    if (trajectory.length <= count) return trajectory; // Retorna todos os pontos se forem poucos

    const sample = [];
    // Calcula o passo para pegar 'count-1' pontos uniformemente espaçados.
    // O último ponto é adicionado separadamente para garantir sua inclusão.
    const step = Math.floor(trajectory.length / (count -1));
    for (let i = 0; i < count -1 ; i++) {
      sample.push(trajectory[i * step]);
    }
    sample.push(trajectory[trajectory.length - 1]); // Garante que o último ponto da trajetória seja incluído.
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
        <label for="initial_velocity">Velocidade Inicial ({initialVelocityUnit}):</label>
        <input type="number" id="initial_velocity" bind:value={params.initial_velocity} min="0.1" step="0.1" required>
        <select bind:value={initialVelocityUnit} class="unit-select">
          {#each VELOCITY_UNITS as unit (unit.value)}
            <option value={unit.value}>{unit.label}</option>
          {/each}
        </select>

        <label for="launch_angle">Ângulo de Lançamento (graus):</label>
        <input type="number" id="launch_angle" bind:value={params.launch_angle} min="1" max="89" step="1" required>
        <small>Valores entre 1 e 89 graus para lançamento oblíquo.</small>
      </fieldset>

      <fieldset>
        <legend>Parâmetros Adicionais (Opcionais)</legend>
        <label for="initial_height">Altura Inicial ({initialHeightUnit}):</label>
        <input type="number" id="initial_height" bind:value={params.initial_height} min="0" step="0.1">
        <select bind:value={initialHeightUnit} class="unit-select">
          {#each HEIGHT_UNITS as unit (unit.value)}
            <option value={unit.value}>{unit.label}</option>
          {/each}
        </select>

        <label for="gravity">Aceleração da Gravidade (m/s²):</label>
        <input type="number" id="gravity" bind:value={params.gravity} min="0.1" step="0.01">
      </fieldset>
    </div>

    <fieldset>
      <legend>Unidades de Saída para Resultados</legend>
      <div class="form-grid">
        <div>
          <label for="output_distance_unit">Unidade para Distâncias (Resultados):</label>
          <select id="output_distance_unit" bind:value={outputDistanceUnit} class="unit-select">
            {#each DISTANCE_OUTPUT_UNITS as unit (unit.value)}
              <option value={unit.value}>{unit.label}</option>
            {/each}
          </select>
        </div>
        <div>
          <label for="output_velocity_unit">Unidade para Velocidades (Resultados):</label>
          <select id="output_velocity_unit" bind:value={outputVelocityUnit} class="unit-select">
            {#each VELOCITY_OUTPUT_UNITS as unit (unit.value)}
              <option value={unit.value}>{unit.label}</option>
            {/each}
          </select>
        </div>
        <div>
          <label for="output_time_unit">Unidade para Tempo (Resultados):</label>
          <select id="output_time_unit" bind:value={outputTimeUnit} class="unit-select">
            {#each TIME_OUTPUT_UNITS as unit (unit.value)}
              <option value={unit.value}>{unit.label}</option>
            {/each}
          </select>
        </div>
      </div>
    </fieldset>

    <button type="submit" class="submit-button" disabled={isLoading}>
      {#if isLoading}
        Calculando Trajetória...
      {:else}
        Simular Lançamento
      {/if}
    </button>
  </form>

  {#if simulationResult}
    {#if simulationResult.max_range_unit && simulationResult.max_height_unit && simulationResult.total_time_unit && simulationResult.initial_velocity_x_unit && simulationResult.initial_velocity_y_unit && simulationResult.parameters_used && simulationResult.trajectory && simulationResult.trajectory.length > 0}
    <section class="results-section" transition:fade={{ duration: 300 }}>
      <h2>Resultados do Lançamento</h2>
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

      <h3>Trajetória do Projétil:</h3>
      {#if simulationResult.trajectory && simulationResult.trajectory.length > 0}
        <div class="trajectory-container" role="img" aria-label="Gráfico da trajetória do projétil">
          <svg
            width="100%"
            height="300"
            viewBox="{getSvgViewBox(simulationResult.trajectory, simulationResult.max_range, simulationResult.max_height, simulationResult.parameters_used.initial_height)}"
            preserveAspectRatio="xMidYMin meet"
            style="border: 1px solid #ccc; background-color: #f0f8ff;"
          >
            <!-- Eixos (simplificado) - Using version from Turn 40 prompt -->
            <line x1="0" y1="{svgAdjustedY(0, simulationResult.trajectory, simulationResult.max_height, simulationResult.parameters_used.initial_height)}"
                  x2="{svgAdjustedX(simulationResult.max_range, simulationResult.trajectory)}"
                  y2="{svgAdjustedY(0, simulationResult.trajectory, simulationResult.max_height, simulationResult.parameters_used.initial_height)}"
                  stroke="#aaa" stroke-width="1"/>
            <line x1="{svgAdjustedX(0, simulationResult.trajectory)}" y1="0"
                  x2="{svgAdjustedX(0, simulationResult.trajectory)}"
                  y2="{svgAdjustedY(simulationResult.max_height, simulationResult.trajectory, simulationResult.max_height, simulationResult.parameters_used.initial_height) + 20}"
                  stroke="#aaa" stroke-width="1"/>

            <!-- Trajetória -->
            <polyline
              points="{formatTrajectoryForSvg(simulationResult.trajectory, simulationResult.max_height, simulationResult.parameters_used.initial_height)}"
              fill="none"
              stroke="#2980b9"
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
    <section class="results-section" transition:fade={{ duration: 300 }}>
      <h2>Resultados da Simulação (Dados Incompletos)</h2>
      <p class="error-message">
        Os resultados da simulação foram recebidos, mas alguns dados necessários para a exibição completa estão ausentes (ex: unidades específicas como `max_range_unit`, `parameters_used` ou `trajectory`).
      </p>
      <p><strong>Dados recebidos:</strong></p>
      <pre class="raw-json-output">{JSON.stringify(simulationResult, null, 2)}</pre>

      <!-- Tentativa de exibir dados básicos se disponíveis -->
      <h4>Sumário Básico (se disponível):</h4>
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
  .unit-select {
    width: 100%;
    padding: 10px;
    margin-top: 2px; /* Espaço entre o input e o select */
    margin-bottom: 10px; /* Espaço antes do próximo label */
    border: 1px solid #ccc;
    border-radius: 4px;
    box-sizing: border-box;
    font-size: 0.95em;
    background-color: #fff;
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
    color: #c0392b; /* Darker red for errors */
    background-color: #fdecea;
    border: 1px solid #e74c3c;
    padding: 10px; border-radius: 4px; margin-top: 20px;
  }
  .raw-json-output {
    background-color: #f0f0f0;
    border: 1px solid #ddd;
    padding: 10px;
    border-radius: 4px;
    white-space: pre-wrap; /* Wrap long lines */
    word-break: break-all; /* Break words if necessary */
    max-height: 300px;
    overflow-y: auto;
    font-family: 'Courier New', Courier, monospace;
    font-size: 0.85em;
  }

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
