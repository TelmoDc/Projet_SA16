import numpy as np


# Une transition a lieux toutes les secondes.
def transition(routeActuelle, vmax, p_ralentis):
    routeActuelle_new = routeActuelle.copy()
    n = len(routeActuelle)

    voituresDejaBougee = [0]
    for i in range(n):
        if (routeActuelle[i] not in voituresDejaBougee):
            voiture_act = routeActuelle_new[i]
            pos_voiture_act = i

            # 1 avance vmax au plus
            avance = 0
            for j in range(vmax):
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

            # 3 Ajout de la voiture dans la liste de celle qui ont deja avancÃ©es
            voituresDejaBougee.append(voiture_act)

    return np.array(routeActuelle_new)


def CM_Route(route_0, temps_en_sec, vmax, p_ralentis):
    Chaine = [route_0]
    for i in range(temps_en_sec):
        Chaine.append(transition(Chaine[i], vmax, p_ralentis))
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
    subdiv = (np.arange(nb_voitures)*taille/nb_voitures).astype(int)
    route[subdiv] = np.arange(1, nb_voitures+1)
    return route