(function () {
  "use strict";

  const NAV_ITEMS = [
    { id: "home", label: "Accueil", href: "/" },
    { id: "project", label: "Le Projet", href: "/projet/" },
    { id: "dashboard", label: "Dashboard", href: "/dashboard/" },
    { id: "simulations", label: "Simulations IA", href: "/dashboard/simulations/" },
    { id: "library", label: "Bibliothèque", href: "/dashboard/simulations/library/" },
    { id: "osint", label: "OSINT v1.2", href: "/dashboard/transparence/osint/" },
    { id: "infrastructure", label: "Infrastructure Overview", href: "/dashboard/transparence/infrastructure/" },
    { id: "podcast", label: "Podcast", href: "/podcast/" }
  ];

  const ACTIVE_MATCHERS = [
    { id: "library", paths: ["/dashboard/simulations/library/"] },
    { id: "osint", paths: ["/dashboard/transparence/osint/"] },
    { id: "infrastructure", paths: ["/dashboard/transparence/infrastructure/", "/transparence/"] },
    { id: "simulations", paths: ["/dashboard/simulations/", "/simulations/"] },
    { id: "dashboard", paths: ["/dashboard/"] },
    { id: "project", paths: ["/projet/"] },
    { id: "podcast", paths: ["/podcast/"] },
    { id: "home", paths: ["/", "/index.html"] }
  ];

  function normalizePath(pathname) {
    if (!pathname || pathname === "/") return "/";
    return pathname.endsWith("/") ? pathname : `${pathname}/`;
  }

  function activeId() {
    const current = normalizePath(window.location.pathname);
    const match = ACTIVE_MATCHERS.find(item => item.paths.some(path => current === path || current.startsWith(path)));
    return match ? match.id : "";
  }

  function render(host) {
    const active = host.dataset.active || activeId();
    host.className = "os-topnav";
    host.innerHTML = `
      <nav class="os-nav" aria-label="Navigation Ocean Sentinelle">
        <div class="os-nav__brand-row">
          <a class="os-nav__brand" href="/" aria-label="Ocean Sentinelle - Accueil">
            <span class="os-nav__mark" aria-hidden="true">OS</span>
            <span>
              <span class="os-nav__title">Ocean Sentinelle</span>
              <span class="os-nav__subtitle">Bassin d'Arcachon - transparence publique</span>
            </span>
          </a>
          <span class="os-nav__status">Version publique volontairement partielle - Shadow mode - Non décisionnel - Simulation ≠ mesure</span>
        </div>
        <div class="os-nav__tabs" role="list" aria-label="Onglets canoniques">
          ${NAV_ITEMS.map(item => {
            const current = item.id === active ? ' aria-current="page"' : "";
            return `<a class="os-nav__tab" href="${item.href}" role="listitem"${current}>${item.label}</a>`;
          }).join("")}
        </div>
      </nav>
    `;
  }

  function mount() {
    const host = document.getElementById("os-topnav");
    if (host) render(host);
  }

  if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", mount);
  } else {
    mount();
  }
})();
