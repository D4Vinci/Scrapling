// A stand-in for the SBSD challenge script: posts {"body": ...} to ?t=<n> after %DELAY_MS% ms (never when -1).
(function () {
  var delay = %DELAY_MS%;
  if (delay < 0) { return; }
  setTimeout(function () {
    var xhr = new XMLHttpRequest();
    xhr.open("POST", "/Gq7p/Rf/k2/sbsd?t=183446611");
    xhr.setRequestHeader("Content-Type", "application/json");
    xhr.send(JSON.stringify({body: "payload-" + Date.now()}));
  }, delay);
})();
