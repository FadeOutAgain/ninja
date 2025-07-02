#!/usr/bin/env bash

# Création de l'environnement virtuel
echo "📦 Création de l'environnement virtuel dash-venv..."
python3 -m venv dash-venv

# Activation
echo "⚙️ Activation de l'environnement..."
source dash-venv/bin/activate

# Mise à jour de pip
echo "🔧 Mise à jour de pip..."
pip install --upgrade pip

# Installation des modules nécessaires
echo "📚 Installation de dash, beautifulsoup4 et pandas..."
pip install dash beautifulsoup4 pandas

# Fin
echo "✅ Environnement prêt. Activez-le avec :"
echo "   source dash-venv/bin/activate"
