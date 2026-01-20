import discord
from discord.ext import tasks, commands
from discord import app_commands
import datetime
import json
import os
import pytz

# --- CONFIGURATION ---
TOKEN = "your_actual_token_here"
SERVER_ID = your_server_id_here      
CHANNEL_ID = your_channel_id_here

intents = discord.Intents.default()
intents.message_content = True 

bot = commands.Bot(command_prefix="!", intents=intents)

FICHIER_SAUVEGARDE = "devoirs.json"
liste_devoirs = []
bot_est_pret = False

# --- FONCTIONS DE GESTION DES DONNÉES ---
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
    liste_devoirs.sort(key=lambda x: x['date'])
    data_to_save = []
    for d in liste_devoirs:
        copie = d.copy()
        copie['date'] = d['date'].strftime("%Y-%m-%d")
        data_to_save.append(copie)
    with open(FICHIER_SAUVEGARDE, "w", encoding="utf-8") as f:
        json.dump(data_to_save, f, indent=4, ensure_ascii=False)

# --- COMMANDES SLASH ---
@bot.tree.command(name="ajouter", description="Ajoute un nouveau devoir")
@app_commands.describe(date="Format JJ/MM/AAAA", description="Description du devoir")
async def ajouter(interaction: discord.Interaction, date: str, description: str):
    try:
        date_butoir = datetime.datetime.strptime(date, "%d/%m/%Y").date()
        
        paris_tz = pytz.timezone("Europe/Paris")
        aujourdhui = datetime.datetime.now(paris_tz).date()
        if date_butoir < aujourdhui:
             await interaction.response.send_message("⚠️ Tu essaies d'ajouter un devoir pour une date déjà passée !", ephemeral=True)
             return

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

    liste_devoirs.sort(key=lambda x: x['date'])
    
    message = "**📅 Liste des devoirs :**\n"
    for i, d in enumerate(liste_devoirs, 1):
        date_fr = d['date'].strftime("%d/%m/%Y")
        message += f"`{i}.` **{date_fr}** : {d['desc']} (par {d['auteur']})\n"
    
    await interaction.response.send_message(message)
    
@bot.tree.command(name="supprimer", description="Supprime un devoir par son numéro")
@app_commands.describe(numero="Le numéro affiché dans la liste /devoir")
async def supprimer(interaction: discord.Interaction, numero: int):
    liste_devoirs.sort(key=lambda x: x['date'])

    if 0 < numero <= len(liste_devoirs):
        devoir_supprime = liste_devoirs.pop(numero - 1) 
        sauvegarder_donnees()
        
        date_fr = devoir_supprime['date'].strftime("%d/%m/%Y")
        await interaction.response.send_message(f"🗑️ Devoir supprimé : **{devoir_supprime['desc']}** (était prévu pour le {date_fr})")
    else:
        await interaction.response.send_message(f"❌ Numéro {numero} invalide. Tape `/devoir` pour vérifier.", ephemeral=True)

# --- EVENEMENTS ET BOUCLES ---
@bot.event
async def on_ready():
    global bot_est_pret

    if bot_est_pret:
        print(f"[INFO] Reconnexion détectée. Pas de resynchronisation.")
        return

    print(f'[OK] Connecte en tant que {bot.user}')
    charger_donnees()

    print("[WAIT] Debut de la synchronisation des commandes...")
    try:
        guild = discord.Object(id=SERVER_ID)
        bot.tree.copy_global_to(guild=guild)
        synced = await bot.tree.sync(guild=guild)
        print(f"[SUCCES] {len(synced)} commandes synchronisees !")
    except Exception as e:
        print(f"[ERREUR] Probleme de synchro : {e}")

    if not verifier_dates.is_running():
        verifier_dates.start()
    
    bot_est_pret = True

@tasks.loop(hours=1)
async def verifier_dates():
    await bot.wait_until_ready()
    channel = bot.get_channel(CHANNEL_ID)
    if not channel: return
    
    paris_tz = pytz.timezone("Europe/Paris")
    aujourdhui = datetime.datetime.now(paris_tz).date() 

    global liste_devoirs
    devoirs_a_garder = []
    changement = False

    for d in liste_devoirs:
        delta = (d['date'] - aujourdhui).days
        
        if delta < 0:
            print(f"[AUTO-DELETE] Suppression du devoir : {d['desc']} (Date: {d['date']})")
            changement = True
            continue 

        if delta == 7 and not d.get('rappel_7j_fait'):
            await channel.send(f"📢 **RAPPEL (J-7)** : '{d['desc']}' pour le {d['date'].strftime('%d/%m')}")
            d['rappel_7j_fait'] = True
            changement = True
        elif delta == 1 and not d.get('rappel_1j_fait'):
            await channel.send(f"🚨 **URGENT (DEMAIN)** : '{d['desc']}' !")
            d['rappel_1j_fait'] = True
            changement = True
        
        devoirs_a_garder.append(d)

    if changement:
        liste_devoirs = devoirs_a_garder
        sauvegarder_donnees()

bot.run(TOKEN)