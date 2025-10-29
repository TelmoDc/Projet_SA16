import numpy as np


# Une transition a lieux toutes les secondes.
def transition(routeActuelle, vmax, p_ralentis) :
    routeActuelle_new = routeActuelle.copy()
    n = len(routeActuelle)
    voituresDejaBougee = [0]
    for i in range (n) :
        if  (routeActuelle[i] not in voituresDejaBougee) :
            voiture_act = routeActuelle_new[i]
            pos_voiture_act = i
            #1 avance vmax au plus
            avance=0
            for j in range(vmax) :
                if (routeActuelle[(i+j+1)%n] == 0 ) : 
                    avance+=1
                    routeActuelle_new[(i+j)%n], routeActuelle_new[(i+j+1)%n], pos_voiture_act = 0, voiture_act , (i+j+1)%n
                else : break
            #2 ralatentit avec proba p_ralentis si possible
            if avance > 0 :
                u = np.random.rand()
                if ( u < p_ralentis ) : 
                    
                    routeActuelle_new[(pos_voiture_act-1)%n], routeActuelle_new[(pos_voiture_act)%n] = voiture_act , 0
                    
            #3 Ajout de la voiture dans la liste de celle qui ont deja avancées 
            voituresDejaBougee.append(voiture_act)
            
    return routeActuelle_new

def CM_Route(route_0, temps_en_sec, vmax , p_ralentis) :
    Chaine = [ route_0 ]
    for i in range (temps_en_sec) :
        Chaine.append(transition(Chaine[i], vmax, p_ralentis))
    return Chaine

def repartition_Unif_voitures(route, nbVoiture) :
    n = nbVoiture
    i=0
    while n!= 0 :
        u = np.random.rand()
        if u < (nbVoiture/len(route)) and route[i]==0 :
            route[i] = n
            n = n-1
        i = (i+1)%len(route)
    return route
# -----------------------------------------------------------------------Test-------------------------------------------------------------------------------------------------- :

# Route circulaire de 5 km (5m * 1000)
route_5km_0 = []

for i in range (1000) :
    route_5km_0.append(0)
    
# nb de voitures reparties unif :
nb_Voitures = 100
route_5km_0 = repartition_Unif_voitures(route_5km_0, nb_Voitures)
print("Route initiale : ")
print (route_5km_0)

# Route après 100 sec avec vmax = 5 (simulation d'une vitesse de 100 km environ) et p_ralentis au hasard mais plutot bas

Ch = CM_Route(route_5km_0,100,5,0.1)

print("\n")
print("\n")
print("Apres 1 sec :")
print(transition(route_5km_0,5,0.1))

print("\n")
print("\n")
print(route_5km_0)
print("\n")
print("\n")


print(Ch[99])
#LLes Test montres bien que pour un nombre de voiture pas très grands le traffic s'uniformise au cours du temps !