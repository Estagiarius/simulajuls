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
  <link rel="preconnect" href="https://fonts.googleapis.com">
  <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
  <link href="https://fonts.googleapis.com/css2?family=Roboto:wght@400;700&display=swap" rel="stylesheet">
</svelte:head>

<main>
  <h1>Simulador de Experimentos Educativos</h1>

  {#if isLoading}
    <p>Carregando experimentos...</p>
  {:else if error}
    <p style="color: red;">Erro ao carregar experimentos: {error}</p>
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
              <button style="background-color: #ADD8E6; border: none; padding: 8px 12px; border-radius: 4px; cursor: pointer;">
                Iniciar Simulação
              </button>
            </div>
          {/each}
        </div>
      </section>
    {/each}
  {/if}
</main>

<style>
  :global(body) {
    font-family: 'Roboto', sans-serif;
    margin: 0;
    padding: 0;
    background-color: #f4f4f4;
    color: #333;
  }

  main {
    padding: 20px;
    max-width: 1200px;
    margin: auto;
  }

  h1 {
    text-align: center;
    color: #2c3e50;
  }

  .category-section {
    margin-bottom: 30px;
    padding: 20px;
    background-color: #fff;
    border-radius: 8px;
    box-shadow: 0 2px 4px rgba(0,0,0,0.1);
  }

  .category-section h2 {
    color: #2980b9;
    border-bottom: 2px solid #ADD8E6;
    padding-bottom: 10px;
  }

  .experiments-grid {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
    gap: 20px;
  }

  .experiment-card {
    border: 1px solid #ddd;
    border-radius: 4px;
    padding: 15px;
    background-color: #f9f9f9;
    display: flex;
    flex-direction: column;
    justify-content: space-between;
  }

  .experiment-card h3 {
    color: #34495e;
    margin-top: 0;
  }

  .description {
    font-size: 0.9em;
    margin-bottom: 10px;
    flex-grow: 1;
  }

 .experiment-image {
   width: 100%;
   height: 150px; /* Altura fixa para a imagem */
   object-fit: cover; /* Para cobrir o espaço sem distorcer */
   border: 1px solid #eee;
   margin-bottom: 10px;
 }

  .image-placeholder {
    font-style: italic;
    color: #777;
    text-align: center;
    padding: 20px 0;
    border: 1px dashed #ccc;
    margin-bottom: 10px;
    height: 150px;
    display: flex;
    align-items: center;
    justify-content: center;
  }
</style>
