```svelte
<script>
  // import { goto } from '$app/navigation'; // For navigation - remove if not used

  let analyte_is_acid = true; // Default to acid
  let acid_name = 'HCl';
  let acid_concentration = 0.1;
  let acid_volume = 50;
  let acid_ka = ''; // Optional, so can be empty string

  let base_name = 'NaOH';
  let base_concentration = 0.1;
  let base_volume = 50;
  let base_kb = ''; // Optional

  let titrant_is_acid = false; // Titrant is typically the opposite of analyte
  let titrant_name = 'NaOH'; // Default titrant name, can be changed by user
  let titrant_concentration = 0.1;
  let initial_titrant_volume_ml = 0.0;
  let final_titrant_volume_ml = 100;
  let volume_increment_ml = 1;

  // Update titrant_is_acid based on analyte_is_acid
  $: titrant_is_acid = !analyte_is_acid;

  let simulationResults = null;
  let titrationCurveData = [];
  let errorMessage = '';
  let isLoading = false;

  // SVG Chart related variables
  const width = 700; // SVG width
  const height = 400; // SVG height
  const padding = { top: 20, right: 20, bottom: 50, left: 50 }; // Adjusted bottom and left for labels
  const svgWidth = width;
  const svgHeight = height;

  let svgPathD = '';
  let xAxisTicks = [];
  let yAxisTicks = [];

  $: if (titrationCurveData && titrationCurveData.length > 0) {
    updateChartVisuals();
  }

  function updateChartVisuals() {
    if (!titrationCurveData || titrationCurveData.length === 0) {
      svgPathD = '';
      xAxisTicks = [];
      yAxisTicks = [];
      return;
    }

    const xValues = titrationCurveData.map(d => d.titrant_volume_added_ml);
    const yValues = titrationCurveData.map(d => d.ph);

    const minX = Math.min(...xValues);
    const maxX = Math.max(...xValues);
    const minY = 0;
    const maxY = 14;

    const drawableWidth = svgWidth - padding.left - padding.right;
    const drawableHeight = svgHeight - padding.top - padding.bottom;

    const xScale = (val) => {
      if (maxX === minX) {
        return padding.left + drawableWidth / 2;
      }
      return padding.left + ((val - minX) / (maxX - minX)) * drawableWidth;
    };

    const yScale = (val) => {
        const clampedVal = Math.max(minY, Math.min(maxY, val));
        return svgHeight - padding.bottom - ((clampedVal - minY) / (maxY - minY)) * drawableHeight;
    };

    if (titrationCurveData.length > 0) {
        svgPathD = "M" + titrationCurveData.map(d => `${xScale(d.titrant_volume_added_ml)},${yScale(d.ph)}`).join(" L");
    } else {
        svgPathD = '';
    }

    xAxisTicks = [];
    const xTickCount = Math.min(5, xValues.length > 1 ? 5 : xValues.length);
    if (maxX === minX && xValues.length > 0) {
        xAxisTicks = [{ x: xScale(minX), label: minX.toFixed(1) }];
    } else if (xValues.length === 1) {
        xAxisTicks = [{ x: xScale(xValues[0]), label: xValues[0].toFixed(1) }];
    } else if (xValues.length > 1) {
        const xTickIncrement = (maxX - minX) / (xTickCount > 1 ? (xTickCount -1) : 1) ; // Avoid division by zero if xTickCount is 1
        for (let i = 0; i < xTickCount; i++) {
            const value = minX + i * xTickIncrement;
            xAxisTicks.push({ x: xScale(value), label: value.toFixed(1) });
        }
        // Ensure the last tick is exactly maxX if not already covered and different from the last calculated tick
        if (xTickCount > 1 && xAxisTicks.length > 0 && xAxisTicks[xAxisTicks.length-1].label !== maxX.toFixed(1)) {
             if (xScale(maxX) - xAxisTicks[xAxisTicks.length-1].x > 10) {
                xAxisTicks.push({ x: xScale(maxX), label: maxX.toFixed(1) });
             } else {
                xAxisTicks[xAxisTicks.length-1] = { x: xScale(maxX), label: maxX.toFixed(1) };
             }
        }
    }


    yAxisTicks = [];
    const yTickIncrement = 2;
    for (let i = minY; i <= maxY; i += yTickIncrement) {
      yAxisTicks.push({ y: yScale(i), label: i.toString() });
    }
  }


  async function runSimulation() {
    isLoading = true;
    errorMessage = '';
    // simulationResults = null; // Keep previous results visible during loading if preferred, or clear them:
    // titrationCurveData = [];

    // Client-side validation for volumes
    if (parseFloat(final_titrant_volume_ml) <= parseFloat(initial_titrant_volume_ml)) {
      errorMessage = "O Volume Final de Titulante deve ser maior que o Volume Inicial.";
      isLoading = false;
      return;
    }
    if (parseFloat(volume_increment_ml) <= 0) {
      errorMessage = "O Incremento de Volume deve ser um valor positivo.";
      isLoading = false;
      return;
    }

    const scientificNotationPattern = /^-?\d+(\.\d+)?[eE][-+]?\d+$/;
    if (analyte_is_acid && acid_ka && !scientificNotationPattern.test(acid_ka) && isNaN(parseFloat(acid_ka))) {
        errorMessage = "Ka do ácido parece inválido. Use notação científica (ex: 1.8e-5) ou um número.";
        isLoading = false;
        return;
    }
    if (!analyte_is_acid && base_kb && !scientificNotationPattern.test(base_kb) && isNaN(parseFloat(base_kb))) {
        errorMessage = "Kb da base parece inválido. Use notação científica (ex: 1.8e-5) ou um número.";
        isLoading = false;
        return;
    }

    let params = {
      analyte_is_acid: analyte_is_acid,
      titrant_is_acid: titrant_is_acid,
      titrant_name: titrant_name,
      titrant_concentration: parseFloat(titrant_concentration),
      initial_titrant_volume_ml: parseFloat(initial_titrant_volume_ml),
      final_titrant_volume_ml: parseFloat(final_titrant_volume_ml),
      volume_increment_ml: parseFloat(volume_increment_ml),
    };

    if (analyte_is_acid) {
      params.acid_name = acid_name;
      params.acid_concentration = parseFloat(acid_concentration);
      params.acid_volume = parseFloat(acid_volume);
      params.acid_ka = acid_ka ? acid_ka : null;
      params.base_name = null;
      params.base_concentration = null;
      params.base_volume = null;
      params.base_kb = null;
    } else {
      params.base_name = base_name;
      params.base_concentration = parseFloat(base_concentration);
      params.base_volume = parseFloat(base_volume);
      params.base_kb = base_kb ? base_kb : null;
      params.acid_name = null;
      params.acid_concentration = null;
      params.acid_volume = null;
      params.acid_ka = null;
    }

    try {
      const response = await fetch('/api/simulation/acid-base-titration/start', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(params),
      });

      if (!response.ok) {
        let errorData;
        try {
          errorData = await response.json();
        } catch (e) {
          const textError = await response.text();
          errorData = { detail: textError || response.statusText };
        }
        errorMessage = `Erro ${response.status}: ${errorData.detail || 'Ocorreu um erro desconhecido.'}`;
        if (errorData.errors) {
          errorMessage += ` Detalhes: ${JSON.stringify(errorData.errors)}`;
        }
        titrationCurveData = []; // Clear previous graph data on error
      } else {
        const data = await response.json();
        simulationResults = data;
        if (data && data.titration_curve) {
          titrationCurveData = data.titration_curve;
        } else {
          titrationCurveData = []; // Ensure it's an empty array if no curve data
        }
      }
    } catch (error) {
      console.error('Fetch error:', error);
      errorMessage = `Erro ao conectar com o servidor: ${error.message}`;
      titrationCurveData = []; // Clear previous graph data on error
    } finally {
      isLoading = false;
    }
  }
</script>

<svelte:head>
  <title>Curva de Titulação Ácido-Base - Simulador Químico</title>
  <meta name="description" content="Simulador interativo de curva de titulação ácido-base. Explore diferentes combinações de ácidos e bases." />
</svelte:head>

<main class="container mx-auto p-4 sm:p-6 lg:p-8">
  <div class="mb-6">
    <a href="/" class="text-primary hover:text-primary-focus transition-colors duration-150 ease-in-out">&larr; Voltar para Experimentos</a>
  </div>

  <h1 class="text-3xl font-bold text-center my-8 text-primary-700">Curva de Titulação Ácido-Base</h1>

  <form on:submit|preventDefault={runSimulation} class="space-y-8">
    <section class="p-6 bg-base-100 shadow-xl rounded-lg">
      <h2 class="text-2xl font-semibold mb-6 text-base-content border-b pb-2">Parâmetros da Simulação</h2>

      <!-- Analyte Selection -->
      <div class="mb-6">
        <span class="block text-lg font-medium text-gray-700 mb-2">Analito (Substância a ser Titulada):</span>
        <div class="flex items-center space-x-4 p-2">
          <label class="label cursor-pointer">
            <input type="radio" name="analyte_type" bind:group={analyte_is_acid} value={true} class="radio radio-primary" />
            <span class="label-text ml-2">Ácido</span>
          </label>
          <label class="label cursor-pointer">
            <input type="radio" name="analyte_type" bind:group={analyte_is_acid} value={false} class="radio radio-primary" />
            <span class="ml-2">Base</span>
          </label>
        </div>
      </div>

      <!-- Analyte Details -->
      {#if analyte_is_acid}
        <div class="grid grid-cols-1 md:grid-cols-2 gap-6 mb-6 p-4 border border-base-300 rounded-lg">
          <div>
            <label for="acid_name" class="label"><span class="label-text">Nome do Ácido:</span></label>
            <input type="text" id="acid_name" bind:value={acid_name} class="input input-bordered w-full mt-1" placeholder="Ex: HCl" required>
          </div>
          <div>
            <label for="acid_concentration" class="label"><span class="label-text">Concentração do Ácido (mol/L):</span></label>
            <input type="number" step="any" id="acid_concentration" bind:value={acid_concentration} class="input input-bordered w-full mt-1" placeholder="Ex: 0.1" min="0" required>
          </div>
          <div>
            <label for="acid_volume" class="label"><span class="label-text">Volume do Ácido (mL):</span></label>
            <input type="number" step="any" id="acid_volume" bind:value={acid_volume} class="input input-bordered w-full mt-1" placeholder="Ex: 50" min="0" required>
          </div>
          <div>
            <label for="acid_ka" class="label"><span class="label-text">Constante de Acidez (Ka) (opcional):</span></label>
            <input type="text" id="acid_ka" bind:value={acid_ka} class="input input-bordered w-full mt-1" placeholder="Ex: 1.8e-5 (para ácido fraco)">
          </div>
        </div>
      {:else}
        <div class="grid grid-cols-1 md:grid-cols-2 gap-6 mb-6 p-4 border border-base-300 rounded-lg">
          <div>
            <label for="base_name" class="label"><span class="label-text">Nome da Base:</span></label>
            <input type="text" id="base_name" bind:value={base_name} class="input input-bordered w-full mt-1" placeholder="Ex: NaOH" required>
          </div>
          <div>
            <label for="base_concentration" class="label"><span class="label-text">Concentração da Base (mol/L):</span></label>
            <input type="number" step="any" id="base_concentration" bind:value={base_concentration} class="input input-bordered w-full mt-1" placeholder="Ex: 0.1" min="0" required>
          </div>
          <div>
            <label for="base_volume" class="label"><span class="label-text">Volume da Base (mL):</span></label>
            <input type="number" step="any" id="base_volume" bind:value={base_volume} class="input input-bordered w-full mt-1" placeholder="Ex: 50" min="0" required>
          </div>
          <div>
            <label for="base_kb" class="label"><span class="label-text">Constante de Basicidade (Kb) (opcional):</span></label>
            <input type="text" id="base_kb" bind:value={base_kb} class="input input-bordered w-full mt-1" placeholder="Ex: 1.8e-5 (para base fraca)">
          </div>
        </div>
      {/if}

      <!-- Titrant Details -->
      <div class="mb-6 border-t border-base-300 pt-6">
        <h3 class="text-xl font-semibold text-gray-700 mb-3">Titulante</h3>
        <div class="form-control mb-4">
          <label class="label cursor-pointer">
            <span class="label-text">Titulante é um ácido?</span>
            <input type="checkbox" bind:checked={titrant_is_acid} class="checkbox checkbox-primary" />
          </label>
        </div>
        <div class="grid grid-cols-1 md:grid-cols-2 gap-6">
          <div>
            <label for="titrant_name" class="label"><span class="label-text">Nome do Titulante:</span></label>
            <input type="text" id="titrant_name" bind:value={titrant_name} class="input input-bordered w-full mt-1" placeholder={titrant_is_acid ? "Ex: HCl" : "Ex: NaOH"} required>
          </div>
          <div>
            <label for="titrant_concentration" class="label"><span class="label-text">Concentração do Titulante (mol/L):</span></label>
            <input type="number" step="any" id="titrant_concentration" bind:value={titrant_concentration} class="input input-bordered w-full mt-1" placeholder="Ex: 0.1" min="0" required>
          </div>
        </div>
      </div>

      <!-- Titration Process Parameters -->
      <div class="mb-6 border-t border-base-300 pt-6">
        <h3 class="text-xl font-medium text-gray-700 mb-3">Processo de Titulação:</h3>
        <div class="grid grid-cols-1 md:grid-cols-3 gap-6">
          <div>
            <label for="initial_titrant_volume_ml" class="label"><span class="label-text">Volume Inicial de Titulante (mL):</span></label>
            <input type="number" step="any" id="initial_titrant_volume_ml" bind:value={initial_titrant_volume_ml} class="input input-bordered w-full mt-1" min="0" required>
          </div>
          <div>
            <label for="final_titrant_volume_ml" class="label"><span class="label-text">Volume Final de Titulante (mL):</span></label>
            <input type="number" step="any" id="final_titrant_volume_ml" bind:value={final_titrant_volume_ml} class="input input-bordered w-full mt-1" placeholder="Ex: 100" min="0" required>
          </div>
          <div>
            <label for="volume_increment_ml" class="label"><span class="label-text">Incremento de Volume (mL):</span></label>
            <input type="number" step="any" id="volume_increment_ml" bind:value={volume_increment_ml} class="input input-bordered w-full mt-1" placeholder="Ex: 1" min="0.0000000001" required>
          </div>
        </div>
      </div>

      <div class="text-center mt-8">
        <button type="submit" class="btn btn-primary btn-lg" disabled={isLoading}>
          {#if isLoading}
            <span class="loading loading-spinner"></span>
            Simulando...
          {:else}
            Simular
          {/if}
        </button>
      </div>
    </section>
  </form>

  {#if isLoading || errorMessage || simulationResults}
  <section class="mb-8 p-6 bg-base-100 shadow-md rounded-lg">
    <h2 class="text-2xl font-semibold mb-6 text-base-content border-b pb-2">Resultados da Simulação</h2>

    {#if isLoading}
      <div class="text-center my-4 p-4">
        <span class="loading loading-lg loading-dots text-primary"></span>
        <p class="text-lg text-primary-focus mt-2">Calculando...</p>
      </div>
    {/if}

    {#if errorMessage && !isLoading}
      <div role="alert" class="alert alert-error shadow-lg my-4">
        <svg xmlns="http://www.w3.org/2000/svg" class="stroke-current flex-shrink-0 h-6 w-6" fill="none" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M10 14l2-2m0 0l2-2m-2 2l-2-2m2 2l2 2m7-2a9 9 0 11-18 0 9 9 0 0118 0z" /></svg>
        <span><strong>Erro na Simulação:</strong> {errorMessage}</span>
      </div>
    {/if}

    {#if simulationResults && !isLoading && !errorMessage}
      <div class="mt-4 space-y-6"> {/* Increased spacing for better readability */}
        {#if simulationResults.message}
          <div class="alert alert-info shadow-lg">
            <div>
              <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" class="stroke-current flex-shrink-0 w-6 h-6"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13 16h-1v-4h-1m1-4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z"></path></svg>
              <span>{simulationResults.message}</span>
            </div>
          </div>
        {/if}

        {#if simulationResults.parameters_used}
          <div class="p-4 bg-base-200 rounded-lg shadow">
            <h3 class="text-xl font-semibold text-base-content mb-4">Parâmetros Utilizados:</h3>
            <dl class="grid grid-cols-1 md:grid-cols-2 gap-x-6 gap-y-3 text-sm">
              {#if simulationResults.parameters_used.analyte_is_acid}
                <div class="col-span-full mb-2 text-lg font-medium text-base-content">Analito (Ácido):</div>
                <div>
                  <dt class="font-semibold text-base-content/70">Nome:</dt>
                  <dd class="text-base-content">{simulationResults.parameters_used.acid_name || 'N/A'}</dd>
                </div>
                <div>
                  <dt class="font-semibold text-base-content/70">Concentração:</dt>
                  <dd class="text-base-content">{simulationResults.parameters_used.acid_concentration} mol/L</dd>
                </div>
                <div>
                  <dt class="font-semibold text-base-content/70">Volume:</dt>
                  <dd class="text-base-content">{simulationResults.parameters_used.acid_volume} mL</dd>
                </div>
                {#if simulationResults.parameters_used.acid_ka}
                  <div>
                    <dt class="font-semibold text-base-content/70">Ka:</dt>
                    <dd class="text-base-content">{simulationResults.parameters_used.acid_ka}</dd>
                  </div>
                {/if}
              {:else}
                <div class="col-span-full mb-2 text-lg font-medium text-base-content">Analito (Base):</div>
                <div>
                  <dt class="font-semibold text-base-content/70">Nome:</dt>
                  <dd class="text-gray-800">{simulationResults.parameters_used.base_name || 'N/A'}</dd>
                </div>
                <div>
                  <dt class="font-semibold text-gray-600">Concentração:</dt>
                  <dd class="text-base-content">{simulationResults.parameters_used.base_concentration} mol/L</dd>
                </div>
                <div>
                  <dt class="font-semibold text-gray-600">Volume:</dt>
                  <dd class="text-base-content">{simulationResults.parameters_used.base_volume} mL</dd>
                </div>
                {#if simulationResults.parameters_used.base_kb}
                  <div>
                    <dt class="font-semibold text-gray-600">Kb:</dt>
                    <dd class="text-base-content">{simulationResults.parameters_used.base_kb}</dd>
                  </div>
                {/if}
              {/if}

              <div class="col-span-full mt-3 mb-1 text-lg font-medium text-base-content">Titulante:</div>
              <div>
                <dt class="font-semibold text-gray-600">Tipo:</dt>
                <dd class="text-base-content">{simulationResults.parameters_used.titrant_is_acid ? 'Ácido' : 'Base'}</dd>
              </div>
              <div>
                <dt class="font-semibold text-gray-600">Nome:</dt>
                <dd class="text-base-content">{simulationResults.parameters_used.titrant_name || 'N/A'}</dd>
              </div>
              <div>
                <dt class="font-semibold text-gray-600">Concentração:</dt>
                <dd class="text-base-content">{simulationResults.parameters_used.titrant_concentration} mol/L</dd>
              </div>

              <div class="col-span-full mt-3 mb-1 text-lg font-medium text-base-content">Processo de Titulação:</div>
              <div>
                <dt class="font-semibold text-gray-600">Volume Inicial:</dt>
                <dd class="text-base-content">{simulationResults.parameters_used.initial_titrant_volume_ml} mL</dd>
              </div>
              <div>
                <dt class="font-semibold text-gray-600">Volume Final:</dt>
                <dd class="text-gray-800">{simulationResults.parameters_used.final_titrant_volume_ml} mL</dd>
              </div>
              <div>
                <dt class="font-semibold text-gray-600">Incremento:</dt>
                <dd class="text-base-content">{simulationResults.parameters_used.volume_increment_ml} mL</dd>
              </div>
            </dl>
          </div>
        {/if}

        {#if simulationResults.equivalence_points_ml && simulationResults.equivalence_points_ml.length > 0}
          <div class="alert alert-success shadow-lg mt-4"> {/* Added mt-4 for spacing */}
            <div>
                <svg xmlns="http://www.w3.org/2000/svg" class="stroke-current flex-shrink-0 h-6 w-6" fill="none" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" /></svg>
              <span><strong>Pontos de Equivalência Detectados (mL):</strong> {simulationResults.equivalence_points_ml.join(', ')}</span>
            </div>
          </div>
        {/if}
      </div>
    {/if}
    <!-- The pre tag for raw JSON is now definitely removed/disabled by the logic above -->
  </section>

  <section class="mb-8 p-6 bg-white shadow-md rounded-lg">
    <h2 class="text-2xl font-semibold mb-6 text-gray-700 border-b pb-2">Gráfico da Curva de Titulação</h2>
    {#if titrationCurveData && titrationCurveData.length > 0}
      <div class="chart-container bg-base-100 p-4 rounded-lg shadow-inner" role="figure" aria-labelledby="chart-title"> {/* Added bg-base-100, p-4, rounded-lg, shadow-inner */}
        <svg {width} {height} viewBox="0 0 {svgWidth} {svgHeight}" preserveAspectRatio="xMidYMin meet" aria-labelledby="chart-title-svg" aria-describedby="chart-desc-svg" class="mx-auto"> {/* Added mx-auto to center if width is constrained */}
          <title id="chart-title-svg">Curva de Titulação Ácido-Base</title>
          <desc id="chart-desc-svg">Gráfico de pH em função do volume de titulante adicionado.</desc>

          <!-- Y Axis (pH) -->
          <line x1={padding.left} y1={padding.top} x2={padding.left} y2={svgHeight - padding.bottom} stroke="currentColor" />
          {#each yAxisTicks as tick}
            <g class="tick">
              <line x1={padding.left - 5} y1={tick.y} x2={padding.left} y2={tick.y} stroke="currentColor" />
              <text x={padding.left - 10} y={tick.y + 4} text-anchor="end" font-size="10" class="fill-current text-xs">{tick.label}</text>
            </g>
          {/each}
          <text x={padding.left - 35} y={padding.top + (svgHeight - padding.top - padding.bottom) / 2} transform="rotate(-90, {padding.left - 35}, {padding.top + (svgHeight - padding.top - padding.bottom) / 2})" text-anchor="middle" font-size="12" class="fill-current font-semibold">pH</text>

          <!-- X Axis (Volume) -->
          <line x1={padding.left} y1={svgHeight - padding.bottom} x2={svgWidth - padding.right} y2={svgHeight - padding.bottom} stroke="currentColor" />
          {#each xAxisTicks as tick}
            <g class="tick">
              <line x1={tick.x} y1={svgHeight - padding.bottom} x2={tick.x} y2={svgHeight - padding.bottom + 5} stroke="currentColor" />
              <text x={tick.x} y={svgHeight - padding.bottom + 15} text-anchor="middle" font-size="10" class="fill-current text-xs">{tick.label}</text>
            </g>
          {/each}
          <text x={padding.left + (svgWidth - padding.left - padding.right) / 2} y={svgHeight - padding.bottom + 35} text-anchor="middle" font-size="12" class="fill-current font-semibold">Volume do Titulante Adicionado (mL)</text>

          <!-- Titration Curve Path -->
          <path d={svgPathD} fill="none" stroke="var(--color-primary, oklch(var(--p)))" stroke-width="2" /> {/* Using DaisyUI primary color variable */}

        </svg>
      </div>
    {:else if isLoading}
      <div class="text-center py-10">
        <span class="loading loading-lg loading-dots text-primary"></span>
        <p class="text-gray-500 mt-2">Gerando gráfico...</p>
      </div>
    {:else if !errorMessage && !simulationResults}
      <div class="text-center py-10 text-gray-500">
        <p>Preencha os parâmetros da simulação e clique em "Simular" para gerar o gráfico.</p>
      </div>
    {:else if !errorMessage && simulationResults && (!titrationCurveData || titrationCurveData.length === 0)}
      <div class="alert alert-warning shadow-lg my-4">
        <div>
          <svg xmlns="http://www.w3.org/2000/svg" class="stroke-current flex-shrink-0 h-6 w-6" fill="none" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z" /></svg>
          <span>Não há dados suficientes na curva de titulação para desenhar o gráfico.</span>
        </div>
      </div>
    {/if}
  </section>
</main>

<style>
  .chart-container {
    width: 100%;
    max-width: 700px;
    margin: 20px auto;
    /* background-color: #f9f9f9; Tailwind bg-base-100 used instead */
    /* border: 1px solid #e0e0e0; */ /* Replaced by shadow-md */
    /* border-radius: 4px; */ /* Handled by rounded-lg */
    padding: 1rem; /* Using Tailwind padding classes */
  }
  svg {
    display: block;
    width: 100%;
    height: auto;
  }
  .tick text {
    fill: currentColor; /* Use Tailwind's text color utilities */
    font-size: 0.75rem; /* text-xs */
  }
  path {
    stroke-linecap: round;
    stroke-linejoin: round;
  }
</style>
```
