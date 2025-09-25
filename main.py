# main.py
import tkinter as tk
import os
from tkinter import messagebox
from PIL import Image, ImageTk
from auth import verifier_code, est_admin

from accueil import ouvrir_accueil


def visiteur():
    root.destroy()
    ouvrir_accueil()

from admin import ouvrir_connexion_admin
def admin():
    ouvrir_connexion_admin()

# --- Fenêtre ---
root = tk.Tk()
root.title("Epsipédia")
root.geometry("900x600")
root.minsize(600, 400)

canvas = tk.Canvas(root)
canvas.pack(fill="both", expand=True)

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

image_path = os.path.join(BASE_DIR, "asset", "images", "Shield.jpeg")

bg_orig = Image.open(image_path)  # place ton image ici

title_text = canvas.create_text(0, 0, text="Epsipédia", font=("Arial", 40, "bold"), fill="#111111")
subtitle_text = canvas.create_text(0, 0, text="Bienvenue", font=("Arial", 20), fill="#111111")



btn_visiteur = tk.Button(root, text="Connexion", command=visiteur, font=("Arial", 14), bg="#111", fg="white", activebackground="#222", activeforeground="white")
btn_visiteur_window = canvas.create_window(0, 0, window=btn_visiteur, width=250)

btn_admin = tk.Button(root, text="Admin", command=admin, font=("Arial", 14, "bold"),
                      relief="flat", bg="#B5B5B5", fg="#111111", activebackground="#DDDDDD")
btn_admin_window = canvas.create_window(0, 0, window=btn_admin, width=120, height=40)

def resize(event):
    canvas.delete("all")
    bg_resized = bg_orig.resize((event.width, event.height))
    bg_img = ImageTk.PhotoImage(bg_resized)
    canvas.bg_img = bg_img
    canvas.create_image(0, 0, image=bg_img, anchor="nw")
    # Redessiner les textes et widgets
    global title_text, subtitle_text, btn_visiteur_window, btn_admin_window
    title_text = canvas.create_text(event.width/2, event.height*0.15, text="Epsipédia", font=("Arial", 40, "bold"), fill="#111111")
    subtitle_text = canvas.create_text(event.width/2, event.height*0.25, text="Bienvenue", font=("Arial", 20), fill="#111111")
    btn_visiteur_window = canvas.create_window(event.width/2, event.height*0.75, window=btn_visiteur, width=250)
    btn_admin_window = canvas.create_window(event.width*0.88, event.height*0.88, window=btn_admin, width=120, height=40)

canvas.bind("<Configure>", resize)

root.mainloop()
