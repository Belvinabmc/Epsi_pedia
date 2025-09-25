import os
import tkinter as tk
from tkinter import messagebox
from PIL import Image, ImageTk
import sqlite3
DB_NAME = "database.db"

# --- chemins et couleurs ---
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
image_path = os.path.join(BASE_DIR, "asset", "images", "logo.sheald.png")

BG_COLOR = "#0d0d0d"      # Noir
PANEL_COLOR = "#1c1c1c"   # Gris foncé
TEXT_COLOR = "#e0e0e0"    # Gris clair
ACCENT = "#00aaff"        # Bleu ciel
DANGER = "#ff4d4d"        # Rouge vif

# ─────────────────────────────────────────────────────────────
# Utilitaire : Frame scrollable verticale (Canvas + Scrollbar)
# ─────────────────────────────────────────────────────────────
def make_scrollable(parent, bg_canvas=BG_COLOR, bg_inner=PANEL_COLOR):
    container = tk.Frame(parent, bg=bg_canvas)
    canvas = tk.Canvas(container, bg=bg_canvas, highlightthickness=0, bd=0)
    vsb = tk.Scrollbar(container, orient="vertical", command=canvas.yview, bg=bg_canvas, troughcolor=bg_canvas)
    inner = tk.Frame(canvas, bg=bg_inner)

    inner_id = canvas.create_window((0, 0), window=inner, anchor="nw")

    def _on_configure_inner(event=None):
        canvas.configure(scrollregion=canvas.bbox("all"))
        # adapter la largeur du inner au canvas
        canvas_width = canvas.winfo_width()
        canvas.itemconfig(inner_id, width=canvas_width)

    def _on_configure_canvas(event=None):
        canvas.configure(scrollregion=canvas.bbox("all"))

    inner.bind("<Configure>", _on_configure_inner)
    canvas.bind("<Configure>", _on_configure_inner)

    canvas.configure(yscrollcommand=vsb.set)
    canvas.pack(side="left", fill="both", expand=True)
    vsb.pack(side="right", fill="y")

    # molette souris
    def _on_mousewheel(event):
        # Windows / Linux (delta par 120)
        canvas.yview_scroll(int(-1 * (event.delta / 120)), "units")
    canvas.bind_all("<MouseWheel>", _on_mousewheel)

    return container, inner

# --------------------
# Fenêtre connexion admin (avec logo)
# --------------------
def ouvrir_connexion_admin():
    admin_win = tk.Toplevel()
    admin_win.title("Connexion Admin")
    admin_win.geometry("380x320")
    admin_win.config(bg=BG_COLOR)

    # --- logo ---
    try:
        img = Image.open(image_path)
        img = img.resize((120, 120))
        logo = ImageTk.PhotoImage(img)
        lbl_logo = tk.Label(admin_win, image=logo, bg=BG_COLOR)
        lbl_logo.image = logo
        lbl_logo.pack(pady=10)
    except Exception as e:
        print("Erreur chargement logo:", e)

    tk.Label(admin_win, text="Mot de passe admin :", font=("Arial", 12),
             bg=BG_COLOR, fg=TEXT_COLOR).pack(pady=10)

    entry_pwd = tk.Entry(admin_win, show="*", font=("Arial", 14),
                         justify="center", bg=PANEL_COLOR, fg=TEXT_COLOR,
                         insertbackground="white")
    entry_pwd.pack(pady=5)

    def check_admin():
        if entry_pwd.get() == "admin1234":  # ⚠️ à sécuriser
            admin_win.destroy()
            ouvrir_interface_admin()
        else:
            messagebox.showerror("Erreur", "Mot de passe incorrect")

    tk.Button(admin_win, text="Connexion", command=check_admin,
              font=("Arial", 12), bg=ACCENT, fg="white", relief="flat", padx=10, pady=5).pack(pady=15)

    entry_pwd.bind("<Return>", lambda e: check_admin())

# --------------------
# Interface Admin (avec sliders)
# --------------------
def ouvrir_interface_admin():
    admin_root = tk.Toplevel()
    admin_root.title("Epsipédia - Admin")
    admin_root.geometry("1000x650")
    admin_root.config(bg=BG_COLOR)

    # --- Header avec logo ---
    header = tk.Frame(admin_root, bg=PANEL_COLOR, height=80)
    header.pack(fill="x")

    try:
        img = Image.open(image_path)
        img = img.resize((60, 60))
        logo = ImageTk.PhotoImage(img)
        lbl_logo = tk.Label(header, image=logo, bg=PANEL_COLOR)
        lbl_logo.image = logo
        lbl_logo.pack(side="left", padx=20, pady=10)
    except Exception as e:
        print("Erreur chargement logo:", e)

    tk.Label(header, text="Panneau d'administration", font=("Arial", 16, "bold"),
             bg=PANEL_COLOR, fg=ACCENT).pack(side="left", padx=10)

    # --- Layout principal ---
    main = tk.Frame(admin_root, bg=BG_COLOR)
    main.pack(fill="both", expand=True)

    # Sidebar (gauche) avec scrollbar : Listbox + Scrollbar
    sidebar = tk.Frame(main, bg=PANEL_COLOR, width=240)
    sidebar.pack(side="left", fill="y")

    tk.Label(sidebar, text="Catégories", font=("Arial", 13, "bold"),
             bg=PANEL_COLOR, fg=TEXT_COLOR).pack(anchor="w", padx=10, pady=(12, 4))

    # conteneur listbox + scrollbar
    lb_frame = tk.Frame(sidebar, bg=PANEL_COLOR)
    lb_frame.pack(fill="both", expand=True, padx=8, pady=6)

    lb_scroll = tk.Scrollbar(lb_frame, orient="vertical")
    lb_scroll.pack(side="right", fill="y")

    listbox = tk.Listbox(lb_frame, yscrollcommand=lb_scroll.set,
                         bg=PANEL_COLOR, fg=TEXT_COLOR, selectbackground=ACCENT,
                         selectforeground="white", activestyle="none", borderwidth=0,
                         highlightthickness=1, highlightbackground="#2a2a2a",
                         font=("Arial", 11))
    listbox.pack(side="left", fill="both", expand=True)
    lb_scroll.config(command=listbox.yview)

    # Boutons sidebar
    tk.Button(sidebar, text="+ Ajouter catégorie", command=lambda: ajouter_categorie(refresh_categories),
              bg=ACCENT, fg="white", relief="flat").pack(fill="x", padx=8, pady=(4, 12))

    # Zone droite (cartes tutos) scrollable
    right = tk.Frame(main, bg=BG_COLOR)
    right.pack(side="right", fill="both", expand=True)

    # bouton “+ tuto” en haut
    top_bar = tk.Frame(right, bg=BG_COLOR)
    top_bar.pack(fill="x", pady=(8, 0))
    add_btn = tk.Button(top_bar, text="+ Ajouter tuto", bg=ACCENT, fg="white", relief="flat",
                        padx=10, command=lambda: ajouter_tuto(current_cat_id[0]))
    add_btn.pack(side="right", padx=10)

    # frame scrollable pour les cartes tutos
    tutos_container, tutos_inner = make_scrollable(right, bg_canvas=BG_COLOR, bg_inner=BG_COLOR)
    tutos_container.pack(fill="both", expand=True, padx=8, pady=8)

    # état courant
    current_cat_id = [None]
    cat_index_to_id = []  # mapping index -> id

    # ──────────────────────────
    # Fonctions Catégories
    # ──────────────────────────
    def refresh_categories():
        listbox.delete(0, tk.END)
        cat_index_to_id.clear()
        conn = sqlite3.connect(DB_NAME)
        cur = conn.cursor()
        cur.execute("SELECT id, nom FROM categories ORDER BY nom ASC")
        cats = cur.fetchall()
        conn.close()
        for cid, nom in cats:
            listbox.insert(tk.END, f"📁  {nom}")
            cat_index_to_id.append(cid)

    def on_select_category(event=None):
        if not listbox.curselection():
            return
        idx = listbox.curselection()[0]
        cid = cat_index_to_id[idx]
        current_cat_id[0] = cid
        afficher_tutos_admin(cid)

    listbox.bind("<<ListboxSelect>>", on_select_category)

    def ajouter_categorie(on_done):
        top = tk.Toplevel(admin_root)
        top.title("Nouvelle catégorie")
        top.config(bg=BG_COLOR)
        tk.Label(top, text="Nom de la catégorie :", bg=BG_COLOR, fg=TEXT_COLOR).pack(pady=6, padx=8, anchor="w")
        entry = tk.Entry(top, bg=PANEL_COLOR, fg=TEXT_COLOR, insertbackground="white")
        entry.pack(padx=8, fill="x")

        def valider():
            nom = entry.get().strip()
            if not nom:
                return
            conn = sqlite3.connect(DB_NAME)
            cur = conn.cursor()
            try:
                cur.execute("INSERT INTO categories(nom) VALUES (?)", (nom,))
                conn.commit()
            except sqlite3.IntegrityError:
                messagebox.showerror("Erreur", "Nom déjà existant")
            conn.close()
            top.destroy()
            on_done()

        btns = tk.Frame(top, bg=BG_COLOR)
        btns.pack(pady=10, padx=8, anchor="e", fill="x")
        tk.Button(btns, text="Annuler", command=top.destroy, bg="#3a3a3a", fg="white", relief="flat").pack(side="right", padx=6)
        tk.Button(btns, text="Valider", command=valider, bg=ACCENT, fg="white", relief="flat").pack(side="right")

    # ──────────────────────────
    # Fonctions Tutos (scrollables en cartes)
    # ──────────────────────────
    def afficher_tutos_admin(cat_id):
        # Nettoie le conteneur scrollable
        for w in tutos_inner.winfo_children():
            w.destroy()

        if cat_id is None:
            empty = tk.Label(tutos_inner, text="Sélectionnez une catégorie à gauche.",
                             bg=BG_COLOR, fg=TEXT_COLOR, font=("Arial", 12))
            empty.pack(pady=20, padx=10, anchor="w")
            return

        conn = sqlite3.connect(DB_NAME)
        cur = conn.cursor()
        cur.execute("SELECT id, titre, contenu FROM tutos WHERE categorie_id=? ORDER BY id DESC", (cat_id,))
        tutos = cur.fetchall()
        conn.close()

        if not tutos:
            empty = tk.Label(tutos_inner, text="Aucun tutoriel pour cette catégorie.",
                             bg=BG_COLOR, fg="#9aa0a6", font=("Arial", 12))
            empty.pack(pady=20, padx=10, anchor="w")
            return

        for tuto_id, titre, contenu in tutos:
            card = tk.Frame(tutos_inner, bg=PANEL_COLOR, bd=1, relief="groove")
            card.pack(fill="x", padx=6, pady=6)

            # Titre + boutons
            top = tk.Frame(card, bg=PANEL_COLOR)
            top.pack(fill="x", padx=8, pady=(8, 0))
            tk.Label(top, text=titre, font=("Arial", 14, "bold"),
                     bg=PANEL_COLOR, fg=ACCENT).pack(side="left", anchor="w")
            btns = tk.Frame(top, bg=PANEL_COLOR)
            btns.pack(side="right")
            tk.Button(btns, text="Modifier", command=lambda tid=tuto_id: modifier_tuto(tid),
                      bg=ACCENT, fg="white", relief="flat").pack(side="left", padx=4)
            tk.Button(btns, text="Supprimer", command=lambda tid=tuto_id: supprimer_tuto(tid),
                      bg=DANGER, fg="white", relief="flat").pack(side="left", padx=4)

            # Contenu
            body = tk.Frame(card, bg=PANEL_COLOR)
            body.pack(fill="x", padx=8, pady=(6, 10))
            tk.Label(body, text=contenu, wraplength=820, justify="left",
                     bg=PANEL_COLOR, fg=TEXT_COLOR, font=("Arial", 11)).pack(anchor="w")

    def ajouter_tuto(cat_id):
        if cat_id is None:
            messagebox.showinfo("Info", "Sélectionnez d'abord une catégorie.")
            return

        top = tk.Toplevel(admin_root)
        top.title("Nouveau tutoriel")
        top.config(bg=BG_COLOR)
        tk.Label(top, text="Titre :", bg=BG_COLOR, fg=TEXT_COLOR).pack(pady=(8, 2), padx=8, anchor="w")
        entry_titre = tk.Entry(top, bg=PANEL_COLOR, fg=TEXT_COLOR, insertbackground="white")
        entry_titre.pack(padx=8, fill="x")
        tk.Label(top, text="Contenu :", bg=BG_COLOR, fg=TEXT_COLOR).pack(pady=(8, 2), padx=8, anchor="w")
        entry_contenu = tk.Text(top, height=10, width=60, bg=PANEL_COLOR, fg=TEXT_COLOR, insertbackground="white", wrap="word")
        entry_contenu.pack(padx=8, pady=(0, 8))

        image_var = tk.StringVar(value="")
        def choisir_image():
            from tkinter import filedialog
            path = filedialog.askopenfilename(title="Choisir une image", filetypes=[("Images", "*.jpg *.jpeg *.png *.webp")])
            if path:
                import shutil
                dest_dir = os.path.join(BASE_DIR, "asset", "images_tuto")
                os.makedirs(dest_dir, exist_ok=True)
                dest_path = os.path.join(dest_dir, os.path.basename(path))
                shutil.copy2(path, dest_path)
                image_var.set(os.path.basename(path))
                lbl_img_sel.config(text=os.path.basename(path))

        def supprimer_image():
            image_var.set("")
            lbl_img_sel.config(text="Aucune image")

        img_frame = tk.Frame(top, bg=BG_COLOR)
        img_frame.pack(pady=(8,2), padx=8, anchor="w")
        tk.Label(img_frame, text="Image associée :", bg=BG_COLOR, fg=TEXT_COLOR).pack(side="left")
        lbl_img_sel = tk.Label(img_frame, text="Aucune image", bg=BG_COLOR, fg=ACCENT)
        lbl_img_sel.pack(side="left", padx=8)
        tk.Button(img_frame, text="Choisir...", command=choisir_image, bg=ACCENT, fg="white", relief="flat").pack(side="left", padx=4)
        tk.Button(img_frame, text="Supprimer", command=supprimer_image, bg=DANGER, fg="white", relief="flat").pack(side="left", padx=4)

        def valider():
            titre = entry_titre.get().strip()
            contenu = entry_contenu.get("1.0", "end").strip()
            img_path = image_var.get() if image_var.get() else None
            if not (titre and contenu):
                messagebox.showwarning("Champs manquants", "Merci de renseigner un titre et un contenu.")
                return
            conn = sqlite3.connect(DB_NAME)
            cur = conn.cursor()
            cur.execute("INSERT INTO tutos(titre, contenu, image_path, categorie_id) VALUES (?, ?, ?, ?)", (titre, contenu, img_path, cat_id))
            conn.commit()
            conn.close()
            top.destroy()
            afficher_tutos_admin(cat_id)

        btns = tk.Frame(top, bg=BG_COLOR)
        btns.pack(pady=10, padx=8, anchor="e", fill="x")
        tk.Button(btns, text="Annuler", command=top.destroy, bg="#3a3a3a", fg="white", relief="flat").pack(side="right", padx=6)
        tk.Button(btns, text="Valider", command=valider, bg=ACCENT, fg="white", relief="flat").pack(side="right")

    def modifier_tuto(tuto_id):
        conn = sqlite3.connect(DB_NAME)
        cur = conn.cursor()
        cur.execute("SELECT titre, contenu, image_path, categorie_id FROM tutos WHERE id=?", (tuto_id,))
        row = cur.fetchone()
        conn.close()
        if not row:
            return
        titre, contenu, image_path, cat_id = row

        top = tk.Toplevel(admin_root)
        top.title("Modifier le tutoriel")
        top.config(bg=BG_COLOR)
        tk.Label(top, text="Titre :", bg=BG_COLOR, fg=TEXT_COLOR).pack(pady=(8, 2), padx=8, anchor="w")
        entry_titre = tk.Entry(top, bg=PANEL_COLOR, fg=TEXT_COLOR, insertbackground="white")
        entry_titre.insert(0, titre)
        entry_titre.pack(padx=8, fill="x")
        tk.Label(top, text="Contenu :", bg=BG_COLOR, fg=TEXT_COLOR).pack(pady=(8, 2), padx=8, anchor="w")
        entry_contenu = tk.Text(top, height=10, width=60, bg=PANEL_COLOR, fg=TEXT_COLOR, insertbackground="white", wrap="word")
        entry_contenu.insert("1.0", contenu)
        entry_contenu.pack(padx=8, pady=(0, 8))

        image_var = tk.StringVar(value=image_path if image_path else "")
        def choisir_image():
            from tkinter import filedialog
            path = filedialog.askopenfilename(title="Choisir une image", filetypes=[("Images", "*.jpg *.jpeg *.png *.webp")])
            if path:
                import shutil
                dest_dir = os.path.join(BASE_DIR, "asset", "images_tuto")
                os.makedirs(dest_dir, exist_ok=True)
                dest_path = os.path.join(dest_dir, os.path.basename(path))
                shutil.copy2(path, dest_path)
                image_var.set(os.path.basename(path))
                lbl_img_sel.config(text=os.path.basename(path))

        def supprimer_image():
            image_var.set("")
            lbl_img_sel.config(text="Aucune image")

        img_frame = tk.Frame(top, bg=BG_COLOR)
        img_frame.pack(pady=(8,2), padx=8, anchor="w")
        tk.Label(img_frame, text="Image associée :", bg=BG_COLOR, fg=TEXT_COLOR).pack(side="left")
        lbl_img_sel = tk.Label(img_frame, text=image_path if image_path else "Aucune image", bg=BG_COLOR, fg=ACCENT)
        lbl_img_sel.pack(side="left", padx=8)
        tk.Button(img_frame, text="Choisir...", command=choisir_image, bg=ACCENT, fg="white", relief="flat").pack(side="left", padx=4)
        tk.Button(img_frame, text="Supprimer", command=supprimer_image, bg=DANGER, fg="white", relief="flat").pack(side="left", padx=4)

        def valider():
            new_titre = entry_titre.get().strip()
            new_contenu = entry_contenu.get("1.0", "end").strip()
            img_path = image_var.get() if image_var.get() else None
            if not (new_titre and new_contenu):
                messagebox.showwarning("Champs manquants", "Merci de renseigner un titre et un contenu.")
                return
            conn = sqlite3.connect(DB_NAME)
            cur = conn.cursor()
            cur.execute("UPDATE tutos SET titre=?, contenu=?, image_path=? WHERE id=?", (new_titre, new_contenu, img_path, tuto_id))
            conn.commit()
            conn.close()
            top.destroy()
            afficher_tutos_admin(cat_id)

        btns = tk.Frame(top, bg=BG_COLOR)
        btns.pack(pady=10, padx=8, anchor="e", fill="x")
        tk.Button(btns, text="Annuler", command=top.destroy, bg="#3a3a3a", fg="white", relief="flat").pack(side="right", padx=6)
        tk.Button(btns, text="Enregistrer", command=valider, bg=ACCENT, fg="white", relief="flat").pack(side="right")

    def supprimer_tuto(tuto_id):
        if messagebox.askyesno("Confirmer", "Supprimer ce tutoriel ?"):
            # On supprime et on rafraîchit la vue actuelle
            conn = sqlite3.connect(DB_NAME)
            cur = conn.cursor()
            cur.execute("DELETE FROM tutos WHERE id=?", (tuto_id,))
            conn.commit()
            conn.close()
            if current_cat_id[0] is not None:
                afficher_tutos_admin(current_cat_id[0])

    # Initialisation
    refresh_categories()
    admin_root.focus_force()
