(() => {
  const base = new URL(JSON.parse(document.getElementById("__config").textContent).base, location);
  if (!base.pathname.endsWith("/")) base.pathname += "/";
  const links = [...document.querySelectorAll(".md-select a[hreflang]")].map(link => [link, link.href]);
  const update = () => links.forEach(([link, root]) => {
    link.href = new URL(location.pathname.slice(base.pathname.length) + location.search + location.hash, root).href;
    link.target = "_self";
  });
  update();
  location$.subscribe(update);
  addEventListener("hashchange", update);
  for (const event of ["click", "auxclick", "contextmenu"]) addEventListener(event, update, true);
})();
