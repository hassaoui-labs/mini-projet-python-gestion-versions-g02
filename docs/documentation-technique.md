[README.md](https://github.com/user-attachments/files/25159926/README.md)
# Mini VCS – Système de Contrôle de Version en Python

![Python Version](https://img.shields.io/badge/python-3.9+-blue.svg)
![License](https://img.shields.io/badge/license-MIT-green.svg)
![Status](https://img.shields.io/badge/status-educational-orange.svg)

> **Implémentation pédagogique d'un système de contrôle de version inspiré de Git**  
> Développé en Python pur avec interface CLI interactive et gestion complète des branches.

---

## 📋 Table des matières

- [Vue d'ensemble](#-vue-densemble)
- [Architecture du projet](#-architecture-du-projet)
- [Installation et prérequis](#-installation-et-prérequis)
- [Guide d'utilisation](#-guide-dutilisation)
- [Commandes détaillées](#-commandes-détaillées)
- [Fonctionnement interne](#-fonctionnement-interne)
- [Scénarios d'usage](#-scénarios-dusage)
- [Build et distribution](#-build-et-distribution)
- [Limitations techniques](#-limitations-techniques)
- [Contribution](#-contribution)

---

## 🎯 Vue d'ensemble

Mini VCS est un système de contrôle de version complet qui reproduit les mécanismes fondamentaux de Git avec une approche pédagogique claire. Le projet démontre concrètement :

- **Staging Area (Index)** : Zone tampon pour préparer les commits
- **Commits immuables** : Snapshots identifiés par hash SHA-1
- **DAG (Directed Acyclic Graph)** : Structure de l'historique des commits
- **Système de branches** : Pointeurs mobiles sur les commits
- **Résolution de conflits** : Outil interactif lors des merges
- **HEAD** : Pointeur symbolique vers la branche courante

### Ce que Mini VCS fait

✅ Initialise un dépôt local avec structure `.mini_vcs/`  
✅ Gère une zone de staging pour préparer les snapshots  
✅ Crée des commits avec génération de hash SHA-1  
✅ Supporte la création, navigation et fusion de branches  
✅ Détecte les conflits et propose une résolution interactive  
✅ Restaure l'état des fichiers lors du checkout  
✅ Affiche un graph ASCII du DAG  
✅ Interface CLI colorée avec prompt dynamique  

### Ce que Mini VCS ne fait pas

❌ Communication réseau (pas de push/pull/clone distant)  
❌ Compression des objets (pas de format packfile)  
❌ Diff ligne par ligne (merge au niveau fichier)  
❌ Support des fichiers binaires volumineux  
❌ Index partiel (pas de `git add -p`)  

---

## 🏗️ Architecture du projet

### Structure des fichiers

```
mini-vcs/
│
├── main.py              # Point d'entrée : mode interactif ou démo
├── core.py              # Moteur VCS : commits, staging, hash
├── branches.py          # Gestion branches : create, switch, merge
├── cli.py               # Interface utilisateur : shell interactif
├── build.py             # Script PyInstaller pour exécutable
│
└── .mini_vcs/           # Répertoire créé à l'init (ignoré par Git)
    ├── config.json      # Configuration : HEAD pointer
    ├── staging.json     # Zone de staging (index)
    ├── refs.json        # Mapping branche → commit ID
    └── commits/         # Stockage des snapshots
        ├── abc123...json
        └── def456...json
```

### Responsabilités des modules

| Module | Rôle | Responsabilités clés |
|--------|------|---------------------|
| **`core.py`** | Moteur de versioning | • Calcul hash SHA-1<br>• Gestion staging area<br>• Création/lecture commits<br>• Checkout snapshots |
| **`branches.py`** | Gestionnaire de branches | • Création branches<br>• Switch avec restauration fichiers<br>• Merge avec détection conflits<br>• Mise à jour refs |
| **`cli.py`** | Interface utilisateur | • Shell interactif (cmd.Cmd)<br>• Prompt dynamique coloré<br>• Parsing commandes<br>• Affichage graph/log |
| **`main.py`** | Orchestrateur | • Point d'entrée principal<br>• Mode démo automatisé<br>• Gestion arguments CLI |
| **`build.py`** | Packaging | • Configuration PyInstaller<br>• Génération exécutable standalone |

---

## 🛠️ Installation et prérequis

### Prérequis système

- **Python 3.9+** (utilisation de type hints modernes)
- **colorama** : Pour l'affichage couleur cross-platform

### Installation

#### Méthode 1 : Clonage Git

```bash
git clone https://github.com/votre-org/mini-vcs.git
cd mini-vcs
pip install colorama
```

#### Méthode 2 : Installation des dépendances

```bash
# Si vous avez téléchargé l'archive ZIP
cd mini-vcs
pip install -r requirements.txt  # Contenu : colorama
```

#### Vérification

```bash
python --version  # Doit afficher Python 3.9+
python main.py --help
```

---

## 🚀 Guide d'utilisation

### Mode 1 : Interface interactive (recommandé)

Lancez le shell interactif pour une expérience complète :

```bash
python main.py
```

Vous obtiendrez un prompt interactif :

```
╔══════════════════════════════════════╗
║     Mini VCS - Interface Avancée      ║
║     Version 2.0 (Refactored)          ║
╚══════════════════════════════════════╝
Tapez 'help' pour la liste des commandes.

vcs(main)>
```

### Mode 2 : Démo automatisée

Pour voir un scénario complet sans interaction :

```bash
python main.py --demo
```

**Ce que fait la démo :**
1. Initialise un dépôt
2. Crée `test.txt` (version 1)
3. Commit sur `main`
4. Crée et switch sur branche `dev`
5. Modifie `test.txt` (version 2)
6. Commit sur `dev`
7. Retourne sur `main`
8. Merge `dev` → `main`
9. Vérifie la fusion

---

## 📝 Commandes détaillées

### `init`

Initialise un nouveau dépôt dans le répertoire courant.

```bash
vcs(main)> init
```

**Effet :** Crée la structure `.mini_vcs/` avec :
- `config.json` : `{"head": "main"}`
- `commits/` : Répertoire vide
- Aucun `staging.json` ni `refs.json` (créés à la demande)

---

### `add <fichier1> [fichier2 ...]`

Ajoute des fichiers à la zone de staging.

```bash
vcs(main)> add app.py utils.py
```

**Comportement :**
- Lit le contenu de chaque fichier
- Calcule le hash SHA-1
- Stocke `{filename: {content, hash, added_at}}` dans `staging.json`
- Ignore les fichiers inexistants avec warning

**Détail technique :**
```python
# Dans core.py
file_hash = hashlib.sha1(content.encode('utf-8')).hexdigest()
```

---

### `commit "<message>"`

Crée un snapshot immuable du staging.

```bash
vcs(main)> commit "Initial implementation"
```

**Processus :**
1. Vérifie que le staging n'est pas vide
2. Génère un commit ID unique : `SHA-1(message + timestamp)`
3. Crée un objet commit :
   ```json
   {
     "id": "abc123def456...",
     "message": "Initial implementation",
     "date": "2026-02-06T14:23:45.123456",
     "files": { ... snapshots ... },
     "parent": "main"
   }
   ```
4. Sauvegarde dans `commits/abc123def456.json`
5. Vide le staging
6. Met à jour la branche courante dans `refs.json`

**Important :** Le commit seul ne met PAS à jour la branche. C'est `BranchManager.update_current_branch_commit()` qui le fait.

---

### `status`

Affiche l'état du dépôt.

```bash
vcs(main)> status
```

**Sortie typique :**
```
--- STATUS ---
Branche courante : main

Fichiers dans le staging (prêts à commit) :
  + app.py
  + utils.py

Fichiers non suivis (Untracked) :
  ? temp.log
```

**Logique :**
- **Staged** : Contenu de `staging.json`
- **Untracked** : Fichiers du répertoire non dans `.mini_vcs`, `__pycache__`, etc.

---

### `branch list`

Liste toutes les branches avec leurs commits.

```bash
vcs(main)> branch list
```

**Sortie :**
```
Branches :
 * main      (abc123d)
   dev       (def456a)
   feature   (abc123d)
```

Le `*` indique la branche courante (HEAD).

---

### `branch create <nom>`

Crée une nouvelle branche pointant sur le commit actuel.

```bash
vcs(dev)> branch create feature-auth
```

**Comportement :**
1. Vérifie que la branche n'existe pas
2. Récupère le commit ID de la branche courante
3. Crée l'entrée `refs.json` : `{"feature-auth": "abc123..."}`
4. Ne change PAS de branche (HEAD reste inchangé)

---

### `branch switch <nom>`

Change de branche et restaure les fichiers.

```bash
vcs(main)> branch switch dev
```

**Processus crucial :**
1. Vérifie l'existence de la branche dans `refs.json`
2. Récupère le commit ID cible
3. **Met à jour HEAD** : `config.json` → `{"head": "dev"}`
4. **Restaure les fichiers** : Appelle `checkout_snapshot(commit_id)`
   - Lit le commit JSON
   - Écrit chaque fichier du snapshot sur disque
5. **Met à jour le prompt** : `vcs(dev)>`

**Détail clé :**
```python
# Dans branches.py
self.vcs._update_head_ref(name)       # HEAD → nouvelle branche
self.vcs.checkout_snapshot(commit_id)  # Restauration disque
```

---

### `merge <branche>`

Fusionne une branche dans la branche courante.

```bash
vcs(main)> merge dev
```

**Algorithme de merge :**

1. **Validation** : Vérifier existence de la branche source
2. **Comparaison commits** :
   - Si `source_commit == current_commit` → "Already up to date"
3. **Détection de conflits** :
   - Pour chaque fichier de la source :
     - Si absent dans current → Ajout automatique
     - Si présent avec hash différent → **CONFLIT**
4. **Résolution interactive** (si conflit) :
   ```
   --- Résolution pour 'config.py' ---
   🔵 LOCAL (Branche courante) :
   DEBUG=False
   
   🟠 REMOTE (Branche entrante) :
   DEBUG=True
   -----------------------------------
   Choisir (L)ocal, (R)emote, ou (M)anuel ? [L/R/M] :
   ```
5. **Application** :
   - Écriture des fichiers fusionnés sur disque
   - Si pas de conflit → Fast-forward (déplace le pointeur)
   - Si conflit → Laisse les fichiers modifiés, demande commit manuel

**Code simplifié :**
```python
# Dans branches.py
for filename, data in src_files.items():
    if filename in curr_files:
        if data['hash'] != curr_files[filename]['hash']:
            # CONFLIT : résolution interactive
            resolved = self.resolve_conflict(filename, curr, data)
```

---

### `graph`

Affiche le DAG (Directed Acyclic Graph) des commits.

```bash
vcs(main)> graph
```

**Sortie exemple :**
```
--- REPRÉSENTATION DU GRAPH (DAG) ---
[def456a] --points-to--> [abc123d] <- dev, feature
   └── Second commit: dev changes
[abc123d] --points-to--> [None] <- main (HEAD)
   └── Initial commit: V1
```

**Détails :**
- Lit tous les fichiers dans `commits/`
- Affiche : `[short_id]` → `[parent]` ← branches
- Colore HEAD en cyan, autres branches en jaune
- Affiche le message de commit

---

### `log`

Affiche l'historique simple des commits.

```bash
vcs(main)> log
```

**Sortie :**
```
--- HISTORIQUE ---
def456a - 2026-02-06T14:25:30 : Second commit: dev changes
abc123d - 2026-02-06T14:23:45 : Initial commit: V1
```

---

### Raccourcis

- **`exit`** / **`q`** / **`Ctrl+D`** : Quitter le shell
- **`help`** : Affiche le guide visuel du workflow

---

## ⚙️ Fonctionnement interne

### 1. Structure de données

#### Commit Object (JSON)

```json
{
  "id": "abc123def456789...",
  "message": "Initial commit",
  "date": "2026-02-06T14:23:45.123456",
  "parent": "main",
  "files": {
    "app.py": {
      "content": "print('Hello')\n",
      "hash": "aaf4c61ddcc5e8a2dabede0f3b482cd9aea9434d",
      "added_at": "2026-02-06T14:22:10.987654"
    }
  }
}
```

#### Config (JSON)

```json
{
  "head": "main"
}
```

#### Refs (JSON)

```json
{
  "main": "abc123def456789...",
  "dev": "def456abc123456...",
  "feature-auth": "abc123def456789..."
}
```

#### Staging (JSON)

```json
{
  "app.py": {
    "content": "print('Hello World')\n",
    "hash": "новый_хэш",
    "added_at": "2026-02-06T14:30:00.000000"
  }
}
```

---

### 2. Workflow interne

#### Scénario : Premier commit

```
┌─────────────────┐
│ 1. init         │
│   Crée .mini_vcs│
└────────┬────────┘
         │
         v
┌─────────────────┐
│ 2. Créer app.py │ (sur disque réel)
└────────┬────────┘
         │
         v
┌─────────────────┐
│ 3. add app.py   │
│   staging.json  │ ← {"app.py": {content, hash, added_at}}
└────────┬────────┘
         │
         v
┌─────────────────┐
│ 4. commit "Msg" │
│   ├─ Génère ID  │ (SHA-1)
│   ├─ Crée commit│ (commits/abc123.json)
│   ├─ Vide stage │ (supprime staging.json)
│   └─ Update ref │ (refs.json: {"main": "abc123..."})
└─────────────────┘
```

#### Scénario : Switch de branche

```
État initial :
  - Branche courante : main
  - Fichier app.py : "Version 1"
  
┌──────────────────────────┐
│ branch switch dev        │
└──────────┬───────────────┘
           │
           v
┌──────────────────────────┐
│ 1. Lecture refs.json     │
│    dev → commit_id_dev   │
└──────────┬───────────────┘
           │
           v
┌──────────────────────────┐
│ 2. Update config.json    │
│    {"head": "dev"}       │
└──────────┬───────────────┘
           │
           v
┌──────────────────────────┐
│ 3. checkout_snapshot()   │
│    ├─ Lit commits/...json│
│    └─ Écrit fichiers     │ ← app.py devient "Version 2"
└──────────┬───────────────┘
           │
           v
┌──────────────────────────┐
│ 4. Prompt update         │
│    vcs(dev)>             │
└──────────────────────────┘

Résultat : 
  - HEAD → dev
  - app.py sur disque : "Version 2"
```

---

### 3. Algorithmes clés

#### Génération de hash

```python
def _compute_hash(self, content: str) -> str:
    """SHA-1 pour identifier de manière unique le contenu."""
    return hashlib.sha1(content.encode('utf-8')).hexdigest()
```

**Propriétés :**
- Déterministe : même contenu = même hash
- Collision quasi-impossible
- Utilisé pour : commit ID, file hash

#### Détection de conflits

```python
# Simplifié de branches.py
for filename, remote_data in src_files.items():
    if filename in curr_files:
        if remote_data['hash'] != curr_files[filename]['hash']:
            # CONFLIT : les deux branches ont modifié ce fichier
            conflict_detected = True
            resolved = resolve_conflict(filename, local, remote)
```

**Limitation :** Détection au niveau fichier complet, pas ligne par ligne.

---

## 💡 Scénarios d'usage

### Scénario 1 : Workflow linéaire (main seulement)

```bash
# Terminal
python main.py

# Dans le shell interactif
vcs(main)> init
vcs(main)> add README.md
vcs(main)> commit "Initial commit"
vcs(main)> add app.py
vcs(main)> commit "Add main application"
vcs(main)> log
```

**Résultat :**
```
--- HISTORIQUE ---
def456a - 2026-02-06 : Add main application
abc123d - 2026-02-06 : Initial commit
```

---

### Scénario 2 : Développement parallèle avec branches

```bash
vcs(main)> init
vcs(main)> add config.py
vcs(main)> commit "Base config"

# Créer branche feature
vcs(main)> branch create feature-api
vcs(main)> branch switch feature-api

# Développement sur feature
vcs(feature-api)> add api.py
vcs(feature-api)> commit "Implement REST API"

# Retour sur main pour voir l'état
vcs(feature-api)> branch switch main
# api.py disparaît du disque

# Fusion
vcs(main)> merge feature-api
# api.py réapparaît
```

**État du graph après merge :**
```
[def456a] --> [abc123d] <- feature-api
   └── Implement REST API
[abc123d] --> [None] <- main (HEAD)
   └── Base config
```

---

### Scénario 3 : Résolution de conflit

```bash
# Préparation
vcs(main)> init
vcs(main)> add settings.txt
vcs(main)> commit "Initial settings"

# Branche A
vcs(main)> branch create branch-a
vcs(main)> branch switch branch-a
# Modifier settings.txt → "MODE=PROD"
vcs(branch-a)> add settings.txt
vcs(branch-a)> commit "Set production mode"

# Branche B (depuis main)
vcs(branch-a)> branch switch main
vcs(main)> branch create branch-b
vcs(main)> branch switch branch-b
# Modifier settings.txt → "MODE=DEV"
vcs(branch-b)> add settings.txt
vcs(branch-b)> commit "Set development mode"

# Tentative de merge
vcs(branch-b)> branch switch main
vcs(main)> merge branch-a  # OK
vcs(main)> merge branch-b  # CONFLIT!
```

**Sortie interactive :**
```
⚔️ CONFLIT DÉTECTÉ sur : settings.txt

--- Résolution pour 'settings.txt' ---
🔵 LOCAL (Branche courante) :
MODE=PROD

🟠 REMOTE (Branche entrante) :
MODE=DEV
-----------------------------------
Choisir (L)ocal, (R)emote, ou (M)anuel ? [L/R/M] : M
-> Entrez le nouveau contenu (une ligne) :
> MODE=STAGING

✅ Tous les conflits ont été résolus.
💾 Écriture des fichiers fusionnés sur le disque...
⚠  Le système de fichiers a été mis à jour avec les résolutions.
👉 Veuillez maintenant faire : add . puis commit 'Merge result' pour finaliser.
```

---

## 🔧 Build et distribution

### Génération d'un exécutable standalone

Le fichier `build.py` automatise la création d'un exécutable avec PyInstaller.

#### Installation PyInstaller

```bash
pip install pyinstaller
```

#### Méthode 1 : Script automatisé

```bash
python build.py
```

**Configuration dans `build.py` :**
```python
OPTIONS = [
    "--onefile",           # Tout dans un seul fichier
    "--name=MonApplication",  # Nom de l'exécutable
    "--clean"              # Nettoie les builds précédents
]
ENTRY_POINT = "main.py"
```

#### Méthode 2 : Commande manuelle

```bash
pyinstaller --onefile --name minivcs main.py
```

#### Résultat

```
dist/
├── minivcs           # Linux/macOS
└── minivcs.exe       # Windows
```

#### Utilisation de l'exécutable

```bash
# Linux/macOS
./dist/minivcs
./dist/minivcs --demo

# Windows
dist\minivcs.exe
dist\minivcs.exe --demo
```

**Avantages :**
- Aucune dépendance Python requise pour l'utilisateur final
- Distribution simple (un seul fichier)
- Fonctionne sur Windows, macOS, Linux

**Inconvénient :**
- Taille ~10-15 MB (inclut l'interpréteur Python)

---

## ⚠️ Limitations techniques

### Limitations actuelles

| Limitation | Détail | Impact |
|-----------|--------|--------|
| **Pas de réseau** | Aucune commande `push`, `pull`, `fetch` | Usage local uniquement |
| **Pas de compression** | Objets stockés en JSON brut | Consommation disque élevée |
| **Merge fichier entier** | Pas de diff ligne par ligne | Conflits sur fichier complet |
| **Performance** | Lecture JSON à chaque opération | Lent sur gros dépôts (>1000 fichiers) |
| **Binaires** | Contenu stocké en UTF-8 | Erreur sur images/vidéos |
| **Pas de staging partiel** | Pas de `add -p` | Commit fichier complet |
| **Parent simplifié** | `parent: "main"` au lieu du commit ID | Graphe incomplet |

### Bugs connus

1. **Conflit résolution manuelle :** Mode manuel accepte une seule ligne (limitation `input()`)
2. **Untracked files :** Détection basique, ne gère pas les sous-répertoires
3. **Encodage :** Suppose tous les fichiers en UTF-8

---

## 🚀 Améliorations futures

### Court terme (faisable rapidement)

- [ ] **Compression zlib** : Compresser le contenu dans les commits
  ```python
  import zlib
  compressed = zlib.compress(content.encode())
  ```

- [ ] **Diff ligne par ligne** : Utiliser `difflib` pour merge intelligent
  ```python
  import difflib
  diff = difflib.unified_diff(local_lines, remote_lines)
  ```

- [ ] **Parent commit ID** : Remplacer `"parent": "main"` par le hash du commit parent réel

- [ ] **`.minivcsignore`** : Fichier de patterns à ignorer
  ```python
  import fnmatch
  if fnmatch.fnmatch(filename, pattern): continue
  ```

### Moyen terme

- [ ] Support des sous-répertoires
- [ ] Commande `reset --soft/--mixed/--hard`
- [ ] Graph visuel avec bibliothèque ASCII art
- [ ] Export/import de patches
- [ ] Tags (pointeurs fixes sur commits)

### Long terme

- [ ] Interface TUI avec `rich` ou `textual`
- [ ] Protocole réseau simple (HTTP)
- [ ] Format binaire optimisé (remplacer JSON)
- [ ] Support submodules

---

## 👥 Contribution

### Développé par Groupe 02

| Rôle | Module | Responsable |
|------|--------|-------------|
| **Core Engine** | `core.py` | Algorithmes de hashing, staging, commits |
| **Branch System** | `branches.py` | Logique de fusion, gestion pointeurs |
| **User Interface** | `cli.py` | Shell interactif, affichage coloré |
| **Orchestration** | `main.py`, `build.py` | Tests, démo, packaging |

### Workflow de développement

1. **Développement** : Chaque membre travaille sur une branche feature
2. **Code Review** : PR avec relecture avant merge
3. **Tests** : Validation via `--demo` avant merge dans `main`
4. **Documentation** : README synchronisé avec le code

### Comment contribuer

1. Fork le projet
2. Créer une branche : `git checkout -b feature/amazing-feature`
3. Commit : `git commit -m 'Add amazing feature'`
4. Push : `git push origin feature/amazing-feature`
5. Ouvrir une Pull Request

---

## 📚 Références techniques

### Concepts Git reproduits

- **Blob** : Stockage du contenu des fichiers (ici dans `files.content`)
- **Commit** : Snapshot avec métadonnées (message, date, parent)
- **Tree** : Représenté par le dictionnaire `files` dans le commit
- **DAG** : Graph acyclique dirigé des commits
- **HEAD** : Pointeur symbolique vers la branche courante
- **Refs** : Mapping nom_branche → commit_id

### Différences avec Git

| Git | Mini VCS |
|-----|----------|
| Objets compressés (zlib) | JSON brut |
| Hash des objets (contenu) | Hash du contenu + timestamp |
| Tree objects séparés | Dictionnaire `files` dans commit |
| Packfiles pour performance | Un fichier JSON par commit |
| Three-way merge | Two-way merge |
| Index binaire | `staging.json` |

### Ressources pour approfondir

- [Pro Git Book](https://git-scm.com/book/en/v2) – Chapitre 10 (Git Internals)
- [Git from the Bottom Up](https://jwiegley.github.io/git-from-the-bottom-up/)
- [Gitlet Project](https://sp21.datastructur.es/materials/proj/proj2/proj2) – Berkeley CS61B

---

## 📄 License

Ce projet est distribué sous licence MIT. Voir le fichier `LICENSE` pour plus de détails.



**Développé par Groupe 02 – Projet pédagogique de système de contrôle de version**

*"The best way to understand Git is to build Git"*
