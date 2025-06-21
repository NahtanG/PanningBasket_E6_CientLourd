# PlanningBasket – E6 ClientLourd

# Gestion des entraînements de basketball

Application de bureau développée en Python avec interface Tkinter, permettant à un coach de gérer les créneaux hebdomadaires d'entraînement de différentes catégories (U13, U15, etc.).

---

## 🚀 Lancement rapide (Windows)

1. Téléchargez le fichier **`main.exe`** depuis le dossier [`dist/`](./dist) ou le fichier `.zip` fourni.
2. Double-cliquez sur `main.exe` pour lancer l'application.
3. La base de données `trainings.db` sera générée automatiquement au premier lancement.

✅ **Aucune installation de Python n’est requise** pour cette version.

---

## 🧪 Lancer depuis les sources (macOS/Linux/Windows)

### 1. Cloner le dépôt

```bash
git clone https://github.com/NahtanG/PanningBasket_E6_ClientLourd.git
cd PanningBasket_E6_ClientLourd
```

### 2. Création de l'environnement Conda

```bash
conda env create -f env.yml
conda activate tkinter
python main.py
```

---

## 📂 Structure du projet

```
PanningBasket_E6_ClientLourd/
│
├── main.py                     # Point d’entrée de l’application
├── env.yml                    # Environnement Conda avec dépendances
├── trainings.db               # Base SQLite (créée automatiquement)
│
├── db/                        # Gestion de la base
│   └── database.py
│
├── ui/                        # Interface graphique
│   └── weekly_view.py
│
├── models/                    # Modèle Pydantic
│   └── training.py
│
├── utils/                     # Fonctions utilitaires
│   └── date_utils.py
│
├── exporter/                 # Export PDF
│   └── pdf_exporter.py
│
└── README.txt
```

---

## ✨ Fonctionnalités

- 📅 Affichage hebdomadaire sous forme de calendrier
- ➕ Ajout, modification, suppression de créneaux
- 📤 Export PDF des entraînements par mois
- 🗃️ Stockage local via SQLite
- 🖱️ Interface intuitive et fluide (Tkinter)

---

## 📦 Création de l’exécutable (.exe)

L’exécutable peut être généré avec [PyInstaller](https://www.pyinstaller.org/) :

```bash
pyinstaller --onefile --noconsole main.py
```

Il sera disponible dans le dossier `dist/`.

---

## 🔗 Auteur

**Nathan Guillaumot**  
Projet réalisé dans le cadre du BTS SIO – Épreuve E6 (Client lourd)  
GitHub : [NahtanG](https://github.com/NahtanG)
