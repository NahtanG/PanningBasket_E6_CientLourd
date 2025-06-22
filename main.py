from ui.weekly_view import WeeklyPlanner
import tkinter as tk

def main():
    root = tk.Tk()
    root.title("PlanningBasket")  # Nom de l'application changé ici
    # --- Définir l'icône de la fenêtre ---
    try:
        import sys
        if sys.platform.startswith("win"):
            root.iconbitmap("assets/basket.ico")
        else:
            # Pour Mac/Linux, il faut un .png (transparence gérée)
            icon = tk.PhotoImage(file="assets/basket.png")
            root.iconphoto(True, icon)
    except Exception as e:
        print("Impossible de charger l'icône personnalisée :", e)
    # --- Fin icône ---
    app = WeeklyPlanner(root)
    app.pack(fill="both", expand=True)
    root.mainloop()

if __name__ == "__main__":
    main()