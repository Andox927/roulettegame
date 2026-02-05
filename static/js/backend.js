const rowsContainer = document.getElementById('prize-rows');
const loadBtn = document.getElementById('load-config');
const backendSelect = document.getElementById('backend-config');

function updateRemoveButtons() {
  if (!rowsContainer) return;
  const rows = rowsContainer.querySelectorAll('.row');
  const showRemove = rows.length > 1;
  rows.forEach((row) => {
    const removeBtn = row.querySelector('.remove');
    if (removeBtn) {
      removeBtn.style.display = showRemove ? 'inline-flex' : 'none';
    }
  });
}

function addRow(sourceRow) {
  if (!rowsContainer) return;
  const row = sourceRow ? sourceRow.cloneNode(true) : rowsContainer.querySelector('.row').cloneNode(true);
  row.querySelectorAll('input').forEach((input) => {
    input.value = '';
  });
  rowsContainer.appendChild(row);
  updateRemoveButtons();
}

function removeRow(row) {
  if (!rowsContainer) return;
  const rows = rowsContainer.querySelectorAll('.row');
  if (rows.length <= 1) return;
  row.remove();
  updateRemoveButtons();
}

if (rowsContainer) {
  rowsContainer.addEventListener('click', (event) => {
    const target = event.target;
    if (target.classList.contains('add')) {
      addRow(target.closest('.row'));
    }
    if (target.classList.contains('remove')) {
      removeRow(target.closest('.row'));
    }
  });
  updateRemoveButtons();
}

if (loadBtn && backendSelect) {
  loadBtn.addEventListener('click', () => {
    const value = backendSelect.value;
    if (value) {
      window.location.href = `/backend/?config=${value}`;
    }
  });
}
