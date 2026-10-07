"""Modèle de devoir et persistance dans un fichier JSON."""
from __future__ import annotations

import datetime
import json
import logging
import os
from dataclasses import asdict, dataclass
from pathlib import Path

log = logging.getLogger(__name__)

FORMAT_DATE_JSON = "%Y-%m-%d"


@dataclass
class Devoir:
    date: datetime.date
    desc: str
    auteur: str
    rappel_7j_fait: bool = False
    rappel_1j_fait: bool = False

    def vers_json(self) -> dict:
        data = asdict(self)
        data["date"] = self.date.strftime(FORMAT_DATE_JSON)
        return data

    @classmethod
    def depuis_json(cls, data: dict) -> Devoir:
        return cls(
            date=datetime.datetime.strptime(data["date"], FORMAT_DATE_JSON).date(),
            desc=data["desc"],
            auteur=data["auteur"],
            rappel_7j_fait=data.get("rappel_7j_fait", False),
            rappel_1j_fait=data.get("rappel_1j_fait", False),
        )


class DepotDevoirs:
    """Liste des devoirs, toujours triée par date et sauvegardée à chaque modification."""

    def __init__(self, chemin: Path):
        self.chemin = chemin
        self._devoirs: list[Devoir] = []

    @property
    def devoirs(self) -> list[Devoir]:
        return list(self._devoirs)

    def charger(self) -> None:
        if not self.chemin.exists():
            log.info("Aucun fichier de sauvegarde, création d'une nouvelle liste.")
            self._devoirs = []
            return

        try:
            data = json.loads(self.chemin.read_text(encoding="utf-8"))
            self._devoirs = sorted((Devoir.depuis_json(d) for d in data), key=lambda d: d.date)
        except (json.JSONDecodeError, KeyError, ValueError, TypeError):
            # On met le fichier de côté plutôt que de l'écraser à la prochaine sauvegarde.
            sauvegarde = self.chemin.with_suffix(".corrompu.json")
            self.chemin.replace(sauvegarde)
            log.error("Fichier de sauvegarde illisible, déplacé vers %s.", sauvegarde.name)
            self._devoirs = []
            return

        log.info("%d devoirs chargés.", len(self._devoirs))

    def sauvegarder(self) -> None:
        self._devoirs.sort(key=lambda d: d.date)
        contenu = json.dumps([d.vers_json() for d in self._devoirs], indent=4, ensure_ascii=False)
        # Écriture atomique : un crash pendant l'écriture ne corrompt pas le fichier existant.
        temporaire = self.chemin.with_suffix(".tmp")
        temporaire.write_text(contenu, encoding="utf-8")
        os.replace(temporaire, self.chemin)

    def ajouter(self, devoir: Devoir) -> None:
        self._devoirs.append(devoir)
        self.sauvegarder()

    def supprimer(self, numero: int) -> Devoir | None:
        """Supprime le devoir n°`numero` (à partir de 1, dans l'ordre affiché par /devoir)."""
        if not 0 < numero <= len(self._devoirs):
            return None
        devoir = self._devoirs.pop(numero - 1)
        self.sauvegarder()
        return devoir

    def retirer_passes(self, aujourdhui: datetime.date) -> list[Devoir]:
        """Retire les devoirs dont la date est passée et les renvoie."""
        passes = [d for d in self._devoirs if d.date < aujourdhui]
        if passes:
            self._devoirs = [d for d in self._devoirs if d.date >= aujourdhui]
            self.sauvegarder()
        return passes
