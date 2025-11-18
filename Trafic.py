import numpy as np


# Une transition a lieux toutes les secondes.
def transition(routeActuelle, vmax_par_voiture, p_ralentis):
    routeActuelle_new = routeActuelle.copy()
    n = len(routeActuelle)

    voituresDejaBougee = [0]
    for i in range(n):
        if (routeActuelle[i] not in voituresDejaBougee and routeActuelle[i] != 0):
            voiture_act = routeActuelle_new[i]
            pos_voiture_act = i
            # chaque voiture a sa vitesse max
            vmax_i = vmax_par_voiture[voiture_act]

            # 1 avance vmax au plus
            avance = 0
            for j in range(vmax_i):
                if (routeActuelle[(i + j + 1) % n] == 0):
                    avance += 1
                    routeActuelle_new[(i + j) % n] = 0
                    routeActuelle_new[(i + j + 1) % n] = voiture_act
                    pos_voiture_act = (i + j + 1) % n
                else:
                    break

            # 2 ralatentit avec proba p_ralentis si possible
            if avance > 0:
                u = np.random.rand()
                if (u < p_ralentis):
                    routeActuelle_new[(pos_voiture_act - 1) % n] = voiture_act
                    routeActuelle_new[(pos_voiture_act) % n] = 0

            # 3 Ajout de la voiture dans la liste de celle qui ont deja avances
            voituresDejaBougee.append(voiture_act)

    return np.array(routeActuelle_new)


def CM_Route(route_0, temps_en_sec, vmax_par_voiture, p_ralentis):
    Chaine = [route_0]
    for i in range(temps_en_sec):
        Chaine.append(transition(Chaine[i], vmax_par_voiture, p_ralentis))
    return np.array(Chaine)


def repartition_Unif_voitures(route, nbVoiture):
    n = nbVoiture
    i = 0
    while n != 0:
        u = np.random.rand()
        if u < (nbVoiture / len(route)) and route[i] == 0:
            route[i] = n
            n = n - 1
        i = (i + 1) % len(route)
    return route


def route_vide(taille):
    return np.zeros(taille, dtype=int)


def route_unif(taille, nb_voitures):
    route = route_vide(taille)
    subdiv = (np.arange(nb_voitures) * taille / nb_voitures).astype(int)
    route[subdiv] = np.arange(1, nb_voitures + 1)
    return route


# ------------------Partie Vmax diff--------------------
# ici je vais essayer d'introduire des vm diff
# -------------------------------------------------------


import numpy as np

nb_voitures = 30
vmax_par_voiture = np.zeros(nb_voitures + 1, dtype=int)  # index 0 inutilisé

for id_voiture in range(1, nb_voitures + 1):
    # je fait le type de véhicule en fonction du numéro pour l'instant donc pas aléatoire
    if id_voiture % 5 == 0:
        # camion
        vmax_par_voiture[id_voiture] = 2
    elif id_voiture % 3 == 0:
        # moto
        vmax_par_voiture[id_voiture] = 7
    else:
        # voiture normale
        vmax_par_voiture[id_voiture] = 5



#--------simulations accidents---------------


def detect_distance(route, pos):
    #retourne la distance en cases jusqu'a la prochaine voiture devant
    n = len(route)
    for d in range(1, n):
        if route[(pos + d) % n] != 0:
            return d
    return None  # route vide (cas impossible si nb_voitures > 0)


def simulate_accident(route, vmax_par_voiture, base_prob=0.02):
    """
    verifie si un accident doit se produire sur la route actuelle.
    si oui, elle retourne une route modifiée (avec accidents marqués)
    si non, elle retourne None.
    """
    n = len(route)
    vmax_max = np.max(vmax_par_voiture)

    for pos in range(n):
        idv = route[pos]
        if idv == 0:
            continue

        vmax_i = vmax_par_voiture[idv]
        distance = detect_distance(route, pos)

        if distance is None:
            continue

        # Si la distance est < à la vitesse max → freinage violent
        if distance < vmax_i:
            proba = base_prob * (vmax_i / vmax_max)

            if np.random.rand() < proba:
                # ACCIDENT !
                new_route = route.copy()

                pos_front = (pos + distance) % n
                new_route[pos] = -1
                new_route[pos_front] = -1

                return new_route   # route modifié

    return None   # pas d'accident


def transition_accidents(route, vmax_par_voiture, p_ralentis, base_prob=0.02):
    #simule un accident eventuel, et si pas d'accifent alors applique la transition normale
    #on teste si un accident se produit
    accident_route = simulate_accident(route, vmax_par_voiture, base_prob)

    if accident_route is not None:
        return accident_route

    #sinon on appelle la transition
    return transition(route, vmax_par_voiture, p_ralentis)



def CM_Route_accidents(route_0, temps, vmax_par_voiture, p_ralentis, base_prob=0.02):
    chaine = [route_0]
    for t in range(temps):
        nxt = transition_accidents(chaine[-1], vmax_par_voiture, p_ralentis, base_prob)
        chaine.append(nxt)
    return np.array(chaine)



# application
if __name__ == "__main__":
    L = 100
    nb_voitures = 30

    # exemple de route
    route = route_unif(L, nb_voitures)

    # exemple de vitesses
    vmax_par_voiture = np.zeros(nb_voitures + 1, dtype=int)
    for idv in range(1, nb_voitures + 1):
        if idv % 5 == 0: vmax_par_voiture[idv] = 2
        elif idv % 3 == 0: vmax_par_voiture[idv] = 7
        else: vmax_par_voiture[idv] = 5

    # simulateur avec accidents
    traj = CM_Route_accidents(route, 50, vmax_par_voiture, p_ralentis=0.2, base_prob=0.03)

    print(traj)
