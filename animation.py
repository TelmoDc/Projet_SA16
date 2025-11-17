import tkinter as tk
import time
import math
import threading

from Trafic import *


# parametres (je les ai modifié pour une représentation visuelle)

route_5km_0 = [0 for _ in range(80)]
nb_Voitures = 30
route_5km_0 = repartition_Unif_voitures(route_5km_0, nb_Voitures)

vmax = 5
p_ralentis = 0.1
duree = 300
Ch = CM_Route(route_5km_0, duree, vmax, p_ralentis)

# interface avec route circulaire
ROAD_COLOR = "#404040"
CAR_COLOR = "#ff9933"
TEXT_COLOR = "black"
BG_COLOR = "#222222"
PADDING = 25

n = len(route_5km_0)
width = 400
height = 400
radius = (min(width, height) // 2) - PADDING

root = tk.Tk()
root.title("projet de simu")
root.configure(bg=BG_COLOR)

canvas = tk.Canvas(root, width=width, height=height, bg=BG_COLOR, highlightthickness=0)
canvas.pack(pady=20)

# Barre de contrôle de vitesse
control_frame = tk.Frame(root, bg=BG_COLOR)
control_frame.pack(pady=10)
tk.Label(control_frame, text="Vitesse (temps entre frames en secondes)", bg=BG_COLOR, fg="white").pack()
speed_var = tk.DoubleVar(value=0.1)
speed_slider = tk.Scale(control_frame, from_=0.01, to=0.5, resolution=0.01,
                        orient="horizontal", variable=speed_var, length=300, bg=BG_COLOR,
                        fg="white", troughcolor="#555555", highlightthickness=0)
speed_slider.pack()

status_label = tk.Label(root, text="", bg=BG_COLOR, fg="white", font=("Arial", 11))
status_label.pack(pady=10)

def afficher_route(route):
    canvas.delete("all")

    # Dessiner la route circulaire
    canvas.create_oval(PADDING, PADDING, width - PADDING, height - PADDING,
                       outline="gray60", width=30)

    # Dessiner les voitures
    for i, v in enumerate(route):
        if v != 0:
            angle = 2 * math.pi * i / n
            cx = width / 2 + radius * math.cos(angle)
            cy = height / 2 + radius * math.sin(angle)

            car_size = 10
            canvas.create_oval(cx - car_size, cy - car_size, cx + car_size, cy + car_size,
                               fill=CAR_COLOR, outline="black")
            canvas.create_text(cx, cy, text=str(v), fill=TEXT_COLOR, font=("Arial", 8, "bold"))
    root.update()


# ===================== Animation =====================

stop_flag = False

def animation():
    global stop_flag
    stop_flag = False
    for t, etat in enumerate(Ch):
        if stop_flag:
            break
        afficher_route(etat)
        status_label.config(text=f"Temps : {t + 1} s / {duree} s")
        time.sleep(speed_var.get())
    status_label.config(text="Simulation terminée ✅")

def start_animation():
    thread = threading.Thread(target=animation, daemon=True)
    thread.start()

def stop_animation():
    global stop_flag
    stop_flag = True
    status_label.config(text="Simulation arrêtée ⛔")

# Boutons
button_frame = tk.Frame(root, bg=BG_COLOR)
button_frame.pack(pady=10)
tk.Button(button_frame, text="▶ Lancer", command=start_animation, bg="#4CAF50", fg="white", width=10).grid(row=0, column=0, padx=5)
tk.Button(button_frame, text="⏸ Arrêter", command=stop_animation, bg="#F44336", fg="white", width=10).grid(row=0, column=1, padx=5)

# Démarrage
afficher_route(route_5km_0)
root.mainloop()
