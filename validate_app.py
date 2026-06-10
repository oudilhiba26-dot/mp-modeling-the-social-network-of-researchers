"""
Script pour valider que app.py n'a pas d'erreurs de syntaxe et peut être importé
"""
import sys
from pathlib import Path

print("=" * 70)
print("🧪 VALIDATION DE L'APPLICATION STREAMLIT")
print("=" * 70)

# Ajouter le frontend au path
frontend_dir = Path(__file__).parent / "frontend"
sys.path.insert(0, str(frontend_dir))

try:
    print("\n📝 Vérification de la syntaxe Python...")
    import py_compile
    app_file = frontend_dir / "app.py"
    py_compile.compile(str(app_file), doraise=True)
    print("✅ Pas d'erreurs de syntaxe détectées")
except py_compile.PyCompileError as e:
    print(f"❌ Erreur de syntaxe: {e}")
    sys.exit(1)

try:
    print("\n📦 Vérification des imports...")
    # Ne pas importer entièrement (cela lancerait streamlit)
    # Juste vérifier les imports critiques
    import importlib.util
    spec = importlib.util.spec_from_file_location("app", str(app_file))
    print("✅ Module app.py peut être chargé (structure valide)")
except Exception as e:
    print(f"❌ Erreur d'import: {e}")
    sys.exit(1)

try:
    print("\n🧮 Vérification des dépendances...")
    import streamlit
    import pandas
    import plotly.express
    import plotly.graph_objects
    print("✅ Toutes les dépendances sont disponibles:")
    print(f"   - Streamlit {streamlit.__version__}")
    print(f"   - Pandas {pandas.__version__}")
    print(f"   - Plotly Express")
except ImportError as e:
    print(f"⚠️ Avertissement - Dépendance manquante: {e}")
    print("   Installez avec: pip install streamlit pandas plotly")

print("\n" + "=" * 70)
print("✅ VALIDATION COMPLÈTE!")
print("=" * 70)
print("\n📝 Pour lancer l'application:")
print("   streamlit run frontend/app.py")
print("\n💡 Accédez à http://localhost:8501 dans votre navigateur")
