import numpy as np
from abc import ABC, abstractmethod


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


def route_equidistance(taille, nb_voitures):
    route = route_vide(taille)
    subdiv = (np.arange(nb_voitures)*taille/nb_voitures).astype(int)
    route[subdiv] = np.arange(1, nb_voitures+1)
    return route


class Modele(ABC):
    @abstractmethod
    def transition(self, route):
        pass

    def trajectoire(self, route0, n):
        chaine = [route0]
        for _ in range(n):
            chaine.append(self.transition(chaine[-1]))
        return np.array(chaine)


class ModeleSimple(Modele):
    def __init__(self, vmax, p):
        self.vmax = vmax
        self.p = p
    
    def transition(self, route):
        route_new = route.copy()
        n = len(route)

        voituresDejaBougee = {0}
        for i in range(n):
            if (route[i] not in voituresDejaBougee):
                voiture_act = route_new[i]
                pos_voiture_act = i

                # 1 avance vmax au plus
                avance = 0
                for j in range(self.vmax):
                    if (route[(i + j + 1) % n] == 0):
                        avance += 1
                        route_new[(i + j) % n] = 0
                        route_new[(i + j + 1) % n] = voiture_act
                        pos_voiture_act = (i + j + 1) % n
                    else:
                        break
                
                # 2 ralatentit avec proba p_ralentis si possible
                if avance > 0:
                    u = np.random.rand()
                    if (u < self.p):
                        route_new[(pos_voiture_act - 1) % n] = voiture_act
                        route_new[(pos_voiture_act) % n] = 0

                # 3 Ajout de la voiture dans la liste de celle qui ont deja avancÃ©es
                voituresDejaBougee.add(voiture_act)

        return np.array(route_new)


class ModeleDiffVmax(Modele):
    def __init__(self, vmax_par_voiture, p):
        self.vmax_par_voiture = vmax_par_voiture
        self.p = p
    
    def transition(self, route):
        route_new = route.copy()
        n = len(route)

        voituresDejaBougee = {0}
        for i in range(n):
            if (route[i] not in voituresDejaBougee and route[i] != 0):
                voiture_act = route_new[i]
                pos_voiture_act = i
                #chaque voiture a sa vitesse max    
                vmax_i = self.vmax_par_voiture[voiture_act]

                # 1 avance vmax au plus
                avance = 0
                for j in range(vmax_i):
                    if (route[(i + j + 1) % n] == 0):
                        avance += 1
                        route_new[(i + j) % n] = 0
                        route_new[(i + j + 1) % n] = voiture_act
                        pos_voiture_act = (i + j + 1) % n
                    else:
                        break
                
                # 2 ralatentit avec proba p_ralentis si possible
                if avance > 0:
                    u = np.random.rand()
                    if (u < self.p):
                        route_new[(pos_voiture_act - 1) % n] = voiture_act
                        route_new[(pos_voiture_act) % n] = 0

                # 3 Ajout de la voiture dans la liste de celle qui ont deja avances
                voituresDejaBougee.add(voiture_act)

        return np.array(route_new)
