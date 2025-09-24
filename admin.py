import tkinter as tk
from tkinter import messagebox
from database import DB_NAME
import sqlite3

def ouvrir_connexion_admin():
    admin_win = tk.Toplevel()
    admin_win.title("Connexion Admin")
    admin_win.geometry("350x200")

    tk.Label(admin_win, text="Mot de passe admin :", font=("Arial", 12)).pack(pady=20)
    entry_pwd = tk.Entry(admin_win, show="*", font=("Arial", 14), justify="center")
    entry_pwd.pack(pady=5)

    def check_admin():
        # Mot de passe admin en dur (à améliorer !)
        if entry_pwd.get() == "admin1234":
            admin_win.destroy()
            ouvrir_interface_admin()
        else:
            messagebox.showerror("Erreur", "Mot de passe incorrect")

    btn = tk.Button(admin_win, text="Connexion", command=check_admin, font=("Arial", 12))
    btn.pack(pady=15)
    entry_pwd.bind("<Return>", lambda e: check_admin())


def ouvrir_interface_admin():
    admin_root = tk.Toplevel()
    admin_root.title("Epsipédia - Admin")
    admin_root.geometry("900x600")

    # Frames
    frame_left = tk.Frame(admin_root, width=200, bg="#EEE")
    frame_left.pack(side="left", fill="y")
    frame_right = tk.Frame(admin_root, bg="white")
    frame_right.pack(side="right", expand=True, fill="both")

    # --- Gestion catégories ---
    def refresh_categories():
        for widget in frame_left.winfo_children():
            widget.destroy()
        conn = sqlite3.connect(DB_NAME)
        cur = conn.cursor()
        cur.execute("SELECT id, nom FROM categories")
        cats = cur.fetchall()
        conn.close()
        for cat_id, nom in cats:
            btn = tk.Button(frame_left, text=nom, anchor="w", command=lambda cid=cat_id: afficher_tutos_admin(cid))
            btn.pack(fill="x")
            btn_menu = tk.Menubutton(frame_left, text="⋮", relief="flat")
            menu = tk.Menu(btn_menu, tearoff=0)
            menu.add_command(label="Renommer", command=lambda cid=cat_id: renommer_categorie(cid))
            menu.add_command(label="Supprimer", command=lambda cid=cat_id: supprimer_categorie(cid))
            btn_menu.config(menu=menu)
            btn_menu.pack(fill="x")
        tk.Button(frame_left, text="+ Ajouter catégorie", command=ajouter_categorie, fg="#007700").pack(fill="x", pady=10)

    def ajouter_categorie():
        def valider():
            nom = entry.get()
            if nom:
                conn = sqlite3.connect(DB_NAME)
                cur = conn.cursor()
                try:
                    cur.execute("INSERT INTO categories(nom) VALUES (?)", (nom,))
                    conn.commit()
                except sqlite3.IntegrityError:
                    messagebox.showerror("Erreur", "Nom déjà existant")
                conn.close()
                top.destroy()
                refresh_categories()
        top = tk.Toplevel(admin_root)
        tk.Label(top, text="Nom de la catégorie :").pack()
        entry = tk.Entry(top)
        entry.pack()
        tk.Button(top, text="Valider", command=valider).pack()

    def renommer_categorie(cat_id):
        def valider():
            new_nom = entry.get()
            if new_nom:
                conn = sqlite3.connect(DB_NAME)
                cur = conn.cursor()
                cur.execute("UPDATE categories SET nom=? WHERE id=?", (new_nom, cat_id))
                conn.commit()
                conn.close()
                top.destroy()
                refresh_categories()
        top = tk.Toplevel(admin_root)
        tk.Label(top, text="Nouveau nom :").pack()
        entry = tk.Entry(top)
        entry.pack()
        tk.Button(top, text="Valider", command=valider).pack()

    def supprimer_categorie(cat_id):
        if messagebox.askyesno("Confirmer", "Supprimer cette catégorie ?"):
            conn = sqlite3.connect(DB_NAME)
            cur = conn.cursor()
            cur.execute("DELETE FROM categories WHERE id=?", (cat_id,))
            conn.commit()
            conn.close()
            refresh_categories()

    # --- Gestion tutos ---
    def afficher_tutos_admin(cat_id):
        for widget in frame_right.winfo_children():
            widget.destroy()
        conn = sqlite3.connect(DB_NAME)
        cur = conn.cursor()
        cur.execute("SELECT id, titre, contenu FROM tutos WHERE categorie_id=?", (cat_id,))
        tutos = cur.fetchall()
        conn.close()
        for tuto_id, titre, contenu in tutos:
            frame = tk.Frame(frame_right, bg="white", relief="groove", bd=2)
            frame.pack(fill="x", padx=10, pady=5)
            tk.Label(frame, text=titre, font=("Arial", 14, "bold"), bg="white").pack(anchor="w")
            tk.Label(frame, text=contenu, wraplength=600, justify="left", bg="white").pack(anchor="w")
            btns = tk.Frame(frame, bg="white")
            btns.pack(anchor="e")
            tk.Button(btns, text="Modifier", command=lambda tid=tuto_id: modifier_tuto(tid)).pack(side="left")
            tk.Button(btns, text="Supprimer", command=lambda tid=tuto_id: supprimer_tuto(tid)).pack(side="left")
        tk.Button(frame_right, text="+ Ajouter tuto", command=lambda: ajouter_tuto(cat_id), fg="#007700").pack(pady=10)

    def ajouter_tuto(cat_id):
        def valider():
            titre = entry_titre.get()
            contenu = entry_contenu.get("1.0", "end").strip()
            if titre and contenu:
                conn = sqlite3.connect(DB_NAME)
                cur = conn.cursor()
                cur.execute("INSERT INTO tutos(titre, contenu, categorie_id) VALUES (?, ?, ?)", (titre, contenu, cat_id))
                conn.commit()
                conn.close()
                top.destroy()
                afficher_tutos_admin(cat_id)
        top = tk.Toplevel(admin_root)
        tk.Label(top, text="Titre :").pack()
        entry_titre = tk.Entry(top)
        entry_titre.pack()
        tk.Label(top, text="Contenu :").pack()
        entry_contenu = tk.Text(top, height=8, width=40)
        entry_contenu.pack()
        tk.Button(top, text="Valider", command=valider).pack()

    def modifier_tuto(tuto_id):
        conn = sqlite3.connect(DB_NAME)
        cur = conn.cursor()
        cur.execute("SELECT titre, contenu, categorie_id FROM tutos WHERE id=?", (tuto_id,))
        row = cur.fetchone()
        conn.close()
        if not row:
            return
        titre, contenu, cat_id = row
        def valider():
            new_titre = entry_titre.get()
            new_contenu = entry_contenu.get("1.0", "end").strip()
            if new_titre and new_contenu:
                conn = sqlite3.connect(DB_NAME)
                cur = conn.cursor()
                cur.execute("UPDATE tutos SET titre=?, contenu=? WHERE id=?", (new_titre, new_contenu, tuto_id))
                conn.commit()
                conn.close()
                top.destroy()
                afficher_tutos_admin(cat_id)
        top = tk.Toplevel(admin_root)
        tk.Label(top, text="Titre :").pack()
        entry_titre = tk.Entry(top)
        entry_titre.insert(0, titre)
        entry_titre.pack()
        tk.Label(top, text="Contenu :").pack()
        entry_contenu = tk.Text(top, height=8, width=40)
        entry_contenu.insert("1.0", contenu)
        entry_contenu.pack()
        tk.Button(top, text="Valider", command=valider).pack()

    def supprimer_tuto(tuto_id):
        if messagebox.askyesno("Confirmer", "Supprimer ce tuto ?"):
            conn = sqlite3.connect(DB_NAME)
            cur = conn.cursor()
            cur.execute("DELETE FROM tutos WHERE id=?", (tuto_id,))
            conn.commit()
            conn.close()
            refresh_categories()

    refresh_categories()
    admin_root.mainloop()

