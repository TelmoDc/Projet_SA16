import numpy as np


##############################################
#     Variable utiles
##############################################

accidents_blocking =  {}
DUREE_BLOCAGE = 2700 # car en moyenne selon internet entre 20 min et 2h donc j'ai pris 45 min : 45*60 sec = 2700 sec
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
    base_rate = 1e-4  # taux de base d'accident par pas de temps
    
    nlanes, n = route.shape
    route_new = route.copy()

    ############################
    # Étape 0 : décision
    ############################
    demandes = {}  # voiture -> (-1/0/+1)

    for lane in range(nlanes):
        for pos in range(n):
            car = route[lane][pos]
            if car > 0:                             # accident ne bouge pas donc >
                demandes[car] = decide_lane_change(route, vmax, v[car], lane, pos)

    ############################
    # Étape 1 : application
    # sans conflits (on interdit les swaps pour simplifier)
    ############################
    route_temp = route.copy()

    for lane in range(nlanes):
        for pos in range(n):
            car = route[lane][pos]
            if car == 0 or car == -1:
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
            if car != 0 and car!=-1:
                gap = gap_ahead(route, lane, pos)
                v[car] = min(v[car], gap)

    # 2c ralentissement aléatoire
    for car in v:
        if np.random.rand() < p and v[car] > 0:
            v[car] -= 1
            
            
            
     ############################
    # Étape 2.5 : Gestion des accidents
    ############################
    cars_to_remove = []
    for lane in range(nlanes):
        for pos in range(n):
            car = route[lane][pos]
            if car == 0 or car ==-1:
                continue

            gap = gap_ahead(route, lane, pos)
            move = demandes[car]
            vcar = v[car]

            accident_prob = base_rate * (1 + 0.1 * vcar) * (1 / (gap + 1))
            if move != 0:
                accident_prob *= 2  # changement de voie augmente le risque

            if np.random.rand() < accident_prob: #    -------------------------- >   si l'on ne veux pas prendre en compte les accident mettre 0
                # Accident : suppression de la voiture
                cars_to_remove.append((lane, pos, car))

    for lane, pos, car in cars_to_remove:
        print(f"Accident voiture {car} à la position {pos} voie {lane}")
        route[lane][pos] = -1
        v.pop(car)
        accidents_blocking[(lane, pos)] = DUREE_BLOCAGE


    ############################
    # Étape 3 : déplacement simultané
    ############################

    route_new = np.zeros_like(route)

    for lane in range(nlanes):
        for pos in range(n):
            car = route[lane][pos]
            if car != 0:  
                if car != -1 :     #    Important de gerer les accident aussi
                    new_pos = (pos + v[car]) % n
                    route_new[lane][new_pos] = car
                else :
                    route_new[lane][pos] = car
    ###############################################
    #    Gestion du temps de blockage de l'accident
    ########################################
    for (lane, pos) in list(accidents_blocking.keys()):
        accidents_blocking[(lane, pos)] -= 1
        if accidents_blocking[(lane, pos)] <= 0:
            # Fin du blocage, libération de la case
            route[lane][pos] = 0
            del accidents_blocking[(lane, pos)]
    return route_new

# Initialisation
n = 20
nlanes = 2
route = np.zeros((nlanes, n), dtype=int)

route[0, 12] = 1
route[0, 13] = 2
route[0, 17] = -1    # test si accident yes it works good

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
