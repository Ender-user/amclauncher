import tkinter as tk
from tkinter import ttk, messagebox
import threading
import webbrowser
import os
import urllib.request
import subprocess

import minecraft_launcher_lib
from minecraft_launcher_lib.install import install_minecraft_version
from minecraft_launcher_lib.command import get_minecraft_command
from minecraft_launcher_lib.utils import get_available_versions

# Version du launcher
LAUNCHER_VERSION = "1.0"

# Chemin vers .minecraft
game_directory = os.path.join(os.getcwd(), ".minecraft")

# Liste des versions
available_versions = [v['id'] for v in get_available_versions(game_directory) if not v['id'].endswith("json")]

# Fonction de mise à jour
def check_for_update():
    try:
        version_url = "https://tonsiteweb.com/launcher/version.txt"
        script_url = "https://tonsiteweb.com/launcher/main.py"

        latest_version = urllib.request.urlopen(version_url).read().decode("utf-8").strip()

        if latest_version != LAUNCHER_VERSION:
            if messagebox.askyesno("Mise à jour disponible", f"Nouvelle version {latest_version} disponible.\nVoulez-vous mettre à jour ?"):
                new_code = urllib.request.urlopen(script_url).read()
                with open(__file__, "wb") as f:
                    f.write(new_code)
                messagebox.showinfo("Mise à jour", "Mise à jour effectuée. Relance le launcher.")
                root.quit()
    except Exception as e:
        print(f"Erreur mise à jour : {e}")

# Crée la fenêtre principale
root = tk.Tk()
root.title("A.MC.Launcher")
root.geometry("600x400")
root.iconbitmap("launcher.ico")  # Icône personnalisée

# Widgets
tk.Label(root, text="Pseudo :").pack()
pseudo_entry = tk.Entry(root)
pseudo_entry.pack()

tk.Label(root, text="Version Minecraft :").pack()
version_var = tk.StringVar(value=available_versions[0])
version_menu = ttk.Combobox(root, textvariable=version_var, values=available_versions, state="readonly")
version_menu.pack()

progress = ttk.Progressbar(root, orient="horizontal", length=400, mode="determinate")
progress.pack(pady=10)

# Fonction pour afficher les logs
def open_log_window():
    log_win = tk.Toplevel(root)
    log_win.title("Logs du jeu")
    log_win.geometry("600x400")
    log_text = tk.Text(log_win, wrap="word")
    log_text.pack(expand=True, fill="both")
    return log_text

# Progress bar update
def update_progress(value, message=""):
    progress['value'] = value
    root.update_idletasks()
    if message:
        print(message)

# Vérification fictive de compte premium
def is_premium_account(pseudo):
    return False  # À personnaliser

# Lancement du jeu
def start_game():
    pseudo = pseudo_entry.get()
    version = version_var.get()

    if not pseudo:
        messagebox.showerror("Erreur", "Veuillez entrer un pseudo.")
        return

    if is_premium_account(pseudo):
        messagebox.showerror("Erreur", "Ce pseudo est utilisé par un compte premium.")
        return

    log_text = open_log_window()

    def log(msg):
        log_text.insert(tk.END, msg + "\n")
        log_text.see(tk.END)

    def launch():
        try:
            log("Installation de Minecraft...")
            update_progress(10)

            install_minecraft_version(version, game_directory)
            update_progress(50, "Version installée.")

            options = {
                "username": pseudo,
                "uuid": "0" * 32,
                "token": "0",
                "launcherName": "A.MC.Launcher",
                "launcherVersion": LAUNCHER_VERSION
            }

            command = get_minecraft_command(version, game_directory, options)
            update_progress(80, "Commande prête.")

            log("Démarrage de Minecraft...\n")
            update_progress(100)

            process = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True)
            for line in process.stdout:
                log(line.strip())

        except Exception as e:
            log(f"Erreur : {e}")
            messagebox.showerror("Erreur", str(e))

    threading.Thread(target=launch).start()

# Bouton de démarrage
start_button = tk.Button(root, text="Lancer Minecraft", command=start_game)
start_button.pack(pady=10)

# Liens externes
links_frame = tk.Frame(root)
links_frame.pack(side="bottom", pady=10)

discord_btn = tk.Button(links_frame, text="Support Discord", command=lambda: webbrowser.open("https://discord.gg/aXz6TVeX5d"))
discord_btn.pack(side="left", padx=10)

site_btn = tk.Button(links_frame, text="Site Web", command=lambda: webbrowser.open("https://tonsiteweb.com"))
site_btn.pack(side="right", padx=10)

# Vérifie la mise à jour au démarrage
check_for_update()

root.mainloop()
