const rowsContainer = document.getElementById('prize-rows');
const loadBtn = document.getElementById('load-config');
const backendSelect = document.getElementById('backend-config');
const historyToggle = document.getElementById('history-toggle');
const activityList = document.getElementById('activity-list');
const historyDetail = document.getElementById('history-detail');

function getCsrfToken() {
  const token = document.querySelector('meta[name="csrf-token"]');
  return token ? token.content : '';
}

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

if (historyToggle && activityList) {
  historyToggle.addEventListener('click', () => {
    activityList.classList.toggle('hidden');
    if (historyDetail) {
      historyDetail.classList.add('hidden');
    }
  });
}

if (activityList) {
  activityList.addEventListener('click', async (event) => {
    const target = event.target;
    if (!target.classList.contains('icon-trash')) return;
    const activityName = target.dataset.activity;
    if (!activityName) return;
    if (!confirm(`確定刪除活動「${activityName}」？`)) return;

    const payload = new URLSearchParams();
    payload.append('activity_name', activityName);

    try {
      const response = await fetch('/api/delete-activity/', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/x-www-form-urlencoded',
          'X-CSRFToken': getCsrfToken(),
        },
        body: payload.toString(),
      });
      const data = await response.json();
      if (!data.success) {
        alert(data.message || '刪除失敗');
        return;
      }
      const li = target.closest('li');
      if (li) li.remove();
      if (historyDetail && historyDetail.dataset.activity === activityName) {
        historyDetail.classList.add('hidden');
      }
    } catch (err) {
      alert('刪除失敗，請稍後再試');
    }
  });
}
