"""Configuration du bot, lue depuis les variables d'environnement (ou un fichier .env)."""
import os
from pathlib import Path

import pytz
from dotenv import load_dotenv

DOSSIER = Path(__file__).resolve().parent
load_dotenv(DOSSIER / ".env")


def _variable(nom: str) -> str:
    valeur = os.getenv(nom)
    if not valeur:
        raise RuntimeError(f"Variable d'environnement manquante : {nom} (voir .env.example)")
    return valeur


def _variable_entiere(nom: str) -> int:
    valeur = _variable(nom)
    try:
        return int(valeur)
    except ValueError:
        raise RuntimeError(f"{nom} doit être un identifiant numérique, reçu : {valeur!r}") from None


TOKEN = _variable("TOKEN")
SERVER_ID = _variable_entiere("SERVER_ID")
CHANNEL_ID = _variable_entiere("CHANNEL_ID")

FICHIER_SAUVEGARDE = DOSSIER / "devoirs.json"
FUSEAU = pytz.timezone("Europe/Paris")
