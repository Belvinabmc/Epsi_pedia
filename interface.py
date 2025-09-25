# interface.py

import tkinter as tk
from tkinter import ttk
import sqlite3
DB_NAME = "database.db"


def ouvrir_interface(param=None):
    root = tk.Tk()
    root.title("Epsipédia - Tutoriaux")
    root.state('zoomed')  # Plein écran
    root.configure(bg="#f5f6fa")

    # Style moderne
    style = ttk.Style()
    style.theme_use("clam")
    style.configure("TButton", font=("Segoe UI", 12), background="#1C4E8F", foreground="#fff", borderwidth=0)
    style.map("TButton",
        background=[("active", "#1C4E8F")],
        foreground=[("active", "#fff")]
    )

    # Frame principal
    main_frame = tk.Frame(root, bg="#f5f6fa")
    main_frame.pack(fill="both", expand=True)


    # Frame catégories (plus large)
    frame_left = tk.Frame(main_frame, width=250, bg="#dbeafe")
    frame_left.pack(side="left", fill="y")

    # Bouton Accueil en haut des catégories
    from accueil import ouvrir_accueil
    btn_accueil = ttk.Button(frame_left, text="Accueil", style="Cat.TButton", command=lambda: (root.destroy(), ouvrir_accueil()))
    btn_accueil.pack(fill="x", padx=14, pady=(18, 24))



    # Frame avec scrollbar pour la liste des tutos
    frame_center_container = tk.Frame(main_frame, bg="#f5f6fa")
    frame_center_container.pack(side="left", fill="both", expand=True)
    canvas_center = tk.Canvas(frame_center_container, bg="#f5f6fa", highlightthickness=0)
    scrollbar_center = tk.Scrollbar(frame_center_container, orient="vertical", command=canvas_center.yview)
    frame_center = tk.Frame(canvas_center, bg="#f5f6fa")
    frame_center.bind(
        "<Configure>", lambda e: canvas_center.configure(scrollregion=canvas_center.bbox("all"))
    )
    canvas_center.create_window((0, 0), window=frame_center, anchor="nw")
    canvas_center.configure(yscrollcommand=scrollbar_center.set)
    canvas_center.pack(side="left", fill="both", expand=True)
    scrollbar_center.pack(side="right", fill="y")

    # Barre de recherche
    search_frame = tk.Frame(frame_center, bg="#f5f6fa")
    search_frame.pack(fill="x", padx=20, pady=(10, 0))
    search_var = tk.StringVar()
    search_entry = ttk.Entry(search_frame, textvariable=search_var, width=30)
    search_entry.pack(side="left", padx=(0, 8))
    def lancer_recherche(*args):
        mot_cle = search_var.get().strip()
        for widget in frame_center.winfo_children():
            if widget != search_frame:
                widget.destroy()
        conn = sqlite3.connect(DB_NAME)
        cur = conn.cursor()
        if mot_cle:
            cur.execute("""
                SELECT t.titre, t.contenu, c.nom
                FROM tutos t
                LEFT JOIN categories c ON t.categorie_id = c.id
                WHERE t.titre LIKE ?
            """, (f"%{mot_cle}%",))
        else:
            cur.execute("""
                SELECT t.titre, t.contenu, c.nom
                FROM tutos t
                LEFT JOIN categories c ON t.categorie_id = c.id
            """)
        tutos = cur.fetchall()
        conn.close()
        # Regrouper les tutos par catégorie
        cat_dict = {}
        for titre, contenu, cat in tutos:
            if cat not in cat_dict:
                cat_dict[cat] = []
            cat_dict[cat].append((titre, contenu))
        def afficher_contenu(titre, contenu, cat):
            contenu_text.config(state="normal")
            contenu_text.delete("1.0", "end")
            contenu_text.insert("1.0", f"Catégorie : {cat}\n\n{titre}\n\n{contenu}")
            contenu_text.config(state="disabled")
            lbl_contenu_titre.config(text=titre)
        if cat_dict:
            for cat, tutos_cat in cat_dict.items():
                frame_cat = tk.Frame(frame_center, bg="#e0e7ff", bd=2, relief="solid")
                frame_cat.pack(fill="x", padx=18, pady=12)
                lbl_cat = tk.Label(frame_cat, text=cat, font=("Segoe UI", 13, "bold"), bg="#e0e7ff", fg="#2563eb")
                lbl_cat.pack(anchor="w", padx=8, pady=(6,4))
                for titre, contenu in tutos_cat:
                    btn_titre = ttk.Button(frame_cat, text=titre, style="TButton")
                    btn_titre.pack(fill="x", padx=16, pady=4)
                    btn_titre.bind("<Button-1>", lambda e, t=titre, c=contenu, cat=cat: afficher_contenu(t, c, cat))
        else:
            lbl = tk.Label(frame_center, text="Aucun tuto trouvé.", bg="#f5f6fa", fg="#888", font=("Segoe UI", 12))
            lbl.pack(pady=20)
    search_entry.bind("<Return>", lancer_recherche)
    search_btn = ttk.Button(search_frame, text="Rechercher", command=lancer_recherche)
    search_btn.pack(side="left")

    # Si param est un id de catégorie, affiche les tutos de cette catégorie
    def afficher_param():
        if param is not None:
            # Si param est un entier ou une chaîne représentant un entier
            if isinstance(param, int) or (isinstance(param, str) and param.isdigit()):
                afficher_tutos(int(param))
            elif isinstance(param, str):
                search_var.set(param)
                root.after(100, lancer_recherche)
    root.after(0, afficher_param)

    # Frame affichage contenu (plus grande vers la gauche)
    frame_right = tk.Frame(main_frame, width=700, bg="#fff", relief="groove", bd=2)
    frame_right.pack(side="right", fill="y")

    # Titre de la section contenu
    lbl_contenu_titre = tk.Label(frame_right, text="Contenu du tuto", font=("Segoe UI", 16, "bold"), bg="#fff", fg="#222")
    lbl_contenu_titre.pack(pady=(20, 10))
    image_label = tk.Label(frame_right, bg="#fff")
    image_label.pack(padx=20, pady=(0,10))
    contenu_text = tk.Text(frame_right, wrap="word", font=("Segoe UI", 12), bg="#fff", fg="#222", relief="flat", height=25, width=80, state="disabled")
    contenu_text.pack(padx=20, pady=10, fill="both", expand=True)

    images_tuto_dir = "asset/images_tuto/"

    # Charger catégories depuis la base
    conn = sqlite3.connect(DB_NAME)
    cur = conn.cursor()
    cur.execute("SELECT id, nom FROM categories")
    categories = cur.fetchall()
    conn.close()

    def afficher_tutos(cat_id):
        # Nettoyer frame center sauf la barre de recherche
        for widget in frame_center.winfo_children():
            if widget != search_frame:
                widget.destroy()

        conn = sqlite3.connect(DB_NAME)
        cur = conn.cursor()
        cur.execute("SELECT id, titre, contenu, image_path FROM tutos WHERE categorie_id=?", (cat_id,))
        tutos = cur.fetchall()
        conn.close()

        def afficher_contenu(titre, contenu, image_path):
            contenu_text.config(state="normal")
            contenu_text.delete("1.0", "end")
            contenu_text.insert("1.0", f"{titre}\n\n{contenu}")
            contenu_text.config(state="disabled")
            lbl_contenu_titre.config(text=titre)
            # Afficher l'image si elle existe
            if image_path:
                import os
                if not os.path.isabs(image_path):
                    image_path = os.path.join(images_tuto_dir, image_path)
                try:
                    from PIL import Image, ImageTk
                    img = Image.open(image_path)
                    img = img.resize((320, 180), Image.LANCZOS)
                    photo = ImageTk.PhotoImage(img)
                    image_label.config(image=photo, text="")
                    image_label.image = photo
                except Exception as e:
                    image_label.config(image="", text=f"Image non trouvée : {os.path.basename(image_path)}", fg="red")
            else:
                image_label.config(image="", text="")

        for tuto_id, titre, contenu, image_path in tutos:
            btn_titre = ttk.Button(frame_center, text=titre, style="TButton")
            btn_titre.pack(fill="x", padx=20, pady=8)
            btn_titre.bind("<Button-1>", lambda e, t=titre, c=contenu, ip=image_path: afficher_contenu(t, c, ip))

    # Style spécial pour les boutons de catégories
    style.configure("Cat.TButton", font=("Segoe UI", 14, "bold"), background="#3b82f6", foreground="#fff", borderwidth=0, padding=10)
    style.map("Cat.TButton",
        background=[("active", "#2563eb")],
        foreground=[("active", "#fff")]
    )
    for cat_id_, nom in categories:
        btn = ttk.Button(frame_left, text=nom, style="Cat.TButton", command=lambda cid=cat_id_: afficher_tutos(cid))
        btn.pack(fill="x", padx=14, pady=12)

    # Si une catégorie est passée, affiche directement ses tutos

    root.mainloop()
