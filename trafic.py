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


def config_equidistance(taille, nb_voitures):
    route = route_equidistance(taille, nb_voitures)
    vitesses = {i: 0 for i in range(1, nb_voitures+1)}
    return route, vitesses


def ecart_devant(route, i):
    n = route.shape[0]
    d = 1
    while d < n:
        if route[(i+d)%n] > 0:
            return d-1
        d += 1
    return n-1


class Modele(ABC):
    @abstractmethod
    def transition(self, route, vitesses):
        pass

    def trajectoire(self, route0, vitesses0, n):
        chaine_route = [route0]
        chaine_vitesses = [vitesses0]
        for _ in range(n):
            route, vitesses = self.transition(chaine_route[-1], chaine_vitesses[-1])
            chaine_route.append(route)
            chaine_vitesses.append(vitesses)
        return chaine_route, chaine_vitesses


class ModeleSimple(Modele):
    def __init__(self, vmax, p):
        self.vmax = vmax
        self.p = p
    
    def transition(self, route, vitesses):
        n = route.shape[0]
        route_new = route_vide(n)
        vitesses_new = {}

        # accélération
        for voiture in vitesses:
            vitesses_new[voiture] = min(vitesses[voiture]+1, self.vmax)
        
        # freinage
        for i in range(n):
            voiture = route[i]
            if voiture > 0:
                ecart = ecart_devant(route, i)
                vitesses_new[voiture] = min(vitesses_new[voiture], ecart)
        
        # ralentissement aléatoire
        for voiture in vitesses:
            if np.random.rand() < self.p and vitesses_new[voiture] > 0:
                vitesses_new[voiture] -= 1
        
        # déplacement des voitures
        for i in range(n):
            voiture = route[i]
            if voiture > 0:
                route_new[(i+vitesses_new[voiture])%n] = voiture
        
        return route_new, vitesses_new


class ModeleDiffVmax(Modele):
    def __init__(self, vmax_par_voiture, p):
        self.vmax_par_voiture = vmax_par_voiture
        self.p = p
    
    def transition(self, route, vitesses):
        n = route.shape[0]
        route_new = route_vide(n)
        vitesses_new = {}

        # accélération
        for voiture in vitesses:
            vitesses_new[voiture] = min(vitesses[voiture]+1, self.vmax_par_voiture[voiture])
        
        # freinage
        for i in range(n):
            voiture = route[i]
            if voiture > 0:
                ecart = ecart_devant(route, i)
                vitesses_new[voiture] = min(vitesses_new[voiture], ecart)
        
        # ralentissement aléatoire
        for voiture in vitesses:
            if np.random.rand() < self.p and vitesses_new[voiture] > 0:
                vitesses_new[voiture] -= 1
        
        # déplacement des voitures
        for i in range(n):
            voiture = route[i]
            if voiture > 0:
                route_new[(i+vitesses_new[voiture])%n] = voiture
        
        return route_new, vitesses_new
