# main.py
import tkinter as tk
from tkinter import messagebox
from PIL import Image, ImageTk
from auth import verifier_code, est_admin
from interface import ouvrir_interface

def connexion():
    code = entry_code.get()
    if verifier_code(code):
        messagebox.showinfo("Succès", "Accès autorisé ✅")
        root.destroy()
        ouvrir_interface()
    else:
        messagebox.showerror("Erreur", "Code invalide ❌")

def admin():
    messagebox.showinfo("Admin", "Espace admin 🚪 (en construction)")

# --- Fenêtre ---
root = tk.Tk()
root.title("Epsipédia")
root.geometry("900x600")
root.minsize(600, 400)

canvas = tk.Canvas(root)
canvas.pack(fill="both", expand=True)

bg_orig = Image.open("C:/Users/adamm/OneDrive/Desktop/Projet EpsiPédia/asset/images/background.jpeg")  # place ton image ici

title_text = canvas.create_text(0, 0, text="Epsipédia", font=("Arial", 40, "bold"), fill="#111111")
subtitle_text = canvas.create_text(0, 0, text="Bienvenue", font=("Arial", 20), fill="#111111")

entry_code = tk.Entry(root, show="*", font=("Arial", 16), justify="center")
entry_window = canvas.create_window(0, 0, window=entry_code, width=200)

btn_connexion = tk.Button(root, text="Connexion", command=connexion, font=("Arial", 14))
btn_connexion_window = canvas.create_window(0, 0, window=btn_connexion, width=150)

btn_admin = tk.Button(root, text="Admin", command=admin, font=("Arial", 14, "bold"),
                      relief="flat", bg="#ffffff", fg="#111111", activebackground="#DDDDDD")
btn_admin_window = canvas.create_window(0, 0, window=btn_admin, width=120, height=40)

def resize(event):
    bg_resized = bg_orig.resize((event.width, event.height))
    bg_img = ImageTk.PhotoImage(bg_resized)
    canvas.bg_img = bg_img
    canvas.create_image(0, 0, image=bg_img, anchor="nw")

    canvas.coords(title_text, event.width/2, event.height*0.15)
    canvas.coords(subtitle_text, event.width/2, event.height*0.25)
    canvas.coords(entry_window, event.width/2, event.height*0.40)
    canvas.coords(btn_connexion_window, event.width/2, event.height*0.50)
    canvas.coords(btn_admin_window, event.width*0.88, event.height*0.88)

canvas.bind("<Configure>", resize)

root.mainloop()
