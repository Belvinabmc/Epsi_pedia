import tkinter as tk
from tkinter import ttk
import sqlite3
from database import DB_NAME
from interface import ouvrir_interface

def ouvrir_accueil():
    root = tk.Tk()
    root.title("Epsipédia - Accueil")
    root.state('zoomed')  # Plein écran
    root.configure(bg="#f5f6fa")

    style = ttk.Style()
    style.theme_use("clam")
    style.configure("Cat.TButton", font=("Segoe UI", 16, "bold"), background="#3b82f6", foreground="#fff", borderwidth=0, padding=12)
    style.map("Cat.TButton",
        background=[("active", "#2563eb")],
        foreground=[("active", "#fff")]
    )

    lbl_title = tk.Label(root, text="Bienvenue sur Epsipédia !", font=("Segoe UI", 28, "bold"), bg="#f5f6fa", fg="#222")
    lbl_title.pack(pady=(40, 10))

    # Barre de recherche
    search_frame = tk.Frame(root, bg="#f5f6fa")
    search_frame.pack(pady=(0, 20))
    search_var = tk.StringVar()
    search_entry = ttk.Entry(search_frame, textvariable=search_var, width=32)
    search_entry.pack(side="left", padx=(0, 8))
    def lancer_recherche():
        mot_cle = search_var.get().strip()
        if mot_cle:
            root.destroy()
            from interface import ouvrir_interface
            ouvrir_interface(mot_cle)
    search_entry.bind("<Return>", lambda e: lancer_recherche())
    search_btn = ttk.Button(search_frame, text="Rechercher", command=lancer_recherche)
    search_btn.pack(side="left")

    lbl_sub = tk.Label(root, text="Choisissez une catégorie pour commencer :", font=("Segoe UI", 16), bg="#f5f6fa", fg="#555")
    lbl_sub.pack(pady=(0, 30))

    frame_cats = tk.Frame(root, bg="#f5f6fa")
    frame_cats.pack(pady=10)

    conn = sqlite3.connect(DB_NAME)
    cur = conn.cursor()
    cur.execute("SELECT id, nom FROM categories")
    categories = cur.fetchall()
    conn.close()

    def ouvrir_interface_categorie(cat_id):
        root.destroy()
        # Appelle la page interface en filtrant sur la catégorie choisie
        ouvrir_interface(cat_id)

    for cat_id, nom in categories:
        btn = ttk.Button(frame_cats, text=nom, style="Cat.TButton", command=lambda cid=cat_id: ouvrir_interface_categorie(cid))
        btn.pack(fill="x", padx=40, pady=18)

    root.mainloop()
