# interface.py
import tkinter as tk
import sqlite3
from database import DB_NAME

def ouvrir_interface():
    root = tk.Tk()
    root.title("Epsipédia - Tutoriaux")
    root.geometry("900x600")

    # Frame catégories
    frame_left = tk.Frame(root, width=200, bg="#EEE")
    frame_left.pack(side="left", fill="y")

    # Frame contenu
    frame_right = tk.Frame(root, bg="white")
    frame_right.pack(side="right", expand=True, fill="both")

    # Charger catégories depuis la base
    conn = sqlite3.connect(DB_NAME)
    cur = conn.cursor()
    cur.execute("SELECT id, nom FROM categories")
    categories = cur.fetchall()
    conn.close()

    def afficher_tutos(cat_id):
        # Nettoyer frame droit
        for widget in frame_right.winfo_children():
            widget.destroy()

        conn = sqlite3.connect(DB_NAME)
        cur = conn.cursor()
        cur.execute("SELECT titre, contenu FROM tutos WHERE categorie_id=?", (cat_id,))
        tutos = cur.fetchall()
        conn.close()

        for titre, contenu in tutos:
            lbl_titre = tk.Label(frame_right, text=titre, font=("Arial", 16, "bold"), anchor="w", bg="white")
            lbl_titre.pack(fill="x", padx=10, pady=5)

            lbl_contenu = tk.Label(frame_right, text=contenu, wraplength=600, justify="left", anchor="w", bg="white")
            lbl_contenu.pack(fill="x", padx=20, pady=2)

    # Boutons catégories
    for cat_id, nom in categories:
        btn = tk.Button(frame_left, text=nom, command=lambda cid=cat_id: afficher_tutos(cid), anchor="w")
        btn.pack(fill="x")

    root.mainloop()
