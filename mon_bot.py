"""Point d'entrée du bot de gestion des devoirs."""
import logging

import discord
from discord.ext import commands

import config
from commandes_devoirs import CommandesDevoirs
from stockage import DepotDevoirs

log = logging.getLogger(__name__)


class BotDevoirs(commands.Bot):
    def __init__(self):
        super().__init__(
            command_prefix=commands.when_mentioned,
            intents=discord.Intents.default(),
            # Empêche une description de devoir de déclencher un @everyone ou des mentions.
            allowed_mentions=discord.AllowedMentions.none(),
        )
        self.depot = DepotDevoirs(config.FICHIER_SAUVEGARDE)

    async def setup_hook(self) -> None:
        # Exécuté une seule fois au démarrage, contrairement à on_ready (rappelé à chaque reconnexion).
        self.depot.charger()
        await self.add_cog(CommandesDevoirs(self, self.depot, config.CHANNEL_ID))

        guild = discord.Object(id=config.SERVER_ID)
        self.tree.copy_global_to(guild=guild)
        try:
            synced = await self.tree.sync(guild=guild)
            log.info("%d commandes synchronisées.", len(synced))
        except discord.HTTPException:
            log.exception("Problème de synchronisation des commandes.")

    async def on_ready(self) -> None:
        log.info("Connecté en tant que %s", self.user)


if __name__ == "__main__":
    BotDevoirs().run(config.TOKEN, root_logger=True)
