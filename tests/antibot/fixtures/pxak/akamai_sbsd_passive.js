// A stand-in for passive SBSD: posts two {"body": ...} payloads (index 0 and 1) to the script path, no reload.
(function () {
  function post(index) {
    return fetch("/Gq7p/Rf/k2/sbsd", {method: "POST", headers: {"Content-Type": "application/json"},
      body: JSON.stringify({body: "passive-" + index + "-" + Date.now()})});
  }
  setTimeout(function () { post(0).then(function () { setTimeout(function () { post(1); }, 300); }); }, 400);
})();
