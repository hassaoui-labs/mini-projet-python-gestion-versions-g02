# cli.py
# # !/usr/bin/env python3
import cmd
import os
import json

from colorama import init, Fore, Style

# Gestion des couleurs (Cross-platform safe)
try:
    init(autoreset=True)
except ImportError:
    class Dummy:
        def __getattr__(self, _):
            return ''
    Fore = Dummy()
    Style = Dummy()

from core import VersionControl
from branches import BranchManager

# Important pour Windows
init(autoreset=False)


class EnhancedCLI(cmd.Cmd):

    intro = (
        f"{Fore.CYAN}╔══════════════════════════════════════╗\n"
        f"║     Mini VCS - Interface Avancée      ║\n"
        f"║     Version 2.0 (Refactored)          ║\n"
        f"╚══════════════════════════════════════╝{Style.RESET_ALL}\n"
        "Tapez 'help' pour la liste des commandes.\n"
    )

    def __init__(self):
        super().__init__()
        self.current_branch = "main"
        self.vcs = VersionControl()
        self.bm = BranchManager(self.vcs)
        self.update_prompt()  # Initialisation au démarrage

    def update_prompt(self):
        """Récupère la branche actuelle et met à jour le prompt."""
        current_branch = self.vcs._get_head()
        # On définit le format : vcs(nom_branche)>
        prompt = (
            f'{Fore.BLUE}vcs({Fore.GREEN}{current_branch}'
            f'{Fore.BLUE})>{Style.RESET_ALL} '
        )
        self.prompt = prompt

    def do_help(self, _arg):
        """Affiche le guide visuel des commandes et le flux de travail."""
        hline = (
            f"\n{Fore.CYAN}╔═════════════════════════════════════════════════════════╗"
        )
        print(hline)
        title = (
            "║ SCEMA DU FLUX DE TRAVAIL (VCS WORKFLOW)                      ║"
        )
        print(title)
        bline = (
            f"╚══════════════════════════════════════════════════════════════╝"
            f"{Style.RESET_ALL}"
        )
        print(bline)

        workflow = """
        [ Répertoire de Travail ] ----> ( add ) ----> [ Zone de Staging ]
               (Fichiers réels)                         (staging.json)
                                                              |
                                                              v
        [ Graph de Commits (DAG) ] <--- ( commit ) <-----------+
              (Dépôt /commits)
        """
        print(workflow)

        print(f"{Fore.YELLOW}COMMANDES DISPONIBLES :{Style.RESET_ALL}")
        table_data = [
            ["init", "Initialise le dépôt et crée la structure .mini_vcs"],
            [
                "add <fich>",
                "Prépare un fichier pour le prochain snapshot (Staging)",
            ],
            [
                "commit <msg>",
                "Enregistre définitivement l'état du staging dans le DAG",
            ],
            [
                "status",
                "Compare le disque, le staging et le dernier commit",
            ],
            ["branch list", "Affiche toutes les branches existantes"],
            [
                "branch create",
                "Crée un nouveau pointeur (branche) sur le commit actuel",
            ],
            [
                "branch switch",
                "Déplace HEAD et restaure les fichiers du commit cible",
            ],
            [
                "merge <nom>",
                "Fusionne deux branches et résout les conflits",
            ],
            [
                "graph",
                "Affiche la structure Directed Acyclic Graph des commits",
            ],
            [
                "log",
                "Affiche la liste chronologique des messages de commit",
            ],
        ]

        for command, desc in table_data:
            print(
                f"  {Fore.GREEN}{command:<15}{Style.RESET_ALL} : {desc}"
            )
        print("\n")

    def do_graph(self, arg):
        """Visualise le DAG et indique la position actuelle."""
        if not os.path.exists(self.vcs.commits_dir):
            print("Le graph est vide.")
            return

        msg = f"\n{Fore.MAGENTA}--- REPRÉSENTATION DU GRAPH (DAG) ---"
        print(f"{msg}{Style.RESET_ALL}")

        # Chargement des commits depuis le répertoire
        commits = {}
        for fname in os.listdir(self.vcs.commits_dir):
            if fname.endswith('.json'):
                path = os.path.join(self.vcs.commits_dir, fname)
                with open(path, 'r') as f:
                    data = json.load(f)
                    commits[data['id']] = data

        refs = self.bm._load_refs()
        head_branch = self.vcs._get_head()

        for cid, data in commits.items():
            short_id = cid[:7]
            parent = data.get('parent', "None")
            short_parent = (
                parent[:7] if len(parent) > 20 else parent
            )

            # Détection des branches sur ce commit
            pointers = [
                name for name, ref_id in refs.items() if ref_id == cid
            ]

            suffix = ""
            if pointers:
                # Si branche actuelle parmi les pointeurs, ajoute (HEAD)
                decorated_pointers = []
                for p in pointers:
                    if p == head_branch:
                        deco = (
                            f"{Fore.CYAN}{p} (HEAD){Style.RESET_ALL}"
                        )
                        decorated_pointers.append(deco)
                    else:
                        decorated_pointers.append(
                            f"{Fore.YELLOW}{p}{Style.RESET_ALL}"
                        )
                suffix = " <- " + ", ".join(decorated_pointers)

            output = f"[{short_id}] --points-to--> [{short_parent}]"
            print(f"{output}{suffix}")
            msg_line = f"   └── {Fore.WHITE}{data['message']}"
            print(f"{msg_line}{Style.RESET_ALL}")

    def do_init(self, arg):
        """Initialiser un nouveau dépôt VCS dans le dossier courant."""
        self.vcs.init_repo()

    def do_add(self, _arg):
        """Ajouter des fichiers au staging : add <file1> [file2]..."""
        files = _arg.split()
        if not files:
            print(f"{Fore.YELLOW}Usage: add file1 file2 ...{Style.RESET_ALL}")
            return
        try:
            self.vcs.add(files)
        except Exception as e:
            print(f"{Fore.RED}Erreur: {e}{Style.RESET_ALL}")

    def do_commit(self, arg):
        """Enregistrer modifications : commit "Message du commit" """
        if not arg:
            usage = (
                f'{Fore.YELLOW}Usage: commit "Mon message"'
                f'{Style.RESET_ALL}'
            )
            print(usage)
            return

        msg = arg.strip('"\'')
        try:
            # 1. Créer le commit (Blob)
            commit_id = self.vcs.commit(msg)

            # 2. Mettre à jour branche courante pour pointer
            if commit_id:
                self.bm.update_current_branch_commit(commit_id)
                success = (
                    f"{Fore.GREEN}Commit {commit_id[:7]} "
                    "enregistré avec succès."
                    f"{Style.RESET_ALL}"
                )
                print(success)
        except Exception as e:
            error = (
                f"{Fore.RED}Erreur lors du commit: {e}"
                f"{Style.RESET_ALL}"
            )
            print(error)

    def do_status(self, _arg):
        """Afficher état du dépôt (fichiers, staging, branche)."""
        try:
            data = self.vcs.get_status_data()
            head = data['head']

            print(f"\n{Fore.CYAN}--- STATUS ---{Style.RESET_ALL}")
            print(
                f"Branche courante : "
                f"{Fore.MAGENTA}{head}{Style.RESET_ALL}"
            )

            if data['staged']:
                staged_msg = (
                    f"\n{Fore.GREEN}Fichiers dans le staging "
                    f"(prêts à commit) :{Style.RESET_ALL}"
                )
                print(staged_msg)
                for f in data['staged']:
                    print(f"  + {f}")
            else:
                print(f"\n{Fore.YELLOW}Staging vide.{Style.RESET_ALL}")

            if data['untracked']:
                untrack_msg = (
                    f"\n{Fore.RED}Fichiers non suivis (Untracked) :"
                    f"{Style.RESET_ALL}"
                )
                print(untrack_msg)
                for f in data['untracked']:
                    print(f"  ? {f}")
            print()

        except Exception as e:
            error = (
                f"{Fore.RED}Erreur status (avez-vous fait 'init' ?) : "
                f"{e}{Style.RESET_ALL}"
            )
            print(error)

    def do_branch(self, arg):
        """Commandes: branch list | create <nom> | switch <nom>"""
        args = arg.split()
        if not args:
            self.do_help('branch')
            return

        branch_cmd = args[0]
        try:
            if branch_cmd == 'create' and len(args) > 1:
                self.bm.create_branch(args[1])
            elif branch_cmd == 'switch' and len(args) > 1:
                self.bm.switch_branch(args[1])
                self.update_prompt()
            elif branch_cmd == 'list':
                refs = self.bm._load_refs()
                curr = self.vcs._get_head()
                print(f"\n{Fore.CYAN}Branches :{Style.RESET_ALL}")
                for b, cid in refs.items():
                    prefix = "*" if b == curr else " "
                    cid_str = cid[:7] if cid else 'Empty'
                    print(f" {prefix} {b} \t({cid_str})")
                print()
            else:
                print("Usage: branch [create|switch|list] <args>")
        except Exception as e:
            error = f"{Fore.RED}Erreur branche: {e}{Style.RESET_ALL}"
            print(error)

    def do_merge(self, _arg):
        """Fusionner une branche : merge <nom_branche>"""
        if not _arg:
            print("Usage: merge <nom_branche>")
            return
        try:
            self.bm.merge_branch(_arg)
        except Exception as e:
            print(f"{Fore.RED}Erreur merge: {e}{Style.RESET_ALL}")

    def do_log(self, _arg):
        """Affiche l'historique simple des commits."""
        # Simple lecture des fichiers json dans commits_dir
        if not os.path.exists(self.vcs.commits_dir):
            print("Aucun historique.")
            return

        print(f"\n{Fore.CYAN}--- HISTORIQUE ---{Style.RESET_ALL}")
        for fname in os.listdir(self.vcs.commits_dir):
            if fname.endswith('.json'):
                path = os.path.join(self.vcs.commits_dir, fname)
                with open(path, 'r') as f:
                    c = json.load(f)
                    commit_line = (
                        f"{Fore.YELLOW}{c['id'][:7]}"
                        f"{Style.RESET_ALL} - {c['date']} : "
                        f"{c['message']}"
                    )
                    print(commit_line)
        print()

    def do_exit(self, _arg):
        """Quitter le programme."""
        print("Au revoir!")
        return True

    # Raccourcis
    do_EOF = do_exit
    do_q = do_exit
