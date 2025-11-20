import numpy as np
import matplotlib.pyplot as plt

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











# limitation de vitesse

def transition_vmax_locale(routeActuelle, vmax_par_voiture, p_ralentis):
    vmax_local = [20 for i in range(len(routeActuelle))]
    for i in range(10,20):
        vmax_local[i] = 1 #en considerant que la route fasse une taille supérieure a 20
    routeActuelle_new = routeActuelle.copy()
    n = len(routeActuelle)

    voituresDejaBougee = [0]
    for i in range(n):
        if (routeActuelle[i] not in voituresDejaBougee and routeActuelle[i] != 0):
            voiture_act = routeActuelle_new[i]
            pos_voiture_act = i
            # chaque voiture a sa vitesse max // on prend le min entre ça et vmax locale de la route
            vmax_i = min(vmax_par_voiture[voiture_act],vmax_local[i])

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
    #print(traj)

    traj = [route]

    for t in range(100):
        route = transition_vmax_locale(route, vmax_par_voiture, 0.3)
        traj.append(route)

    traj = np.array(traj)
    img = (traj > 0).astype(int)  # 0 = vide, 1 = voiture

    # ----- AFFICHAGE -----
    plt.figure(figsize=(10, 6))
    plt.imshow(img.T, aspect='auto', cmap='gray_r', origin='lower')
    plt.xlabel("Temps")
    plt.ylabel("Position sur la route")
    plt.title("Évolution trafic avec limitation locale (cases 10–19)")
    plt.show()

    ##version sans lim de vitesse
    route = route_unif(L, nb_voitures)

    traj = [route]

    for t in range(100):
        route = transition(route, vmax_par_voiture, 0.3)
        traj.append(route)

    traj = np.array(traj)
    img = (traj > 0).astype(int)  # 0 = vide, 1 = voiture

    # ----- AFFICHAGE -----
    plt.figure(figsize=(10, 6))
    plt.imshow(img.T, aspect='auto', cmap='gray_r', origin='lower')
    plt.xlabel("Temps")
    plt.ylabel("Position sur la route")
    plt.title("Évolution trafic avec limitation locale (cases 10–19)")
    plt.show()