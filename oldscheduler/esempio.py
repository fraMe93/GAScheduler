import random
import pylab as plt
from deap import base
from deap import creator
from deap import tools

import localschedule as lc

myProblem = lc.GAOptimizer()
index_gen = 0


def evalOneMin(individual):
    myProblem.setSchedule(individual)
    myProblem.updatePerformance()
    fitness = myProblem.performance['energy_out'] - myProblem.performance['energy_in']
    return [(fitness)]

#CAST=Candidate Actual Start Time
#con l'indice si tiene traccia di che gene stiamo parlando, in modo da settare correttamenrte EST e LST
def gen_cast():
    global index_gen
    if (index_gen == len(myProblem.loads)):
        index_gen = 0
    cast = random.randint(myProblem.loads[index_gen].earliest,myProblem.loads[index_gen].latest)
    index_gen += 1
    return cast

def checkBounds(min, max):
    def decorator(func):
        def wrapper(*args, **kargs):
            offspring = func(*args, **kargs)
            for child in offspring:
                for i in xrange(len(child)):
                    if child[i] > max[i]:
                        child[i] = max[i]
                    elif child[i] < min[i]:
                        child[i] = min[i]
            return offspring
        return wrapper
    return decorator

def main():
    myProblem.updatePrediction()
    # vincoli in termini di earliest e latest dei carichi
    #t_constraints = [(1300, 25000), (80, 9121), (4908, 5632), (1, 1), (10100, 15541)]
    t_constraints = [(0, 31680), (0, 31680), (0, 31680), (0, 31680), (0, 31680)]
    MIN = [ele[0] for ele in t_constraints]
    MAX = [ele[1] for ele in t_constraints]
    print("MIN: ", MIN)
    print("MAX: ", MAX)
    myProblem.loadProfiles(t_constraints)
    myProblem.setPivotEnergy(myProblem.duration_average)
    creator.create("FitnessMin", base.Fitness, weights=(-1.0,))
    creator.create("Individual", list, fitness=creator.FitnessMin)

    toolbox = base.Toolbox()
    # Attribute generator
    #creare un atrributo in base a EST e LST (geni)
    toolbox.register("attr_bool", gen_cast)
    # Structure initializers
    # "individual" e' un alias che corrisponde alla chiamata di toolbox.attr_bool un numero di volte
    # pari a len(myproblem.loads); il risultato di queta chiamata ripetuta e' messa nel container creator.Individual
    toolbox.register("individual", tools.initRepeat, creator.Individual,
                     toolbox.attr_bool, len(myProblem.loads))

    toolbox.register("population", tools.initRepeat, list, toolbox.individual)

    # Operator registering
    toolbox.register("evaluate", evalOneMin)
    toolbox.register("mate", tools.cxTwoPoint)
    # sostituisco 0 e 31680
    # toolbox.register("mutate", tools.mutUniformInt, low = myProblem.production.getStartTime(), up = myProblem.production.getEndTime(), indpb=0.1)
    toolbox.register("mutate", tools.mutGaussian, mu=0, indpb=0.2)
    toolbox.register("select", tools.selTournament, tournsize=3)
    # print('TIMES: ', myProblem.production.getStartTime(), ' ' , myProblem.production.getEndTime())

    #toolbox.decorate("mate", checkBounds(MIN, MAX))
    #toolbox.decorate("mutate", checkBounds(MIN, MAX))

    random.seed(64)

    # n e' il parametro che mancava al register di population (il numero di chiamate a toolbox.individual)
    pop = toolbox.population(n=20)
    CXPB, MUTPB, NGEN = 0.5, 0.2, 100
    print("INITIAL POPULATION: ", pop)
    print("Start of evolution")

    # Evaluate the entire population
    fitnesses = list(map(toolbox.evaluate, pop))
    for ind, fit in zip(pop, fitnesses):
        ind.fitness.values = fit

    print("  Evaluated %i individuals" % len(pop))

    # Begin the evolution
    # trattasi di algoritmo generazionale: evoluzionistico con numero di figli (genitori della prossima generazione) uguale al
    # numero di genitori. Si ottiene cio' selezionando un numero di genitori per l'acoppiamneto
    # pari al numro di individui totale
    # ovviamente visto che si fanno tot tornei, i genitori con fitness piu' alta compariranno piu' volte
    # tra i candidati all'accoppiamento per fare figli

    # initial stepsizes:
    stepsizes = [1000] * len(pop)
    alpha = 1.1
    for g in range(NGEN):
        print("-- Generation %i --" % g)

        # Select the next generation individuals
        # la selezione avviene grazie al fatto che nel for precedente ho assegnato una fitness a ogni individuo
        offspring = toolbox.select(pop, len(pop))
        # Clone the selected individuals
        offspring = list(map(toolbox.clone, offspring))

        # Apply crossover and mutation on the offspring
        for child1, child2 in zip(offspring[::2], offspring[1::2]):
            if random.random() < CXPB:
                toolbox.mate(child1, child2)
                # poiche' gli individui sono cambiati, la loro fitness va rivalutata!
                del child1.fitness.values
                del child2.fitness.values

        for index, mutant in enumerate(offspring):
            # cambio lo stepsize dell'individuo
            if random.random() < 0.5:
                stepsizes[index] = stepsizes[index] * alpha
            else:
                stepsizes[index] = round(stepsizes[index] / alpha)
            if random.random() < MUTPB:
                # print (stepsizes[index])
                # print (mutant)
                # controllo che la mutazione non abbia prodotto un individuo (mutante) invalido
                oldmutant = toolbox.clone(mutant)
                while True:
                    breaking = True
                    toolbox.mutate(mutant, sigma=stepsizes[index])
                    # print (mutant)
                    for attr in mutant:
                        # print attr
                        if attr < myProblem.production.getStartTime() or attr > myProblem.production.getEndTime():
                            breaking = False
                    if breaking:
                        break
                    mutant = toolbox.clone(oldmutant)
                    # poiche' l'individuo e' cambiato, la sua fitness va rivalutata!
                del mutant.fitness.values

        # Evaluate the individuals with an invalid fitness
        # (ovvero i risultati di mutazione e crossover, per i quali ho cancellato la fitness e quindi valid e' false)
        invalid_ind = [ind for ind in offspring if not ind.fitness.valid]
        fitnesses = map(toolbox.evaluate, invalid_ind)
        for ind, fit in zip(invalid_ind, fitnesses):
            ind.fitness.values = fit

        print("  Evaluated %i changed individuals" % len(invalid_ind))

        # The population is entirely replaced by the offspring
        pop[:] = offspring

        # Gather all the fitnesses in one list and print the stats
        fits = [ind.fitness.values[0] for ind in pop]

        length = len(pop)
        mean = sum(fits) / length
        sum2 = sum(x * x for x in fits)
        std = abs(sum2 / length - mean ** 2) ** 0.5

        print("  Min %s" % min(fits))
        print("  Max %s" % max(fits))
        print("  Avg %s" % mean)
        print("  Std %s" % std)

        # calcolo della norma dela popolazione per il criterio di arresto
        # calcolo l'individuo medio
        meanind = [0] * len(pop[0])
        C = list()
        ([C.append(list(ci)) for ci in pop])
        meanind = ([sum(x) / length for x in zip(*C)])
        q = 0
        # doppia sommatoria norma
        for j, lol in enumerate(meanind):
            for ci in pop:
                q += ((ci[j] - lol) / lol) ** 2
        qn = q / (len(pop) * len(meanind))
        print("  NORMA %s" % qn)
        # criterio di arresto
        if qn < 0.01:
            break
    print("-- End of (successful) evolution --")

    best_ind = tools.selBest(pop, 1)[0]
    print("Best individual is %s, %s" % (best_ind, best_ind.fitness.values))
    myProblem.setSchedule(best_ind)
    print myProblem.updatePerformance()
    myProblem.plotpower()
    plt.show()


if __name__ == "__main__":
    main()