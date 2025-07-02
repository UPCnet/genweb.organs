// Búsqueda AJAX para Plone 6 sin jQuery
// Solo busca al pulsar Intro o el botón, no en cada letra del input de texto

document.addEventListener('DOMContentLoaded', function () {
  const form = document.querySelector('#search-form');
  const resultsBlock = document.querySelector('#search-results');
  const searchInput = form ? form.querySelector('input[name="SearchableText"]') : null;

  if (!form || !resultsBlock) return;

  // Escucha cambios en los filtros (checkboxes, radios, selects)
  form.addEventListener('input', function (e) {
    if (e.target === searchInput) return; // Ignora el input de texto
    if (["INPUT", "SELECT", "TEXTAREA"].includes(e.target.tagName)) {
      fetchResults();
    }
  });

  // Solo busca al hacer submit (Intro o botón)
  form.addEventListener('submit', function (e) {
    e.preventDefault();
    fetchResults();
  });

  function fetchResults() {
    const formData = new FormData(form);
    const params = new URLSearchParams(formData).toString();
    const url = form.action + '?' + params;

    fetch(url, {
      headers: { 'X-Requested-With': 'XMLHttpRequest' }
    })
      .then(response => response.text())
      .then(html => {
        // Extrae solo el bloque de resultados del HTML devuelto
        const tempDiv = document.createElement('div');
        tempDiv.innerHTML = html;
        const newResults = tempDiv.querySelector('#search-results');
        if (newResults) {
          resultsBlock.innerHTML = newResults.innerHTML;
        }
      });
  }
});