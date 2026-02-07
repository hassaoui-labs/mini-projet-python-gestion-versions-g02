# core.py
import os
import json
import hashlib
from datetime import datetime
from typing import Dict, List, Optional


class VersionControl:
    """
    Cœur du système de gestion de versions.
    Gère le stockage des objets (commits, blobs) et l'état du
    répertoire de travail.
    """

    def __init__(self, repo_path: str = '.'):
        self.repo_path = os.path.abspath(repo_path)
        self.vcs_dir = os.path.join(self.repo_path, '.mini_vcs')
        self.staging_file = os.path.join(self.vcs_dir, 'staging.json')
        self.commits_dir = os.path.join(self.vcs_dir, 'commits')
        self.config_file = os.path.join(self.vcs_dir, 'config.json')

    def init_repo(self):
        """Initialise la structure du dépôt (.mini_vcs)."""
        if os.path.exists(self.vcs_dir):
            print("⚠ Dépôt déjà initialisé.")
            return

        os.makedirs(self.vcs_dir, exist_ok=True)
        os.makedirs(self.commits_dir, exist_ok=True)

        # Configuration initiale : HEAD pointe vers la branche 'main'
        self._save_json(self.config_file, {'head': 'main'})
        print(f"✅ Dépôt initialisé dans {self.vcs_dir}")

    def add(self, files: List[str]):
        """Ajoute des fichiers à l'index (staging area)."""
        if not os.path.exists(self.vcs_dir):
            raise RuntimeError("Dépôt non initialisé. Lancez 'init' d'abord.")

        current_staging = self._load_json(self.staging_file)

        for filename in files:
            path = os.path.join(self.repo_path, filename)
            if os.path.exists(path):
                with open(path, 'r', encoding='utf-8') as f:
                    content = f.read()
                # On stocke le contenu et son hash (SHA-1)
                file_hash = self._compute_hash(content)
                current_staging[filename] = {
                    'content': content,
                    'hash': file_hash,
                    'added_at': datetime.now().isoformat()
                }
            else:
                print(f"⚠ Fichier introuvable : {filename}")

        self._save_json(self.staging_file, current_staging)
        print(f"✅ {len(files)} fichier(s) mis à jour dans le staging.")

    def commit(self, msg: str) -> Optional[str]:
        """Crée un commit (snapshot) à partir du staging."""
        current_staging = self._load_json(self.staging_file)
        if not current_staging:
            print("❌ Rien à commiter (staging vide).")
            return None

        # Création de l'objet commit
        commit_id = self._compute_hash(msg + datetime.now().isoformat())
        head_branch = self._get_head()

        # Note: Dans un vrai git, le parent est le hash du commit précédent.
        # Ici pour simplifier, on stockera la référence dans branches.py,
        # mais core doit connaître le parent direct s'il existe.
        # Pour ce mini-projet, 'parent' est géré via les refs externes
        # ou simplement lié au HEAD courant.

        commit_data = {
            'id': commit_id,
            'message': msg,
            'date': datetime.now().isoformat(),
            'files': current_staging,  # Snapshot complet des fichiers
            'parent': head_branch  # Simplification pédagogique
        }

        # Sauvegarde du commit
        commit_path = os.path.join(self.commits_dir, f"{commit_id}.json")
        self._save_json(commit_path, commit_data)

        # Nettoyage du staging après commit
        os.remove(self.staging_file)

        # Le HEAD est mis à jour par BranchManager, mais core renvoie l'ID
        return commit_id

    def checkout_snapshot(self, commit_id: str):
        """
        Restaure les fichiers de travail à l'état d'un commit spécifique.
        C'est ce qui permet de 'voyager dans le temps' ou changer de branche.
        """
        commit_path = os.path.join(self.commits_dir, f"{commit_id}.json")
        if not os.path.exists(commit_path):
            msg = (f"⚠ Commit {commit_id} introuvable "
                   "(peut-être un nom de branche vide ?)")
            print(msg)
            return

        commit_data = self._load_json(commit_path)
        files_snapshot = commit_data.get('files', {})

        print(f"🔄 Restauration des fichiers du commit {commit_id[:7]}...")
        for filename, data in files_snapshot.items():
            full_path = os.path.join(self.repo_path, filename)
            with open(full_path, 'w', encoding='utf-8') as f:
                f.write(data['content'])
        print("✅ Espace de travail mis à jour.")

    def get_status_data(self) -> Dict:
        """Retourne les données brutes du status pour affichage."""
        return {
            'staged': list(self._load_json(self.staging_file).keys()),
            'untracked': self._get_untracked_files(),
            'head': self._get_head()
        }

    # --- Méthodes utilitaires internes (Helpers) ---

    def _compute_hash(self, content: str) -> str:
        """Génère une signature unique (SHA-1) pour le contenu."""
        return hashlib.sha1(content.encode('utf-8')).hexdigest()

    def _get_untracked_files(self) -> List[str]:
        """Liste les fichiers présents mais non suivis par le VCS."""
        if not os.path.exists(self.repo_path):
            return []
        ignored = {'.mini_vcs', '__pycache__', '.git', '.DS_Store'}
        files = []
        for f in os.listdir(self.repo_path):
            if (f not in ignored and not f.startswith('.')
                    and os.path.isfile(f)):
                files.append(f)
        return files

    def _load_json(self, path: str) -> Dict:
        if os.path.exists(path):
            try:
                with open(path, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except json.JSONDecodeError:
                return {}
        return {}

    def _save_json(self, path: str, data: Dict):
        with open(path, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2)

    def _get_head(self) -> str:
        """Récupère le nom de la branche courante (HEAD)."""
        config = self._load_json(self.config_file)
        return config.get('head', 'main')

    def _update_head_ref(self, branch_name: str):
        """Met à jour le fichier config pour pointer vers une nouvelle
        branche."""
        config = self._load_json(self.config_file)
        config['head'] = branch_name
        self._save_json(self.config_file, config)
