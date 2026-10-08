// A stand-in for bmak: posts sensor_data on pointer input until _abck carries the stop signal.
(function () {
  var moves = 0, posting = false, posts = 0;
  function valid() { return /(^|;\s*)_abck=[^;]*~0~/.test(document.cookie); }
  function post() {
    if (posting || posts >= 5 || valid()) { return; }
    posting = true; posts++;
    fetch("/x5Kq/Ab1/cd2/EfG3/sensor", {method: "POST", headers: {"Content-Type": "text/plain;charset=UTF-8"},
      body: JSON.stringify({sensor_data: "3;0;1;0;" + moves + ";" + Date.now()})})
      .then(function () { posting = false; });
  }
  document.addEventListener("mousemove", function () { moves++; if (moves % 15 === 0) { post(); } });
  document.addEventListener("scroll", function () { post(); });
})();
