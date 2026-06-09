function setLed(action) {
  fetch("/led", {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json'
    },
    body: JSON.stringify({ action: action })
    })
    .then(function (resp) { return resp.json(); })
    .then(function (data) {
      document.getElementById('led-status').textContent = data.status;
    })
    .catch(function (error) {
      console.log('LED control error', error);
    });
}

setInterval(function () {
  fetch('/status')
    .then(function (resp) { return resp.json(); })
    .then(function (data) {
      document.getElementById('led-status').textContent = data.status;
    });
}, 2000);
