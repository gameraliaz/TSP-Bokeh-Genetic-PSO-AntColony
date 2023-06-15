import random
import copy

class Particle:
    def __init__(self,graph,fitness_func):
        self.x = [random.uniform(-len(graph.nodes), len(graph.nodes)) for _ in range(len(graph.nodes))]
        self.v = [random.uniform(-len(graph.nodes), len(graph.nodes)) for _ in range(len(graph.nodes))]
        sorted_indices = sorted(range(len(self.x)), key=lambda j: self.x[j])
        self.S = [idx + 1 for idx in sorted_indices]
        self.pbest = self.x[:]
        self.fitness = 0.0
        self.evaluate_fitness(fitness_func)

    def update(self, w, c1, c2, gbest, graph):
        lv = self.v[:]
        for i in range(len(self.x)):
            r1 = random.uniform(0, 1)
            r2 = random.uniform(0, 1)
            self.v[i] = w * self.v[i] + c1 * r1 * (self.pbest[i] - self.x[i]) + c2 * r2 * (gbest[i] - self.x[i])
            
            self.v[i] = min(max(self.v[i], -len(graph.nodes)), len(graph.nodes))
            
            self.x[i] = self.x[i] + self.lv[i]
            
            self.x[i] = min(max(self.x[i], -len(graph.nodes)), len(graph.nodes))
            
        sorted_indices = sorted(range(len(self.x)), key=lambda j: self.x[j])
        self.S = [idx + 1 for idx in sorted_indices]

    def evaluate_fitness(self, fitness_func):
        self.fitness = fitness_func(self.S)

class PSO:
    def __init__(self, num_particles, graph, fitness_func,w,c1,c2):
        self.fitness_func = fitness_func
        self.w = w
        self.c1 = c1
        self.c2 = c2
        self.num_particles = num_particles
        self.graph = graph
        self.particles = [Particle(graph,fitness_func) for _ in range(num_particles)]
        self.gbest = None
        self.itration_num = 0
        self.gbest_itration = 0

    def Execute(self):
        while True:
            for particle in self.particles:
                particle.evaluate_fitness(self.fitness_func)
                if self.gbest is None or particle.fitness < self.gbest.fitness:
                    self.gbest = copy.deepcopy(particle)
                    self.gbest_itration = self.itration_num
                if particle.fitness < self.fitness_func(particle.pbest):
                    particle.pbest = particle.x[:]
            for particle in self.particles:
                particle.update(self.w, self.c1, self.c2, self.gbest.x, self.graph)
            self.itration_num += 1
            yield self.gbest