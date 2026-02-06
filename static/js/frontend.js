const wheelRotator = document.getElementById('wheel-rotator');
const spinBtn = document.getElementById('spin-btn');
const newActivityBtn = document.getElementById('new-activity');
const modal = document.getElementById('win-modal');
const modalTitle = modal ? modal.querySelector('.modal-title') : null;
const historyList = document.getElementById('history-list');
const configSelect = document.getElementById('config-select');
const drawNameInput = document.getElementById('draw-name');
let spinning = false;
let currentRotation = 0;

if (configSelect) {
  configSelect.addEventListener('change', () => {
    const value = configSelect.value;
    if (value) {
      window.location.href = `/?config=${value}`;
    }
  });
}

function getCsrfToken() {
  const token = document.querySelector('meta[name="csrf-token"]');
  return token ? token.content : '';
}

function updateHistory(items) {
  if (!historyList) return;
  historyList.innerHTML = '';
  if (!items || items.length === 0) {
    const li = document.createElement('li');
    li.className = 'muted';
    li.textContent = '尚無中獎紀錄';
    historyList.appendChild(li);
    return;
  }
  items.forEach((item) => {
    const li = document.createElement('li');
    li.textContent = `${item.time}  ${item.prize} (${item.nickname})`;
    historyList.appendChild(li);
  });
}

if (modal) {
  modal.addEventListener('click', () => {
    modal.classList.remove('show');
  });
}

async function spinWheel() {
    if (spinning) return;
    const nickname = document.getElementById('nickname').value.trim();
    if (!nickname) {
      alert('請先輸入抽獎人暱稱');
      return;
    }
    const configId = wheelRotator ? wheelRotator.dataset.configId : '';
    if (!configId) {
      alert('尚未設定抽獎內容');
      return;
    }

    spinning = true;
    const payload = new URLSearchParams();
    payload.append('config_id', configId);
    payload.append('nickname', nickname);
    payload.append('draw_name', drawNameInput ? drawNameInput.value.trim() : '');

    try {
      const response = await fetch('/api/draw/', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/x-www-form-urlencoded',
          'X-CSRFToken': getCsrfToken(),
        },
        body: payload.toString(),
      });
      const data = await response.json();
      if (!data.success) {
        alert(data.message || '抽獎失敗');
        spinning = false;
        return;
      }

      const duration = 5 + Math.random() * 5;
      const spins = Math.max(50, Math.round(duration * 10));
      const targetAngle = data.target_angle || 0;
      const align = (360 - targetAngle + 360) % 360;
      const rotation = spins * 360 + align;
      if (wheelRotator) {
        wheelRotator.style.transition = `transform ${duration.toFixed(2)}s cubic-bezier(0.12, 0.8, 0.2, 1)`;
        wheelRotator.style.transform = `rotate(${rotation}deg)`;
      }
      currentRotation = rotation % 360;

      setTimeout(() => {
        if (modal && modalTitle) {
          modalTitle.textContent = `恭喜中獎！${data.prize}`;
          modal.classList.add('show');
        }
        updateHistory(data.history);
        spinning = false;
      }, (duration + 0.2) * 1000);
    } catch (err) {
      alert('抽獎失敗，請稍後再試');
      spinning = false;
    }
}

if (spinBtn) {
  spinBtn.addEventListener('click', spinWheel);
}

if (newActivityBtn) {
  newActivityBtn.addEventListener('click', async () => {
    if (spinning) return;
    const activityName = drawNameInput ? drawNameInput.value.trim() : '';
    const configId = wheelRotator ? wheelRotator.dataset.configId : '';
    if (!activityName) {
      alert('請先輸入活動名稱');
      return;
    }
    if (!configId) {
      alert('尚未設定抽獎內容');
      return;
    }
    const payload = new URLSearchParams();
    payload.append('activity_name', activityName);
    payload.append('config_id', configId);

    try {
      const response = await fetch('/api/new-activity/', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/x-www-form-urlencoded',
          'X-CSRFToken': getCsrfToken(),
        },
        body: payload.toString(),
      });
      const data = await response.json();
      if (!data.success) {
        alert(data.message || '建立活動失敗');
        return;
      }
      window.location.href = configId ? `/?config=${configId}` : '/';
    } catch (err) {
      alert('建立活動失敗，請稍後再試');
    }
  });
}
