# PlanningBasket – BTS SIO E6 Client Lourd

Application de gestion des entraînements de basketball  
**Projet présenté pour l’épreuve E6 du BTS SIO (option SLAM)**

---

## 📦 Contenu du dossier à fournir

- **Tout le dossier du projet** :  
  Incluant :
  - `main.py`
  - tous les sous-dossiers (`ui/`, `db/`, `models/`, `utils/`, `exporter/`, etc.)
  - les fichiers d’environnement :
    - `env.yml` (pour Mac/Linux/Windows)
    - `env_windows.yml` (optionnel, pour Windows)
  - les ressources nécessaires (`assets/`, icônes, etc.)
  - la base de données `trainings.db` (si tu veux fournir un exemple, sinon elle sera créée automatiquement)
  - ce fichier `README.md`

---

## 🚀 Lancer l’application (tous systèmes)

### 1. **Cloner ou copier le dossier du projet**

```bash
git clone https://github.com/NahtanG/PanningBasket_E6_ClientLourd.git
cd PanningBasket_E6_ClientLourd
```

ou simplement copier le dossier sur la machine cible.

### 2. **Créer l’environnement Conda**

#### Sous **Windows** :

```bash
conda env create -f env.yml
conda activate tkinter
python main.py
```

#### Sous **Mac/Linux** :

```bash
conda env create -f env.yml
conda activate tkinter
python main.py
```

> **Remarque** :  
> Le fichier `env.yml` fonctionne sur tous les systèmes.  
> Si besoin, un fichier `env_windows.yml` est fourni pour Windows.

---

## 🖥️ Lancer l’exécutable (Windows ou Mac)

### **Windows**

- Un exécutable `PlanningBasket.exe` peut être généré avec :
  ```bash
  pyinstaller --onefile --noconsole --icon=assets/basket.ico --name="PlanningBasket" main.py
  ```
- Il se trouve dans le dossier `dist/`.
- Double-clique sur `PlanningBasket.exe` pour lancer l’application.

### **Mac**

- Un bundle `.app` peut être généré avec :
  ```bash
  pyinstaller --windowed --add-data "ui:ui" --add-data "db:db" --add-data "models:models" --add-data "utils:utils" --add-data "exporter:exporter" --icon=assets/basket.icns --name="PlanningBasket" main.py
  ```
- L’application sera dans `dist/PlanningBasket.app`.
- Si l’app ne se lance pas, exécute dans le terminal :
  ```bash
  xattr -dr com.apple.quarantine dist/PlanningBasket.app
  ```
- Puis lance-la par double-clic ou :
  ```bash
  open dist/PlanningBasket.app
  ```

---

## 📂 Structure du projet

```
PanningBasket_E6_ClientLourd/
│
├── main.py
├── env.yml
├── env_windows.yml
├── trainings.db
├── assets/
│   ├── basket.ico
│   └── basket.png
│
├── db/
│   └── database.py
├── ui/
│   └── weekly_view.py
├── models/
│   └── training.py
├── utils/
│   └── date_utils.py
├── exporter/
│   └── pdf_exporter.py
└── README.md
```

---

## ✨ Fonctionnalités

- **Affichage hebdomadaire** sous forme de calendrier
- **Ajout, modification, suppression** de créneaux d’entraînement
- **Export PDF** des entraînements par mois
- **Statistiques** par catégorie et par semaine
- **Stockage local** via SQLite
- **Interface fluide** (Tkinter)

---

## 📝 Conseils pour l’épreuve E6

- **Explique dans ton dossier E6** comment lancer l’application (copie ce README).
- **Fournis le dossier complet** (pas seulement l’exécutable).
- **Teste sur un autre poste** (Windows et/ou Mac) avant l’épreuve.
- **Vérifie la présence des fichiers d’environnement** (`env.yml`, `env_windows.yml`).

---

## 👤 Auteur

**Nathan Guillaumot**  
Projet réalisé pour le BTS SIO – Épreuve E6 (Client lourd)
