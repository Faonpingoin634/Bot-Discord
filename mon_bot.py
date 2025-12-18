import discord
from discord.ext import tasks, commands
from discord import app_commands
import datetime
import json
import os
import pytz


TOKEN = "your_actual_token_here"
SERVER_ID = your_server_id_here      
CHANNEL_ID = your_channel_id_here

intents = discord.Intents.default()
intents.message_content = True 

bot = commands.Bot(command_prefix="!", intents=intents)

FICHIER_SAUVEGARDE = "devoirs.json"
liste_devoirs = []

def charger_donnees():
    global liste_devoirs
    if os.path.exists(FICHIER_SAUVEGARDE):
        with open(FICHIER_SAUVEGARDE, "r", encoding="utf-8") as f:
            try:
                data = json.load(f)
                for d in data:
                    d['date'] = datetime.datetime.strptime(d['date'], "%Y-%m-%d").date()
                liste_devoirs = data
                print(f"[INFO] {len(liste_devoirs)} devoirs charges.") 
            except json.JSONDecodeError:
                print("[ERREUR] Le fichier de sauvegarde est corrompu ou vide.")
                liste_devoirs = []
    else:
        print("[INFO] Aucun fichier trouve, creation d'une nouvelle liste.")
        liste_devoirs = []

def sauvegarder_donnees():
    data_to_save = []
    for d in liste_devoirs:
        copie = d.copy()
        copie['date'] = d['date'].strftime("%Y-%m-%d")
        data_to_save.append(copie)
    with open(FICHIER_SAUVEGARDE, "w", encoding="utf-8") as f:
        json.dump(data_to_save, f, indent=4, ensure_ascii=False)

@bot.tree.command(name="ajouter", description="Ajoute un nouveau devoir")
@app_commands.describe(date="Format JJ/MM/AAAA", description="Description")
async def ajouter(interaction: discord.Interaction, date: str, description: str):
    try:
        date_butoir = datetime.datetime.strptime(date, "%d/%m/%Y").date()
        nouveau_devoir = {
            "date": date_butoir,
            "desc": description,
            "auteur": interaction.user.name,
            "rappel_7j_fait": False, 
            "rappel_1j_fait": False
        }
        liste_devoirs.append(nouveau_devoir)
        sauvegarder_donnees()
        await interaction.response.send_message(f"✅ Devoir ajouté pour le **{date}** : {description}")
    except ValueError:
        await interaction.response.send_message("❌ Date invalide. Utilise : JJ/MM/AAAA", ephemeral=True)

@bot.tree.command(name="devoir", description="Affiche la liste des devoirs")
async def devoir(interaction: discord.Interaction):
    if not liste_devoirs:
        await interaction.response.send_message("🎉 Aucun devoir !")
        return

    liste_triee = sorted(liste_devoirs, key=lambda x: x['date'])
    message = "**📅 Devoirs :**\n"
    for d in liste_triee:
        date_fr = d['date'].strftime("%d/%m/%Y")
        message += f"- **{date_fr}** : {d['desc']} ({d['auteur']})\n"
    await interaction.response.send_message(message)
    
@bot.tree.command(name="supprimer", description="Supprime un devoir par son numéro")
@app_commands.describe(numero="Le numéro du devoir à supprimer (voir liste)")
async def supprimer(interaction: discord.Interaction, numero: int):
    if 0 < numero <= len(liste_devoirs):
        devoir_supprime = liste_devoirs.pop(numero - 1) 
        sauvegarder_donnees()
        
        date_fr = devoir_supprime['date'].strftime("%d/%m/%Y")
        await interaction.response.send_message(f"🗑️ Devoir supprimé : **{devoir_supprime['desc']}** (pour le {date_fr})")
    else:
        await interaction.response.send_message(f"❌ Numéro invalide. Il y a actuellement {len(liste_devoirs)} devoirs.", ephemeral=True)

@bot.event
async def on_ready():
    print(f'[OK] Connecte en tant que {bot.user}')
    charger_donnees()

    print("[WAIT] Debut de la synchronisation...")
    try:
        guild = discord.Object(id=SERVER_ID)
        bot.tree.copy_global_to(guild=guild)
        synced = await bot.tree.sync(guild=guild)
        
        print(f"[SUCCES] {len(synced)} commandes synchronisees sur le serveur !")
        print("-> Va sur Discord, tape '/' et attends quelques secondes.")
    except Exception as e:
        print(f"[ERREUR] Probleme de synchro : {e}")

    if not verifier_dates.is_running():
        verifier_dates.start()

@tasks.loop(hours=1)
async def verifier_dates():
    await bot.wait_until_ready()
    channel = bot.get_channel(CHANNEL_ID)
    if not channel: return
    
    paris_tz = pytz.timezone("Europe/Paris")
    aujourdhui = datetime.datetime.now(paris_tz).date() 

    changement = False
    for d in liste_devoirs:
        delta = (d['date'] - aujourdhui).days
        if delta == 7 and not d.get('rappel_7j_fait'):
            await channel.send(f"📢 Rappel : '{d['desc']}' dans 1 semaine !")
            d['rappel_7j_fait'] = True
            changement = True
        elif delta == 1 and not d.get('rappel_1j_fait'):
            await channel.send(f"🚨 Urgent : '{d['desc']}' pour DEMAIN !")
            d['rappel_1j_fait'] = True
            changement = True
    if changement: sauvegarder_donnees()

bot.run(TOKEN)