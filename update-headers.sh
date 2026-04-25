#!/bin/bash
# Script de mise à jour des headers Ocean Sentinel V3.2

cd /opt/oceansentinel/frontend

# Fonction pour extraire et remplacer le header
update_header() {
    local page=$1
    local active_page=$2
    
    echo "📝 Mise à jour de $page.html..."
    
    # Créer un backup
    cp "$page.html" "$page.html.bak"
    
    # Extraire le contenu avant et après le header
    sed -n '1,/<header class="header">/p' "$page.html" | head -n -1 > /tmp/${page}_before.html
    sed -n '/<\/header>/,$p' "$page.html" | tail -n +2 > /tmp/${page}_after.html
    
    # Créer le nouveau header avec la bonne page active
    cat > /tmp/${page}_header.html << 'EOF'
    <header class="header">
        <div class="header__inner">
            <div class="header__top">
                <a href="index.html" class="header__logo">
                    <img src="/assets/images/logo.svg" alt="" width="32" height="32">
                    <span class="header__logo-text">Ocean Sentinel</span>
                </a>
            </div>
            
            <!-- Navigation Desktop -->
            <nav class="header__nav">
                <ul class="nav-tabs">
                    <li>
                        <a href="index.html" class="nav-tabs__link NAV_INDEX">
                            <span class="nav-tabs__icon">🏠</span>
                            <span>Accueil</span>
                        </a>
                    </li>
                    <li>
                        <a href="dashboard.html" class="nav-tabs__link NAV_DASHBOARD">
                            <span class="nav-tabs__icon">📊</span>
                            <span>Données en direct</span>
                        </a>
                    </li>
                    <li>
                        <a href="about.html" class="nav-tabs__link NAV_ABOUT">
                            <span class="nav-tabs__icon">📖</span>
                            <span>Le Projet</span>
                        </a>
                    </li>
                    <li>
                        <a href="api.html" class="nav-tabs__link NAV_API">
                            <span class="nav-tabs__icon">⚡</span>
                            <span>API REST</span>
                        </a>
                    </li>
                    <li>
                        <a href="podcast.html" class="nav-tabs__link NAV_PODCAST">
                            <span class="nav-tabs__icon">🎙️</span>
                            <span>Podcast</span>
                        </a>
                    </li>
                </ul>
            </nav>
        </div>
    </header>
EOF
    
    # Activer la bonne page
    sed -i "s/NAV_${active_page^^}/nav-tabs__link--active/g" /tmp/${page}_header.html
    sed -i "s/NAV_[A-Z]*//g" /tmp/${page}_header.html
    
    # Reconstruire le fichier
    cat /tmp/${page}_before.html /tmp/${page}_header.html /tmp/${page}_after.html > "$page.html"
    
    echo "✅ $page.html mis à jour"
}

# Mettre à jour chaque page
update_header "index" "index"
update_header "about" "about"
update_header "api" "api"
update_header "podcast" "podcast"

# Nettoyer
rm -f /tmp/*_before.html /tmp/*_after.html /tmp/*_header.html

echo ""
echo "🎉 Toutes les pages ont été mises à jour!"
echo "Les backups sont dans *.html.bak"
