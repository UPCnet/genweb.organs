// Búsqueda AJAX para Plone 6 sin jQuery
// Actualiza los resultados dinámicamente al cambiar filtros o escribir

document.addEventListener('DOMContentLoaded', function () {
  const form = document.querySelector('#search-form');
  const resultsBlock = document.querySelector('#search-results');

  if (!form || !resultsBlock) return;

  // Escucha cambios en cualquier input del formulario
  form.addEventListener('input', function (e) {
    if (['INPUT', 'SELECT', 'TEXTAREA'].includes(e.target.tagName)) {
      fetchResults();
    }
  });

  // Evita el submit tradicional
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