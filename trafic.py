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

def config_equidistance_plusieurs_voies(taille, nb_voies, nb_voitures):
    route = route_equidistance(taille, nb_voitures)
    for _ in range(nb_voies-1):
        route = np.vstack([route, np.zeros(taille)])
    vitesses = {i: 0 for i in range(1, nb_voitures+1)}
    return route, vitesses


def ecart_devant(route, i):
    n = route.shape[0]
    d = 1
    while d < n:
        if route[(i+d)%n] != 0:
            return d-1
        d += 1
    return n-1


def ecart_derriere(route, i):
    n = route.shape[0]
    d = 1
    while d < n:
        if route[(i-d)%n] != 0:
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


def decider_changer_voie(route, vitesse, lane, pos):
    """
    Renvoie : -1 (aller à droite), 0 (rester), +1 (aller à gauche).
    """
    nlanes = route.shape[0]
    gap_curr = ecart_devant(route[lane], pos)
    # print(f"c={route[lane][pos]} v={vitesse} gc={gap_curr}", end=' ')

    # 1) Tentative de dépassement vers la gauche
    if lane < nlanes - 1:     # s'il existe une voie à gauche
        gap_left_front = ecart_devant(route[lane+1], pos)
        gap_left_back  = ecart_derriere(route[lane+1], pos)
        # print(f"glf={gap_left_front} glb={gap_left_back}", end=' ')

        # if gap_curr < vitesse and gap_left_front > gap_curr:
        if gap_curr == 0 or (gap_curr < vitesse and gap_left_front > gap_curr):
            # sécurité
            if gap_left_front >= vitesse and gap_left_back >= 1:
                # print()
                return +1  # dépassement

    # 2) Retour à droite
    if lane > 0:  # existe voie droite
        gap_right_front = ecart_devant(route[lane-1], pos)
        gap_right_back  = ecart_derriere(route[lane-1], pos)
        # print(f"grf{gap_right_front} grb{gap_right_back}", end=' ')

        # if gap_right_front >= vitesse and gap_right_front >= gap_curr:
        if gap_right_front >= vitesse: # on se remet à droite dès qu'on peut
            if gap_right_back >= 1:
                # print()
                return -1  # retour à droite

    # print()
    # sinon on reste
    return 0


class ModelePlusieursVoies(Modele):
    def __init__(self, vmax_par_voiture, p, taux_accident, duree_accident):
        self.vmax_par_voiture = vmax_par_voiture
        self.p = p
        self.taux_accident = taux_accident
        self.duree_accident = duree_accident
    
    def transition(self, route, vitesses):
        nlanes, n = route.shape
        route_new = route.copy()

        ############################
        # Étape 0 : décision
        ############################
        demandes = {}  # voiture -> (-1/0/+1)

        for lane in range(nlanes):
            for pos in range(n):
                car = route[lane][pos]
                if car > 0:
                    demandes[car] = decider_changer_voie(route, vitesses[car], lane, pos)

        ############################
        # Étape 1 : application sans conflits (on interdit les swaps pour simplifier)
        ############################
        route_temp = route.copy()

        for lane in range(nlanes):
            for pos in range(n):
                car = route[lane][pos]
                if car <= 0:
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

        ############################
        # Étape 2 : NaSch
        ############################
        vitesses_new = {}
        # 2a accélération
        for car in vitesses:
            vitesses_new[car] = min(vitesses[car] + 1, self.vmax_par_voiture[car])

        # 2b freinage
        for lane in range(nlanes):
            for pos in range(n):
                car = route_temp[lane][pos]
                if car > 0:
                    gap = ecart_devant(route_temp[lane], pos)
                    vitesses_new[car] = min(vitesses_new[car], gap)

        # 2c ralentissement aléatoire
        for car in vitesses:
            if np.random.rand() < self.p and vitesses_new[car] > 0:
                vitesses_new[car] -= 1
                
        ############################
        # Étape 2.5 : Gestion des accidents
        ############################
        nouv_accidents = set()
        for lane in range(nlanes):
            for pos in range(n):
                car = route_temp[lane][pos]
                if car <= 0:
                    continue

                gap = ecart_devant(route_temp[lane], pos)
                move = demandes[car]
                vcar = vitesses_new[car]

                accident_prob = self.taux_accident * (1 + 0.1 * vcar) * (1 / (gap + 1))
                if move != 0:
                    accident_prob *= 2  # changement de voie augmente le risque

                if np.random.rand() < accident_prob: #    -------------------------- >   si l'on ne veux pas prendre en compte les accident mettre 0
                    # Accident : suppression de la voiture
                    # route_temp[lane][pos] = -1
                    nouv_accidents.add((lane, pos))
                    vitesses_new.pop(car)

        ############################
        # Étape 3 : déplacement simultané
        ############################

        route_new = np.zeros_like(route_temp)

        for lane in range(nlanes):
            for pos in range(n):
                car = route_temp[lane][pos]
                if car != 0:
                    if (lane, pos) in nouv_accidents:
                        route_new[lane][pos] = -1
                    elif car < 0:
                        if abs(car-1) > self.duree_accident:
                            route_new[lane][pos] = 0
                        else:
                            route_new[lane][pos] = car-1
                    else:
                        new_pos = (pos + vitesses_new[car]) % n
                        route_new[lane][new_pos] = car

        return route_new, vitesses_new