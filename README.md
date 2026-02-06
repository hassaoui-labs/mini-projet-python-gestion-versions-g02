Mini VCS — Système de gestion de versions en Python

Mini VCS est une implémentation pédagogique d’un système de contrôle de version inspiré de Git. Le projet permet de comprendre concrètement le fonctionnement des commits, branches et fusions en manipulant un dépôt local via une interface en ligne de commande.

Objectif du projet

Ce projet a pour but de :

* Illustrer les mécanismes internes d’un VCS

* Manipuler les concepts de commit, branch et merge

* Visualiser l’historique des versions d’un projet

* Comprendre le rôle du HEAD et du staging area

Fonctionnalités principales

1. Initialisation d’un dépôt local

2. Ajout de fichiers dans une zone de staging

3. Création de commits identifiés par hash

4. Création et changement de branches.
5. Fusion de branches avec détection de conflits
6. Affichage de l’historique et du graphe des versions


Installation

    1. Cloner le projet::             git clone <url-du-repo>    cd mini-vcs       
    2. Installer les dépendances::    pip install colorama
    3. Lancer le programme:          python main.py

Utilisation rapide

Exemple de workflow: 
                    
                    init
                    add fichier.py
                    commit "Premier commit"
                    branch create dev
                    branch switch dev
                    add fichier.py
                    commit "Modification"
                    branch switch main
                    merge dev
                    log


Structure du projet

          mini-vcs/
          │── main.py # Point d’entrée                             # Point d’entrée 
          │── core.py # Gestion des commits et du staging          # Gestion des commits et du staging
          │── branches.py # Gestion des branches et merges         # Gestion des branches et merges
          │── cli.py # Interface utilisateur                       # Interface utilisateur
          │── build.py # Création exécutable                       # Création exécutable
          │── .mini_vcs/ # Données du dépôt (créé après init)      # Données du dépôt (créé après init)

Documentation technique

La documentation détaillée expliquant l’architecture interne et les algorithmes est disponible dans le dossier :docs/

        Auteurs
              1. LAMAMRA Soraya
              2. BRAHAMI Lyes
              3. Bessaoudi Sabrina
              4. AMIR Ouassila
        






