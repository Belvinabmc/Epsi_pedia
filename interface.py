# interface.py
import tkinter as tk
from tkinter import messagebox
import sqlite3

from database import DB_NAME
from core.services.integrity_service import IntegrityService

def ouvrir_interface(parent: tk.Misc | None = None) -> None:
    """
    Ouvre l'interface Utilisateur.
    - Si un parent est fourni (cas du menu principal), on crée un Toplevel.
    - Sinon on crée une fenêtre racine (Tk).
    """
    root = tk.Toplevel(parent) if parent is not None else tk.Tk()
    root.title("Epsipédia - Tutoriaux")
    root.geometry("900x600")

    # --- Sécurité / Intégrité au démarrage ---
    integrity = IntegrityService()
    report = integrity.verify()  # calcule ok/KO + lecture_seule

    
    # --- Layout principal ---
    frame_left = tk.Frame(root, width=200, bg="#EEE")
    frame_left.pack(side="left", fill="y")

    frame_right = tk.Frame(root, bg="white")
    frame_right.pack(side="right", expand=True, fill="both")

    # --- Charger catégories depuis la base ---
    conn = sqlite3.connect(DB_NAME)
    cur = conn.cursor()
    cur.execute("SELECT id, nom FROM categories")
    categories = cur.fetchall()
    conn.close()

    # --- Affichage des tutos (texte DB) ---
    def afficher_tutos(cat_id: int):
        # Nettoyer frame droit
        for widget in frame_right.winfo_children():
            widget.destroy()

        conn = sqlite3.connect(DB_NAME)
        cur = conn.cursor()
        cur.execute("SELECT titre, contenu FROM tutos WHERE categorie_id=?", (cat_id,))
        tutos = cur.fetchall()
        conn.close()

        if not tutos:
            tk.Label(frame_right, text="Aucun tuto pour cette catégorie.", bg="white").pack(pady=10)
            return

        for titre, contenu in tutos:
            lbl_titre = tk.Label(frame_right, text=titre, font=("Arial", 16, "bold"), anchor="w", bg="white")
            lbl_titre.pack(fill="x", padx=10, pady=5)

            lbl_contenu = tk.Label(frame_right, text=contenu, wraplength=600, justify="left", anchor="w", bg="white")
            lbl_contenu.pack(fill="x", padx=20, pady=2)

    # --- Boutons catégories ---
    for cat_id, nom in categories:
        btn = tk.Button(frame_left, text=nom, command=lambda cid=cat_id: afficher_tutos(cid), anchor="w")
        btn.pack(fill="x")

    # Si l'écran est lancé tout seul (sans parent), on doit entrer dans la boucle
    if parent is None:
        root.mainloop()
