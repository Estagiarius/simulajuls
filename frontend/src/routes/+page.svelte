<script>
  import { onMount } from 'svelte';

  let categories = [];
  let isLoading = true;
  let error = null;

  onMount(async () => {
    try {
      const response = await fetch('http://localhost:8000/api/experiments'); // URL do backend FastAPI
      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }
      const data = await response.json();

      // Agrupar experimentos por categoria
      const grouped = data.reduce((acc, exp) => {
        const category = acc.find(c => c.name === exp.category);
        if (category) {
          category.experiments.push(exp);
        } else {
          acc.push({ name: exp.category, experiments: [exp] });
        }
        return acc;
      }, []);
      categories = grouped;
    } catch (e) {
      error = e.message;
      console.error("Falha ao buscar experimentos:", e);
    } finally {
      isLoading = false;
    }
  });
</script>

<svelte:head>
  <title>Simulador de Experimentos Educativos - Seleção</title>
  <!-- <link rel="preconnect" href="https://fonts.googleapis.com"> -->
  <!-- <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin> -->
  <!-- <link href="https://fonts.googleapis.com/css2?family=Roboto:wght@400;700&display=swap" rel="stylesheet"> -->
</svelte:head>

<main>
  <h1>Simulador de Experimentos Educativos</h1>

  {#if isLoading}
    <p>Carregando experimentos...</p>
  {:else if error}
    <p class="error-message">Erro ao carregar experimentos: {error}</p>
    <p>Certifique-se de que o servidor backend (FastAPI) está rodando em http://localhost:8000 e que o CORS está configurado corretamente.</p>
  {:else if categories.length === 0}
    <p>Nenhum experimento encontrado.</p>
  {:else}
    {#each categories as category}
      <section class="category-section">
        <h2>{category.name}</h2>
        <div class="experiments-grid">
          {#each category.experiments as exp}
            <div class="experiment-card">
              <h3>{exp.name}</h3>
              <p class="description">{exp.description}</p>
              {#if exp.image_url}
                 <img src={exp.image_url} alt="Ilustração para {exp.name}" class="experiment-image">
              {:else}
                 <p class="image-placeholder">[Imagem Ilustrativa]</p>
              {/if}
              <a href={`/experiments/${exp.category.toLowerCase()}/${exp.id}`} style="text-decoration: none;">
                <button class="fluent-button">
                  Iniciar Simulação
                </button>
              </a>
            </div>
          {/each}
        </div>
      </section>
    {/each}
  {/if}
</main>

<style>
  /* :global(body) { */
    /* font-family: 'Roboto', sans-serif; */
    /* margin: 0; */
    /* padding: 0; */
    /* background-color: #f4f4f4; */
    /* color: #333; */
  /* } */

  main {
    padding: var(--spacing-l); /* 24px */
    max-width: 1200px;
    margin: auto;
  }

  h1 {
    text-align: center;
    /* color: #2c3e50; */
  }

  .category-section {
    margin-bottom: var(--spacing-xl); /* 32px */
    padding: var(--spacing-l); /* 24px */
    background-color: var(--color-neutral-layer-1);
    border-radius: var(--border-radius-large); /* 8px */
    box-shadow: var(--shadow-depth-8);
  }

  .category-section h2 {
    /* color: #2980b9; */
    border-bottom: 2px solid var(--color-neutral-stroke-default);
    padding-bottom: var(--spacing-s); /* 8px */
  }

  .experiments-grid {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
    gap: var(--spacing-m); /* 16px */
  }

  .experiment-card {
    background-color: var(--color-neutral-layer-1);
    border: 1px solid var(--color-neutral-stroke-default);
    border-radius: var(--border-radius-medium); /* 6px */
    padding: var(--spacing-m); /* 16px */
    box-shadow: var(--shadow-depth-4);
    display: flex;
    flex-direction: column;
    justify-content: space-between;
  }

  .experiment-card h3 {
    /* color: #34495e; */ /* Will inherit --color-text-primary or be covered by global h3 */
    margin-top: 0;
    /* font-size: var(--font-size-subheader); Ensure this if global h3 isn't enough */
  }

  .description {
    font-size: var(--font-size-body);
    color: var(--color-text-secondary);
    margin-bottom: var(--spacing-s); /* 8px */
    flex-grow: 1;
  }

 .experiment-image {
   width: 100%;
   height: 150px; /* Altura fixa para a imagem */
   object-fit: cover; /* Para cobrir o espaço sem distorcer */
   border: 1px solid var(--color-neutral-stroke-default);
   margin-bottom: var(--spacing-s); /* 8px */
   border-radius: var(--border-radius-small); /* 4px */
 }

  .image-placeholder {
    font-style: italic;
    color: var(--color-text-secondary);
    text-align: center;
    padding: 20px 0;
    border: 1px dashed var(--color-neutral-stroke-default);
    margin-bottom: var(--spacing-s); /* 8px */
    height: 150px; /* Mantendo altura fixa */
    display: flex;
    align-items: center;
    justify-content: center;
    background-color: var(--color-neutral-background);
    border-radius: var(--border-radius-small); /* 4px */
  }

  .fluent-button {
    background-color: var(--color-accent-primary);
    color: var(--color-text-on-accent);
    border: 1px solid transparent; /* Fluent buttons often have a transparent border or one that matches the background */
    padding: var(--spacing-s) var(--spacing-m); /* e.g., 8px 16px */
    border-radius: var(--border-radius-small);
    cursor: pointer;
    font-family: var(--font-family-base);
    font-size: var(--font-size-body);
    font-weight: var(--font-weight-semibold);
    width: 100%; /* Retain full width as per original design */
    text-align: center;
    transition: background-color 0.2s ease-in-out, box-shadow 0.2s ease-in-out; /* For hover/active states */
  }

  .fluent-button:hover {
    background-color: var(--color-accent-primary-hover);
    box-shadow: var(--shadow-depth-2); /* Subtle shadow on hover */
  }

  .fluent-button:active {
    background-color: var(--color-accent-primary-active);
    box-shadow: none; /* Remove shadow on active or use inset */
  }

  .error-message {
    color: var(--color-text-error);
    font-weight: var(--font-weight-semibold);
    padding: var(--spacing-m);
    background-color: color-mix(in srgb, var(--color-text-error) 15%, var(--color-neutral-layer-1));
    border: 1px solid var(--color-text-error);
    border-radius: var(--border-radius-small);
    margin-top: var(--spacing-m);
    margin-bottom: var(--spacing-m);
  }
</style>
