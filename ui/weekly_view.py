# ui/weekly_view.py
import tkinter as tk
from tkinter import simpledialog, messagebox, filedialog
from datetime import datetime, timedelta, time
from db.database import get_trainings_for_week, add_training, delete_training, update_training, get_trainings_for_month
from models.training import Training
from utils.date_utils import get_week_dates
from exporter.pdf_exporter import export_trainings_to_pdf
import hashlib
import colorsys
from datetime import datetime
import calendar

class WeeklyPlanner(tk.Frame):
    def __init__(self, master):
        super().__init__(master)
        self.current_date = datetime.now().date()
        self.category_colors = {}  # Ajouté
        self.init_ui()

    def get_category_color(self, category):
        """Retourne une couleur pastel unique pour chaque catégorie."""
        if category not in self.category_colors:
            # Hash la catégorie pour obtenir une couleur stable
            h = int(hashlib.md5(category.encode()).hexdigest(), 16)
            hue = (h % 360) / 360.0
            lightness = 0.8
            saturation = 0.5
            r, g, b = colorsys.hls_to_rgb(hue, lightness, saturation)
            hex_color = '#%02x%02x%02x' % (int(r*255), int(g*255), int(b*255))
            self.category_colors[category] = hex_color
        return self.category_colors[category]

    def init_ui(self):
        self.header = tk.Frame(self)
        self.header.pack(fill="x")

        self.header.grid_columnconfigure(0, weight=1)
        self.header.grid_columnconfigure(1, weight=2)
        self.header.grid_columnconfigure(2, weight=1)

        self.prev_btn = tk.Button(self.header, text="<", command=self.prev_week)
        self.prev_btn.grid(row=0, column=0, sticky="w", padx=10)

        self.month_year_label = tk.Label(self.header, font=("Segoe UI", 14, "bold"))
        self.month_year_label.grid(row=0, column=1, sticky="nsew", padx=10)

        right_btns = tk.Frame(self.header)
        self.export_btn = tk.Button(right_btns, text="Exporter PDF", command=self.export_pdf)
        self.export_btn.pack(side="left", padx=5)
        self.next_btn = tk.Button(right_btns, text=">", command=self.next_week)
        self.next_btn.pack(side="left", padx=5)
        right_btns.grid(row=0, column=2, sticky="e", padx=10)

        self.canvas_frame = tk.Frame(self)
        self.canvas_frame.pack(fill="both", expand=True)

        self.canvas = tk.Canvas(self.canvas_frame, width=1000, height=960)
        self.canvas.pack(side="left", fill="both", expand=True)

        self.master.geometry("980x960")
        self.master.lift()
        self.master.attributes("-topmost", True)
        self.master.after(0, lambda: self.master.attributes("-topmost", False))
        self.draw_table()

    def draw_table(self):
        self.canvas.delete("all")

        # Met à jour le label mois/année
        month_name = calendar.month_name[self.current_date.month].capitalize()
        year = self.current_date.year
        self.month_year_label.config(text=f"{month_name} {year}")

        self.slots = {}
        start_time = time(8, 0)
        end_time = time(22, 0)
        week_dates = get_week_dates(self.current_date)
        slot_height = 40
        slot_width = 120

        for i, date in enumerate(week_dates):
            self.canvas.create_text(60 + i*slot_width + slot_width//2 - 5, 10, text=date.strftime("%A"), font=("Segoe UI", 10, "bold"), fill="#ffffff", anchor="n")
            self.canvas.create_text(60 + i*slot_width + slot_width//2 - 5, 30, text=date.strftime("%d/%m"), font=("Segoe UI", 9), fill="#ffffff", anchor="n")

        def make_bindings(r, d, t):
            def on_enter(event): self.canvas.itemconfig(r, fill="#e6f7ff")
            def on_leave(event): self.canvas.itemconfig(r, fill="#ffffff")
            def on_press(event): self.canvas.itemconfig(r, fill="#b3e5fc")
            def on_release(event): self.canvas.itemconfig(r, fill="#e6f7ff"); self.add_popup(d, t)

            self.canvas.tag_bind(r, "<Enter>", on_enter)
            self.canvas.tag_bind(r, "<Leave>", on_leave)
            self.canvas.tag_bind(r, "<ButtonPress-1>", on_press)
            self.canvas.tag_bind(r, "<ButtonRelease-1>", on_release)

        for row, minutes in enumerate(range(12*60, 21*60 + 30, 30)):
            t = time(minutes//60, minutes%60)
            self.canvas.create_text(30, 60 + row*slot_height, text=t.strftime("%H:%M"), fill="#ffffff")
            for col, date in enumerate(week_dates):
                x, y = 60 + col*slot_width, 60 + row*slot_height
                rect = self.canvas.create_rectangle(x, y, x+slot_width-10, y+slot_height, fill="#ffffff", outline="#cccccc", width=1)
                self.canvas.create_line(x, y, x+slot_width-10, y, fill="#dddddd")

                make_bindings(rect, date, t)

                self.slots[(date, t)] = rect
        # Affiche "22:00" sous le dernier créneau
        self.canvas.create_text(30, 60 + (row + 1)*slot_height, text="22:00", fill="#ffffff")

        self.draw_trainings()

    def draw_trainings(self):
        trainings = get_trainings_for_week(self.current_date)
        for t in trainings:
            col = (t.date.weekday())
            row = ((t.start_time.hour - 12) * 2) + (1 if t.start_time.minute == 30 else 0)
            x, y = 60 + col*120, 60 + row*40
            h = int(((t.end_time.hour - t.start_time.hour) * 2 + (t.end_time.minute - t.start_time.minute)//30) * 40)
            color = self.get_category_color(t.category)
            # Couleur de contour plus sobre
            item = self.canvas.create_rectangle(
                x, y, x+110, y+h,
                fill=color,
                outline="#4a5a6a",  # bleu-gris foncé, sobre et bien visible
                width=1.5
            )
            text = self.canvas.create_text(x+5, y+5, anchor="nw", text=f"{t.category}\n{t.description}", font=("Segoe UI", 9), fill="#000000")
            self.canvas.tag_bind(item, "<Button-3>", lambda e, t=t: self.open_edit_popup(t))
            self.canvas.tag_bind(item, "<Double-Button-1>", lambda e, t=t: self.open_edit_popup(t))

    def add_popup(self, date, start_time):
        popup = tk.Toplevel(self)
        popup.title("Ajouter un entraînement")
        popup.geometry("320x280")
        popup.grab_set()

        tk.Label(popup, text="Catégorie :").pack(pady=(10, 0))
        category_entry = tk.Entry(popup)
        category_entry.pack(pady=5)

        tk.Label(popup, text="Description :").pack(pady=(10, 0))
        description_entry = tk.Entry(popup)
        description_entry.pack(pady=5)

        tk.Label(popup, text="Heure de fin :").pack(pady=(10, 0))
        
        # Créneaux valides de fin à partir de start_time jusqu'à 22:00
        possible_end_times = []
        current_minutes = start_time.hour * 60 + start_time.minute + 30
        while current_minutes <= 22 * 60:
            h = current_minutes // 60
            m = current_minutes % 60
            possible_end_times.append(f"{h:02}:{m:02}")
            current_minutes += 30

        end_time_var = tk.StringVar(popup)
        if possible_end_times:
            end_time_var.set(possible_end_times[0])

        end_time_menu = tk.OptionMenu(popup, end_time_var, *possible_end_times)
        end_time_menu.pack(pady=10)

        def submit():
            category = category_entry.get()
            description = description_entry.get()
            try:
                end_hour, end_min = map(int, end_time_var.get().split(":"))
                end_time = time(end_hour, end_min)
                if end_time <= start_time:
                    raise ValueError("L’heure de fin doit être après l’heure de début.")
                new_t = Training(category=category, description=description, date=date, start_time=start_time, end_time=end_time)
                add_training(new_t)
                self.draw_table()
                popup.destroy()
            except Exception as e:
                messagebox.showerror("Erreur", str(e))

        add_btn = tk.Button(popup, text="Ajouter", command=submit, relief="raised", bd=3, font=("Segoe UI", 10, "bold"))
        add_btn.pack(pady=(10, 20))

    def edit_popup(self, training):
        description = simpledialog.askstring("Description", "", initialvalue=training.description)
        category = simpledialog.askstring("Catégorie", "", initialvalue=training.category)
        end_time_str = simpledialog.askstring("Heure de fin", "Format HH:MM", initialvalue=training.end_time.strftime("%H:%M"))
        try:
            end_hour, end_min = map(int, end_time_str.split(":"))
            training.description = description
            training.category = category
            training.end_time = time(end_hour, end_min)
            update_training(training)
            self.draw_table()
        except Exception as e:
            messagebox.showerror("Erreur", str(e))

    def delete_training(self, training_id):
        delete_training(training_id)
        self.draw_table()

    def prev_week(self):
        self.current_date -= timedelta(days=7)
        self.draw_table()

    def next_week(self):
        self.current_date += timedelta(days=7)
        self.draw_table()

    def export_pdf(self):
        popup = tk.Toplevel(self)
        popup.title("Exporter au format PDF")
        popup.geometry("340x320")
        popup.grab_set()

        # Choix de l'année
        tk.Label(popup, text="Année :").pack(pady=(10, 0))
        year_var = tk.StringVar(popup)
        year_choices = [str(y) for y in range(2023, 2031)]
        year_var.set(str(datetime.now().year))
        year_menu = tk.OptionMenu(popup, year_var, *year_choices)
        year_menu.pack(pady=5)

        # Choix du mois
        tk.Label(popup, text="Mois :").pack(pady=(10, 0))
        month_var = tk.StringVar(popup)
        month_choices = [f"{i:02}" for i in range(1, 13)]
        month_var.set(f"{datetime.now().month:02}")
        month_menu = tk.OptionMenu(popup, month_var, *month_choices)
        month_menu.pack(pady=5)

        # Choix de la catégorie
        tk.Label(popup, text="Catégorie :").pack(pady=(10, 0))
        category_var = tk.StringVar(popup)
        from db.database import get_all_categories
        categories = get_all_categories()
        category_choices = ["Toutes"] + categories
        category_var.set("Toutes")
        category_menu = tk.OptionMenu(popup, category_var, *category_choices)
        category_menu.pack(pady=5)

        # Bouton Exporter
        def do_export():
            try:
                year = int(year_var.get())
                month = int(month_var.get())
                category = category_var.get()
                trainings = get_trainings_for_month(year, month, category)
                filepath = filedialog.asksaveasfilename(defaultextension=".pdf", filetypes=[("PDF files", "*.pdf")])
                if filepath:
                    export_trainings_to_pdf(trainings, filepath)
                    messagebox.showinfo("Exporté", f"PDF généré : {filepath}")
                    popup.destroy()
            except Exception as e:
                messagebox.showerror("Erreur", str(e))

        export_btn = tk.Button(popup, text="Exporter", command=do_export, relief="raised", bd=3, font=("Segoe UI", 10, "bold"))
        export_btn.pack(pady=20)

    def open_edit_popup(self, training):
        popup = tk.Toplevel(self)
        popup.title("Modifier l'entraînement")
        popup.geometry("340x350")
        popup.grab_set()

        tk.Label(popup, text="Catégorie :").pack(pady=(10, 0))
        category_entry = tk.Entry(popup)
        category_entry.insert(0, training.category)
        category_entry.pack(pady=5)

        tk.Label(popup, text="Description :").pack(pady=(10, 0))
        description_entry = tk.Entry(popup)
        description_entry.insert(0, training.description)
        description_entry.pack(pady=5)

        tk.Label(popup, text="Heure de début :").pack(pady=(10, 0))
        start_var = tk.StringVar(popup)
        all_times = [f"{h:02}:{m:02}" for h in range(12, 22) for m in (0,30)]
        start_str = training.start_time.strftime("%H:%M")
        start_var.set(start_str)

        start_menu = tk.OptionMenu(popup, start_var, *all_times)
        start_menu.pack(pady=5)

        tk.Label(popup, text="Heure de fin :").pack(pady=(10, 0))
        end_var = tk.StringVar(popup)
        def update_end_times(*_):
            selected_start = start_var.get()
            h, m = map(int, selected_start.split(":"))
            end_options = []
            total_minutes = h * 60 + m + 30
            while total_minutes <= 22 * 60:
                eh = total_minutes // 60
                em = total_minutes % 60
                end_options.append(f"{eh:02}:{em:02}")
                total_minutes += 30
            current_end = end_var.get()
            menu = end_menu["menu"]
            menu.delete(0, "end")
            for val in end_options:
                menu.add_command(label=val, command=lambda v=val: end_var.set(v))
            if current_end in end_options:
                end_var.set(current_end)
            elif end_options:
                end_var.set(end_options[0])

        end_menu = tk.OptionMenu(popup, end_var, "")
        end_menu.pack(pady=5)
        start_var.trace_add("write", update_end_times)
        start_var.set(start_str)  # Triggers end time update

        # Set end_var to current training's end_time if possible
        end_var.set(training.end_time.strftime("%H:%M"))

        def save():
            try:
                category = category_entry.get()
                description = description_entry.get()
                start_h, start_m = map(int, start_var.get().split(":"))
                end_h, end_m = map(int, end_var.get().split(":"))
                start_time_val = time(start_h, start_m)
                end_time_val = time(end_h, end_m)
                if end_time_val <= start_time_val:
                    raise ValueError("L’heure de fin doit être après celle de début.")
                training.category = category
                training.description = description
                training.start_time = start_time_val
                training.end_time = end_time_val
                update_training(training)
                self.draw_table()
                popup.destroy()
            except Exception as e:
                messagebox.showerror("Erreur", str(e))

        def delete():
            delete_training(training.id)
            self.draw_table()
            popup.destroy()

        btn_frame = tk.Frame(popup)
        btn_frame.pack(pady=20)

        tk.Button(btn_frame, text="Valider", command=save, relief="raised", bd=3, font=("Segoe UI", 10, "bold")).pack(side="left", padx=5)
        tk.Button(btn_frame, text="Supprimer", command=delete, relief="raised", bd=3, font=("Segoe UI", 10, "bold")).pack(side="left", padx=5)
        tk.Button(btn_frame, text="Annuler", command=popup.destroy, relief="raised", bd=3, font=("Segoe UI", 10, "bold")).pack(side="left", padx=5)