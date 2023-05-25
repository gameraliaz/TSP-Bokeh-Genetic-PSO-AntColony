import random
import pandas as pd
from numpy import Inf
import networkx as nx

class Chromosome:
    fitness_function = None
    mutation_rate = None

    def __init__(self, gene):
        self.gene = gene
        self.fitness = Chromosome.calculate_fitness(self.gene)

    def crossover(self,argc):
        if argc['type']=='single_point':
            return self.crossover_single_point(argc['other_chromosome'])
        elif argc['type']=='two_point':
            return self.crossover_two_point(argc['other_chromosome'])
        elif argc['type']=='uniforms':
            return self.crossover_uniforms(argc['other_chromosome'])
        elif argc['type']=='pmx':
            return self.crossover_pmx(argc['other_chromosome'])
        elif argc['type']=='ox':
            return self.crossover_ox(argc['other_chromosome'])
        elif argc['type']=='cx':
            return self.crossover_cx(argc['other_chromosome'])

    def mutation(self,argc):
        if argc['type']=='all':
            self.mutation_all()
            self.fitness = Chromosome.calculate_fitness(self.gene)
        elif argc['type']=='some':
            if 'k' in argc.keys():
                self.mutation_some(argc['k'])
            else:
                self.mutation_some()
            self.fitness = Chromosome.calculate_fitness(self.gene)
        elif argc['type']=='swap':
            if 'k' in argc.keys():
                self.mutation_swap(argc['k'])
            else:
                self.mutation_swap()
            self.fitness = Chromosome.calculate_fitness(self.gene)
        elif argc['type']=='insert':
            self.mutation_insert()
            self.fitness = Chromosome.calculate_fitness(self.gene)
        elif argc['type']=='inversion':
            self.mutation_inversion()
            self.fitness = Chromosome.calculate_fitness(self.gene)
        elif argc['type']=='scrumble':
            self.mutation_scrumble()
            self.fitness = Chromosome.calculate_fitness(self.gene)

    def crossover_single_point(self, other_chromosome):
        crossover_point = random.randint(1, len(self.gene) - 1)

        gene1 = self.gene[:crossover_point] + other_chromosome.gene[crossover_point:]
        gene2 = other_chromosome.gene[:crossover_point] + self.gene[crossover_point:]

        chromosome1 = Chromosome(gene1)
        chromosome2 = Chromosome(gene2)

        return chromosome1, chromosome2

    def crossover_two_point(self, other_chromosome):
        crossover_point1 = random.randint(1, len(self.gene) - 2)
        crossover_point2 = random.randint(crossover_point1 + 1, len(self.gene) - 1)

        gene1 = self.gene[:crossover_point1] + other_chromosome.gene[crossover_point1:crossover_point2] + self.gene[crossover_point2:]
        gene2 = other_chromosome.gene[:crossover_point1] + self.gene[crossover_point1:crossover_point2] + other_chromosome.gene[crossover_point2:]

        chromosome1 = Chromosome(gene1)
        chromosome2 = Chromosome(gene2)

        return chromosome1, chromosome2

    def crossover_uniforms(self, other_chromosome):
        mask = [random.randint(0,1) for _ in range(len(self.gene))]
        
        gene1 = []
        gene2= []
        for i,v in enumerate(mask):
            if v==0:
                gene1.append(self.gene[i])
                gene2.append(other_chromosome.gene[i])
            else:
                gene1.append(other_chromosome.gene[i])
                gene2.append(self.gene[i])

    def crossover_pmx(self, other_chromosome):
        try:
            crossover_point1 = random.randint(0, len(self.gene) - 2)
            crossover_point2 = random.randint(crossover_point1 + 1, len(self.gene) - 1)

            gene1 = self.gene
            gene2 = other_chromosome.gene

            offspring_gene1 = self.__pmx_crossover(gene1, gene2, crossover_point1, crossover_point2)
            offspring_gene2 = self.__pmx_crossover(gene2, gene1, crossover_point1, crossover_point2)

            chromosome1 = Chromosome(offspring_gene1)
            chromosome2 = Chromosome(offspring_gene2)

            return chromosome1, chromosome2
        except:
            print("ERRRRRRRRRRRRRR1")

    def crossover_ox(self, other_chromosome):
        crossover_point1 = random.randint(0, len(self.gene) - 2)
        crossover_point2 = random.randint(crossover_point1 + 1, len(self.gene) - 1)

        gene1 = self.gene
        gene2 = other_chromosome.gene

        offspring_gene1 = self.__ox_crossover(gene1, gene2, crossover_point1, crossover_point2)
        offspring_gene2 = self.__ox_crossover(gene2, gene1, crossover_point1, crossover_point2)

        chromosome1 = Chromosome(offspring_gene1)
        chromosome2 = Chromosome(offspring_gene2)

        return chromosome1, chromosome2

    def crossover_cx(self, other_chromosome):
        offspring_gene1 = [None for _ in range(len(self.gene))]
        offspring_gene2 = [None for _ in range(len(other_chromosome.gene))]
        visited_indices = set()

        current_index = 0
        while True:
            if current_index in visited_indices:
                # If the current index has already been visited, find the next available index
                current_index = next(i for i in range(len(self.gene)) if i not in visited_indices)
            visited_indices.add(current_index)
            offspring_gene1[current_index] = self.gene[current_index]
            offspring_gene2[current_index] = other_chromosome.gene[current_index]

            # Check if the current index exists in the other chromosome's gene
            if other_chromosome.gene[current_index] in self.gene:
                current_index = self.gene.index(other_chromosome.gene[current_index])
            else:
                # If the current index doesn't exist, find the next available index
                current_index = next(i for i in range(len(self.gene)) if i not in visited_indices)

            # Break the loop if we've returned to the starting index
            if current_index == 0:
                break

        for i in range(len(offspring_gene1)):
            if offspring_gene1[i] is None:
                offspring_gene1[i] = other_chromosome.gene[i]
                offspring_gene2[i] = self.gene[i]

        chromosome1 = Chromosome(offspring_gene1)
        chromosome2 = Chromosome(offspring_gene2)

        return chromosome1, chromosome2


    #only for binery
    def mutation_all(self):
        if Chromosome.mutation_rate is not None:
            for v,i in enumerate(self.gene):
                if random.random()<Chromosome.mutation_rate:
                    if v:
                        self.gene[i] = 0
                    else:
                        self.gene[i] = 1
        else:
            raise ValueError("Mutation rate is not set")
    
    #only for binery
    def mutation_some(self,k=1):
        if Chromosome.mutation_rate is not None:
            A = random.choices(range(len(self.gene)),k=k)
            for i in A:
                if random.random()<Chromosome.mutation_rate:
                    if self.gene[i]:
                        self.gene[i] = 0
                    else:
                        self.gene[i] = 1
        else:
            raise ValueError("Mutation rate is not set")

    def mutation_swap(self,k=1):
        if Chromosome.mutation_rate is not None:
            A = random.choices(range(len(self.gene)),k=k*2)
            for i in range(k):
                a1 = A.pop()
                a2 = A.pop()
                if not random.random()<Chromosome.mutation_rate:
                    continue
                self.gene[a1] , self.gene[a2] = self.gene[a2] , self.gene[a1] 
        else:
            raise ValueError("Mutation rate is not set")

    def mutation_insert(self):
        if Chromosome.mutation_rate is not None:
            if random.random()<Chromosome.mutation_rate:
                return
            point1 = random.randint(0, len(self.gene) - 2)
            point2 = random.randint(point1 + 1, len(self.gene) - 1)

            for i in range(point2,point1+1,-1):
                self.gene[i] , self.gene[i-1] = self.gene[i-1] , self.gene[i]
        else:
            raise ValueError("Mutation rate is not set")
    
    def mutation_inversion(self):
        if Chromosome.mutation_rate is not None:
            if random.random()<Chromosome.mutation_rate:
                return
            point1 = random.randint(0, len(self.gene) - 2)
            point2 = random.randint(point1 + 1, len(self.gene) - 1)
            self.gene[point1:point2+1] = self.gene[point1:point2+1][::-1]
        else:
            raise ValueError("Mutation rate is not set")

    def mutation_scrumble(self):
        if Chromosome.mutation_rate is not None:
            if random.random()<Chromosome.mutation_rate:
                return
            point1 = random.randint(0, len(self.gene) - 2)
            point2 = random.randint(point1 + 1, len(self.gene) - 1)
            self.gene[point1:point2+1] = random.sample(self.gene[point1:point2+1],k=point2+1-point1)
        else:
            raise ValueError("Mutation rate is not set")

    def __pmx_crossover(self,gene1, gene2, crossover_point1, crossover_point2):
        try:
            offspring_gene = [None for i in range(len(gene1))]
            offspring_gene[crossover_point1:crossover_point2+1] = gene1[crossover_point1:crossover_point2+1]

            index2 = 0
            for i in range(len(gene1)):
                if offspring_gene[i] == None:
                    while True:
                        if gene2[index2] not in offspring_gene:
                            offspring_gene[i] = gene2[index2]
                            index2 += 1
                            break
                        index2 += 1
                            

            return offspring_gene
        except:
            print("ERRRRRRR")

    def __ox_crossover(self,gene1, gene2, crossover_point1, crossover_point2):
        offspring_gene = [None for i in range(len(gene1))]
        offspring_gene[crossover_point1:crossover_point2+1] = gene1[crossover_point1:crossover_point2+1]

        gene2_index = 0
        for i in range(len(gene2)):
            if offspring_gene[i] ==None:
                while gene2[gene2_index] in offspring_gene:
                    gene2_index += 1
                offspring_gene[i] = gene2[gene2_index]
                gene2_index += 1

        return offspring_gene

    @staticmethod
    def calculate_fitness(gene):
        if Chromosome.fitness_function is not None:
            return Chromosome.fitness_function(gene)
        else:
            raise ValueError("Fitness function is not set")

    def __eq__(self, other):
        if other is None:
            return False
        return self.gene == other.gene

class Genetic:
    def __init__(self,fitness_function,population_size,
                mutation_rate,random_gen_maker,crossover_type,
                mutation_type,isbest_min,selection_function_type,
                replacement_function_type,selection_size) -> None:
        self.population_size = population_size
        Chromosome.fitness_function = fitness_function
        Chromosome.mutation_rate = mutation_rate
        self.generation = 0
        self.randome_gene_maker = random_gen_maker
        self.mutation_type = mutation_type
        self.crossover_type = crossover_type
        self.best = None
        self.bestgen = 0
        self.isbest_min = isbest_min
        self.selection_type = selection_function_type
        self.replacement_function_type = replacement_function_type
        self.selection_size = selection_size
    

    def selection_function(self,population):
        if self.selection_type=='random':
            return random.sample(population,self.selection_size[0])
        elif self.selection_type=='best':
            return sorted(population,key=lambda x:x.fitness)[:self.selection_size[0]]
        elif self.selection_type == 'roulette':
            selected = []
            total_fitness = sum(1 / chromosome.fitness for chromosome in population)  # Invert fitness values

            while len(selected) < self.selection_size[0]:
                r = random.uniform(0, total_fitness)
                cumulative_fitness = 0

                for chromosome in population:
                    cumulative_fitness += 1 / chromosome.fitness  # Invert fitness values

                    if cumulative_fitness >= r:
                        selected.append(chromosome)
                        break

            return selected
        elif self.selection_type == 'tournament':
            selected = []

            while len(selected) < self.selection_size[0]:
                tournament = random.sample(population, self.selection_size[1])
                winner = min(tournament, key=lambda chromosome: chromosome.fitness)
                selected.append(winner)

            return selected
        elif self.selection_type == 'rank':
            ranked_population = sorted(population, key=lambda chromosome: chromosome.fitness,reverse=True)
            probabilities = [i / len(ranked_population) for i in range(1, len(ranked_population) + 1)]
    
            selected = random.choices(ranked_population, weights=probabilities, k=self.selection_size[0])
            return selected
        else:
            # Default selection method: random selection
            return random.sample(population, self.selection_size[0])
    def replacement_function(self,oldgeneration,newgeneration):
        if self.replacement_function_type == 'new':
            A = newgeneration
            index = 0
            while len(A)<len(oldgeneration):
                rndch=random.choice(oldgeneration)
                if rndch not in A:
                    A.append(rndch)
                    index = 0
                else:
                    index += 1
                if index>=50:
                    A.append(rndch)
            return newgeneration 
        elif self.replacement_function_type == 'best':
            A = []
            outed = sorted(oldgeneration + newgeneration , key=lambda x:x.fitness)
            for i in outed:
                if i not in A:
                    A.append(i)
                    if len(A)==len(oldgeneration):
                        break
            while(len(A)<len(oldgeneration)):
                A.append(random.choice(newgeneration))
            return A
        elif self.replacement_function_type == 'best-half':
            ot1 = sorted(oldgeneration,key=lambda x:x.fitness)
            ot2 = sorted(newgeneration,key=lambda x:x.fitness)
            A = []
            for i in ot1:
                if i not in A:
                    A.append(i)
                    if len(A)==len(oldgeneration)//2:
                        break
            index = 0
            for i in ot2:
                if i not in A:
                    A.append(i)
                    index == 0
                    if len(A)==len(oldgeneration):
                        break
                else:
                    index += 1
                    if index>=20:
                        A.append(i)
            while(len(A)<len(oldgeneration)):
                A.append(random.choice(newgeneration))
            return A
        elif self.replacement_function_type == 'new-best-old':
            ot1 = sorted(oldgeneration,key=lambda x:x.fitness)
            A = newgeneration
            for i in ot1:
                if len(A)>=len(oldgeneration):break
                if i not in A:
                    A.append(i)
            while(len(A)<len(oldgeneration)):
                A.append(random.choice(newgeneration))
            return A

    def Execute(self):
        population = []
        while len(population)<self.population_size:
            rndgene = self.randome_gene_maker()
            if rndgene not in population:
                population.append(rndgene)
        population = list(map(lambda x:Chromosome(x),population))
        while True:
            if self.best != None:
                a = self.best
                if self.isbest_min:
                    self.best = min(self.best,min(population,key=lambda x:x.fitness),key=lambda x:x.fitness)
                else:
                    self.best = max(self.best,max(population,key=lambda x:x.fitness),key=lambda x:x.fitness)
                if self.best is not a:
                    self.bestgen = self.generation
            else:
                if self.isbest_min:
                    self.best = min(population,key=lambda x:x.fitness)
                    self.bestgen = self.generation
                else:
                    self.best = max(population,key=lambda x:x.fitness)
                    self.bestgen = self.generation
            yield population

            # Generate new population
            new_generation = []
            selected_chromosomes = self.selection_function(population)

            for i in range(0, len(selected_chromosomes), 2):
                for p in range(100):
                    chromosome1 = selected_chromosomes[i]
                    chromosome2 = selected_chromosomes[i + 1]

                    self.crossover_type.update({'other_chromosome':chromosome2})

                    offspring1, offspring2 = chromosome1.crossover(self.crossover_type)

                    offspring1.mutation(self.mutation_type)
                    offspring2.mutation(self.mutation_type)

                    for j in new_generation:
                        if j.gene == offspring1.gene or j.gene == offspring2.gene:
                            break
                    else:
                        new_generation += [offspring1, offspring2]
                        break

            # Apply replacement
            population = self.replacement_function(population, new_generation)
            self.generation += 1