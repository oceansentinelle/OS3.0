#!/usr/bin/env python3
"""
Script de synchronisation des headers Ocean Sentinel V3.2
Met à jour index.html, about.html, api.html, podcast.html avec le header du dashboard
"""

import subprocess
import re

# Pages à mettre à jour
pages = ['index', 'about', 'api', 'podcast']

# CSS du header (extrait du dashboard)
header_css = """
        /* HEADER */
        .header {
            position: sticky;
            top: 0;
            z-index: 30;
            background: rgba(0, 26, 46, 0.95);
            backdrop-filter: blur(12px);
            border-bottom: 2px solid var(--color-info);
            padding-top: calc(var(--safe-top) + var(--space-md));
        }

        .header__inner {
            max-width: 1200px;
            margin: 0 auto;
            padding: 0 var(--space-md);
        }

        .header__top {
            display: flex;
            align-items: center;
            justify-content: space-between;
            padding-bottom: 12px;
        }

        .header__logo {
            display: flex;
            align-items: center;
            gap: 8px;
            text-decoration: none;
            color: var(--text-primary);
        }

        .header__logo-text {
            font-size: 18px;
            font-weight: 700;
        }

        /* NAVIGATION TABS */
        .header__nav {
            display: none;
        }

        @media (min-width: 768px) {
            .header__nav {
                display: block;
            }
        }

        .nav-tabs {
            display: flex;
            gap: 8px;
            list-style: none;
            border-bottom: 1px solid var(--border-default);
            margin: 0 calc(var(--space-md) * -1);
            padding: 0 var(--space-md);
        }

        .nav-tabs__link {
            display: flex;
            align-items: center;
            gap: 8px;
            padding: 12px 16px;
            text-decoration: none;
            color: #94a3b8;
            font-size: 13px;
            font-weight: 600;
            border-bottom: 3px solid transparent;
            transition: all 0.2s;
            white-space: nowrap;
        }

        .nav-tabs__link:hover {
            color: var(--color-info);
            border-bottom-color: var(--color-info);
        }

        .nav-tabs__link--active {
            color: var(--text-primary);
            border-bottom-color: var(--color-info);
            background: rgba(56, 189, 248, 0.05);
        }

        .nav-tabs__icon {
            font-size: 18px;
        }
"""

def get_header_html(active_page):
    """Génère le HTML du header avec la page active"""
    pages_config = {
        'index': ('Accueil', '🏠'),
        'dashboard': ('Données en direct', '📊'),
        'about': ('Le Projet', '📖'),
        'api': ('API REST', '⚡'),
        'podcast': ('Podcast', '🎙️')
    }
    
    nav_items = []
    for page, (label, icon) in pages_config.items():
        active_class = ' nav-tabs__link--active' if page == active_page else ''
        nav_items.append(f'''                    <li>
                        <a href="{page}.html" class="nav-tabs__link{active_class}">
                            <span class="nav-tabs__icon">{icon}</span>
                            <span>{label}</span>
                        </a>
                    </li>''')
    
    return f'''    <header class="header">
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
{chr(10).join(nav_items)}
                </ul>
            </nav>
        </div>
    </header>'''

for page in pages:
    print(f"📝 Mise à jour de {page}.html...")
    
    # Télécharger le fichier
    result = subprocess.run(
        ['ssh', 'root@76.13.43.3', f'cat /opt/oceansentinel/frontend/{page}.html'],
        capture_output=True,
        text=True
    )
    
    content = result.stdout
    
    # Remplacer le header
    new_header = get_header_html(page)
    content = re.sub(
        r'<header class="header">.*?</header>',
        new_header,
        content,
        flags=re.DOTALL
    )
    
    # Sauvegarder localement
    with open(f'C:\\Users\\ktprt\\Documents\\OSwindsurf\\{page}-updated.html', 'w', encoding='utf-8') as f:
        f.write(content)
    
    # Uploader
    subprocess.run([
        'scp',
        f'C:\\Users\\ktprt\\Documents\\OSwindsurf\\{page}-updated.html',
        f'root@76.13.43.3:/opt/oceansentinel/frontend/{page}.html'
    ])
    
    print(f"✅ {page}.html mis à jour")

print("\n🎉 Toutes les pages ont été synchronisées!")
