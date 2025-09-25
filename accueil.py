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
    search_frame.pack(pady=(0, 20), side="top", anchor="center")
    search_var = tk.StringVar()
    search_entry = ttk.Entry(search_frame, textvariable=search_var, width=28, font=("Segoe UI", 12))
    search_entry.pack(side="left", padx=(0, 6), ipady=3)
    def lancer_recherche():
        mot_cle = search_var.get().strip()
        if mot_cle:
            root.destroy()
            from interface import ouvrir_interface
            ouvrir_interface(mot_cle)
    search_entry.bind("<Return>", lambda e: lancer_recherche())
    style.configure("Search.TButton", font=("Segoe UI", 12, "bold"), background="#2563eb", foreground="#fff", borderwidth=0, padding=8)
    style.map("Search.TButton",
        background=[("active", "#1C4E8F")],
        foreground=[("active", "#fff")]
    )
    search_btn = ttk.Button(search_frame, text="Rechercher", style="Search.TButton", command=lancer_recherche)
    search_btn.pack(side="left", ipadx=4, ipady=3)

    lbl_sub = tk.Label(root, text="Choisissez une catégorie pour commencer :", font=("Segoe UI", 16), bg="#f5f6fa", fg="#555")
    lbl_sub.pack(pady=(0, 30))

    frame_cats = tk.Frame(root, bg="#f5f6fa")
    frame_cats.pack(pady=10, fill="both", expand=True)

    conn = sqlite3.connect(DB_NAME)
    cur = conn.cursor()
    cur.execute("SELECT id, nom FROM categories")
    categories = cur.fetchall()
    conn.close()

    def ouvrir_interface_categorie(cat_id):
        root.destroy()
        from interface import ouvrir_interface
        ouvrir_interface(cat_id)

    # Images associées aux catégories (doit correspondre à l'ordre)
    import os
    from PIL import Image, ImageTk
    image_paths = [
        os.path.join(os.getcwd(), "asset", "images", "1703350621_27_La-survie-en-milieu-naturel-comme-therapie-avec-Dan-Coyle.jpeg"),
        os.path.join(os.getcwd(), "asset", "images", "Nourriture et ressource.jpg"),
        os.path.join(os.getcwd(), "asset", "images", "secour.jpg"),
        os.path.join(os.getcwd(), "asset", "images", "COMM.png"),
        os.path.join(os.getcwd(), "asset", "images", "Bricolage.jpg"),
        os.path.join(os.getcwd(), "asset", "images", "COMM.png")
    ]
    images = []
    for path in image_paths:
        try:
            if path.endswith('.webp'):
                # Si webp non supporté, utiliser une image jpg à la place
                path = os.path.join(os.getcwd(), "asset", "images", "Bricolage.jpg")
            img = Image.open(path)
            img = img.resize((600, 240), Image.LANCZOS)
            images.append(ImageTk.PhotoImage(img))
        except Exception as e:
            # Si erreur, bouton sans image
            images.append(None)

    # Placement en grille 3 colonnes x 2 lignes avec images
    for idx, (cat_id, nom) in enumerate(categories):
        row = idx // 3
        col = idx % 3
        if images[idx]:
            btn = tk.Button(frame_cats, text=nom, font=("Segoe UI", 18, "bold"), fg="#fff", compound="center",
                           image=images[idx], borderwidth=0, highlightthickness=0,
                           command=lambda cid=cat_id: ouvrir_interface_categorie(cid))
        else:
            btn = tk.Button(frame_cats, text=nom, font=("Segoe UI", 18, "bold"), fg="#fff",
                           borderwidth=0, highlightthickness=0,
                           command=lambda cid=cat_id: ouvrir_interface_categorie(cid))
        btn.grid(row=row, column=col, sticky="nsew", padx=20, pady=20)
    # Empêcher le garbage collector de supprimer les images
    frame_cats.images = images

    # Rendre chaque colonne et ligne extensible
    for i in range(3):
        frame_cats.grid_columnconfigure(i, weight=1)
    for i in range(2):
        frame_cats.grid_rowconfigure(i, weight=1)

    root.mainloop()
