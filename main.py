# main.py
import sys
import os
import argparse
from core import VersionControl
from branches import BranchManager
from cli import EnhancedCLI


def scenario_demo():
    """
    Scénario automatisé pour démontrer les fonctionnalités sans
    taper de commandes.
    """
    print("--- Démarrage du scénario de démo ---\n")

    # 0. Nettoyage (pour la démo uniquement)
    import shutil
    if os.path.exists('.mini_vcs'):
        shutil.rmtree('.mini_vcs')
    if os.path.exists('test.txt'):
        os.remove('test.txt')

    vcs = VersionControl('.')
    bm = BranchManager(vcs)

    print("1) Initialisation du dépôt")
    vcs.init_repo()

    print("\n2) Création d'un fichier 'test.txt' (v1)")
    with open('test.txt', 'w') as f:
        f.write("Contenu Version 1\n")

    print("3) Add & Commit")
    vcs.add(['test.txt'])
    cid1 = vcs.commit("Premier commit: V1")
    # Important : lier la branche au commit
    bm.update_current_branch_commit(cid1)

    print("\n4) Création de la branche 'dev' et switch")
    bm.create_branch('dev')
    bm.switch_branch('dev')

    print("\n5) Modification fichier dans 'dev' (v2)")
    with open('test.txt', 'w') as f:
        f.write("Contenu Version 2 (Dev)\n")
    vcs.add(['test.txt'])
    cid2 = vcs.commit("Commit sur dev: V2")
    bm.update_current_branch_commit(cid2)

    print("\n6) Retour sur main et verification du contenu")
    bm.switch_branch('main')
    with open('test.txt', 'r') as f:
        content = f.read().strip()
        print(f"   [Main] Contenu fichier : {content}")

    print("\n7) Merge dev -> main")
    bm.merge_branch('dev')
    with open('test.txt', 'r') as f:
        content = f.read().strip()
        print(f"   [Main après Merge] Contenu fichier : {content}")

    print("\n--- Fin du scénario ---")


def main():
    parser = argparse.ArgumentParser(
        description="Mini VCS - Outil pédagogique"
    )
    parser.add_argument(
        '--demo',
        action='store_true',
        help="Lancer le scénario de démonstration"
    )
    args = parser.parse_args()

    if args.demo:
        scenario_demo()
    else:
        # Mode interactif par défaut
        try:
            cli = EnhancedCLI()
            cli.cmdloop()
        except KeyboardInterrupt:
            print("\nInterruption clavier. Sortie.")
            sys.exit(0)


if __name__ == "__main__":
    main()
