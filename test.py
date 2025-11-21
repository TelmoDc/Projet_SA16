import time
import os
import string
import numpy as np

# On suppose que ton fichier principal contenant `transition`,
# `v`, `vmax`, etc. s'appelle main.py
# Import uniquement la fonction transition
from traficPlusieursVoie import transition

def display(route):
    """
    Affiche la route sous forme ASCII :
    - '.' = vide
    - 'X' = accident (-1)
    - A, B, C... = voitures 1,2,3...
    """
    nlanes, n = route.shape
    symbols = "ABCDEFGHIJKLMNOPQRSTUVWYZ"

    for lane in range(nlanes):
        line = ""
        for pos in range(n):
            cell = route[lane][pos]
            if cell == 0:
                line += "."
            elif cell == -1:
                line += "X"
            else:
                # Voiture n → lettre
                line += symbols[(cell-1) % len(symbols)]
        print(line)

# ==== PARAMÈTRES DE TEST ====
# Route 2 voies, 200 cases
n = 200
nlanes = 2
route = np.zeros((nlanes, n), dtype=int)
# Quelques voitures (25 au total)
# Placement régulier toutes les 8 cases environ


num_cars = 24
positions = np.linspace(0, n-1, num_cars, dtype=int)


v = {}
vmax = {}
car_id = 1


for i, pos in enumerate(positions):
    lane = i % 2 # alterne voie 0 / voie 1
    route[lane, pos] = car_id
    v[car_id] = np.random.randint(1, 4) # vitesse initiale 1 à 3
    vmax[car_id] = 5 # vmax uniforme
    car_id += 1
# Accident test :
route[0][3]=-1
route[1][3]=-1


# Probabilité de ralentissement aléatoire
p = 0.05

# Fonction pour effacer la console
def clear_screen():
    os.system("cls" if os.name == "nt" else "clear")

# Boucle de test simple
while True:
    clear_screen()
    print("=== TEST SIMULATION (1 FPS) ===")
    print()
    display(route)
    route = transition(route, vmax, v, p)
    time.sleep(1)
