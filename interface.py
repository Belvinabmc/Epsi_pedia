# interface.py

import tkinter as tk
from tkinter import ttk
import sqlite3
from database import DB_NAME


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


    # Frame recherche + liste tutos
    frame_center = tk.Frame(main_frame, bg="#f5f6fa")
    frame_center.pack(side="left", fill="both", expand=True)

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

    # Si param est un mot-clé, lance la recherche automatiquement
    if param is not None and isinstance(param, str):
        search_var.set(param)
        root.after(100, lancer_recherche)

    # Frame affichage contenu (plus grande)
    frame_right = tk.Frame(main_frame, width=500, bg="#fff", relief="groove", bd=2)
    frame_right.pack(side="right", fill="y")

    # Titre de la section contenu
    lbl_contenu_titre = tk.Label(frame_right, text="Contenu du tuto", font=("Segoe UI", 16, "bold"), bg="#fff", fg="#222")
    lbl_contenu_titre.pack(pady=(20, 10))
    contenu_text = tk.Text(frame_right, wrap="word", font=("Segoe UI", 12), bg="#fff", fg="#222", relief="flat", height=25, width=60, state="disabled")
    contenu_text.pack(padx=20, pady=10, fill="both", expand=True)

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
        cur.execute("SELECT id, titre, contenu FROM tutos WHERE categorie_id=?", (cat_id,))
        tutos = cur.fetchall()
        conn.close()

        def afficher_contenu(titre, contenu):
            contenu_text.config(state="normal")
            contenu_text.delete("1.0", "end")
            contenu_text.insert("1.0", f"{titre}\n\n{contenu}")
            contenu_text.config(state="disabled")
            lbl_contenu_titre.config(text=titre)

        for tuto_id, titre, contenu in tutos:
            btn_titre = ttk.Button(frame_center, text=titre, style="TButton")
            btn_titre.pack(fill="x", padx=20, pady=8)
            btn_titre.bind("<Button-1>", lambda e, t=titre, c=contenu: afficher_contenu(t, c))

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
