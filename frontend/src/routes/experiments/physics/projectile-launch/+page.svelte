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

  // Função assíncrona para iniciar a simulação de lançamento de projétil.
  // Envia os parâmetros para a API backend e processa a resposta.
  async function startSimulation() {
    isLoading = true; // Ativa o indicador de carregamento.
    error = null; // Limpa erros anteriores.
    simulationResult = null; // Limpa resultados de simulações anteriores.

    // Garante que os tipos de dados dos parâmetros estão corretos (float) antes de enviar para a API.
    // Os inputs HTML podem retornar strings, então a conversão explícita é uma boa prática.
    const payload = {
      initial_velocity: parseFloat(params.initial_velocity),
      launch_angle: parseFloat(params.launch_angle),
      initial_height: parseFloat(params.initial_height),
      gravity: parseFloat(params.gravity)
    };

    console.log("Enviando para API Lançamento Oblíquo:", payload); // Log para depuração.

    try {
      // Realiza a chamada POST para o endpoint da API que inicia a simulação.
      const response = await fetch('http://localhost:8000/api/simulation/physics/projectile-launch/start', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json', // Informa à API que o corpo da requisição é JSON.
        },
        body: JSON.stringify(payload), // Converte o objeto payload para uma string JSON.
      });

      // Verifica se a resposta da API foi bem-sucedida (status HTTP 2xx).
      if (!response.ok) {
        // Se a resposta não for OK, tenta extrair detalhes do erro do corpo da resposta JSON.
        // Se falhar ao parsear o JSON do erro, usa o statusText da resposta.
        const errorData = await response.json().catch(() => ({ detail: response.statusText }));
        throw new Error(errorData.detail || `Erro HTTP: ${response.status}`); // Lança um erro com a mensagem apropriada.
      }

      // Se a resposta for OK, converte o corpo da resposta JSON para um objeto JavaScript.
      simulationResult = await response.json();
      console.log("Resultado da simulação de Lançamento Oblíquo:", simulationResult); // Log do resultado para depuração.

    } catch (e) {
      // Captura quaisquer erros que ocorram durante a chamada fetch ou processamento da resposta.
      console.error("Falha ao iniciar simulação de Lançamento Oblíquo:", e);
      error = e.message || "Ocorreu um erro desconhecido ao contatar a API de física."; // Define a mensagem de erro para exibição.
    } finally {
      // Este bloco é executado independentemente de ter ocorrido um erro ou não.
      isLoading = false; // Desativa o indicador de carregamento.
    }
  }

  // Calcula o atributo viewBox para o SVG, para enquadrar corretamente a trajetória.
  // O viewBox define a "janela" de visualização das coordenadas internas do SVG.
  // Formato: "minX minY width height".
  // trajectory: Array de pontos da trajetória.
  // maxRange: Alcance horizontal máximo do projétil.
  // maxHeight: Altura máxima atingida pelo projétil.
  // initialHeight: Altura inicial do lançamento.
  function getSvgViewBox(trajectory, maxRange, maxHeight, initialHeight) {
    if (!trajectory || trajectory.length === 0) {
      return "0 0 100 100"; // Retorna um viewBox padrão se não houver trajetória.
    }
    const padding = 20; // Define um espaçamento visual (margem) ao redor da trajetória dentro do SVG.

    // Calcula a largura visual do viewBox.
    // Baseia-se no alcance máximo (maxRange), adicionando padding em ambos os lados.
    // Se maxRange for 0 (ex: lançamento vertical que cai no mesmo lugar), usa uma largura padrão de 100 unidades.
    const viewWidth = (maxRange > 0 ? maxRange : 100) + 2 * padding;

    // Calcula a altura visual do viewBox.
    // Considera a maior altura física relevante: o pico da trajetória (maxHeight) ou a altura inicial (initialHeight),
    // o que for maior, para garantir que tudo seja visível. Adiciona padding em cima e embaixo.
    // Se a altura efetiva for 0, usa uma altura padrão de 100 unidades.
    const effectiveMaxPhysicalY = Math.max(maxHeight, initialHeight);
    const viewHeight = (effectiveMaxPhysicalY > 0 ? effectiveMaxPhysicalY : 100) + 2 * padding;

    // Define o minX do viewBox. Começa a visualização 'padding' unidades à esquerda da origem física (x=0).
    // Isso centraliza a trajetória horizontalmente se ela começar em x=0.
    const minX = -padding;

    // Define o minY do viewBox. No SVG, o eixo Y cresce para baixo.
    // Esta configuração de viewBox, em conjunto com a função de ajuste svgAdjustedY,
    // inverte o eixo Y para que ele se comporte como um sistema cartesiano tradicional (Y cresce para cima).
    // O 'minY = -padding' posiciona a origem do viewBox de forma que o "chão" (y=0 físico)
    // tenha 'padding' abaixo dele e o ponto mais alto da trajetória tenha 'padding' acima.
    const minY = -padding;

    return `${minX} ${minY} ${viewWidth} ${viewHeight}`; // Retorna a string formatada do viewBox.
  }


  // Ajusta a coordenada X física para o sistema de coordenadas do SVG.
  // physicalX: A coordenada X no sistema de coordenadas da simulação física.
  // trajectory: Array de pontos da trajetória (atualmente não usado nesta função, mas pode ser útil para escalas mais complexas).
  // Nesta implementação, as coordenadas X da física são usadas diretamente como coordenadas X no SVG.
  // O viewBox (com minX = -padding) já lida com o posicionamento e padding horizontal.
  function svgAdjustedX(physicalX, trajectory) {
    return physicalX;
  }

  // Ajusta e INVERTE a coordenada Y física para o sistema de coordenadas do SVG.
  // physicalY: Coordenada Y no sistema físico (y=0 é o solo, valores positivos são para cima).
  // trajectory: Array de pontos da trajetória (atualmente não usado).
  // overallMaxHeight: Altura máxima atingida pela trajetória, medida a partir do solo (y=0 físico).
  // physicalInitialHeight: Altura inicial do lançamento (y0 físico).
  // O SVG tem y=0 no topo e o eixo Y cresce para baixo. Esta função inverte o Y físico.
  function svgAdjustedY(physicalY, trajectory, overallMaxHeight, physicalInitialHeight) {
    const padding = 20; // Mesmo padding usado em getSvgViewBox.
    // Determina a maior altura física relevante para o cálculo da escala Y.
    const effectiveMaxPhysicalY = Math.max(overallMaxHeight, physicalInitialHeight);

    // A transformação da coordenada Y para o SVG é feita para:
    // 1. Inverter o eixo Y: No SVG, Y cresce para baixo; na física, Y cresce para cima.
    //    A subtração de 'physicalY' de um valor de referência realiza essa inversão.
    // 2. Posicionar a trajetória dentro do viewBox com padding.
    // A expressão '(effectiveMaxPhysicalY + padding) - physicalY' faz isso:
    //    - '(effectiveMaxPhysicalY + padding)' define uma linha de referência "acima" do ponto mais alto da trajetória no sistema SVG.
    //    - Subtraindo 'physicalY':
    //      - Se 'physicalY' é 0 (solo físico), o resultado é 'effectiveMaxPhysicalY + padding' (parte inferior do gráfico no SVG).
    //      - Se 'physicalY' é 'effectiveMaxPhysicalY' (ponto mais alto físico), o resultado é 'padding' (parte superior do gráfico no SVG, perto do topo do viewBox).
    // Esta lógica funciona em conjunto com o viewBox que tem minY = -padding e uma altura que acomoda effectiveMaxPhysicalY + 2*padding.
    return (effectiveMaxPhysicalY + padding) - physicalY;
  }

  // Formata a lista de pontos da trajetória (objetos {time, x, y})
  // em uma string única de coordenadas "x,y" para o atributo `points` da tag `<polyline>` do SVG.
  // Exemplo de saída: "x1,y1 x2,y2 x3,y3 ...".
  // overallMaxHeight e physicalInitialHeight são passados para svgAdjustedY para o correto ajuste de escala.
  function formatTrajectoryForSvg(trajectory, overallMaxHeight, physicalInitialHeight) {
    if (!trajectory) return ""; // Retorna string vazia se não houver trajetória.
    return trajectory
      .map(p => `${svgAdjustedX(p.x, trajectory)},${svgAdjustedY(p.y, trajectory, overallMaxHeight, physicalInitialHeight)}`) // Mapeia cada ponto para "x_svg,y_svg".
      .join(" "); // Une todos os pontos formatados com um espaço.
  }

  // Retorna uma amostra dos pontos da trajetória para exibição em uma tabela.
  // Se a trajetória tiver muitos pontos, exibir todos pode tornar a tabela muito longa e lenta.
  // Esta função seleciona aproximadamente 'count' pontos, incluindo sempre o primeiro e o último.
  function getTrajectorySample(trajectory, count = 10) {
    if (!trajectory || trajectory.length === 0) return []; // Retorna array vazio se não houver trajetória.
    if (trajectory.length <= count) return trajectory; // Retorna todos os pontos se a quantidade já for menor ou igual à desejada.

    const sample = []; // Array para armazenar os pontos da amostra.
    // Calcula o 'step' (passo) para selecionar 'count-1' pontos uniformemente espaçados do array original.
    // O último ponto da trajetória é adicionado separadamente para garantir sua inclusão.
    const step = Math.floor(trajectory.length / (count - 1));
    for (let i = 0; i < count - 1; i++) {
      sample.push(trajectory[i * step]); // Adiciona o ponto da trajetória no índice calculado.
    }
    sample.push(trajectory[trajectory.length - 1]); // Garante que o último ponto da trajetória original seja incluído na amostra.
    return sample; // Retorna a amostra de pontos.
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
