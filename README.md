# Bot-Discord 🤖

![Python](https://img.shields.io/badge/Python-3.8%2B-blue?style=for-the-badge&logo=python&logoColor=white)
![Discord.py](https://img.shields.io/badge/Discord.py-2.0%2B-5865F2?style=for-the-badge&logo=discord&logoColor=white)
![Discloud](https://img.shields.io/badge/Discloud-Ready-orange?style=for-the-badge&logo=cloud&logoColor=white)
![Status](https://img.shields.io/badge/Status-Maintained-green?style=for-the-badge)

Ce projet est un bot Discord écrit en Python, conçu pour la gestion et le suivi des devoirs scolaires ou des tâches. Il dispose d'un système de rappel automatique et de nettoyage de la base de données, le tout hébergé facilement sur Discloud.

## ✨ Fonctionnalités

* **📅 Gestion des devoirs :** Ajout, consultation et suppression manuelle via des commandes Slash (`/`).
* **💾 Base de données Persistante :** Sauvegarde automatique dans un fichier local `devoirs.json`.
* **⏰ Rappels Intelligents :**
    * Envoie une notification automatique **7 jours avant** l'échéance.
    * Envoie une alerte "URGENT" **la veille** (J-1).
* **🧹 Nettoyage Automatique :** Le bot supprime tout seul les devoirs dont la date est passée (J+1) pour garder la liste propre.
* **☁️ Discloud Ready :** Pré-configuré pour un déploiement instantané.

## 📂 Structure du projet

* `mon_bot.py` : Le cœur du bot contenant la logique, les commandes et les boucles de vérification.
* `devoirs.json` : Base de données locale (créée automatiquement si absente).
* `requirements.txt` : Liste des dépendances (`discord.py`, `pytz`).
* `discloud.config` : Configuration pour l'hébergeur Discloud.

## 💻 Commandes Disponibles

| Commande | Description | Exemple |
| :--- | :--- | :--- |
| `/ajouter` | Ajoute un devoir. Format date : `JJ/MM/AAAA`. | `/ajouter 25/12/2023 Faire l'exercice de maths` |
| `/devoir` | Affiche la liste triée par date des devoirs en cours. | `/devoir` |
| `/supprimer`| Supprime un devoir manuellement selon son numéro dans la liste. | `/supprimer 1` |

## 🛠️ Installation et Lancement (Local)

Avant de commencer, assurez-vous d'avoir installé **Python 3.8+**.

1.  **Cloner le dépôt**
    ```bash
    git clone [https://github.com/Faonpingoin634/Bot-Discord.git](https://github.com/Faonpingoin634/Bot-Discord.git)
    cd Bot-Discord
    ```

2.  **Installer les dépendances**
    ```bash
    pip install -r requirements.txt
    ```

3.  **Configuration du Token**
    * Ouvrez `mon_bot.py`.
    * Remplacez la variable `TOKEN` par votre token de bot (disponible sur le [Discord Developer Portal](https://discord.com/developers/applications)).
    * ⚠️ **Important :** Si vous rendez ce code public, ne mettez pas le token en clair ! Utilisez des variables d'environnement.

4.  **Lancer le bot**
    ```bash
    python mon_bot.py
    ```

## ☁️ Hébergement (Discloud)

Ce bot est optimisé pour **Discloud**.

1.  Assurez-vous que le fichier `discloud.config` est présent.
2.  Dans le fichier `mon_bot.py`, il est recommandé d'utiliser `os.getenv("TOKEN")` et de configurer votre token dans l'onglet **ENV** de Discloud pour plus de sécurité.
3.  Uploadez le dossier (ou un fichier `.zip` contenant le dossier) sur votre dashboard Discloud.
4.  Le bot tournera 24/7, vérifiera les dates toutes les heures et nettoiera les anciens devoirs automatiquement.

## 🤝 Contribution

Les contributions sont les bienvenues !
1.  Forkez le projet.
2.  Créez une branche (`git checkout -b feature/AmazingFeature`).
3.  Committez vos changements (`git commit -m 'Add some AmazingFeature'`).
4.  Push sur la branche (`git push origin feature/AmazingFeature`).
5.  Ouvrez une Pull Request.