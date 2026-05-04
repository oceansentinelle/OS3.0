(function () {
    const links = [
        ["Accueil", "/"],
        ["Le Projet", "/projet/"],
        ["Dashboard", "/dashboard/"],
        ["Simulations IA", "/dashboard/simulations/"],
        ["Bibliothèque", "/dashboard/simulations/library/"],
        ["OSINT v1.2", "/dashboard/transparence/osint/"],
        ["Infrastructure Overview", "/dashboard/transparence/infrastructure/"],
        ["Podcast", "/podcast/"]
    ];

    function normalizedPath() {
        const declared = document.body && document.body.getAttribute("data-route");
        const path = declared || window.location.pathname || "/";
        if (path === "" || path === "/index.html") return "/";
        return path.endsWith("/") ? path : `${path}/`;
    }

    function buildNav() {
        document.querySelectorAll("#os-topnav").forEach((node) => node.remove());

        const current = normalizedPath();
        const header = document.createElement("header");
        header.id = "os-topnav";
        header.className = "os-topnav";

        const inner = document.createElement("div");
        inner.className = "os-topnav__inner";

        const brand = document.createElement("a");
        brand.className = "os-topnav__brand";
        brand.href = "/";
        brand.textContent = "Ocean Sentinelle";
        inner.appendChild(brand);

        const nav = document.createElement("nav");
        nav.className = "os-topnav__links";
        nav.setAttribute("aria-label", "Navigation principale");

        links.forEach(([label, href]) => {
            const item = document.createElement("a");
            item.className = "os-topnav__link";
            item.href = href;
            item.textContent = label;
            if (href === current) {
                item.setAttribute("aria-current", "page");
            }
            nav.appendChild(item);
        });

        inner.appendChild(nav);
        header.appendChild(inner);
        document.body.prepend(header);
    }

    if (document.readyState === "loading") {
        document.addEventListener("DOMContentLoaded", buildNav);
    } else {
        buildNav();
    }
})();
