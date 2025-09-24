# main.py : Point d'entrée principal de l'application
import tkinter as tk  # Importation du module d'interface graphique Tkinter
from tkinter import messagebox  # Pour afficher des popups d'information/erreur
from PIL import Image, ImageTk  # Pour gérer les images (Pillow)
from auth import verifier_code, est_admin  # Fonctions d'authentification
from interface import ouvrir_interface  # Fonction pour ouvrir l'interface principale


# Fonction appelée lors de la tentative de connexion
def connexion():
    code = entry_code.get()  # Récupère le code saisi
    if verifier_code(code):  # Vérifie le code
        messagebox.showinfo("Succès", "Accès autorisé ✅")  # Affiche un message de succès
        root.destroy()  # Ferme la fenêtre de connexion
        ouvrir_interface()  # Ouvre l'interface principale
    else:
        messagebox.showerror("Erreur", "Code invalide ❌")  # Affiche une erreur si le code est faux


# Importe la fonction pour ouvrir la page de connexion admin
from admin import ouvrir_connexion_admin
# Fonction appelée lors du clic sur le bouton Admin
def admin():
    ouvrir_connexion_admin()  # Ouvre la fenêtre de connexion admin

# --- Fenêtre ---

# --- Fenêtre principale ---
root = tk.Tk()  # Crée la fenêtre principale
root.title("Epsipédia")  # Titre de la fenêtre
root.geometry("900x600")  # Taille initiale
root.minsize(600, 400)  # Taille minimale


canvas = tk.Canvas(root)  # Crée un canvas pour dessiner et placer les widgets
canvas.pack(fill="both", expand=True)  # Le canvas prend toute la place


bg_orig = Image.open("C:/Users/adamm/OneDrive/Desktop/Epsi_pedia/asset/images/Shield.jpeg")  # Charge l'image de fond


title_text = canvas.create_text(0, 0, text="Epsipédia", font=("Arial", 40, "bold"), fill="#111111")  # Titre principal
subtitle_text = canvas.create_text(0, 0, text="Bienvenue", font=("Arial", 20), fill="#111111")  # Sous-titre



entry_code = tk.Entry(root, show="*", font=("Arial", 16), justify="center")  # Champ de saisie du mot de passe
entry_window = canvas.create_window(0, 0, window=entry_code, width=200)  # Place le champ sur le canvas
# Permettre la connexion avec la touche Entrée
entry_code.bind("<Return>", lambda event: connexion())  # Active la connexion avec Entrée


btn_connexion = tk.Button(root, text="Connexion", command=connexion, font=("Arial", 14))  # Bouton de connexion
btn_connexion_window = canvas.create_window(0, 0, window=btn_connexion, width=150)  # Place le bouton sur le canvas


btn_admin = tk.Button(
    root, text="Admin", command=admin, font=("Arial", 14, "bold"),
    relief="flat", bg="#B5B5B5", fg="#111111", activebackground="#DDDDDD"
)  # Bouton pour accéder à l'espace admin
btn_admin_window = canvas.create_window(0, 0, window=btn_admin, width=120, height=40)  # Place le bouton admin


# Fonction appelée à chaque redimensionnement de la fenêtre
def resize(event):
    canvas.delete("all")  # Efface tout le canvas
    bg_resized = bg_orig.resize((event.width, event.height))  # Redimensionne l'image de fond
    bg_img = ImageTk.PhotoImage(bg_resized)  # Convertit l'image pour Tkinter
    canvas.bg_img = bg_img  # Garde une référence pour éviter le garbage collector
    canvas.create_image(0, 0, image=bg_img, anchor="nw")  # Affiche l'image de fond
    # Redessiner les textes et widgets
    global title_text, subtitle_text, entry_window, btn_connexion_window, btn_admin_window
    title_text = canvas.create_text(event.width/2, event.height*0.15, text="Epsipédia", font=("Arial", 40, "bold"), fill="#111111")  # Titre
    subtitle_text = canvas.create_text(event.width/2, event.height*0.25, text="Bienvenue", font=("Arial", 20), fill="#111111")  # Sous-titre
    entry_window = canvas.create_window(event.width/2, event.height*0.44, window=entry_code, width=200)  # Champ mdp
    btn_connexion_window = canvas.create_window(event.width/2, event.height*0.53, window=btn_connexion, width=150)  # Bouton connexion
    btn_admin_window = canvas.create_window(event.width*0.88, event.height*0.88, window=btn_admin, width=120, height=40)  # Bouton admin


canvas.bind("<Configure>", resize)  # Appelle resize à chaque changement de taille


root.mainloop()  # Boucle principale Tkinter (affichage de la fenêtre)
