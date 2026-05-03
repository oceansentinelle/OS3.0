(function () {
  const items = [
    { id: "home", label: "Accueil", href: "/" },
    { id: "dashboard", label: "Dashboard", href: "/dashboard/" },
    { id: "simulations", label: "Simulations IA", href: "/dashboard/" },
    { id: "osint", label: "OSINT v1.2", href: "/dashboard/transparence/osint/" },
    { id: "library", label: "Bibliothèque", href: "/dashboard/simulations/library/" },
    { id: "infrastructure", label: "Infrastructure Overview", href: "/dashboard/transparence/infrastructure/" },
    { id: "project", label: "Le Projet", href: "/projet/" },
    { id: "podcast", label: "Podcast", href: "/podcast/" },
    { id: "transparency", label: "Transparence", href: "/dashboard/transparence/infrastructure/" },
    { id: "data", label: "API / Data", href: "/data/schema/scenario_template.schema.json" },
    { id: "contact", label: "Contact", href: "/#contact" }
  ];

  function injectStyles() {
    if (document.getElementById("os-shared-nav-style")) return;
    const style = document.createElement("style");
    style.id = "os-shared-nav-style";
    style.textContent = `
      .os-topbar{position:sticky;top:0;z-index:80;background:rgba(5,18,32,.92);backdrop-filter:blur(18px);border-bottom:1px solid rgba(126,215,255,.24)}
      .os-nav{max-width:1180px;margin:0 auto;padding:10px 20px}
      .os-brand-row{display:flex;align-items:center;justify-content:space-between;gap:16px;margin-bottom:10px}
      .os-brand{display:inline-flex;align-items:center;gap:10px;color:#EAF4FF;text-decoration:none;font-weight:900;white-space:nowrap}
      .os-brand-mark{display:inline-flex;align-items:center;justify-content:center;width:34px;height:34px;border-radius:8px;background:linear-gradient(135deg,#56B6E9,#7ED7FF);color:#052033;font-size:.8rem;font-weight:950}
      .os-brand-subtitle{display:block;color:#B8CBE0;font-size:.78rem;font-weight:700;margin-top:1px}
      .os-status{color:#B8CBE0;border:1px solid rgba(126,215,255,.22);border-radius:999px;padding:6px 10px;font-size:.78rem;font-weight:800;background:rgba(255,255,255,.05);white-space:nowrap}
      .os-tabs{display:flex;gap:8px;overflow-x:auto;scrollbar-width:none;-webkit-overflow-scrolling:touch;padding:2px 0 5px}
      .os-tabs::-webkit-scrollbar{display:none}
      .os-tab{display:inline-flex;align-items:center;justify-content:center;min-height:40px;border:1px solid rgba(255,255,255,.14);background:rgba(255,255,255,.055);color:#B8CBE0;border-radius:999px;padding:8px 14px;font-size:14px;font-weight:800;text-decoration:none;white-space:nowrap}
      .os-tab:hover,.os-tab:focus-visible{color:#EAF4FF;border-color:#56B6E9;outline:3px solid rgba(86,182,233,.25);outline-offset:2px}
      .os-tab[aria-current="page"]{color:#fff;border-color:#56B6E9;background:rgba(86,182,233,.16)}
      @media(max-width:680px){.os-brand-row{align-items:flex-start;flex-direction:column}.os-status{white-space:normal}.os-nav{padding:10px 14px}}
    `;
    document.head.appendChild(style);
  }

  function renderNav(host) {
    const active = host.dataset.active || "";
    host.className = `${host.className} os-topbar`.trim();
    host.innerHTML = `
      <nav class="os-nav" aria-label="Navigation Ocean Sentinelle">
        <div class="os-brand-row">
          <a class="os-brand" href="/" aria-label="Ocean Sentinelle - Accueil">
            <span class="os-brand-mark">OS</span>
            <span>
              <span>Ocean Sentinelle</span>
              <span class="os-brand-subtitle">Bassin d'Arcachon - transparence publique</span>
            </span>
          </a>
          <span class="os-status">Version publique volontairement partielle · Shadow mode · Non décisionnel · Simulation ≠ mesure</span>
        </div>
        <div class="os-tabs" role="list" aria-label="Onglets du site">
          ${items.map(item => `<a class="os-tab" href="${item.href}" role="listitem"${item.id === active ? ' aria-current="page"' : ""}>${item.label}</a>`).join("")}
        </div>
      </nav>
    `;
  }

  injectStyles();
  document.querySelectorAll("[data-os-nav]").forEach(renderNav);
})();
