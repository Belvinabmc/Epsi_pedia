# interface.py

import tkinter as tk
from tkinter import ttk
import sqlite3
from database import DB_NAME


def ouvrir_interface():
    root = tk.Tk()
    root.title("Epsipédia - Tutoriaux")
    root.geometry("1000x650")
    root.minsize(700, 400)
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
        if mot_cle:
            conn = sqlite3.connect(DB_NAME)
            cur = conn.cursor()
            cur.execute("SELECT titre, contenu FROM tutos WHERE titre LIKE ? OR contenu LIKE ?", (f"%{mot_cle}%", f"%{mot_cle}%"))
            tutos = cur.fetchall()
            conn.close()
            def afficher_contenu(titre, contenu):
                contenu_text.config(state="normal")
                contenu_text.delete("1.0", "end")
                contenu_text.insert("1.0", f"{titre}\n\n{contenu}")
                contenu_text.config(state="disabled")
                lbl_contenu_titre.config(text=titre)
            for titre, contenu in tutos:
                btn_titre = ttk.Button(frame_center, text=titre, style="TButton")
                btn_titre.pack(fill="x", padx=20, pady=8)
                btn_titre.bind("<Button-1>", lambda e, t=titre, c=contenu: afficher_contenu(t, c))
            if not tutos:
                lbl = tk.Label(frame_center, text="Aucun tuto trouvé.", bg="#f5f6fa", fg="#888", font=("Segoe UI", 12))
                lbl.pack(pady=20)
        else:
            # Si champ vide, on vide la zone centrale
            for widget in frame_center.winfo_children():
                if widget != search_frame:
                    widget.destroy()
    search_entry.bind("<Return>", lancer_recherche)
    search_btn = ttk.Button(search_frame, text="Rechercher", command=lancer_recherche)
    search_btn.pack(side="left")

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
    for cat_id, nom in categories:
        btn = ttk.Button(frame_left, text=nom, style="Cat.TButton", command=lambda cid=cat_id: afficher_tutos(cid))
        btn.pack(fill="x", padx=14, pady=12)

    root.mainloop()
