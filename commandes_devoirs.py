"""Commandes slash de gestion des devoirs et boucle de rappels."""
import datetime
import logging

import discord
from discord import app_commands
from discord.ext import commands, tasks

import config
from stockage import DepotDevoirs, Devoir

log = logging.getLogger(__name__)

FORMAT_DATE_FR = "%d/%m/%Y"
LIMITE_MESSAGE = 2000


def aujourdhui() -> datetime.date:
    return datetime.datetime.now(config.FUSEAU).date()


def decouper_message(lignes: list[str], limite: int = LIMITE_MESSAGE) -> list[str]:
    """Regroupe les lignes en messages qui respectent la limite de caractères de Discord."""
    messages, courant = [], ""
    for ligne in lignes:
        if courant and len(courant) + len(ligne) + 1 > limite:
            messages.append(courant)
            courant = ""
        courant += ligne + "\n"
    if courant:
        messages.append(courant)
    return messages


class CommandesDevoirs(commands.Cog):
    def __init__(self, bot: commands.Bot, depot: DepotDevoirs, salon_rappels_id: int):
        self.bot = bot
        self.depot = depot
        self.salon_rappels_id = salon_rappels_id

    async def cog_load(self) -> None:
        self.verifier_dates.start()

    async def cog_unload(self) -> None:
        self.verifier_dates.cancel()

    # --- COMMANDES SLASH ---

    @app_commands.command(name="ajouter", description="Ajoute un nouveau devoir")
    @app_commands.describe(date="Format JJ/MM/AAAA", description="Description du devoir")
    async def ajouter(
        self,
        interaction: discord.Interaction,
        date: str,
        description: app_commands.Range[str, 1, 500],
    ):
        try:
            date_butoir = datetime.datetime.strptime(date, FORMAT_DATE_FR).date()
        except ValueError:
            await interaction.response.send_message("❌ Date invalide. Utilise : JJ/MM/AAAA", ephemeral=True)
            return

        if date_butoir < aujourdhui():
            await interaction.response.send_message(
                "⚠️ Tu essaies d'ajouter un devoir pour une date déjà passée !", ephemeral=True
            )
            return

        self.depot.ajouter(Devoir(date=date_butoir, desc=description, auteur=interaction.user.name))
        await interaction.response.send_message(f"✅ Devoir ajouté pour le **{date}** : {description}")

    @app_commands.command(name="devoir", description="Affiche la liste des devoirs")
    async def devoir(self, interaction: discord.Interaction):
        devoirs = self.depot.devoirs
        if not devoirs:
            await interaction.response.send_message("🎉 Aucun devoir !")
            return

        lignes = ["**📅 Liste des devoirs :**"] + [
            f"`{i}.` **{d.date.strftime(FORMAT_DATE_FR)}** : {d.desc} (par {d.auteur})"
            for i, d in enumerate(devoirs, 1)
        ]
        premier, *suite = decouper_message(lignes)
        await interaction.response.send_message(premier)
        for message in suite:
            await interaction.followup.send(message)

    @app_commands.command(name="supprimer", description="Supprime un devoir par son numéro")
    @app_commands.describe(numero="Le numéro affiché dans la liste /devoir")
    async def supprimer(self, interaction: discord.Interaction, numero: int):
        devoir = self.depot.supprimer(numero)
        if devoir is None:
            await interaction.response.send_message(
                f"❌ Numéro {numero} invalide. Tape `/devoir` pour vérifier.", ephemeral=True
            )
            return

        await interaction.response.send_message(
            f"🗑️ Devoir supprimé : **{devoir.desc}** (était prévu pour le {devoir.date.strftime(FORMAT_DATE_FR)})"
        )

    # --- RAPPELS AUTOMATIQUES ---

    @tasks.loop(hours=1)
    async def verifier_dates(self):
        date_du_jour = aujourdhui()

        for devoir in self.depot.retirer_passes(date_du_jour):
            log.info("Suppression automatique du devoir : %s (date : %s)", devoir.desc, devoir.date)

        salon = self.bot.get_channel(self.salon_rappels_id)
        if salon is None:
            log.warning("Salon de rappels %s introuvable.", self.salon_rappels_id)
            return

        changement = False
        for devoir in self.depot.devoirs:
            delta = (devoir.date - date_du_jour).days
            try:
                if delta == 7 and not devoir.rappel_7j_fait:
                    await salon.send(
                        f"📢 **RAPPEL (J-7)** : '{devoir.desc}' pour le {devoir.date.strftime('%d/%m')}"
                    )
                    devoir.rappel_7j_fait = True
                    changement = True
                elif delta == 1 and not devoir.rappel_1j_fait:
                    await salon.send(f"🚨 **URGENT (DEMAIN)** : '{devoir.desc}' !")
                    devoir.rappel_1j_fait = True
                    changement = True
            except discord.HTTPException:
                # Le rappel sera retenté à la prochaine vérification.
                log.exception("Échec de l'envoi du rappel pour : %s", devoir.desc)

        if changement:
            self.depot.sauvegarder()

    @verifier_dates.before_loop
    async def avant_verification(self):
        await self.bot.wait_until_ready()
