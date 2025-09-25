# admin.py — Admin UI : gestion des médias + login sécurisé (mot de passe Argon2 + code offline)

import tkinter as tk
from tkinter import messagebox, filedialog, ttk
import sqlite3, shutil, os, json, time, hashlib
from pathlib import Path

from argon2 import PasswordHasher
from argon2.exceptions import VerifyMismatchError

from database import DB_NAME
from core.config import ASSETS, ALLOWED_EXT, STORAGE_PATH
from core.services.integrity_service import IntegrityService
from core.services.security_logger import log_event


# =============== Sécurité / Auth ===============

ADMIN_FILE = STORAGE_PATH / "admin.json"
PH = PasswordHasher()

def _load_admin() -> dict:
    ADMIN_FILE.parent.mkdir(parents=True, exist_ok=True)
    if ADMIN_FILE.exists():
        try:
            return json.loads(ADMIN_FILE.read_text(encoding="utf-8"))
        except Exception:
            pass
    return {}

def _save_admin(data: dict) -> None:
    ADMIN_FILE.parent.mkdir(parents=True, exist_ok=True)
    ADMIN_FILE.write_text(json.dumps(data, indent=2, ensure_ascii=False), encoding="utf-8")

def is_initialized() -> bool:
    data = _load_admin()
    return bool(data.get("pwd_hash"))

def initialize_admin(password: str) -> None:
    """Enregistre (ou remplace) le mot de passe admin en Argon2 (aucun stockage en clair)."""
    _save_admin({"pwd_hash": PH.hash(password)})
    log_event("ADMIN_INIT", "Mot de passe admin initialisé")

def verify_password_only(password: str) -> bool:
    data = _load_admin()
    h = data.get("pwd_hash")
    if not h:
        return False
    try:
        PH.verify(h, password)
        return True
    except VerifyMismatchError:
        return False
    except Exception:
        return False

def generate_offline_code() -> str:
    """
    Code à 6 chiffres OFFLINE, change toutes les 2 minutes.
    Basé sur l'heure locale et une clé fixe (non secrète).
    """
    window = int(time.time() // 120)  # tranche de 2 minutes
    seed = f"Epsipedia|{os.name}|{window}".encode()
    digest = hashlib.sha256(seed).digest()
    n = int.from_bytes(digest[:4], "big") % 1_000_000
    return f"{n:06d}"


# =============== Utilitaires UI ===============

def slugify(name: str) -> str:
    import unicodedata
    n = unicodedata.normalize("NFKD", name).encode("ascii", "ignore").decode("ascii")
    n = "".join(ch if ch.isalnum() else "_" for ch in n)
    n = "_".join(filter(None, n.split("_"))).lower()
    return n or "categorie"

def is_text_ext(p: Path) -> bool:
    return p.suffix.lower() in {".txt", ".md"}


# =============== Login Admin ===============

def ouvrir_connexion_admin(parent: tk.Misc):
    """
    1) Si pas initialisé → on demande de définir un mot de passe.
    2) Sinon → on affiche l'écran de connexion (mot de passe + code offline).
    """
    if not is_initialized():
        top = tk.Toplevel(parent)
        top.title("Initialiser l'administrateur")
        top.geometry("380x220")

        tk.Label(top, text="Choisissez un mot de passe admin :").pack(pady=(12, 4))
        e1 = tk.Entry(top, show="*"); e1.pack()
        tk.Label(top, text="Confirmez :").pack(pady=(10, 4))
        e2 = tk.Entry(top, show="*"); e2.pack()
        info = tk.Label(top, fg="#555"); info.pack(pady=6)

        def do_init():
            p1, p2 = e1.get().strip(), e2.get().strip()
            if not p1 or p1 != p2:
                info.config(text="Les mots de passe ne correspondent pas.")
                return
            initialize_admin(p1)
            messagebox.showinfo("Admin créé", "Mot de passe enregistré.")
            top.destroy()
            ouvrir_connexion_admin(parent)

        tk.Button(top, text="Initialiser", command=do_init).pack(pady=10)
        return

    # Sinon → écran de connexion
    win = tk.Toplevel(parent)
    win.title("Connexion Admin")
    win.geometry("360x240")

    # Affiche le code offline dans la console pour l'admin
    code_attendu = generate_offline_code()
    print(f"[SECURITE] Code de connexion actuel (2 min) : {code_attendu}")

    tk.Label(win, text="Mot de passe :").pack(pady=(14, 4))
    e_pwd = tk.Entry(win, show="*"); e_pwd.pack()

    tk.Label(win, text="Code de sécurité (6 chiffres) :").pack(pady=(10, 4))
    e_code = tk.Entry(win); e_code.pack()

    def submit():
        pwd = e_pwd.get().strip()
        code = e_code.get().strip()

        if not verify_password_only(pwd):
            messagebox.showerror("Authentification", "Mot de passe incorrect.")
            log_event("AUTH_FAIL", "bad_password")
            return

        if code != generate_offline_code():  # recalcule (au cas où)
            messagebox.showerror("Authentification", "Code de sécurité incorrect ou expiré.")
            log_event("AUTH_FAIL", "bad_offline_code")
            return

        log_event("AUTH_OK", "admin connecté")
        win.destroy()
        ouvrir_interface_admin(parent)

    tk.Button(win, text="Connexion", command=submit).pack(pady=12)
    e_code.bind("<Return>", lambda _: submit())


# =============== Interface Admin ===============

def ouvrir_interface_admin(parent: tk.Misc):
    root = tk.Toplevel(parent)
    root.title("Epsipédia - Admin")
    root.geometry("1040x680")

    frame_left = tk.Frame(root, width=280, bg="#EEE"); frame_left.pack(side="left", fill="y")
    frame_right = tk.Frame(root, bg="white");           frame_right.pack(side="right", expand=True, fill="both")

    # ---- Import de fichiers vers une catégorie ----
    def ouvrir_import_fichiers():
        top = tk.Toplevel(root)
        top.title("Importer fichiers → catégorie")
        top.geometry("480x320")

        tk.Label(top, text="Catégorie :").pack(anchor="w", padx=10, pady=(10,4))
        conn = sqlite3.connect(DB_NAME); cur = conn.cursor()
        cur.execute("SELECT id, nom FROM categories ORDER BY nom")
        cats = cur.fetchall(); conn.close()

        combo = ttk.Combobox(top, values=[c[1] for c in cats], state="readonly")
        if cats: combo.current(0)
        combo.pack(fill="x", padx=10)

        tk.Label(top, text="Sélectionner fichiers (pdf / images / vidéos / texte) :").pack(anchor="w", padx=10, pady=(10,4))
        files_var = tk.StringVar(value="(aucun fichier)")
        tk.Label(top, textvariable=files_var, wraplength=440, fg="#555").pack(anchor="w", padx=10)

        selected = []
        def choisir():
            paths = filedialog.askopenfilenames(
                parent=top, title="Choisir fichiers",
                filetypes=[
                    ("Fichiers autorisés", "*.pdf;*.jpg;*.jpeg;*.png;*.webp;*.gif;*.bmp;*.mp4;*.txt;*.md"),
                    ("Tous les fichiers", "*.*")
                ]
            )
            if paths:
                selected[:] = [Path(p) for p in paths]
                files_var.set("\n".join(p.name for p in selected))
        tk.Button(top, text="Parcourir…", command=choisir).pack(anchor="w", padx=10)

        def lancer_import():
            if not combo.get():
                messagebox.showwarning("Catégorie", "Choisis une catégorie."); return
            if not selected:
                messagebox.showwarning("Fichiers", "Aucun fichier sélectionné."); return

            cible = ASSETS / slugify(combo.get()); cible.mkdir(parents=True, exist_ok=True)
            imported, skipped = [], []
            for src in selected:
                if src.suffix.lower() not in ALLOWED_EXT:
                    skipped.append((src.name, "extension non autorisée"))
                    log_event("IMPORT_SKIP", src.name)
                    continue
                dst = cible / src.name
                i = 1
                while dst.exists():
                    dst = cible / f"{src.stem}_{i}{src.suffix}"; i += 1
                try:
                    shutil.copy2(src, dst)
                    imported.append(dst.name)
                    log_event("IMPORT_FILE", dst.as_posix())
                except Exception as e:
                    skipped.append((src.name, f"erreur: {e}"))
                    log_event("IMPORT_ERROR", f"{src.name} -> {e}")

            IntegrityService().rebuild_manifest()
            msg = f"✔ Importés : {len(imported)}\n✖ Ignorés : {len(skipped)}"
            if skipped: msg += "\n\n" + "\n".join(f"- {n} ({r})" for n, r in skipped)
            messagebox.showinfo("Import", msg, parent=top)
            top.destroy()
            sel = current_cat_id.get()
            if sel: afficher_tutos_admin(sel)

        tk.Button(top, text="Importer", command=lancer_import).pack(pady=10)

    tk.Button(frame_left, text="📥 Importer fichiers…",
              command=ouvrir_import_fichiers).pack(fill="x", padx=8, pady=8)

    # ---- Catégories / tutos ----
    current_cat_id = tk.IntVar(value=0)

    def refresh_categories():
        for w in list(frame_left.winfo_children())[1:]:  # garder le bouton d'import
            w.destroy()
        conn = sqlite3.connect(DB_NAME); cur = conn.cursor()
        cur.execute("SELECT id, nom FROM categories ORDER BY nom")
        cats = cur.fetchall(); conn.close()

        for cid, nom in cats:
            tk.Button(frame_left, text=nom, anchor="w",
                      command=lambda _cid=cid: (current_cat_id.set(_cid), afficher_tutos_admin(_cid)))\
                .pack(fill="x", padx=8, pady=2)
        tk.Button(frame_left, text="+ Ajouter catégorie", fg="#007700",
                  command=ajouter_categorie).pack(fill="x", padx=8, pady=10)

    def ajouter_categorie():
        top = tk.Toplevel(root); tk.Label(top, text="Nom catégorie :").pack()
        e = tk.Entry(top); e.pack()
        def valider():
            nom = e.get().strip()
            if not nom: return
            conn = sqlite3.connect(DB_NAME); cur = conn.cursor()
            try:
                cur.execute("INSERT INTO categories(nom) VALUES (?)", (nom,)); conn.commit()
            except sqlite3.IntegrityError:
                messagebox.showerror("Erreur", "Nom déjà existant")
            conn.close(); top.destroy(); refresh_categories()
        tk.Button(top, text="Valider", command=valider).pack()

    def renommer_categorie(cat_id):
        top = tk.Toplevel(root); tk.Label(top, text="Nouveau nom :").pack()
        e = tk.Entry(top); e.pack()
        def valider():
            nn = e.get().strip()
            if not nn: return
            conn = sqlite3.connect(DB_NAME); cur = conn.cursor()
            cur.execute("UPDATE categories SET nom=? WHERE id=?", (nn, cat_id)); conn.commit(); conn.close()
            top.destroy(); refresh_categories(); afficher_tutos_admin(cat_id)
        tk.Button(top, text="Valider", command=valider).pack()

    def supprimer_categorie(cat_id):
        if not messagebox.askyesno("Confirmer", "Supprimer cette catégorie ?"): return
        conn = sqlite3.connect(DB_NAME); cur = conn.cursor()
        cur.execute("DELETE FROM tutos WHERE categorie_id=?", (cat_id,))
        conn.commit()
        cur.execute("DELETE FROM categories WHERE id=?", (cat_id,))
        conn.commit(); conn.close()
        refresh_categories()
        for w in frame_right.winfo_children(): w.destroy()

    # ---- Affichage cartes : tutos + médias ----
    def afficher_tutos_admin(cat_id: int):
        for w in frame_right.winfo_children(): w.destroy()

        conn = sqlite3.connect(DB_NAME); cur = conn.cursor()
        cur.execute("SELECT nom FROM categories WHERE id=?", (cat_id,)); row = cur.fetchone()
        cat_name = row[0] if row else "?"
        conn.close()
        cat_slug = slugify(cat_name)

        tk.Label(frame_right, text=f"Catégorie : {cat_name}", bg="white",
                 font=("Arial", 14, "bold")).pack(anchor="w", padx=10, pady=(10,6))

        # Tutos (texte DB)
        conn = sqlite3.connect(DB_NAME); cur = conn.cursor()
        cur.execute("SELECT id, titre, contenu FROM tutos WHERE categorie_id=?", (cat_id,))
        tutos = cur.fetchall(); conn.close()

        for tid, titre, contenu in tutos:
            card = tk.Frame(frame_right, bg="white", relief="groove", bd=2)
            card.pack(fill="x", padx=10, pady=6)
            tk.Label(card, text=titre, font=("Arial", 12, "bold"), bg="white").pack(anchor="w", padx=8, pady=(6,2))
            tk.Label(card, text=contenu, bg="white", justify="left", wraplength=780)\
                .pack(anchor="w", padx=12, pady=(0,6))
            btns = tk.Frame(card, bg="white"); btns.pack(anchor="e", padx=6, pady=6)
            tk.Button(btns, text="Modifier", command=lambda _id=tid: modifier_tuto(_id)).pack(side="left", padx=3)
            tk.Button(btns, text="Supprimer", command=lambda _id=tid: supprimer_tuto(_id)).pack(side="left", padx=3)

        # Médias (fichiers importés)
        media_folder = ASSETS / cat_slug
        medias = []
        if media_folder.exists():
            for f in sorted(media_folder.iterdir()):
                if f.is_file() and f.suffix.lower() in ALLOWED_EXT:
                    medias.append(f)

        if medias:
            tk.Label(frame_right, text="Fichiers importés :", bg="white",
                     font=("Arial", 12, "bold")).pack(anchor="w", padx=10, pady=(12,4))
            for f in medias:
                card = tk.Frame(frame_right, bg="white", relief="ridge", bd=1)
                card.pack(fill="x", padx=10, pady=4)
                tk.Label(card, text=f.name, font=("Arial", 11, "bold"), bg="white")\
                    .pack(anchor="w", padx=8, pady=(6,2))

                btns = tk.Frame(card, bg="white"); btns.pack(anchor="e", padx=6, pady=6)

                def open_file(p=f):
                    try:
                        os.startfile(p)
                    except Exception as e:
                        messagebox.showerror("Ouverture", f"{p.name}\n{e}")

                def edit_text_file(p=f):
                    if not is_text_ext(p):
                        messagebox.showinfo("Édition", "Seuls .txt/.md sont éditables ici.")
                        return
                    top = tk.Toplevel(root); top.title(f"Modifier - {p.name}")
                    txt = tk.Text(top, width=90, height=26)
                    txt.insert("1.0", p.read_text(encoding="utf-8", errors="ignore"))
                    txt.pack()
                    def save():
                        p.write_text(txt.get("1.0", "end").rstrip("\n"), encoding="utf-8")
                        IntegrityService().rebuild_manifest()
                        log_event("MEDIA_EDIT", p.as_posix())
                        messagebox.showinfo("Édition", "Enregistré.")
                        top.destroy()
                    tk.Button(top, text="Enregistrer", command=save).pack(pady=6)

                def rename_file(p=f):
                    top = tk.Toplevel(root); top.title(f"Renommer - {p.name}")
                    e = tk.Entry(top, width=60); e.insert(0, p.name); e.pack(padx=10, pady=10)
                    def do():
                        new_name = e.get().strip()
                        if not new_name: return
                        dst = p.with_name(new_name)
                        if dst.exists():
                            messagebox.showwarning("Renommer", "Un fichier de ce nom existe déjà."); return
                        try:
                            p.rename(dst)
                            IntegrityService().rebuild_manifest()
                            log_event("MEDIA_RENAME", f"{p.name} -> {dst.name}")
                            afficher_tutos_admin(cat_id)
                            top.destroy()
                        except Exception as ex:
                            messagebox.showerror("Renommer", str(ex))
                    tk.Button(top, text="OK", command=do).pack(pady=6)

                def move_file(p=f):
                    top = tk.Toplevel(root); top.title(f"Déplacer - {p.name}")
                    conn = sqlite3.connect(DB_NAME); cur = conn.cursor()
                    cur.execute("SELECT id, nom FROM categories ORDER BY nom")
                    cats2 = cur.fetchall(); conn.close()
                    tk.Label(top, text="Nouvelle catégorie :").pack(padx=10, pady=(10,4))
                    combo2 = ttk.Combobox(top, values=[c[1] for c in cats2], state="readonly"); combo2.pack(padx=10)
                    if cats2: combo2.current(0)
                    def do():
                        target = ASSETS / slugify(combo2.get())
                        target.mkdir(parents=True, exist_ok=True)
                        dst = target / p.name
                        i = 1
                        while dst.exists():
                            dst = target / f"{p.stem}_{i}{p.suffix}"; i += 1
                        try:
                            shutil.move(str(p), str(dst))
                            IntegrityService().rebuild_manifest()
                            log_event("MEDIA_MOVE", f"{p.name} -> {dst.as_posix()}")
                            afficher_tutos_admin(cat_id); top.destroy()
                        except Exception as ex:
                            messagebox.showerror("Déplacer", str(ex))
                    tk.Button(top, text="Déplacer", command=do).pack(pady=8)

                def delete_file(p=f):
                    if not messagebox.askyesno("Supprimer", f"Supprimer {p.name} ?"):
                        return
                    try:
                        p.unlink()
                        IntegrityService().rebuild_manifest()
                        log_event("MEDIA_DELETE", p.as_posix())
                        afficher_tutos_admin(cat_id)
                    except Exception as e:
                        messagebox.showerror("Supprimer", str(e))

                tk.Button(btns, text="Ouvrir",   command=open_file).pack(side="left", padx=3)
                tk.Button(btns, text="Modifier", command=edit_text_file).pack(side="left", padx=3)
                tk.Button(btns, text="Renommer", command=rename_file).pack(side="left", padx=3)
                tk.Button(btns, text="Déplacer", command=move_file).pack(side="left", padx=3)
                tk.Button(btns, text="Supprimer",command=delete_file).pack(side="left", padx=3)
        else:
            tk.Label(frame_right, text="(Aucun fichier importé pour cette catégorie)",
                     bg="white", fg="#666").pack(anchor="w", padx=10, pady=(8,0))

    # CRUD tutos (texte)
    def ajouter_tuto(cat_id):
        top = tk.Toplevel(root); tk.Label(top, text="Titre :").pack()
        e_titre = tk.Entry(top); e_titre.pack()
        tk.Label(top, text="Contenu :").pack()
        e_txt = tk.Text(top, height=8, width=60); e_txt.pack()
        def valider():
            titre = e_titre.get().strip(); contenu = e_txt.get("1.0", "end").strip()
            if not titre or not contenu: return
            conn = sqlite3.connect(DB_NAME); cur = conn.cursor()
            cur.execute("INSERT INTO tutos(titre, contenu, categorie_id) VALUES (?,?,?)",
                        (titre, contenu, cat_id))
            conn.commit(); conn.close(); top.destroy(); afficher_tutos_admin(cat_id)
        tk.Button(top, text="Valider", command=valider).pack(pady=6)

    def modifier_tuto(tuto_id):
        conn = sqlite3.connect(DB_NAME); cur = conn.cursor()
        cur.execute("SELECT titre, contenu, categorie_id FROM tutos WHERE id=?", (tuto_id,))
        row = cur.fetchone(); conn.close()
        if not row: return
        titre, contenu, cat_id = row
        top = tk.Toplevel(root); tk.Label(top, text="Titre :").pack()
        e_titre = tk.Entry(top); e_titre.insert(0, titre); e_titre.pack()
        tk.Label(top, text="Contenu :").pack()
        e_txt = tk.Text(top, height=8, width=60); e_txt.insert("1.0", contenu); e_txt.pack()
        def valider():
            nt = e_titre.get().strip(); nc = e_txt.get("1.0","end").strip()
            if not nt or not nc: return
            conn = sqlite3.connect(DB_NAME); cur = conn.cursor()
            cur.execute("UPDATE tutos SET titre=?, contenu=? WHERE id=?", (nt, nc, tuto_id))
            conn.commit(); conn.close(); top.destroy(); afficher_tutos_admin(cat_id)
        tk.Button(top, text="Valider", command=valider).pack(pady=6)

    def supprimer_tuto(tuto_id):
        if not messagebox.askyesno("Confirmer", "Supprimer ce tuto ?"): return
        conn = sqlite3.connect(DB_NAME); cur = conn.cursor()
        cur.execute("DELETE FROM tutos WHERE id=?", (tuto_id,))
        conn.commit(); conn.close(); afficher_tutos_admin(current_cat_id.get())

    refresh_categories()
