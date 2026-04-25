# Script de déploiement Design System V3.1
# Ocean Sentinel - Frontend Mobile-First

Write-Host "🚀 Déploiement Design System V3.1..." -ForegroundColor Cyan

# 1. Créer le fichier design-system.css complet
$designSystemCSS = @"
/**
 * OCEAN SENTINEL DESIGN SYSTEM V3.1
 * Mobile-First | WCAG 2.2 AA | Terrain-Ready
 */

/* RESET & BASE */
*, *::before, *::after {
    margin: 0;
    padding: 0;
    box-sizing: border-box;
    -webkit-tap-highlight-color: transparent;
}

:root {
    /* Colors */
    --color-bg-primary: #001a2e;
    --color-bg-secondary: #002642;
    --color-bg-tertiary: #003459;
    --color-bg-overlay: rgba(0, 26, 46, 0.95);
    
    --color-text-primary: #ffffff;
    --color-text-secondary: #cbd5e1;
    --color-text-tertiary: #94a3b8;
    
    --color-critical: #ff0000;
    --color-critical-bg: #1a0000;
    --color-critical-text: #ff6666;
    --color-success: #10b981;
    --color-success-bg: #065f46;
    --color-warning: #f59e0b;
    --color-info: #38bdf8;
    
    --color-border-default: #334155;
    --color-border-focus: #38bdf8;
    
    /* Badges Règle de Vérité */
    --badge-measured-bg: #065f46;
    --badge-measured-border: #10b981;
    --badge-inferred-bg: #7c2d12;
    --badge-inferred-border: #f59e0b;
    --badge-simulated-bg: #1f2937;
    --badge-simulated-border: #9ca3af;
    
    /* Typography */
    --font-primary: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
    --text-xs: 12px;
    --text-sm: 14px;
    --text-base: 16px;
    --text-lg: 18px;
    --text-xl: 20px;
    --text-2xl: 24px;
    --text-3xl: 32px;
    --text-4xl: 48px;
    
    --font-normal: 400;
    --font-semibold: 600;
    --font-bold: 700;
    
    /* Spacing */
    --space-xs: 4px;
    --space-sm: 8px;
    --space-md: 16px;
    --space-lg: 24px;
    --space-xl: 32px;
    
    --touch-min: 48px;
    
    /* Borders */
    --border-width-thin: 1px;
    --border-width-default: 2px;
    --border-width-thick: 3px;
    --radius-sm: 6px;
    --radius-md: 8px;
    --radius-lg: 12px;
    --radius-full: 9999px;
    
    /* Shadows */
    --shadow-md: 0 4px 6px rgba(0, 0, 0, 0.4);
    --shadow-alert: 0 4px 12px rgba(255, 0, 0, 0.4);
    
    /* Z-index */
    --z-sticky: 20;
    --z-fixed: 30;
    --z-alert: 60;
    
    /* Transitions */
    --transition-fast: 150ms cubic-bezier(0.4, 0, 0.2, 1);
    
    /* Safe Areas */
    --safe-top: env(safe-area-inset-top, 0px);
    --safe-bottom: env(safe-area-inset-bottom, 0px);
}

html {
    font-size: 16px;
    -webkit-font-smoothing: antialiased;
}

body {
    font-family: var(--font-primary);
    font-size: var(--text-base);
    line-height: 1.6;
    color: var(--color-text-primary);
    background: var(--color-bg-primary);
    min-height: 100vh;
    padding-bottom: calc(var(--safe-bottom) + 60px);
}

/* BADGES RÈGLE DE VÉRITÉ */
.data-badge {
    display: inline-flex;
    align-items: center;
    gap: var(--space-sm);
    padding: var(--space-sm) var(--space-md);
    border-radius: var(--radius-sm);
    font-size: var(--text-sm);
    font-weight: var(--font-bold);
    text-transform: uppercase;
    letter-spacing: 0.05em;
    border-width: var(--border-width-default);
    border-style: solid;
}

.data-badge__icon {
    width: 16px;
    height: 16px;
}

.data-badge--measured {
    background: var(--badge-measured-bg);
    color: #ffffff;
    border-color: var(--badge-measured-border);
}

.data-badge--inferred {
    background: var(--badge-inferred-bg);
    color: #ffffff;
    border-color: var(--badge-inferred-border);
}

.data-badge--simulated {
    background: var(--badge-simulated-bg);
    color: #ffffff;
    border-color: var(--badge-simulated-border);
}

/* HEADER */
.header {
    position: sticky;
    top: 0;
    z-index: var(--z-sticky);
    background: var(--color-bg-overlay);
    backdrop-filter: blur(12px);
    border-bottom: var(--border-width-thin) solid var(--color-border-default);
    padding: var(--space-md);
    padding-top: calc(var(--safe-top) + var(--space-md));
}

.header__content {
    display: flex;
    align-items: center;
    justify-content: space-between;
    max-width: 1200px;
    margin: 0 auto;
}

.header__logo {
    display: flex;
    align-items: center;
    gap: var(--space-sm);
    text-decoration: none;
    color: var(--color-text-primary);
}

.header__logo-img {
    width: 32px;
    height: 32px;
}

.header__logo-text {
    font-size: var(--text-lg);
    font-weight: var(--font-bold);
}

/* BOTTOM NAVIGATION */
.bottom-nav {
    position: fixed;
    bottom: 0;
    left: 0;
    right: 0;
    z-index: var(--z-fixed);
    background: var(--color-bg-overlay);
    backdrop-filter: blur(12px);
    border-top: var(--border-width-thin) solid var(--color-border-default);
    padding-bottom: var(--safe-bottom);
}

.bottom-nav__list {
    display: flex;
    justify-content: space-around;
    list-style: none;
}

.bottom-nav__link {
    display: flex;
    flex-direction: column;
    align-items: center;
    justify-content: center;
    min-height: 60px;
    text-decoration: none;
    color: var(--color-text-tertiary);
    font-size: 11px;
    gap: var(--space-xs);
}

.bottom-nav__link--active {
    color: var(--color-text-primary);
}

.bottom-nav__icon {
    font-size: var(--text-2xl);
}

/* ALERTES SACS */
.alert-sacs {
    position: sticky;
    top: calc(60px + var(--safe-top));
    z-index: var(--z-alert);
    display: flex;
    align-items: center;
    gap: var(--space-md);
    padding: var(--space-md);
    border-radius: var(--radius-lg);
    margin: var(--space-md);
    border-width: var(--border-width-thick);
    border-style: solid;
    background: linear-gradient(135deg, var(--color-critical-bg) 0%, #330000 100%);
    border-color: var(--color-critical);
    box-shadow: var(--shadow-alert);
    animation: pulse-alert 2s infinite;
}

@keyframes pulse-alert {
    0%, 100% { border-color: var(--color-critical); }
    50% { border-color: var(--color-critical-text); }
}

.alert-sacs__icon {
    font-size: var(--text-3xl);
    flex-shrink: 0;
}

.alert-sacs__content {
    flex: 1;
}

.alert-sacs__title {
    font-size: var(--text-lg);
    font-weight: var(--font-bold);
    text-transform: uppercase;
    margin-bottom: var(--space-xs);
}

.alert-sacs__value {
    font-size: var(--text-2xl);
    font-weight: var(--font-bold);
    color: var(--color-critical-text);
    margin-bottom: var(--space-xs);
}

.alert-sacs__action {
    font-size: var(--text-sm);
    color: #ffcccc;
}

.alert-sacs__dismiss {
    width: var(--touch-min);
    height: var(--touch-min);
    background: rgba(255, 255, 255, 0.1);
    border: var(--border-width-default) solid rgba(255, 255, 255, 0.3);
    border-radius: var(--radius-md);
    color: var(--color-text-primary);
    font-size: var(--text-2xl);
    cursor: pointer;
}

/* METRIC CARDS */
.station-grid {
    display: grid;
    grid-template-columns: 1fr;
    gap: var(--space-md);
    padding: var(--space-md);
    max-width: 1200px;
    margin: 0 auto;
}

.metric-card {
    background: var(--color-bg-secondary);
    border: var(--border-width-default) solid var(--color-border-default);
    border-radius: var(--radius-lg);
    padding: var(--space-lg);
    position: relative;
}

.metric-card::before {
    content: '';
    position: absolute;
    left: 0;
    top: 0;
    bottom: 0;
    width: 4px;
    background: var(--color-success);
}

.metric-card--critical::before {
    background: var(--color-critical);
}

.metric-card__header {
    display: flex;
    justify-content: space-between;
    margin-bottom: var(--space-md);
}

.metric-card__label {
    font-size: var(--text-sm);
    font-weight: var(--font-semibold);
    text-transform: uppercase;
    color: var(--color-text-secondary);
}

.metric-card__value {
    font-size: 48px;
    font-weight: var(--font-bold);
    line-height: 1;
    color: var(--color-text-primary);
    margin-bottom: var(--space-md);
}

.metric-card--critical .metric-card__value {
    color: var(--color-critical-text);
}

.metric-card__unit {
    font-size: 24px;
    color: var(--color-text-secondary);
}

.metric-card__threshold {
    font-size: var(--text-sm);
    color: var(--color-text-tertiary);
    margin-bottom: var(--space-md);
}

.metric-card--critical .metric-card__threshold {
    color: var(--color-critical-text);
    font-weight: var(--font-semibold);
}

.metric-card__meta {
    border-top: var(--border-width-thin) solid var(--color-border-default);
    padding-top: var(--space-md);
}

.metric-card__station {
    font-size: var(--text-xs);
    color: var(--color-text-tertiary);
    margin-bottom: var(--space-xs);
}

.metric-card__timestamp {
    font-size: var(--text-xs);
    color: var(--color-text-tertiary);
}

@media (min-width: 640px) {
    .station-grid {
        grid-template-columns: repeat(2, 1fr);
    }
}

@media (min-width: 1024px) {
    .station-grid {
        grid-template-columns: repeat(4, 1fr);
    }
}
"@

Set-Content -Path "design-system.css" -Value $designSystemCSS -Encoding UTF8
Write-Host "✅ Fichier design-system.css créé" -ForegroundColor Green

# 2. Déployer sur VPS
Write-Host "📤 Déploiement sur VPS..." -ForegroundColor Yellow
scp design-system.css root@76.13.43.3:/opt/oceansentinel/frontend/assets/css/

Write-Host "✅ Déploiement terminé!" -ForegroundColor Green
