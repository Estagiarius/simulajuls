<script>
  import { fade } from 'svelte/transition';

  const experimentDetails = {
    name: "Genética Mendeliana (Cruzamento Monoíbrido)",
    description: "Simule um cruzamento genético simples (um gene, dois alelos) e observe as proporções genotípicas e fenotípicas da prole."
  };

  let params = {
    parent1_genotype: "Aa",
    parent2_genotype: "Aa",
    dominant_allele: "A",
    recessive_allele: "a",
    dominant_phenotype_description: "Amarelo",
    recessive_phenotype_description: "Verde"
  };

  let simulationResult = null;
  let isLoading = false;
  let error = null;

  $: parent1GenotypeError = validateGenotypeInput(params.parent1_genotype);
  $: parent2GenotypeError = validateGenotypeInput(params.parent2_genotype);

  function validateGenotypeInput(genotype) {
    if (!genotype) return "Genótipo não pode ser vazio.";
    if (genotype.length !== 2) return "Genótipo deve ter 2 alelos (ex: AA, Aa, aa).";
    // Validação de caracteres pode ser mais robusta se os alelos forem fixos
    const allowedChars = (params.dominant_allele || 'A') + (params.recessive_allele || 'a');
    const regex = new RegExp(`^[${allowedChars.toUpperCase()}${allowedChars.toLowerCase()}]{2}$`);
    if (!regex.test(genotype)) {
        // return `Genótipo contém alelos inválidos. Use apenas '${params.dominant_allele}' ou '${params.recessive_allele}'.`;
    } // A validação principal de alelos é no backend.
    return "";
  }

  async function startSimulation() {
    if (parent1GenotypeError || parent2GenotypeError) {
      error = "Corrija os erros nos genótipos dos pais antes de simular.";
      // Se houver erros de validação de frontend, não prosseguir.
      // A validação de `validateGenotypeInput` já estabelece as mensagens de erro se houver.
      // Aqui apenas garantimos que não prossiga.
      if(parent1GenotypeError) error = parent1GenotypeError;
      else if(parent2GenotypeError) error = parent2GenotypeError;
      else error = "Verifique os campos de genótipo."; // Fallback, mas um dos erros de cima deve ser pego.
      return;
    }
    isLoading = true;
    error = null;
    simulationResult = null;

    const payload = { ...params };
    // Garante que alelos vazios sejam null ou string vazia se o backend esperar assim,
    // ou use os defaults se o backend não os aceitar como opcionais no sentido de não-presença.
    // O backend atual já define defaults se não enviados, então enviar strings vazias é ok.

    console.log("Enviando para API Genética Mendeliana:", payload);

    try {
      const response = await fetch('http://localhost:8000/api/simulation/biology/mendelian-genetics/start', {
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
      console.log("Resultado da simulação de Genética Mendeliana:", simulationResult);

    } catch (e) {
      console.error("Falha ao iniciar simulação de Genética Mendeliana:", e);
      error = e.message || "Ocorreu um erro desconhecido ao contatar a API de biologia.";
    } finally {
      isLoading = false;
    }
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
    <h2>Configurar Cruzamento Genético</h2>

    <div class="form-grid">
      <fieldset>
        <legend>Progenitor 1</legend>
        <label for="parent1_genotype">Genótipo do Progenitor 1 (ex: AA, Aa, aa):</label>
        <input type="text" id="parent1_genotype" bind:value={params.parent1_genotype} maxlength="2" pattern="[a-zA-Z]{2}" title="Digite 2 letras para o genótipo (ex: Aa)" required>
        {#if parent1GenotypeError}
          <small class="input-error">{parent1GenotypeError}</small>
        {/if}
      </fieldset>

      <fieldset>
        <legend>Progenitor 2</legend>
        <label for="parent2_genotype">Genótipo do Progenitor 2 (ex: AA, Aa, aa):</label>
        <input type="text" id="parent2_genotype" bind:value={params.parent2_genotype} maxlength="2" pattern="[a-zA-Z]{2}" title="Digite 2 letras para o genótipo (ex: Aa)" required>
        {#if parent2GenotypeError}
          <small class="input-error">{parent2GenotypeError}</small>
        {/if}
      </fieldset>
    </div>

    <fieldset class="definition-fieldset">
      <legend>Definição de Alelos e Fenótipos (Opcional)</legend>
      <div class="form-grid">
        <div>
          <label for="dominant_allele">Alelo Dominante:</label>
          <input type="text" id="dominant_allele" bind:value={params.dominant_allele} maxlength="1" pattern="[a-zA-Z]{1}">
        </div>
        <div>
          <label for="recessive_allele">Alelo Recessivo:</label>
          <input type="text" id="recessive_allele" bind:value={params.recessive_allele} maxlength="1" pattern="[a-zA-Z]{1}">
        </div>
        <div>
          <label for="dominant_phenotype_description">Descrição do Fenótipo Dominante:</label>
          <input type="text" id="dominant_phenotype_description" bind:value={params.dominant_phenotype_description}>
        </div>
        <div>
          <label for="recessive_phenotype_description">Descrição do Fenótipo Recessivo:</label>
          <input type="text" id="recessive_phenotype_description" bind:value={params.recessive_phenotype_description}>
        </div>
      </div>
    </fieldset>

    <button type="submit" class="submit-button" disabled={isLoading || parent1GenotypeError || parent2GenotypeError}>
      {#if isLoading}
        Calculando Proporções...
      {:else}
        Realizar Cruzamento
      {/if}
    </button>
  </form>

  {#if simulationResult}
    <section class="results-section" transition:fade={{ duration: 300 }}>
      <h2>Resultados do Cruzamento Genético</h2>

      <div class="punnett-section">
        <h3>Quadro de Punnett:</h3>
        <table class="punnett-square">
          <thead>
            <tr>
              <th></th>
              {#each simulationResult.parent2_alleles as allele}
                <th>{allele}</th>
              {/each}
            </tr>
          </thead>
          <tbody>
            {#each simulationResult.parent1_alleles as p1_allele, i}
              <tr>
                <th>{p1_allele}</th>
                {#each simulationResult.punnett_square[i] as offspring_genotype}
                  <td>{offspring_genotype}</td>
                {/each}
              </tr>
            {/each}
          </tbody>
        </table>
      </div>

      <div class="proportions-grid">
        <div class="genotype-proportions">
          <h3>Proporções Genotípicas da Prole:</h3>
          <ul>
            {#each simulationResult.offspring_genotypes as geno}
              <li>
                <strong>{geno.genotype}:</strong> {geno.fraction} ({geno.percentage}%)
                <em>(Contagem: {geno.count})</em>
              </li>
            {/each}
          </ul>
        </div>

        <div class="phenotype-proportions">
          <h3>Proporções Fenotípicas da Prole:</h3>
          <ul>
            {#each simulationResult.offspring_phenotypes as pheno}
              <li>
                <strong>{pheno.phenotype_description}:</strong> {pheno.fraction} ({pheno.percentage}%)
                <em>(Genótipos: {pheno.associated_genotypes.join(', ')}; Contagem: {pheno.count})</em>
              </li>
            {/each}
          </ul>
        </div>
      </div>

      <div class="parameters-used">
          <h4>Parâmetros Utilizados na Simulação:</h4>
          <p>Progenitor 1: {simulationResult.parameters_used.parent1_genotype}, Progenitor 2: {simulationResult.parameters_used.parent2_genotype}</p>
          <p>Alelo Dominante: {simulationResult.parameters_used.dominant_allele} ({simulationResult.parameters_used.dominant_phenotype_description})</p>
          <p>Alelo Recessivo: {simulationResult.parameters_used.recessive_allele} ({simulationResult.parameters_used.recessive_phenotype_description})</p>
      </div>
    </section>
  {/if}

  {#if error}
    <p class="error-message" use:fade>Erro: {error}</p>
  {/if}

</main>

<style>
  :global(body) {font-family: 'Roboto', sans-serif; background-color: #f4f7f6; color: #333; line-height: 1.6;}
  .container {max-width: 800px; margin: 20px auto; padding: 20px; background-color: #fff; border-radius: 8px; box-shadow: 0 2px 10px rgba(0,0,0,0.05);}
  .back-link {display: inline-block; margin-bottom: 20px; color: #2980b9; text-decoration: none;}
  .back-link:hover {text-decoration: underline;}
  h1 {color: #2c3e50; text-align: center; margin-bottom: 10px;}
  .description {text-align: center; margin-bottom: 30px; color: #555;}
  .simulation-form h2 {margin-bottom: 20px; text-align: center; color: #34495e;}
  .form-grid {display: grid; grid-template-columns: repeat(auto-fit, minmax(280px, 1fr)); gap: 20px; margin-bottom: 20px;}
  fieldset {border: 1px solid #ddd; border-radius: 6px; padding: 20px; background-color: #fdfdfd; margin-bottom:15px;}
  legend {font-weight: bold; color: #2980b9; padding: 0 10px;}
  label {display: block; margin-bottom: 8px; font-weight: 500; color: #444;}
  input[type="text"], input[type="number"] {
    width: 100%; padding: 10px; margin-bottom: 5px;
    border: 1px solid #ccc; border-radius: 4px; box-sizing: border-box; font-size: 1em;
  }
  input[type="text"]:focus, input[type="number"]:focus {
    border-color: #2980b9; outline: none; box-shadow: 0 0 0 2px rgba(41, 128, 185, 0.2);
  }
  .definition-fieldset .form-grid div {
      margin-bottom: 10px;
  }
  .input-error {
    display: block;
    font-size: 0.85em;
    color: #d32f2f;
    margin-top: 2px;
  }
  .submit-button {display: block; width: 100%; padding: 12px 20px; background-color: #ADD8E6; color: #333; font-size: 1.1em; font-weight: bold; border: none; border-radius: 4px; cursor: pointer; transition: background-color 0.2s ease;}
  .submit-button:hover:not(:disabled) {background-color: #9BC9E0;}
  .submit-button:disabled {background-color: #ccc; cursor: not-allowed;}
  .results-section {margin-top: 30px; padding: 20px; background-color: #e9f5ff; border: 1px solid #ADD8E6; border-radius: 6px;}
  .results-section h2 {margin-top: 0; color: #2980b9; text-align:center; margin-bottom: 20px;}
  .error-message {color: #FFA500; background-color: #fff3e0; border: 1px solid #FFA500; padding: 10px; border-radius: 4px; margin-top: 20px;}

  /* NOVOS ESTILOS PARA GENÉTICA */
  .punnett-section {
    margin-bottom: 25px;
    text-align: center;
  }
  .punnett-section h3 {
    margin-bottom: 10px;
    color: #34495e;
  }
  .punnett-square {
    margin: 0 auto;
    border-collapse: collapse;
    border: 2px solid #666;
    min-width: 200px;
    box-shadow: 0 1px 3px rgba(0,0,0,0.1);
  }
  .punnett-square th, .punnett-square td {
    border: 1px solid #999;
    padding: 10px 15px;
    text-align: center;
    font-size: 1.1em;
    min-width: 50px;
  }
  .punnett-square th {
    background-color: #e0e0e0;
    font-weight: bold;
  }
  .punnett-square td {
    background-color: #f9f9f9;
  }
  .proportions-grid {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
    gap: 20px;
    margin-bottom: 20px;
  }
  .genotype-proportions, .phenotype-proportions {
    background-color: #f9f9f9;
    padding: 15px 20px;
    border-radius: 6px;
    border: 1px solid #e0e0e0;
  }
  .genotype-proportions h3, .phenotype-proportions h3 {
    margin-top: 0;
    margin-bottom: 12px;
    color: #34495e;
    border-bottom: 1px solid #ccc;
    padding-bottom: 8px;
  }
  .genotype-proportions ul, .phenotype-proportions ul {
    list-style: none;
    padding-left: 0;
    margin: 0;
  }
  .genotype-proportions li, .phenotype-proportions li {
    padding: 6px 0;
    border-bottom: 1px dashed #eee;
    font-size: 0.95em;
  }
  .genotype-proportions li:last-child, .phenotype-proportions li:last-child {
    border-bottom: none;
  }
  .genotype-proportions li strong, .phenotype-proportions li strong {
    color: #2980b9;
  }
  .genotype-proportions li em, .phenotype-proportions li em {
    font-size: 0.9em;
    color: #777;
    margin-left: 5px;
  }
  .parameters-used {
      margin-top: 20px;
      padding: 15px;
      background-color: #fafafa;
      border: 1px solid #eee;
      border-radius: 4px;
      font-size: 0.9em;
  }
  .parameters-used h4 {
      margin-top: 0;
      margin-bottom: 10px;
      color: #34495e;
  }
  .parameters-used p {
      margin: 5px 0;
      color: #555;
  }
</style>
