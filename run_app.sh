#!/bin/bash
# Script de démarrage rapide de l'application

echo "=================================="
echo "🚀 Démarrage de l'Application"
echo "=================================="
echo ""

# Vérification de Streamlit
if ! command -v streamlit &> /dev/null; then
    echo "❌ Streamlit n'est pas installé."
    echo "Installation..."
    pip install streamlit pandas plotly
fi

echo "✅ Tous les éléments sont prêts!"
echo ""
echo "Lancement de l'application..."
echo ""
echo "💡 Tips:"
echo "   - L'application s'ouvrira automatiquement dans votre navigateur"
echo "   - Accédez à http://localhost:8501 si ce n'est pas le cas"
echo "   - Appuyez sur Ctrl+C pour arrêter l'application"
echo "   - Appuyez sur 'R' dans l'interface pour redémarrer"
echo ""

cd "$(dirname "$0")"
streamlit run frontend/app.py
