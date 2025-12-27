# Bot-Discord 🤖

Ce projet est un bot Discord écrit en Python, conçu principalement pour la gestion et le suivi des devoirs. Il utilise un système de stockage de données local via un fichier JSON et est pré-configuré pour un déploiement sur Discloud.

## ✨ Fonctionnalités

* **Gestion des devoirs** : Système permettant de stocker et consulter des devoirs (basé sur le fichier `devoirs.json`).
* **Base de données JSON** : Les données sont persistantes et stockées localement dans `devoirs.json`.
* **Déploiement Discloud** : Le projet inclut un fichier `discloud.config` pour un hébergement rapide.

## 📂 Structure du projet

* `mon_bot.py` : Le fichier principal contenant le code source et la logique du bot.
* `devoirs.json` : Fichier utilisé pour stocker la liste des devoirs/tâches.
* `requirements.txt` : Liste des dépendances Python nécessaires au fonctionnement du bot.
* `discloud.config` : Fichier de configuration pour l'hébergeur Discloud.

## 🛠️ Prérequis

Avant de commencer, assurez-vous d'avoir installé :
* [Python](https://www.python.org/downloads/) (version 3.8 ou supérieure)
* Un compte Discord et un bot créé sur le [Portail Développeur Discord](https://discord.com/developers/applications).

## 🚀 Installation et Lancement

1.  **Cloner le dépôt**
    ```bash
    git clone [https://github.com/Faonpingoin634/Bot-Discord.git](https://github.com/Faonpingoin634/Bot-Discord.git)
    cd Bot-Discord
    ```

2.  **Installer les dépendances**
    Installez les bibliothèques requises (comme `discord.py`) via pip :
    ```bash
    pip install -r requirements.txt
    ```

3.  **Configuration du Token**
    * Ouvrez le fichier `mon_bot.py`.
    * Insérez votre **Token de bot** à l'endroit indiqué (ou configurez une variable d'environnement pour plus de sécurité).
    * *Note : Ne partagez jamais votre token publiquement.*

4.  **Lancer le bot**
    ```bash
    python mon_bot.py
    ```

## ☁️ Hébergement (Discloud)

Ce bot est prêt à être hébergé sur **Discloud**. Le fichier `discloud.config` est déjà présent. Vous pouvez simplement uploader le dossier (ou le zip du dossier) sur votre dashboard Discloud pour mettre le bot en ligne 24/7.

## 🤝 Contribution

Les contributions sont les bienvenues ! Si vous souhaitez ajouter des fonctionnalités ou corriger des bugs :
1.  Forkez le projet.
2.  Créez une branche pour votre modification (`git checkout -b feature/AmazingFeature`).
3.  Committez vos changements (`git commit -m 'Add some AmazingFeature'`).
4.  Push sur la branche (`git push origin feature/AmazingFeature`).
5.  Ouvrez une Pull Request.

---
*Créé par [Faonpingoin634](https://github.com/Faonpingoin634)*
