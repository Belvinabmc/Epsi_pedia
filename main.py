# main.py
import tkinter as tk
from interface import ouvrir_interface
from admin import ouvrir_connexion_admin
from database import init_db

def main():
    # DB ready
    init_db()

    root = tk.Tk()
    root.title("Epsipédia - Menu principal")
    root.geometry("400x250")

    tk.Label(root, text="Bienvenue sur Epsipédia",
             font=("Arial", 16, "bold")).pack(pady=20)

    # On ouvre les écrans en leur passant *root* comme parent
    tk.Button(root, text="👤 Utilisateur",
              command=lambda: ouvrir_interface(root),
              font=("Arial", 14)).pack(pady=10)

    tk.Button(root, text="🔐 Admin",
              command=lambda: ouvrir_connexion_admin(root),
              font=("Arial", 14)).pack(pady=10)

    root.mainloop()

if __name__ == "__main__":
    main()
