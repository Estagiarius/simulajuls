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
  let dominantAlleleError = '';
  let recessiveAlleleError = '';

  $: parent1GenotypeError = validateGenotypeInput(params.parent1_genotype);
  $: parent2GenotypeError = validateGenotypeInput(params.parent2_genotype);

  $: {
    const allele = params.dominant_allele;
    if (allele === '') {
      dominantAlleleError = 'Alelo Dominante é obrigatório.';
    } else if (allele && allele.length !== 1) {
      dominantAlleleError = 'Alelo Dominante deve ter exatamente 1 caractere.';
    } else if (allele && !/^[a-zA-Z]$/.test(allele)) {
      dominantAlleleError = 'Alelo Dominante deve ser uma letra (A-Z, a-z).';
    } else {
      dominantAlleleError = '';
    }
  }

  $: {
    const allele = params.recessive_allele;
    if (allele === '') {
      recessiveAlleleError = 'Alelo Recessivo é obrigatório.';
    } else if (allele && allele.length !== 1) {
      recessiveAlleleError = 'Alelo Recessivo deve ter exatamente 1 caractere.';
    } else if (allele && !/^[a-zA-Z]$/.test(allele)) {
      recessiveAlleleError = 'Alelo Recessivo deve ser uma letra (A-Z, a-z).';
    } else {
      recessiveAlleleError = '';
    }
  }

  function validateGenotypeInput(genotype) {
    // 1. Handle null or undefined genotype
    if (genotype === null || genotype === undefined) {
      return "Genótipo não pode ser vazio.";
    }

    // 2. Trim the genotype
    const trimmedGenotype = genotype.trim();

    // 3. Check if trimmedGenotype is empty
    if (trimmedGenotype.length === 0) {
      if (genotype.length > 0) {
        return "Genótipo não pode ser composto apenas por espaços.";
      } else {
        return "Genótipo não pode ser vazio.";
      }
    }

    // 4. Check if trimmedGenotype length is not 2
    if (trimmedGenotype.length !== 2) {
      return `Genótipo "${trimmedGenotype}" deve ter exatamente 2 alelos (ex: AA, Aa, aa). Por favor, insira duas letras.`;
    }

    // 5. Validate allowed characters using regex
    const domAllele = params.dominant_allele || 'A';
    const recAllele = params.recessive_allele || 'a';
    // Ensure allowedChars uses the actual allele characters for the regex, case-insensitively
    const allowedChars = `${domAllele}${recAllele}`;
    // Regex to match exactly two characters from the allowed alleles (case-insensitive).
    const regex = new RegExp(`^[${allowedChars.toUpperCase()}${allowedChars.toLowerCase()}]{2}$`);

    if (!regex.test(trimmedGenotype)) {
      return `Genótipo "${trimmedGenotype}" contém alelos inválidos. Use apenas '${domAllele}' e '${recAllele}'.`;
    }

    // 6. If all checks pass
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
      const response = await fetch('http://localhost:8000/api/simulation/mendelian-genetics/start', {
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
  <a href="/" class="fluent-link" use:fade>← Voltar para Seleção de Experimentos</a>

  <h1>{experimentDetails.name}</h1>
  <p class="description">{experimentDetails.description}</p>

  <form on:submit|preventDefault={startSimulation} class="simulation-form">
    <h2 style="text-align: center; margin-bottom: var(--spacing-l); color: var(--color-text-primary); font-size: var(--font-size-title); font-weight: var(--font-weight-semibold);">Configurar Cruzamento Genético</h2>

    <div class="form-grid">
      <fieldset>
        <legend>Progenitor 1</legend>
        <label for="parent1_genotype">Genótipo do Progenitor 1 (ex: AA, Aa, aa):</label>
        <input type="text" id="parent1_genotype" bind:value={params.parent1_genotype} class="fluent-input" maxlength="2" required>
        {#if parent1GenotypeError}
          <small class="input-error">{parent1GenotypeError}</small>
        {/if}
      </fieldset>

      <fieldset>
        <legend>Progenitor 2</legend>
        <label for="parent2_genotype">Genótipo do Progenitor 2 (ex: AA, Aa, aa):</label>
        <input type="text" id="parent2_genotype" bind:value={params.parent2_genotype} class="fluent-input" maxlength="2" required>
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
          <input type="text" id="dominant_allele" bind:value={params.dominant_allele} class="fluent-input" maxlength="1" required>
          {#if dominantAlleleError}
            <small class="input-error">{dominantAlleleError}</small>
          {/if}
        </div>
        <div>
          <label for="recessive_allele">Alelo Recessivo:</label>
          <input type="text" id="recessive_allele" bind:value={params.recessive_allele} class="fluent-input" maxlength="1" required>
          {#if recessiveAlleleError}
            <small class="input-error">{recessiveAlleleError}</small>
          {/if}
        </div>
        <div>
          <label for="dominant_phenotype_description">Descrição do Fenótipo Dominante:</label>
          <input type="text" id="dominant_phenotype_description" bind:value={params.dominant_phenotype_description} class="fluent-input">
        </div>
        <div>
          <label for="recessive_phenotype_description">Descrição do Fenótipo Recessivo:</label>
          <input type="text" id="recessive_phenotype_description" bind:value={params.recessive_phenotype_description} class="fluent-input">
        </div>
      </div>
    </fieldset>

    <button type="submit" class="fluent-button" disabled={isLoading || parent1GenotypeError || parent2GenotypeError || !!dominantAlleleError || !!recessiveAlleleError}>
      {#if isLoading}
        Calculando Proporções...
      {:else}
        Realizar Cruzamento
      {/if}
    </button>
  </form>

  {#if simulationResult}
    <section class="results-section" transition:fade={{ duration: 300 }}>
      <h2 style="text-align: center; margin-bottom: var(--spacing-l); color: var(--color-text-primary); font-size: var(--font-size-title); font-weight: var(--font-weight-semibold);">Resultados do Cruzamento Genético</h2>

      <div class="punnett-section">
        <h3 style="color: var(--color-text-primary); font-size: var(--font-size-subheader); font-weight: var(--font-weight-semibold); margin-bottom: var(--spacing-s);">Quadro de Punnett:</h3>
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
          <h3 style="color: var(--color-text-primary); font-size: var(--font-size-subheader); font-weight: var(--font-weight-semibold); margin-bottom: var(--spacing-s); border-bottom: 1px solid var(--color-neutral-stroke-default); padding-bottom: var(--spacing-xs);">Proporções Genotípicas da Prole:</h3>
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
          <h3 style="color: var(--color-text-primary); font-size: var(--font-size-subheader); font-weight: var(--font-weight-semibold); margin-bottom: var(--spacing-s); border-bottom: 1px solid var(--color-neutral-stroke-default); padding-bottom: var(--spacing-xs);">Proporções Fenotípicas da Prole:</h3>
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
          <h4 style="color: var(--color-text-primary); font-size: var(--font-size-subheader); font-weight: var(--font-weight-semibold); margin-bottom: var(--spacing-s);">Parâmetros Utilizados na Simulação:</h4>
          <p>Progenitor 1: {simulationResult.parameters_used.parent1_genotype}, Progenitor 2: {simulationResult.parameters_used.parent2_genotype}</p>
          <p>Alelo Dominante: {simulationResult.parameters_used.dominant_allele} ({simulationResult.parameters_used.dominant_phenotype_description})</p>
          <p>Alelo Recessivo: {simulationResult.parameters_used.recessive_allele} ({simulationResult.parameters_used.recessive_phenotype_description})</p>
      </div>
    </section>
  {/if}

  {#if error}
    <p class="fluent-alert-error" use:fade>Erro: {error}</p>
  {/if}

</main>

<style>
  /* :global(body) rule removed */
  .container {
    max-width: 900px; /* Fluent width */
    margin: var(--spacing-l) auto; /* Fluent spacing */
    padding: var(--spacing-xl); /* Fluent padding */
    background-color: var(--color-neutral-background); /* Page background */
    /* Removed border-radius and box-shadow for page background */
  }
  /* .back-link rule removed, replaced by .fluent-link */
  .back-link:hover {text-decoration: underline;} /* This would be covered by .fluent-link:hover */
  h1 {
    text-align: center;
    margin-bottom: var(--spacing-s);
    /* Color and font are from fluent-theme.css global h1 */
  }
  .description {
    text-align: center;
    margin-bottom: var(--spacing-l);
    color: var(--color-text-secondary);
    /* Font size from fluent-theme.css global p */
  }
  /* .simulation-form h2 rule removed, styles applied inline or via global h2 */
  .form-grid {display: grid; grid-template-columns: repeat(auto-fit, minmax(280px, 1fr)); gap: var(--spacing-m); margin-bottom: var(--spacing-l);}
  fieldset {
    border: 1px solid var(--color-neutral-stroke-default);
    border-radius: var(--border-radius-medium);
    padding: var(--spacing-l);
    background-color: var(--color-neutral-layer-1);
    margin-bottom: var(--spacing-l);
    box-shadow: var(--shadow-depth-2);
  }
  legend {
    font-weight: var(--font-weight-semibold);
    color: var(--color-text-primary);
    padding: 0 var(--spacing-xs);
    margin-bottom: var(--spacing-m);
    font-size: var(--font-size-subheader); /* Added for consistency */
  }
  label {
    display: block;
    margin-bottom: var(--spacing-xs);
    font-weight: var(--font-weight-regular);
    color: var(--color-text-primary);
  }
  /* input[type="text"], input[type="number"] rules removed, replaced by .fluent-input */
  /* input[type="text"]:focus, input[type="number"]:focus rules removed */

  .definition-fieldset .form-grid div {
      margin-bottom: var(--spacing-s); /* Adjusted spacing */
  }
  .input-error {
    display: block;
    font-size: var(--font-size-caption);
    color: var(--color-text-error);
    margin-top: var(--spacing-xs);
  }
  /* .submit-button rules removed, replaced by .fluent-button */
  /* .submit-button:hover:not(:disabled) rule removed */
  /* .submit-button:disabled rule removed */
  .results-section {
    margin-top: var(--spacing-xl);
    padding: var(--spacing-l);
    background-color: var(--color-neutral-layer-1);
    border: none; /* Was 1px solid #ADD8E6 */
    border-radius: var(--border-radius-large);
    box-shadow: var(--shadow-depth-4);
  }
  /* .results-section h2 rule removed, styled inline or via global h2 */
  /* .error-message rule removed, replaced by .fluent-alert-error */

  /* Updated styles for Genética */
  .punnett-section {
    margin-bottom: var(--spacing-l);
    text-align: center;
  }
  /* .punnett-section h3 rule removed, styled inline or via global h3 */
  .punnett-square {
    margin: 0 auto;
    border-collapse: collapse;
    border: 1px solid var(--color-neutral-stroke-default); /* Updated border */
    min-width: 200px;
    box-shadow: var(--shadow-depth-2); /* Added Fluent shadow */
  }
  .punnett-square th, .punnett-square td {
    border: 1px solid var(--color-neutral-stroke-default); /* Updated border */
    padding: var(--spacing-s); /* Updated padding */
    text-align: center;
    font-size: 1em; /* Kept relative size, can be var(--font-size-body) */
    min-width: 50px;
  }
  .punnett-square th {
    background-color: var(--color-neutral-layer-2); /* Updated background */
    font-weight: var(--font-weight-semibold);
    color: var(--color-text-primary);
  }
  .punnett-square td {
    background-color: var(--color-neutral-layer-1); /* Updated background */
    color: var(--color-text-primary);
  }
  .proportions-grid {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
    gap: var(--spacing-l); /* Updated gap */
    margin-bottom: var(--spacing-l); /* Updated margin */
  }
  .genotype-proportions, .phenotype-proportions {
    background-color: var(--color-neutral-layer-2); /* Updated background */
    padding: var(--spacing-m); /* Updated padding */
    border-radius: var(--border-radius-medium); /* Updated radius */
    border: 1px solid var(--color-neutral-stroke-default); /* Updated border */
  }
  /* .genotype-proportions h3, .phenotype-proportions h3 rules removed, styled inline or via global h3 */

  .genotype-proportions ul, .phenotype-proportions ul {
    list-style: none;
    padding-left: 0;
    margin: 0;
  }
  .genotype-proportions li, .phenotype-proportions li {
    padding: var(--spacing-xs) 0; /* Updated padding */
    border-bottom: 1px dashed var(--color-neutral-stroke-default); /* Updated border */
    font-size: var(--font-size-body); /* Updated font size */
  }
  .genotype-proportions li:last-child, .phenotype-proportions li:last-child {
    border-bottom: none;
  }
  .genotype-proportions li strong, .phenotype-proportions li strong {
    color: var(--color-text-primary); /* Was accent, changed to primary */
    font-weight: var(--font-weight-semibold);
  }
  .genotype-proportions li em, .phenotype-proportions li em {
    font-size: var(--font-size-caption); /* Updated font size */
    color: var(--color-text-secondary);
    margin-left: var(--spacing-xs); /* Updated margin */
  }
  .parameters-used {
      margin-top: var(--spacing-l); /* Updated margin */
      padding: var(--spacing-m); /* Updated padding */
      background-color: var(--color-neutral-layer-2); /* Updated background */
      border: 1px solid var(--color-neutral-stroke-default); /* Updated border */
      border-radius: var(--border-radius-medium); /* Updated radius */
      font-size: var(--font-size-body); /* Updated font size */
  }
  /* .parameters-used h4 rule removed, styled inline or via global h4 */
  .parameters-used p {
      margin: var(--spacing-xs) 0; /* Updated margin */
      color: var(--color-text-secondary);
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

  .fluent-input {
    background-color: var(--color-neutral-layer-1);
    border: 1px solid var(--color-neutral-stroke-default);
    color: var(--color-text-primary);
    padding: var(--spacing-s) var(--spacing-m);
    border-radius: var(--border-radius-medium);
    width: 100%;
    box-sizing: border-box; /* Ensure padding doesn't expand width */
  }
  .fluent-input:focus {
    outline: 2px solid transparent;
    outline-offset: 2px;
    border-color: var(--color-accent-primary);
    box-shadow: 0 0 0 1px var(--color-accent-primary);
  }
  .fluent-input::placeholder {
    color: var(--color-text-secondary);
    opacity: 0.7;
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
