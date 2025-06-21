from ui.weekly_view import WeeklyPlanner
import tkinter as tk

def main():
    root = tk.Tk()
    root.title("Planification des Entraînements Basket")
    app = WeeklyPlanner(root)
    app.pack(fill="both", expand=True)
    root.mainloop()

if __name__ == "__main__":
    main()