import random

class Chromosome:
    fitness_function = None
    mutation_rate = None

    def __init__(self, gene):
        self.gene = gene
        self.fitness = Chromosome.calculate_fitness(self.gene)

    def crossover(self,**arg):
        if arg['type']=='single_point':
            return self.crossover_single_point(arg['other_chromosome'])
        elif arg['type']=='two_point':
            return self.crossover_two_point(arg['other_chromosome'])
        elif arg['type']=='uniforms':
            return self.crossover_uniforms(arg['other_chromosome'])
        elif arg['type']=='pmx':
            return self.crossover_pmx(arg['other_chromosome'])
        elif arg['type']=='ox':
            return self.crossover_ox(arg['other_chromosome'])
        elif arg['type']=='cx':
            return self.crossover_cx(arg['other_chromosome'])

    def mutation(self,**arg):
        if arg['type']=='all':
            self.mutation_all()
            self.fitness = Chromosome.calculate_fitness(self.gene)
        elif arg['type']=='some':
            if 'k' in arg.keys:
                self.mutation_some(arg['k'])
            else:
                self.mutation_some()
            self.fitness = Chromosome.calculate_fitness(self.gene)
        elif arg['type']=='swap':
            if 'k' in arg.keys:
                self.mutation_swap(arg['k'])
            else:
                self.mutation_swap()
            self.fitness = Chromosome.calculate_fitness(self.gene)
        elif arg['type']=='insert':
            self.mutation_insert()
            self.fitness = Chromosome.calculate_fitness(self.gene)
        elif arg['type']=='inversion':
            self.mutation_inversion()
            self.fitness = Chromosome.calculate_fitness(self.gene)
        elif arg['type']=='scrumble':
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
        crossover_point1 = random.randint(0, len(self.gene) - 2)
        crossover_point2 = random.randint(crossover_point1 + 1, len(self.gene) - 1)

        gene1 = self.gene
        gene2 = other_chromosome.gene

        offspring_gene1 = self.__pmx_crossover(gene1, gene2, crossover_point1, crossover_point2)
        offspring_gene2 = self.__pmx_crossover(gene2, gene1, crossover_point1, crossover_point2)

        chromosome1 = Chromosome(offspring_gene1)
        chromosome2 = Chromosome(offspring_gene2)

        return chromosome1, chromosome2

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
        offspring_gene1 = [None for i in range(len(self.gene))]
        offspring_gene2 = [None for i in range(len(other_chromosome.gene))]

        visited_indices = set()

        current_index = 0
        while True:
            if current_index in visited_indices:
                break
            visited_indices.add(current_index)
            offspring_gene1[current_index] = self.gene[current_index]
            offspring_gene2[current_index] = other_chromosome.gene[current_index]
            current_index = self.gene.index(other_chromosome.gene[current_index])
            if current_index == next(i for i in range(len(self.gene)) if i not in visited_indices):
                break

        for i,v in enumerate(offspring_gene1):
            if v==None:
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
            self.gene[point1:point2+1] = self.gene[point2:point1-1:-1]
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

    @staticmethod
    def __pmx_crossover(gene1, gene2, crossover_point1, crossover_point2):
        offspring_gene = [None for i in range(len(gene1))]
        offspring_gene[crossover_point1:crossover_point2+1] = gene1[crossover_point1:crossover_point2+1]

        for i in range(crossover_point1, crossover_point2+1):
            if gene2[i] not in offspring_gene:
                value = gene2[i]
                index = i

                while gene1[index] in gene2[crossover_point1:crossover_point2+1]:
                    index = gene2.index(gene1[index])
                    value = gene1[index]

                offspring_gene[index] = value

        for i in range(len(gene1)):
            if offspring_gene[i] == None:
                offspring_gene[i] = gene2[i]

        return offspring_gene
    
    @staticmethod
    def __ox_crossover(gene1, gene2, crossover_point1, crossover_point2):
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

class Genetic:
    def __init__(self,fitness_function,population_size,
                mutation_rate,random_gen_maker,crossover_type,
                mutation_type,isbest_min,selection_function,
                replacement_function) -> None:
        self.population_site = population_size
        Chromosome.fitness_function = fitness_function
        Chromosome.mutation_rate = mutation_rate
        self.generation = 0
        self.randome_gene_maker = random_gen_maker
        self.mutation_type = mutation_type
        self.crossover_type = crossover_type
        self.best = None
        self.isbest_min = isbest_min
        self.selection_function = selection_function
        self.replacement_function = replacement_function
    
    def Execute(self):
        population = [Chromosome(self.randome_gene_maker()) for i in range(self.population_site)]
        while True:
            if self.isbest_min:
                self.best = min(population,key=lambda x:x.fitness)
            else:
                self.best = max(population,key=lambda x:x.fitness)
            yield population

            # Generate new population
            new_generation = []
            selected_chromosomes = self.selection_function(population,self.population_size)

            for i in range(0, len(selected_chromosomes), 2):
                chromosome1 = selected_chromosomes[i]
                chromosome2 = selected_chromosomes[i + 1]

                self.crossover_type.update({'other_chromosome':chromosome2})

                offspring1, offspring2 = chromosome1.crossover(self.crossover_type)

                offspring1.mutation(self.mutation_type)
                offspring2.mutation(self.mutation_type)

                new_generation += [offspring1, offspring2]

            # Apply replacement
            population = self.replacement_function(population, new_generation)
            self.generation += 1
