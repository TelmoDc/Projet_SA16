import numpy as np

###############################################
#   FONCTIONS UTILES
###############################################

def gap_ahead(route, lane, pos):
    """Distance jusqu'à la prochaine voiture sur la même voie."""
    n = len(route[0])
    d = 1
    while d < n:
        if route[lane][(pos + d) % n] != 0:
            return d - 1
        d += 1
    return n - 1  # route circulaire entièrement vide devant


def gap_behind(route, lane, pos):
    """Distance jusqu'à la voiture derrière sur la voie cible."""
    n = len(route[0])
    d = 1
    while d < n:
        if route[lane][(pos - d) % n] != 0:
            return d - 1
        d += 1
    return n - 1


###############################################
#   DECISION DE CHANGEMENT DE VOIE
###############################################

def decide_lane_change(route, vmax, v, lane, pos):
    """
    Renvoie : -1 (aller à droite), 0 (rester), +1 (aller à gauche).
    """
    nlanes = len(route)
    gap_curr = gap_ahead(route, lane, pos)

    # vitesse actuelle
    vcur = v

    # 1) Tentative de dépassement vers la gauche
    if lane < nlanes - 1:     # s'il existe une voie à gauche
        gap_left_front = gap_ahead(route, lane + 1, pos)
        gap_left_back  = gap_behind(route, lane + 1, pos)

        if gap_curr < vcur and gap_left_front > gap_curr:
            # sécurité
            if gap_left_front >= vcur and gap_left_back >= 1:
                return +1  # dépassement

    # 2) Retour à droite
    if lane > 0:  # existe voie droite
        gap_right_front = gap_ahead(route, lane - 1, pos)
        gap_right_back  = gap_behind(route, lane - 1, pos)

        if gap_right_front >= vcur and gap_right_front >= gap_curr:
            if gap_right_back >= 1:
                return -1  # retour à droite

    # sinon on reste
    return 0


###############################################
#   TRANSITION AVEC NASCH + LANE CHANGE
###############################################

def transition(route, vmax, v, p):
    """
    route : matrice [2][n]
    v : dictionnaire {id_voiture: vitesse}
    vmax : idem
    p : probabilité de ralentissement aléatoire
    """

    nlanes, n = route.shape
    route_new = route.copy()

    ############################
    # Étape 0 : décision
    ############################
    demandes = {}  # voiture -> (-1/0/+1)

    for lane in range(nlanes):
        for pos in range(n):
            car = route[lane][pos]
            if car != 0:
                demandes[car] = decide_lane_change(route, vmax, v[car], lane, pos)

    ############################
    # Étape 1 : application
    # sans conflits (on interdit les swaps pour simplifier)
    ############################
    route_temp = route.copy()

    for lane in range(nlanes):
        for pos in range(n):
            car = route[lane][pos]
            if car == 0:
                continue

            move = demandes[car]
            new_lane = lane + move

            # si aucun changement
            if move == 0:
                continue

            # case cible déjà occupée ? -> changement annulé
            if route_temp[new_lane][pos] != 0:
                continue

            # appliquer le changement
            route_temp[lane][pos] = 0
            route_temp[new_lane][pos] = car

    route = route_temp

    ############################
    # Étape 2 : NaSch
    ############################
    # 2a accélération
    for car in v:
        v[car] = min(v[car] + 1, vmax[car])

    # 2b freinage
    for lane in range(nlanes):
        for pos in range(n):
            car = route[lane][pos]
            if car != 0:
                gap = gap_ahead(route, lane, pos)
                v[car] = min(v[car], gap)

    # 2c ralentissement aléatoire
    for car in v:
        if np.random.rand() < p and v[car] > 0:
            v[car] -= 1

    ############################
    # Étape 3 : déplacement simultané
    ############################

    route_new = np.zeros_like(route)

    for lane in range(nlanes):
        for pos in range(n):
            car = route[lane][pos]
            if car != 0:
                new_pos = (pos + v[car]) % n
                route_new[lane][new_pos] = car

    return route_new

# Initialisation
n = 20
nlanes = 2
route = np.zeros((nlanes, n), dtype=int)

# Mettons voiture 1 en voie 0 position 2, voiture 2 en voie 1 position 5
route[0, 12] = 1
route[0, 13] = 2

# Vitesse initiale et vitesse max
v = {1: 2, 2: 0}
vmax = {1: 5, 2: 5}

p = 0.1  # faible probabilité de ralentissement

print("Etat initial:")
print(route)

# Simuler 3 pas de temps
for step in range(10):
    route = transition(route, vmax, v, p)
    print(f"Après étape {step+1}:")
    print(route)
    print("Vitesses:", v)