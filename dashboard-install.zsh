#!/usr/bin/env bash

# Création de l'environnement virtuel
echo "📦 Création de l'environnement virtuel dash-venv..."
python3 -m venv dash-env

# Activation
echo "⚙️ Activation de l'environnement..."
source dash-env/bin/activate

# Mise à jour de pip
echo "🔧 Mise à jour de pip..."
pip install --upgrade pip

# Installation des modules nécessaires
echo "📚 Installation de dash, beautifulsoup4 et pandas..."
pip install dash beautifulsoup4 pandas

# Fin

echo "🛢️ Préparation de la base de données..."
python init_db.py

echo "✅ Environnement prêt. Activez-le avec :"
echo "   source dash-env/bin/activate"
