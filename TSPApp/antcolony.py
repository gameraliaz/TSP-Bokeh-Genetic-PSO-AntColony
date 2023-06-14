import random
from networkx import Graph

class Ant:
    def __init__(self) -> None:
        self.path = []
        self.distance = 0

    def move(self,G:Graph,alpha,beta,heuristic):
        if self.path[0]==self.path[-1]:
            raise Exception("Ended!")
        j = None
        if len(self.path>0):
            i = self.path[-1]
            L = [k for k in G.neighbors(i) if k not in self.path] 
            
            S = [G.edges[i,l]["pheromone"]**alpha * heuristic(i,l,G)**beta for l in L]

            X = sum(S)

            P = [p/X for p in S]

            x = 0
            rnd = random.random()
            for p in range(len(P)):
                x+=P[p]
                if rnd<=x:
                    j=L[p]
                    break

            self.distance += G.edges[i,j]["w"]
        else:
            j = random.choice(G.nodes)
        self.path.append(j)
        
        if len(self.path) == len(G.nodes):
            i=self.path[0]
            self.path.append(i)
            self.distance += G.edges[j,i]["w"]

class AntColony:
    def __init__(self, num_ants, alpha, beta, evaporation_rate, initial_pheromone, G: Graph):
        self.num_ants = num_ants
        self.alpha = alpha
        self.beta = beta
        self.evaporation_rate = evaporation_rate
        self.initial_pheromone = initial_pheromone
        self.heuristic = lambda x,y,g:1/g[x,y]["w"]
        self.G = G
        self.ants = []
        self.itration_num = 0

        # Initialize pheromone levels on the graph edges
        for u, v in self.G.edges:
            self.G.edges[u, v]["pheromone"] = self.initial_pheromone

    def update_pheromone(self):
        # Evaporate pheromone on all edges
        for u, v in self.G.edges:
            self.G.edges[u, v]["pheromone"] *= (1 - self.evaporation_rate)

        # Deposit pheromone on edges visited by ants
        for ant in self.ants:
            path = ant.path
            distance = ant.distance
            for i in range(len(path) - 1):
                u = path[i]
                v = path[i + 1]
                self.G.edges[u, v]["pheromone"] += self.evaporation_rate*(1/distance)
    def Execute(self):
        while True:
            self.ants = []
            for _ in range(self.num_ants):
                ant = Ant()
                for _ in self.G.nodes:
                    if len(ant.path) < len(self.G):
                        ant.move(self.G, self.alpha, self.beta, self.heuristic)
                self.ants.append(ant)

            self.update_pheromone()
            self.itration_num += 1
            yield min(self.ants,key=lambda x:x.distance)