import random
import pylab as plt
import os
import csv
import time
import shutil
from datetime import datetime 
from deap import base
from deap import creator
from deap import tools
from itertools import repeat
from collections import Sequence

import oldscheduler.localschedule as lc

myProblem = lc.GAOptimizer()
index_gen = 0
index_ind = 0
actual_incr = 0


def evalOneMul(individual):
    myProblem.setSchedule(individual)
    myProblem.updatePerformance()
    fitness1 = myProblem.performance['energy_out'] - myProblem.performance['energy_in']
    fitness2 = myProblem.production.getPeak() - myProblem.max_consumption
    return fitness1, fitness2

#CAST=Candidate Actual Start Time
#con l'indice si tiene traccia di che gene stiamo parlando, in modo da settare correttamenrte EST e LST
def gen_cast():
   global index_gen
   if (index_gen == len(myProblem.loads)):
       index_gen = 0
   cast = random.randint(myProblem.loads[index_gen].earliest, myProblem.loads[index_gen].latest)
   index_gen += 1
   return cast

#defines increasing intervals, splatting start times in uniform way each time
def smart_gen_cast(numind):
    global myProblem
    global index_gen
    global index_ind
    global actual_incr
    amplitude = myProblem.production.getEndTime() - myProblem.production.getStartTime()
    increment_const = int(amplitude / numind)
    if (index_gen == len(myProblem.loads)):
        index_gen = 0
        index_ind += 1
        actual_incr += increment_const
    if (index_ind == 0):
        #print ("AVERAGE: ", myProblem.duration_average)
        actual_incr = myProblem.duration_average
        step = int(actual_incr / len(myProblem.loads))
        cast = myProblem.getPivot() - step
    else:
        step = int(actual_incr / len(myProblem.loads))
        cast = (myProblem.getPivot() - step) + index_gen * (step)
    #recompute start time
    if (cast < myProblem.production.getStartTime()):
        myProblem.setPivot(myProblem.getPivot() + abs(cast))
        cast = myProblem.getPivot() - step
    # recompute start time
    else:
        if (cast > myProblem.production.getEndTime() - myProblem.loads[index_gen].duration):
            myProblem.setPivot(myProblem.getPivot() - abs(cast))
            cast = myProblem.getPivot() - step
    # recompute start time
    if cast not in xrange(int(myProblem.loads[index_gen].earliest), int(myProblem.loads[index_gen].latest)+1):
        if myProblem.loads[index_gen].earliest - cast > 0:
            cast = myProblem.loads[index_gen].earliest
        else:
            cast = myProblem.loads[index_gen].latest
    index_gen += 1
    #print ("ACTUAL NTERVAL: " , step)
    return cast

#defines increasing intervals, splatting start times randomly each time
def smart_gen_cast_rand(numind):
    global myProblem
    global index_gen
    global index_ind
    global actual_incr
    #the amplitude should be equal to the time_window.. for now it is 24 hours
    amplitude = 86400 - 0
    increment_const = int(amplitude / numind)
    if (index_gen == len(myProblem.loads)):
        index_gen = 0
        index_ind += 1
        actual_incr += increment_const
    if (index_ind == 0):
        #print ("AVERAGE: ", myProblem.duration_average)
        #actual_incr = myProblem.duration_average
        actual_incr = increment_const
        #step = int(actual_incr/len(myProblem.loads))
        cast =  myProblem.getPivot() - myProblem.duration_average/2
    else:
        #step = int(actual_incr / len(myProblem.loads))
        cast = random.uniform(myProblem.getPivot() - actual_incr/2,
                              (myProblem.getPivot() + actual_incr/2) #- myProblem.loads[index_gen].duration
                              )
        print ("ACTUAL RANGE: %d , %d" % (
                         myProblem.getPivot() - actual_incr/2, myProblem.getPivot() + actual_incr/2 #- myProblem.loads[index_gen].duration
                            ))
    #recompute start time if outside the start time of time_window.. for now it is 0-86400(24hrs)
    #while (cast < myProblem.production.getStartTime()):
    while (myProblem.getPivot() - actual_incr/2 < 0) \
                    or (myProblem.getPivot() + actual_incr/2 > 86400):
        if(myProblem.getPivot() - actual_incr / 2 < 0):
            #myProblem.setPivot(myProblem.getPivot() - (myProblem.getPivot() - actual_incr / 2))
            myProblem.setPivot(myProblem.getPivot() + (0-(
                                                       myProblem.getPivot() - actual_incr / 2)))
        else:
            #myProblem.setPivot(myProblem.getPivot() - (myProblem.getPivot() + actual_incr/2))
            myProblem.setPivot(myProblem.getPivot() - ((myProblem.getPivot() + actual_incr / 2)-
                               86400))
        cast = random.uniform(myProblem.getPivot() - actual_incr/2,
                              (myProblem.getPivot() + actual_incr/2) #- myProblem.loads[index_gen].duration
                              )
        print ("ACTUAL RANGE: %d , %d" % (
                        myProblem.getPivot() - actual_incr/2, myProblem.getPivot() + actual_incr/2 #- myProblem.loads[index_gen].duration
                         ))

    # recompute start time
    '''else:
        while (cast > myProblem.production.getEndTime() - myProblem.loads[index_gen].duration):
            myProblem.setPivot(myProblem.getPivot() - abs(cast))
            cast = random.uniform(myProblem.getPivot() - actual_incr/2,
                                  (myProblem.getPivot() + actual_incr/2) #- myProblem.loads[index_gen].duration
                                  )
            print ("ACTUAL RANGE: %d , %d" % (
                        myProblem.getPivot() - actual_incr/2, myProblem.getPivot() + actual_incr/2 #- myProblem.loads[index_gen].duration
                        ))'''
    # recompute start time
    if int(cast) not in xrange(int(myProblem.loads[index_gen].earliest), int(myProblem.loads[index_gen].latest)+1):
        #if myProblem.loads[index_gen].earliest - cast > 0:
            #cast = myProblem.loads[index_gen].earliest
        #    cast = random.randint(myProblem.loads[index_gen].earliest,myProblem.loads[index_gen].latest)
        #else:
            #cast = myProblem.loads[index_gen].latest
        cast = random.randint(myProblem.loads[index_gen].earliest, myProblem.loads[index_gen].latest)
    index_gen += 1
    print ("ACTUAL NTERVAL: %d" % actual_incr)
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


def smart_cxUniform(ind1, ind2):
    """Executes a uniform crossover that modify in place the two
    :term:`sequence` individuals. The attributes are swapped accordingto the
    *indpb* probability, that is calculated for each gene.

    :param ind1: The first individual participating in the crossover.
    :param ind2: The second individual participating in the crossover.
    :returns: A tuple of two individuals.

    This function uses the :func:`~random.random` function from the python base
    :mod:`random` module.
    """
    size = min(len(ind1), len(ind2))
    for i in xrange(size):
        indpb = 0.5
        val1 = myProblem.getProductionValue(ind1[i])
        val2 = myProblem.getProductionValue(ind2[i])

        #nextval1 = myProblem.getProductionValueByIndex(val1[1] + 10)
        nextval1 = myProblem.getProductionValue(val1[0] + myProblem.loads[i].duration/2)
        slope1 = nextval1[0] - val1[0]
        #nextval2 = myProblem.getProductionValueByIndex(val2[1] + 10)
        nextval2 = myProblem.getProductionValue(val2[0] + myProblem.loads[i].duration/2)
        slope2 = nextval2[0] - val2[0]
        if (slope1 < slope2):
            indpb = 0.6
        else:
            if (slope1 > slope2):
                indpb = 0.4

        if random.random() < indpb:
            ind1[i], ind2[i] = ind2[i], ind1[i]


    return ind1, ind2


def smart_cxTwoPoint(ind1, ind2):
    """Executes a SMART wrapped two-point crossover on the input :term:`sequence`
    individuals. The two individuals are modified in place and both keep
    their original length.

    :param ind1: The first individual participating in the crossover.
    :param ind2: The second individual participating in the crossover.
    :returns: A tuple of two individuals.
    This function uses the :func:`~random.randint` function from the Python
    base :mod:`random` module.
    """
    size = min(len(ind1), len(ind2))
    head = random.randint(0, size - 1)
    tail = random.randint(0, size - 1)
    if tail == head:
        tail += 1
    if tail>head:
        siz = tail - head
    else:
        siz = size - (head - tail)
    subsetindexes = [0] * siz
    i = head
    j = 0
    while (i != tail) and (j < siz):
        subsetindexes[j] = i
        i = (i+1) % size
        j += 1
    #if partial production should be used, the partialPerformance function must be changed
    #myProblem.setPartialProduction(subsetindexes)
    myProblem.setSchedule(ind1)
    perf1 = myProblem.partialPerformance(subsetindexes)
    myProblem.setSchedule(ind2)
    perf2 = myProblem.partialPerformance(subsetindexes)
    if (perf1['self_consumption']<perf2['self_consumption']):
        if tail > head:
            ind1[head:tail], ind2[head:tail] = ind2[head:tail], ind1[head:tail]
        else:
            ind1[head:], ind2[head:] = ind2[head:], ind1[head:]
            ind1[:tail], ind2[:tail] = ind2[:tail], ind1[:tail]

    return ind1, ind2


def smart_mutGaussian(individual, sigma, indpb):
    """This function applies a SMART gaussian mutation of mean *mu* and standard
    deviation *sigma* on the input individual. This mutation expects a
    :term:`sequence` individual composed of real valued attributes.
    The *indpb* argument is the probability of each attribute to be mutated.

    :param individual: Individual to be mutated.

    :param sigma: Standard deviation or :term:`python:sequence` of
                  standard deviations for the gaussian addition mutation.
    :returns: A tuple of one individual.

    This function uses the :func:`~random.random` and :func:`~random.gauss`
    functions from the python base :mod:`random` module.
    """
    size = len(individual)
    myProblem.setSchedule(individual)
    #this is to evaluate the performance of the entire individual
    performance = myProblem.updatePerformance()
    #print ("SMART MUTATION PERFORMANCE: %d" %(performance['energy_in']))
    #if not isinstance(mu, Sequence):
    #    mu = repeat(mu, size)
    #elif len(mu) < size:
    #    raise IndexError("mu must be at least the size of individual: %d < %d" % (len(mu), size))
    mu = [0] * size
    for k, start_time in enumerate(individual):
        #this one is to evaluate the performance of a single gene
        #performance = myProblem.partialPerformance([k])
        actual_val = myProblem.getProductionValue(start_time)
        #print "WATCH OUT: %s" %(str(actual_val[0]))
        #next_val = myProblem.getProductionValueByIndex(actual_val[1] + 10)
        #prev_val = myProblem.getProductionValueByIndex(actual_val[1] - 10)
        next_val = myProblem.getProductionValue(start_time + myProblem.loads[k].duration/2)
        prev_val = myProblem.getProductionValue(start_time - myProblem.loads[k].duration/2)
        if performance['energy_in'] < 0:
            if(next_val[0]-actual_val[0]) >= (actual_val[0]-prev_val[0]):
                mu[k] = int(sigma/2)
            #else (next_val[0]-actual_val[0]) < (actual_val[0]-prev_val[0]):
            else:
                mu[k] = -int(sigma/2)
            #in other cases we are outside the production bell, so mutation will try to bring him back
            #else:
                #if(start_time < myProblem.production.getStartTime()):
                #    mu[k] = myProblem.production.getStartTime() - start_time
                #else:
                #    mu[k] = -(start_time - myProblem.production.getEndTime())
                #another option is to center the bell in zero
                #mu[k] = 0
        else:
            if (next_val[0] - actual_val[0]) >= (actual_val[0] - prev_val[0]):
                mu[k] = -int(sigma/2)
            else:
                mu[k] = int(sigma/2)

    if not isinstance(sigma, Sequence):
        sigma = repeat(sigma, size)
    elif len(sigma) < size:
        raise IndexError("sigma must be at least the size of individual: %d < %d" % (len(sigma), size))

    for i, m, s in zip(xrange(size), mu, sigma):
        if random.random() < indpb:
            correction = random.gauss(m, s)
            #print("CORRECTION: %d" %(correction))
            #print("INDIVIDUO PRIMA: %d" %(individual[i]))
            individual[i] += correction
            #print("INDIVIDUO DOPO: %d" % (individual[i]))


    return individual,

def main(dirname,constFile,dirResults):
 
    global actual_incr
    global index_gen
    global index_ind
    actual_incr=0
    index_gen = 0
    index_ind = 0

    #random.seed(288)
    numind = 20
    myProblem.updatePrediction(dirname)
    # vincoli in termini di earliest e latest dei carichi
    #t_constraints = [(10100, 25541), (80, 9121), (0, 31500), (10208, 10208), (18956, 25000)]

    myProblem.loadProfiles(dirname)
    MIN = myProblem.ESTs  #[ele[0] for ele in t_constraints]
    MAX = myProblem.LSTs  #[ele[1] for ele in t_constraints]
    print("MIN: ", MIN)
    print("MAX: ", MAX)
    myProblem.setPivotEnergy(myProblem.duration_average)
    creator.create("FitnessMul", base.Fitness, weights=(-1.0,-1.0))
    creator.create("Individual", list, fitness=creator.FitnessMul)

    toolbox = base.Toolbox()
    # Attribute generator
    #creare un atrributo in base a EST e LST (geni)
    #toolbox.register("attr_bool", random.randint, myProblem.production.getStartTime(),
    #                 myProblem.production.getEndTime())
    toolbox.register("attr_bool", smart_gen_cast_rand, numind)
    #toolbox.register("attr_bool", gen_cast)
    # Structure initializers
    # "individual" e' un alias che corrisponde alla chiamata di toolbox.attr_bool un numero di volte
    # pari a len(myproblem.loads); il risultato di queta chiamata ripetuta e' messa nel container creator.Individual
    toolbox.register("individual", tools.initRepeat, creator.Individual,
                     toolbox.attr_bool, len(myProblem.loads))

    toolbox.register("population", tools.initRepeat, list, toolbox.individual)

    # Operator registering
    toolbox.register("evaluate", evalOneMul)
    #toolbox.register("mate", tools.cxTwoPoint)
    #toolbox.register("mate", smart_cxUniform)
    toolbox.register("mate", smart_cxTwoPoint)
    # sostituisco 0 e 31680
    #toolbox.register("mutate", tools.mutUniformInt, low = myProblem.production.getStartTime(), up = myProblem.production.getEndTime(), indpb=0.1)
    #toolbox.register("mutate", tools.mutGaussian, mu = 0, indpb=0.2)
    toolbox.register("mutate", smart_mutGaussian, indpb=0.2)
    toolbox.register("select", tools.selTournament, tournsize=3)
    # print('TIMES: ', myProblem.production.getStartTime(), ' ' , myProblem.production.getEndTime())

    toolbox.decorate("mate", checkBounds(MIN, MAX))
    toolbox.decorate("mutate", checkBounds(MIN, MAX))

    # n e' il parametro che mancava al register di population (il numero di chiamate a toolbox.individual)
    pop = toolbox.population(n=numind)
    CXPB, MUTPB, NGEN = 0.5, 0.2, 10
    print("INITIAL POPULATION: ", pop)
    print("Start of evolution")
    start = time.time()
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
                #oldmutant = toolbox.clone(mutant)
                #while True:
                    #breaking = True
                toolbox.mutate(mutant, sigma=stepsizes[index])
                    # print (mutant)
                    #for attr in mutant:
                        # print attr
                    #    if attr < myProblem.production.getStartTime() or attr > myProblem.production.getEndTime():
                    #        breaking = False
                    #if breaking:
                    #    break
                    #mutant = toolbox.clone(oldmutant)
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
        #meanind = [0] * len(pop[0])
        C = list()
        ([C.append(list(ci)) for ci in pop])
        meanind = ([sum(x) / length for x in zip(*C)])
        q = 0
        # doppia sommatoria norma
        for j, lol in enumerate(meanind):
            if(lol != 0):
                for ci in pop:
                    q += ((ci[j] - lol) / lol) ** 2
        qn = q / (len(pop) * len(meanind))
        print("  NORMA %s" % qn)
        # criterio di arresto
        if qn < 0.000001:
            break
    print("-- End of (successful) evolution --")
    end = time.time()
    best_ind = tools.selBest(pop, 1)[0]
    print("Best individual is %s, %s" % (best_ind, best_ind.fitness.values))
    myProblem.setSchedule(best_ind)
    result = myProblem.updatePerformance()
    date=datetime.now().strftime('%Y-%m-%d_%H:%M:%S')
    print result

    if not os.path.exists(dirResults+"/"+constFile):
    	os.makedirs(dirResults+"/"+constFile)

    if not os.path.exists(dirResults+"/"+constFile+"/"+date):
    	os.makedirs(dirResults+"/"+constFile+"/"+date)

    with open(dirResults+'/'+constFile+'/'+date+'/results.csv', 'ab') as csvfile:
        b = best_ind
        best_ind[:] = [int(x) for x in best_ind]
        reswriter = csv.writer(csvfile, delimiter=',',quotechar='"', quoting=csv.QUOTE_MINIMAL)
        reswriter.writerow([result['pvtotal'], result['energy_out'], result['energy_in'], result['self_consumption'], result['max_consumption'], mean, qn, MIN, MAX, b, end-start])
  
    shutil.copyfile(dirname+"/production/"+constFile+".constraints.csv",dirResults+"/"+constFile+"/"+date+"/"+constFile+"P.constraints.csv")
    shutil.copyfile(dirname+"/consumption/"+constFile+".constraints.csv",dirResults+"/"+constFile+"/"+date+"/"+constFile+"C.constraints.csv")

    #myProblem.plotpower()
    #plt.show()


if __name__ == "__main__":
    main("./web/behaviours/B12","./results")
