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
import calendar
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

def wrap_text(text, width=22, max_lines=None, force_single_line=False):
    """
    Coupe le texte en lignes de longueur maximale 'width', en conservant les retours à la ligne utilisateur
    sauf si force_single_line=True (dans ce cas, tout est sur une seule ligne).
    Si max_lines est défini, coupe à ce nombre de lignes et ajoute '...' si besoin.
    """
    if force_single_line:
        # Remplace tous les retours à la ligne par des espaces
        text = text.replace('\n', ' ')
    lines = []
    for paragraph in text.splitlines():
        words = paragraph.split()
        current = ""
        for word in words:
            if len(current + " " + word) <= width:
                current = (current + " " + word).strip()
            else:
                lines.append(current)
                current = word
        if current:
            lines.append(current)
        if not force_single_line and paragraph != text.splitlines()[-1]:
            lines.append("")
    if max_lines is not None and len(lines) > max_lines:
        lines = lines[:max_lines]
        if lines:
            lines[-1] = lines[-1].rstrip() + "..."
    return "\n".join(lines)

class WeeklyPlanner(tk.Frame):
    def __init__(self, master):
        super().__init__(master, bg="#f7f7f9")
        self.current_date = datetime.now().date()
        self.category_colors = {}
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
        self.master.configure(bg="#f7f7f9")
        self.configure(bg="#f7f7f9")

        self.header = tk.Frame(self, bg="#f7f7f9")
        self.header.pack(fill="x")

        self.header.grid_columnconfigure(0, weight=1)
        self.header.grid_columnconfigure(1, weight=2)
        self.header.grid_columnconfigure(2, weight=1)
        self.header.grid_columnconfigure(3, weight=2)
        self.header.grid_columnconfigure(4, weight=1)

        nav_btn_style = {
            "font": ("Segoe UI", 14, "bold"),
            "bg": "#f7f7f9",
            "fg": "#4a5a6a",
            "activebackground": "#e0e4ea",
            "activeforeground": "#2d3a4a",
            "bd": 0,
            "relief": "flat",
            "width": 2,
            "cursor": "hand2",
            "highlightthickness": 0,
            "highlightbackground": "#f7f7f9"
        }
        self.prev_btn = tk.Button(self.header, text="←", command=self.prev_week, **nav_btn_style)
        self.prev_btn.grid(row=0, column=0, sticky="w", padx=10)

        self.month_year_label = tk.Label(
            self.header,
            font=("Segoe UI", 20, "bold"),
            fg="#2d3a4a",
            bg="#f7f7f9",
            pady=8
        )
        self.month_year_label.grid(row=0, column=1, sticky="nsew", padx=10)

        right_btns = tk.Frame(self.header, bg="#f7f7f9")
        self.export_btn = tk.Button(
            right_btns,
            text="Exporter PDF",
            font=("Segoe UI", 11, "bold"),
            bg="#f7f7f9",
            fg="#4a5a6a",
            activebackground="#e0e4ea",
            activeforeground="#2d3a4a",
            bd=0,
            relief="flat",
            padx=10,
            pady=2,
            cursor="hand2",
            highlightthickness=0,
            highlightbackground="#f7f7f9",
            command=self.export_pdf
        )
        self.export_btn.pack(side="left", padx=5)
        self.next_btn = tk.Button(right_btns, text="→", command=self.next_week, **nav_btn_style)
        self.next_btn.pack(side="left", padx=5)
        right_btns.grid(row=0, column=2, sticky="e", padx=10)

        self.stats_btn = tk.Button(
            self.header,
            text="📊 Statistiques",
            font=("Segoe UI", 11, "bold"),
            bg="#f7f7f9",
            fg="#4a5a6a",
            activebackground="#e0e4ea",
            activeforeground="#2d3a4a",
            bd=0,
            relief="flat",
            padx=10,
            pady=2,
            cursor="hand2",
            highlightthickness=0,
            highlightbackground="#f7f7f9",
            command=self.show_stats_popup
        )
        self.stats_btn.grid(row=0, column=4, sticky="e", padx=(0, 10))

        # --- BARRE DE RECHERCHE ---
        search_frame = tk.Frame(self.header, bg="#f7f7f9")
        search_frame.grid(row=0, column=3, sticky="e", padx=(10, 20))
        tk.Label(search_frame, text="🔍", bg="#f7f7f9", fg="#4a5a6a", font=("Segoe UI", 12)).pack(side="left")
        self.search_var = tk.StringVar()
        search_entry = tk.Entry(
            search_frame,
            textvariable=self.search_var,
            width=18,
            font=("Segoe UI", 10),
            bg="#ffffff",
            fg="#222222",
            insertbackground="#222222"
        )
        search_entry.pack(side="left", padx=2)
        search_entry.bind("<KeyRelease>", lambda e: self.draw_table())

        self.canvas_frame = tk.Frame(self, bg="#f7f7f9")
        self.canvas_frame.pack(fill="both", expand=True)

        self.canvas = tk.Canvas(self.canvas_frame, bg="#f7f7f9", highlightthickness=0)
        self.canvas.pack(side="left", fill="both", expand=True)
        self.canvas.bind("<Configure>", self.on_canvas_resize)

        self.master.geometry("980x960")
        self.master.minsize(800, 600)
        self.master.lift()
        self.master.attributes("-topmost", True)
        self.master.after(0, lambda: self.master.attributes("-topmost", False))
        self.draw_table()

    def on_canvas_resize(self, event):
        self.draw_table()

    def draw_table(self):
        self.canvas.delete("all")
        canvas_width = self.canvas.winfo_width()
        canvas_height = self.canvas.winfo_height()
        slot_width = max(60, (canvas_width - 60) // 7)
        slot_height = max(20, (canvas_height - 60) // 20)

        month_name = calendar.month_name[self.current_date.month].capitalize()
        year = self.current_date.year
        week_number = self.current_date.isocalendar()[1]
        self.month_year_label.config(text=f"{month_name} {year} – Semaine {week_number}")

        self.slots = {}
        week_dates = get_week_dates(self.current_date)

        border_color = "#bbbbbb"
        fill_color = "#ffffff"
        text_gray = "#888888"

        for i, date in enumerate(week_dates):
            x_center = 60 + i*slot_width + slot_width//2 - 5
            self.canvas.create_rectangle(
                x_center-45, 5, x_center+45, 55,
                fill=fill_color, outline=border_color, width=2
            )
            self.canvas.create_text(
                x_center, 18,
                text=date.strftime("%A"),
                font=("Segoe UI", 10, "bold"),
                fill=text_gray
            )
            self.canvas.create_text(
                x_center, 38,
                text=date.strftime("%d/%m"),
                font=("Segoe UI", 9),
                fill=text_gray
            )

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
            y_center = 60 + row*slot_height
            self.canvas.create_rectangle(
                5, y_center-15, 55, y_center+15,
                fill=fill_color, outline=border_color, width=2
            )
            self.canvas.create_text(
                30, y_center,
                text=t.strftime("%H:%M"),
                font=("Segoe UI", 10, "bold"),
                fill=text_gray
            )
            for col, date in enumerate(week_dates):
                x, y = 60 + col*slot_width, 60 + row*slot_height
                rect = self.canvas.create_rectangle(x, y, x+slot_width-10, y+slot_height, fill="#ffffff", outline="#cccccc", width=1)
                self.canvas.create_line(x, y, x+slot_width-10, y, fill="#dddddd")
                make_bindings(rect, date, t)
                self.slots[(date, t)] = rect
        self.canvas.create_rectangle(
            5, 60 + (row + 1)*slot_height - 15, 55, 60 + (row + 1)*slot_height + 15,
            fill=fill_color, outline=border_color, width=2
        )
        self.canvas.create_text(
            30, 60 + (row + 1)*slot_height,
            text="22:00",
            font=("Segoe UI", 10, "bold"),
            fill=text_gray
        )

        self.draw_trainings(
            fade=getattr(self, "_fade_events", False),
            slot_width=slot_width,
            slot_height=slot_height
        )
        self._fade_events = False

    def fade_in_events(self, events_data, slot_width, slot_height, steps=10, delay=20):
        # --- Ajout du wrapping dynamique ---
        if slot_width < 80:
            wrap_chars = 10
            force_single_line = True
            max_lines = 1
        elif slot_width < 120:
            wrap_chars = 15
            force_single_line = False
            max_lines = 2
        else:
            wrap_chars = 22
            force_single_line = False
            max_lines = 4

        min_font = 7
        max_font = 11
        font_size = max(min_font, min(max_font, int((slot_width-10) / 10)))
        event_font = ("Segoe UI", font_size)
        # --- Fin ajout wrapping dynamique ---

        for step in range(1, steps + 1):
            alpha = step / steps
            for event in events_data:
                x, y, h, color, outline, text, t = event
                # Wrapping dynamique pour affichage
                text = f"{t.category}\n{wrap_text(t.description, width=wrap_chars, max_lines=max_lines, force_single_line=force_single_line)}"
                r1, g1, b1 = self.winfo_rgb("#ffffff")
                r2, g2, b2 = self.winfo_rgb(color)
                r = int(r1 + (r2 - r1) * alpha) // 256
                g = int(g1 + (g2 - g1) * alpha) // 256
                b = int(b1 + (b2 - b1) * alpha) // 256
                fade_color = f"#{r:02x}{g:02x}{b:02x}"
                rect = self.canvas.create_rectangle(
                    x, y, x+slot_width-10, y+h,
                    fill=fade_color,
                    outline=outline,
                    width=1.5,
                    tags="event_fade"
                )
                txt = self.canvas.create_text(
                    x+5, y+5, anchor="nw", text=text, font=event_font, fill="#000000", tags="event_fade"
                )
                def on_enter(event, item=rect, txt=txt):
                    self.canvas.itemconfig(item, outline="#2d3a4a", width=2.5)
                    self.canvas.tag_raise(item)
                    self.canvas.tag_raise(txt)
                    self.canvas.config(cursor="hand2")
                def on_leave(event, item=rect):
                    self.canvas.itemconfig(item, outline="#4a5a6a", width=1.5)
                    self.canvas.config(cursor="")
                def on_click(event, t=t):
                    self.open_edit_popup(t)
                self.canvas.tag_bind(rect, "<Enter>", on_enter)
                self.canvas.tag_bind(rect, "<Leave>", on_leave)
                self.canvas.tag_bind(rect, "<Button-1>", on_click)
                self.canvas.tag_bind(txt, "<Enter>", on_enter)
                self.canvas.tag_bind(txt, "<Leave>", on_leave)
                self.canvas.tag_bind(txt, "<Button-1>", on_click)
            self.canvas.update()
            self.after(delay)
            if step != steps:
                self.canvas.delete("event_fade")

    def draw_trainings(self, fade=False, slot_width=120, slot_height=40):
        keyword = self.search_var.get().strip().lower() if hasattr(self, "search_var") else ""
        year = self.current_date.year
        month = self.current_date.month

        trainings_month = get_trainings_for_month(year, month, "toutes")
        if keyword:
            trainings_month = [
                t for t in trainings_month
                if keyword in t.description.lower() or keyword in t.category.lower()
            ]
        week_dates = get_week_dates(self.current_date)
        week_dates_set = set(week_dates)
        trainings = [t for t in trainings_month if t.date in week_dates_set]

        # Paramètres de police
        min_font = 7
        max_font = 11
        font_size = max(min_font, min(max_font, int((slot_width-10) / 10)))
        event_font = ("Segoe UI", font_size)

        # Largeur de texte pour le wrapping
        if slot_width < 80:
            wrap_chars = 10
        elif slot_width < 120:
            wrap_chars = 15
        else:
            wrap_chars = 22

        for t in trainings:
            col = t.date.weekday()
            # Calcule la position y en fonction de l'heure de début
            row = ((t.start_time.hour - 12) * 2) + (1 if t.start_time.minute == 30 else 0)
            x = 60 + col * slot_width
            y = 60 + row * slot_height

            # Hauteur "horaire" (durée de l'événement)
            duration_slots = ((t.end_time.hour - t.start_time.hour) * 2 + (t.end_time.minute - t.start_time.minute)//30)
            h_time = max(1, duration_slots) * slot_height

            # Texte complet wrappé (catégorie + description)
            desc_wrapped = wrap_text(t.description, width=wrap_chars, max_lines=None, force_single_line=False)
            nb_desc_lines = desc_wrapped.count('\n') + 1
            h_text = (nb_desc_lines + 1) * (font_size + 2) + 10  # +1 pour la catégorie
            h = max(h_time, h_text)

            color = self.get_category_color(t.category)
            outline = "#4a5a6a"

            rect = self.canvas.create_rectangle(
                x, y, x+slot_width-10, y+h,
                fill=color,
                outline=outline,
                width=1.5,
                tags="event_fade"
            )

            # Catégorie centrée, en gras
            cat_text_id = self.canvas.create_text(
                x + (slot_width-10)//2, y + 8,
                text=t.category,
                font=("Segoe UI", font_size, "bold"),
                fill="#2d3a4a",
                anchor="n",
                tags="event_fade"
            )

            # Description alignée à gauche sous la catégorie
            desc_text_id = self.canvas.create_text(
                x+8, y + font_size + 16,
                text=desc_wrapped,
                font=("Segoe UI", font_size),
                fill="#222222",
                anchor="nw",
                tags="event_fade"
            )

            elements = [rect, cat_text_id, desc_text_id]

            def on_enter(event, item=rect):
                self.canvas.itemconfig(item, outline="#2d3a4a", width=2.5)
                self.canvas.config(cursor="hand2")

            def on_leave(event, item=rect):
                self.canvas.itemconfig(item, outline="#4a5a6a", width=1.5)
                self.canvas.config(cursor="")

            def on_click(event, t=t):
                self.open_edit_popup(t)

            # Lier les événements à tous les éléments de l'événement
            for el in elements:
                self.canvas.tag_bind(el, "<Enter>", on_enter)
                self.canvas.tag_bind(el, "<Leave>", on_leave)
                self.canvas.tag_bind(el, "<Button-1>", on_click)

    def add_popup(self, date, start_time):
        popup = tk.Toplevel(self)
        popup.title("Ajouter un entraînement")
        popup.geometry("320x320")
        popup.grab_set()

        tk.Label(popup, text="Catégorie :").pack(pady=(10, 0))
        category_entry = tk.Entry(popup)
        category_entry.pack(pady=5)

        tk.Label(popup, text="Description :").pack(pady=(10, 0))
        # Bloc texte multi-ligne pour la description
        description_text = tk.Text(popup, height=4, width=32, wrap="word")
        description_text.pack(pady=5)

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
            description = description_text.get("1.0", "end").strip()
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
        self._fade_events = True
        self.draw_table()

    def next_week(self):
        self.current_date += timedelta(days=7)
        self._fade_events = True
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
        popup.geometry("330x380")
        popup.grab_set()

        tk.Label(popup, text="Catégorie :").pack(pady=(10, 0))
        category_entry = tk.Entry(popup)
        category_entry.insert(0, training.category)
        category_entry.pack(pady=5)

        tk.Label(popup, text="Description :").pack(pady=(10, 0))
        # Bloc texte multi-ligne pour la description
        description_text = tk.Text(popup, height=4, width=32, wrap="word")
        description_text.insert("1.0", training.description)
        description_text.pack(pady=5)

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
                description = description_text.get("1.0", "end").strip()
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

    def show_stats_popup(self):
        # Récupère les trainings du mois affiché
        year = self.current_date.year
        month = self.current_date.month
        trainings = get_trainings_for_month(year, month, "toutes")

        # Statistiques
        nb_total = len(trainings)
        weeks_in_month = sorted(set(t.date.isocalendar()[1] for t in trainings))
        cat_counts = {}
        for t in trainings:
            cat_counts[t.category] = cat_counts.get(t.category, 0) + 1

        # Création du popup stylisé
        popup = tk.Toplevel(self)
        popup.title("Statistiques du mois")
        popup.geometry("420x650")
        popup.configure(bg="#f7f7f9")
        popup.grab_set()

        # Carte principale (effet carte blanche arrondie)
        card = tk.Frame(popup, bg="#ffffff", bd=0, highlightthickness=0)
        card.place(relx=0.5, rely=0.03, anchor="n", width=380, height=600)

        # Ombre portée (optionnel, effet simple)
        # (Tkinter ne gère pas l'ombre nativement, mais le fond gris clair autour donne déjà un effet "carte")

        # Titre principal
        tk.Label(
            card,
            text=f"Statistiques – {calendar.month_name[month].capitalize()} {year}",
            font=("Segoe UI", 16, "bold"),
            bg="#ffffff",
            fg="#222222"
        ).pack(pady=(22, 10))

        # Encadré résumé
        resume_frame = tk.Frame(card, bg="#f4f6fa", bd=1, relief="solid", highlightbackground="#e0e4ea", highlightthickness=1)
        resume_frame.pack(pady=(0, 18), padx=18, fill="x")

        # Nombre total de séances
        tk.Label(
            resume_frame,
            text="Nombre total de séances :",
            font=("Segoe UI", 11, "bold"),
            bg="#f4f6fa",
            fg="#222222",
            anchor="w"
        ).pack(anchor="w", pady=(10, 0), padx=12)
        tk.Label(
            resume_frame,
            text=f"{nb_total}",
            font=("Segoe UI", 12),
            bg="#f4f6fa",
            fg="#222222",
            anchor="w"
        ).pack(anchor="w", padx=12, pady=(0, 10))

        # Séparateur
        tk.Frame(resume_frame, bg="#e0e4ea", height=1).pack(fill="x", padx=8, pady=2)

        # Nombre de séances par semaine (ISO)
        tk.Label(
            resume_frame,
            text="Nombre de séances par semaine (ISO) :",
            font=("Segoe UI", 11, "bold"),
            bg="#f4f6fa",
            fg="#222222",
            anchor="w"
        ).pack(anchor="w", padx=12, pady=(6, 0))
        for week in weeks_in_month:
            count = sum(1 for t in trainings if t.date.isocalendar()[1] == week)
            tk.Label(
                resume_frame,
                text=f"  Semaine {week} : {count}",
                font=("Segoe UI", 11),
                bg="#f4f6fa",
                fg="#222222",
                anchor="w"
            ).pack(anchor="w", padx=18)

        # Séparateur
        tk.Frame(resume_frame, bg="#e0e4ea", height=1).pack(fill="x", padx=8, pady=2)

        # Répartition par catégorie
        tk.Label(
            resume_frame,
            text="Répartition par catégorie :",
            font=("Segoe UI", 11, "bold"),
            bg="#f4f6fa",
            fg="#222222",
            anchor="w"
        ).pack(anchor="w", padx=12, pady=(6, 0))
        for cat, count in cat_counts.items():
            tk.Label(
                resume_frame,
                text=f"  {cat} : {count}",
                font=("Segoe UI", 11),
                bg="#f4f6fa",
                fg="#222222",
                anchor="w"
            ).pack(anchor="w", padx=18, pady=(0, 2))

        # Carte graphique
        graph_card = tk.Frame(card, bg="#f4f6fa", bd=1, relief="solid", highlightbackground="#e0e4ea", highlightthickness=1)
        graph_card.pack(pady=(0, 10), padx=18, fill="x")

        if cat_counts:
            fig, ax = plt.subplots(figsize=(3.2, 2.5), dpi=100)
            ax.pie(cat_counts.values(), labels=cat_counts.keys(), autopct='%1.0f%%', startangle=90, textprops={'fontsize': 9, 'color': '#222222'})
            ax.set_title("Répartition par catégorie", fontsize=11, color="#222222")
            fig.patch.set_facecolor('#f4f6fa')
            canvas_fig = FigureCanvasTkAgg(fig, master=graph_card)
            canvas_fig.draw()
            canvas_fig.get_tk_widget().pack(pady=10)
        else:
            tk.Label(
                graph_card,
                text="Aucune donnée pour ce mois.",
                font=("Segoe UI", 11, "italic"),
                bg="#f4f6fa",
                fg="#888888"
            ).pack(pady=30)

        # Bouton fermer
        tk.Button(
            card,
            text="Fermer",
            command=popup.destroy,
            font=("Segoe UI", 10, "bold"),
            bg="#e0e4ea",
            fg="#2d3a4a",
            relief="flat",
            padx=12,
            pady=4,
            cursor="hand2"
        ).pack(pady=18)