# 🚗 TraficoStat — Application de collecte et d'analyse du trafic urbain

## Description
Application web Flask de collecte et d'analyse descriptive de données de trafic urbain.
- Import CSV/Excel
- Saisie manuelle de données
- Données de démonstration intégrées
- Statistiques descriptives complètes (moyenne, médiane, écart-type, quartiles...)
- Visualisations interactives (histogrammes par variable)
- Interface moderne responsive

---

## Lancer en local

```bash
pip install -r requirements.txt
python app.py
# Ouvrir http://localhost:5000
```

---

## Déployer gratuitement sur Render.com (lien en ligne)

1. Créez un compte sur https://render.com
2. Cliquez **New → Web Service**
3. Connectez votre dépôt GitHub contenant ce code
4. Configurez :
   - **Build Command** : `pip install -r requirements.txt`
   - **Start Command** : `gunicorn app:app`
   - **Environment** : Python 3
5. Cliquez **Deploy** → vous obtenez un lien `https://traficostat.onrender.com`

---

## Déployer sur Railway.app

1. Créez un compte sur https://railway.app
2. **New Project → Deploy from GitHub**
3. Sélectionnez votre repo
4. Railway détecte Flask automatiquement
5. Lien généré en 2 minutes

---

## Structure du projet
```
traficostat/
├── app.py              # Application Flask principale
├── requirements.txt    # Dépendances Python
├── templates/
│   └── index.html      # Interface utilisateur
└── uploads/            # Dossier pour les fichiers uploadés
```

---

## Fonctionnalités
| Fonctionnalité | Description |
|---|---|
| Import fichier | CSV, XLSX, XLS jusqu'à 16 Mo |
| Saisie manuelle | Formulaire interactif avec liste des entrées |
| Données exemple | 120 observations simulées |
| Stats descriptives | N, Moyenne, Médiane, Écart-type, Min, Max, Q1, Q3 |
| Visualisations | Histogrammes par variable numérique |
| Aperçu données | Tableau des 10 premières lignes |
