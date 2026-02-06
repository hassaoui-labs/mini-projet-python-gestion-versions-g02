# branches.py
import json
import os
from core import VersionControl


class BranchManager:
    """
    Gestionnaire de branches.
    S'occupe des références (refs.json) qui lient un nom de
    branche à un Commit ID.
    """

    def __init__(self, vcs: VersionControl):
        self.vcs = vcs
        self.refs_path = os.path.join(self.vcs.vcs_dir, 'refs.json')

    def _load_refs(self) -> dict:
        if os.path.exists(self.refs_path):
            with open(self.refs_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        return {}

    def _save_refs(self, refs: dict):
        os.makedirs(self.vcs.vcs_dir, exist_ok=True)
        with open(self.refs_path, 'w', encoding='utf-8') as f:
            json.dump(refs, f, indent=2)

    def update_current_branch_commit(self, commit_id: str):
        """Appelé après un commit pour faire avancer la branche
        courante."""
        refs = self._load_refs()
        current_branch = self.vcs._get_head()
        refs[current_branch] = commit_id
        self._save_refs(refs)
        msg = f"🌲 Branche '{current_branch}' pointe maintenant vers "
        print(msg + f"{commit_id[:7]}")

    def create_branch(self, name: str):
        """Crée une nouvelle branche pointant vers le commit
        courant."""
        refs = self._load_refs()
        if name in refs:
            print(f"❌ La branche '{name}' existe déjà.")
            return

        # On récupère le commit ID de la branche courante
        current_head_branch = self.vcs._get_head()
        current_commit_id = refs.get(current_head_branch)

        if not current_commit_id:
            msg = "⚠ Impossible de créer une branche : "
            print(msg + "aucun commit initial.")
            return

        refs[name] = current_commit_id
        self._save_refs(refs)
        msg = f"✅ Branche '{name}' créée à partir de "
        print(msg + f"{current_head_branch} ({current_commit_id[:7]})")

    def switch_branch(self, name: str):
        """Change de branche et met à jour les fichiers de
        travail."""
        refs = self._load_refs()
        if name not in refs:
            raise ValueError(f"Branche '{name}' inexistante")

        target_commit_id = refs[name]

        # 1. Mettre à jour HEAD dans config
        self.vcs._update_head_ref(name)

        # 2. Restaurer les fichiers (Checkout)
        # C'est l'étape cruciale pour voir les fichiers changer !
        self.vcs.checkout_snapshot(target_commit_id)

        print(f"✅ Switch vers branche '{name}'")
        return name

    def merge_branch(self, source_branch: str):
        """
        Fusionne la branche source dans la branche courante avec
        gestion de conflits.
        """
        refs = self._load_refs()
        if source_branch not in refs:
            raise ValueError(f"Branche source '{source_branch}' inexistante")

        current_branch = self.vcs._get_head()
        source_commit_id = refs[source_branch]
        current_commit_id = refs.get(current_branch)

        # Cas 1 : À jour
        if source_commit_id == current_commit_id:
            print("Already up to date.")
            return

        # Chargement des données des deux commits
        # Note: On suppose ici que les commits existent.
        # Gestion d'erreur simplifiée.
        src_path = os.path.join(
            self.vcs.commits_dir, f"{source_commit_id}.json"
        )
        curr_path = os.path.join(
            self.vcs.commits_dir, f"{current_commit_id}.json"
        )
        src_commit = self.vcs._load_json(src_path)
        curr_commit = self.vcs._load_json(curr_path)

        src_files = src_commit.get('files', {})
        curr_files = curr_commit.get('files', {})

        print(f"🔀 Début du merge : {source_branch} -> {current_branch}")

        # Détection des conflits et préparation du nouvel état des fichiers
        final_files_state = curr_files.copy()
        conflict_detected = False

        # On parcourt les fichiers de la branche source
        for filename, data in src_files.items():
            # Si le fichier existe dans la branche courante
            if filename in curr_files:
                # Si le hash est différent, il y a un changement de contenu
                if data['hash'] != curr_files[filename]['hash']:
                    print(f"⚔️  CONFLIT DÉTECTÉ sur : {filename}")
                    conflict_detected = True
                    # Appel au résolveur interactif
                    resolved_content = self.resolve_conflict(
                        filename, curr_files[filename], data
                    )

                    # Mise à jour avec le contenu résolu
                    final_files_state[filename] = {
                        'content': resolved_content,
                        'hash': self.vcs._compute_hash(
                            resolved_content
                        )  # Recalcul du hash
                    }
            else:
                # Si le fichier est nouveau dans la source,
                # on l'ajoute simplement
                msg = "📄 Nouveau fichier ajouté par le merge : "
                print(msg + filename)
                final_files_state[filename] = data

        if conflict_detected:
            print("\n✅ Tous les conflits ont été résolus.")
        else:
            print("✨ Fusion automatique réussie (Fast-Forward/Auto-merge).")

        # APPLICATION DU MERGE SUR LE DISQUE
        # Dans un vrai Git, le merge modifie le Working Directory et l'Index,
        # puis demande un commit. Nous allons simuler cela.

        print("💾 Écriture des fichiers fusionnés sur le disque...")
        for filename, data in final_files_state.items():
            full_path = os.path.join(self.vcs.repo_path, filename)
            with open(full_path, 'w', encoding='utf-8') as f:
                f.write(data['content'])

        # Mise à jour de la référence (HEAD avance)
        # Note pédagogique : Normalement, un merge crée un NOUVEAU
        # commit de fusion. Ici, pour simplifier, on déplace le
        # pointeur sur le commit source SI pas de conflit, sinon on
        # laisse l'utilisateur faire un nouveau commit.

        if not conflict_detected:
            # Fast-forward simple
            refs[current_branch] = source_commit_id
            self._save_refs(refs)
            msg = f"🚀 Branche '{current_branch}' avancée vers "
            print(msg + f"{source_commit_id[:7]}.")
        else:
            print("⚠  Le système de fichiers a été mis à jour avec")
            print("les résolutions.")
            print("👉 Veuillez maintenant faire : add . puis commit")
            print("'Merge result' pour finaliser.")

    def resolve_conflict(self, filename: str, local_data: dict,
                         remote_data: dict) -> str:
        """
        Outil interactif de résolution de conflits.
        Retourne le contenu final choisi par l'utilisateur.
        """
        content_local = local_data['content']
        content_remote = remote_data['content']

        print(f"\n--- Résolution pour '{filename}' ---")
        print(f"🔵 LOCAL (Branche courante) :\n{content_local}")
        print(f"🟠 REMOTE (Branche entrante) :\n{content_remote}")
        print("-----------------------------------")

        while True:
            prompt = ("Choisir (L)ocal, (R)emote, ou (M)anuel ? "
                      "[L/R/M] : ")
            choice = input(prompt).strip().upper()

            if choice == 'L':
                print("-> Conservation de la version LOCALE.")
                return content_local

            elif choice == 'R':
                print("-> Acceptation de la version REMOTE.")
                return content_remote

            elif choice == 'M':
                print("-> Entrez le nouveau contenu (une ligne) :")
                new_content = input("> ")
                # Pour un projet simple, on gère le contenu ligne
                # à ligne ou concaténé. Si vous voulez gérer
                # plusieurs lignes, c'est plus complexe en
                # `input()` simple
                return new_content + "\n"

            else:
                print("❌ Choix invalide. Réessayez.")
