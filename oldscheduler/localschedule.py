import scipy.interpolate as inter
import scipy.integrate as integ
import numpy as np
import pylab as plt
import random
from numpy import linspace
from numpy.lib.function_base import append
from os import listdir
from os.path import isfile, join


class Load():
    start_time = 0
    duration = 0
    spline = None
    earliest = 0
    latest = 0
    times = []

    def __init__(self, start_time, duration, spline, earliest, latest, times):
        self.start_time = start_time
        self.duration = duration
        self.spline = spline
        self.earliest = earliest
        self.latest = latest
        self.times = times

    def getSPLine(self):
        return self.spline

    def getStartTime(self):
        return self.start_time

    def getDuration(self):
        return self.duration

    def getTimes(self, delta):
        #tt = np.arange(self.start_time, self.start_time + self.duration, delta * 60)
        #return tt
        new_list = [x + self.start_time for x in self.times]

        return new_list

    # questa funzione prende in ingresso un array di tempi, li scala sotraendo lo start_time e poi
    # calcola l'array di valori corrispondenti a tali tempi e lo restituisce
    def getValues(self, tt):
        tt1 = np.zeros(len(tt))
        tt1[:] = [x - self.start_time for x in tt]
        return self.spline(tt1)

    def setStartTime(self, t):
        self.start_time = t

    def setEarliest(self, e):
        self.earliest = e

    def getEarliest(self):
        return self.earliest

    def setLatest(self, l):
        self.latest = l

    def getLatest(self):
        return self.latest


class Production():
    xx = []
    yy = []
    peak = 0

    def __init__(self, xx, yy, peak):
        self.xx = xx
        self.yy = yy
        self.peak = peak

    def getTimes(self):
        return self.xx

    def getValues(self):
        return self.yy

    def getStartTime(self):
        return self.xx[0]

    def getEndTime(self):
        return self.xx[len(self.xx) - 1]

    def getPeak(self):
        return self.peak


class GAOptimizer():
    delta = 3
    prediction_dir = "production"
    profile_dir = "consumption"
    production = None
    partial_prod = None
    schedule = None
    loads = []
    ESTs = []
    LSTs = []
    duration_average = 0
    max_consumption = 0
    performance = None
    self_consumption = []
    tot_consumption = []
    pivot = None

    def updatePrediction(self, dirname):

        mypath = dirname + "/" + self.prediction_dir
        behIDarr = dirname.split("/")
        behID = behIDarr[len(behIDarr)-1]
        constraints = []
        try:
            with open(mypath + "/" + behID + ".constraints.csv") as f:
                content = f.readlines()
                for item in content:
                    constraints.append(item.split(","))
            #constraints = np.genfromtxt(mypath + "/" + behID + ".constraints.csv", delimiter=",")
        except IOError:
            print('IO error opening the file ' + mypath + "/" + behID + ".constraints.csv")
            exit(0)
        # profiles contiene le spline, cioe' le funzioni interpolanti
        profiles = []
        end_times = []
        start_times = []

        for row in constraints:
            for count in range(0, int(row[1].strip())):
                csv = np.genfromtxt(mypath + "/" + row[0], delimiter=" ")
                print ("opening %s" %(mypath + "/" + row[0]))
                time1 = csv[:, 0]
                y1 = csv[:, 1]
                #print("prod: %s" %(time1))
                # questa funzione genera una spline: y=si(x)
                si = inter.InterpolatedUnivariateSpline(time1, y1)
                #knots=self.max_dev_knots(csv,3)
                #si = inter.LSQUnivariateSpline(time1, y1, k=3, t=knots)
                profiles.append(si)
                start_times.append(time1[0])
                end_times.append(time1[len(time1) - 1])

        # si procede col costruire un'unica funzione di produzione dell'energia
        # si somma la produzione di tutti i panneli in ogni intervallo
        # bisogna prima creare l'asse x prendendo il tempo piu' piccolo tra tutti i pannelli
        max_time = np.amax(end_times)
        # idem per quello massimo
        min_time = np.amin(start_times)
        #np.arange esclude l'estremo superiore, per includerlo dovremmo aggiungere un valore (per ora lascio commentato)
        xx = np.arange(min_time, max_time
                       #+ self.delta * 60
                        , self.delta * 60)
        yy = np.zeros(xx.shape)
        for i in range(0, len(xx)):
            for j in range(0, len(profiles)):
                if xx[i] >= start_times[j]:
                    if xx[i] <= end_times[j]:
                        yy[i] = yy[i] + profiles[j](xx[i])
                    else:
                        # se il pannello ha finito di produrre, si somma il suo valore all'istante finale
                        yy[i] = yy[i] + profiles[j](end_times[j])
        #convert energy2power
        y2 = np.zeros(len(yy))
        for jk in range(1, len(yy)):
            y2[jk] = 3600 * (yy[jk] - yy[jk - 1]) / (xx[jk] - xx[jk - 1])
        peak_value=np.amax(y2)
        # si inserisce in testa (0) all'array xx il valore min_time-300
        # COMMENTATE due righe
        # xx = np.insert(xx,0,min_time-300);
        # yy = np.insert(yy,0,0);
        # * 3 per generare una produzione comparabile con i consumi
        # yy[:] = [x*3 for x in yy]
        # l'oggetto production e' la produzione totale di tutti i pannelli
        self.production = Production(xx, yy, peak_value)

    def setPartialProduction(self, subsetindexes):
        xx = self.production.getTimes()
        yy = self.production.getValues()
        yy1 = np.zeros(yy.shape)
        yy1[0] = yy[0]
        for i in range(1, len(xx)):
            yy1[i] = yy[i]
            for j in range(0, len(self.loads)):
                temp = yy1[i] - yy1[i - 1]
                # if j not in subsetindexes, then it is a fixed load
                if j not in subsetindexes:
                    # bisogna usare la durata perche' sottraggo lo start time (individual[j]) all'istante attuale (xx[i])
                    # quindi t va confrontato con la durata, anche se la variabile si chiama end_time
                    end_time = self.loads[j].getDuration()
                    t = xx[i] - self.loads[j].getStartTime()
                    # se t>=0 significa che sto valutando un istante di tempo in cui il dispositivo e' gia' partito
                    # l'individuo e' infatti il tempo di avvio del dispositivo j-esimo
                    if t <= end_time and t >= 0:
                        #print("prod time %d, load %d start: %d,  end: %d" %(xx[i], j, int(self.loads[j].getStartTime()), int(self.loads[j].getStartTime()+self.loads[j].getDuration())))
                        #print("PRIMA: %d" %yy[i])
                        val = self.loads[j].getSPLine()(t) - self.loads[j].getSPLine()(xx[i - 1] - self.loads[j].getStartTime())
                        if val < 0:
                            val = 0
                        temp = temp - (val)
                        #yy[i] -= self.loads[j].getSPLine()(t)
                        #print("DOPO: %d" % yy[i])
                        if temp >=0 :
                            yy1[i] = yy1[i-1] + temp
                        else:
                            yy1[i] = yy1[i-1]
                            break
        #convert energy2power
        y2 = np.zeros(len(yy1))
        for jk in range(1, len(yy1)):
            y2[jk] = 3600 * (yy1[jk] - yy1[jk - 1]) / (xx[jk] - xx[jk - 1])
        peak_value = np.amax(y2)
        self.partial_prod = Production(xx, yy1, peak_value)


    def setPivotEnergy(self, interval_length):
        # compute the middle point of the interval with the max slope, given an interval length
        xx = self.production.getTimes()
        yy = self.production.getValues()
        maxi = 0
        piv_point = 0
        # we need to translate interval_length to the distance between indexes of times array
        distance = 0
        for i in range(0, len(xx)):
            if (xx[i] >= interval_length + xx[0]):
                distance = i
                break
        print distance
        for j in range(distance, len(xx), distance):
            if (yy[j] - yy[j - distance] > maxi):
                maxi = yy[j] - yy[j - distance]
                piv_point = xx[j] - interval_length / 2
                # print (xx[j]-xx[j-distance])

        self.pivot = piv_point
        print piv_point
        print maxi

    def setPivotPower(self, interval_length):
        # compute the middle point of the interval with the max area, given an interval length
        xx = self.production.getTimes()
        yy = self.production.getValues()
        yy1 = np.zeros(len(yy))
        for i in range(1, len(yy)):
            yy1[i] = (yy[i] - yy[i - 1]) / (xx[i] - xx[i - 1])

        # print xx
        # print yy1
        maxi = 0
        piv_point = 0
        for i in range(0, len(xx)):
            if (xx[i] <= xx[len(xx) - 1] - interval_length):
                xx2 = np.arange(xx[i], xx[i] + interval_length
                                #+ self.delta * 60
                                , self.delta * 60)
                yy2 = np.zeros(xx2.shape)
                for j in range(0, len(yy2)):
                    yy2[j] = yy1[i + j]
                temp_maxi = integ.simps(yy2, xx2)
                # print xx2, yy2
                if (temp_maxi > maxi):
                    maxi = temp_maxi
                    piv_point = xx[i] + interval_length / 2
        self.pivot = piv_point
        print piv_point

    # print maxi

    def setPivot(self, pivot):
        self.pivot = pivot

    def getPivot(self):
        return self.pivot

    # this function receives a time and returns the value and the index at that time
    def getProductionValue(self, time):
        #xx = self.production.getTimes()
        yy = self.production.getValues()
        index = int(time/(self.delta*60))
        if (index<len(yy) and index>=0):
            return (yy[index], index)
        elif index>=len(yy):
            return (yy[len(yy)-1], len(yy)-1)
        else:
            return (yy[0], 0)

    def getProductionValueByIndex(self, index):
        #xx = self.production.getTimes()
        yy = self.production.getValues()
        if (index<len(yy) and index>=0):
            return yy[index]
        elif index>=len(yy):
            return yy[len(yy)-1]
        else:
            return yy[0]

    def loadProfiles(self, dirname):

        cpath = dirname + "/" + self.profile_dir
        behIDarr = dirname.split("/")
        behID = behIDarr[len(behIDarr) - 1]
        constraints = []
        try:
            with open(cpath + "/" + behID + ".constraints.csv") as f:
                content = f.readlines()
                for item in content:
                    constraints.append(item.split(","))
            #constraints = np.genfromtxt(cpath + "/" + behID + ".constraints.csv", delimiter=",")
        except IOError:
            print('IO error opening the file ' + cpath + "/" + behID + ".constraints.csv")
            exit(0)

        sp_profiles = []
        start_times = []
        end_times = []
        temp_times = []

        #csv=[]
        for row in constraints:

            csv = np.genfromtxt(cpath + "/" + row[0], delimiter=" ")

            time1 = csv[:, 0]
            #print(time1)
            y1 = csv[:, 1]
            self.ESTs.append(int(row[1].strip()))
            self.LSTs.append(int(row[2].strip()))
            if not time1[0] == 0:
                time1 = np.insert(time1, 0, 0);
                y1 = np.insert(y1, 0, 0);
            si = inter.InterpolatedUnivariateSpline(time1, y1)
            #knots = self.max_dev_knots(csv, 3)
            #si = inter.LSQUnivariateSpline(time1, y1, k=3, t=knots)
            sp_profiles.append(si)
            start_times.append(time1[0])
            end_times.append(time1[len(time1) - 1])
            temp_times.append(time1)

        self.loads = []
        for i in range(0, len(sp_profiles)):
            #print(temp_times[i])
            # visto che il consumo parte da zero, l'end_time e' la durata
            self.loads.append(Load(start_times[i], end_times[i], sp_profiles[i], self.ESTs[i], self.LSTs[i], temp_times[i]))
            #calcolo durata media dei carichi
            self.duration_average += end_times[i]

        self.duration_average = self.duration_average/len(sp_profiles)
        self.duration_average = int(self.duration_average)

    def randomSchedule(self):
        if self.loads:
            individual = np.zeros(len(self.loads))
            for i in range(0, len(individual)):
                individual[i] = random.randrange(self.production.getStartTime(), self.production.getEndTime())
                # si aggiornano i tempi di partenza dei load, ovviamente poiche' ogni load ha la duration,
                # si possono eventualmente calcolare gli end_time
                self.loads[i].setStartTime(individual[i])
            self.schedule = individual

    def setSchedule(self, individual):
        if self.loads:
            for i in range(0, len(individual)):
                self.loads[i].setStartTime(individual[i])
            self.schedule = individual

    def plot(self):

        plt.plot(self.production.getTimes(), self.production.getValues(), 'b', linestyle='-', marker='.',
                 label="pv production")
        for j in range(0, len(self.schedule)):
            xx = self.loads[j].getTimes(self.delta)
            # print xx
            plt.plot(xx, self.loads[j].getValues(xx), 'r', linestyle='', marker='.', label="spline" + str(j))

        if self.self_consumption.any():
            plt.plot(self.production.getTimes(), self.self_consumption, 'y', linestyle='-', marker='.',
                     label="self_consumption")
        if self.tot_consumption.any():
            plt.plot(self.production.getTimes(), self.tot_consumption, 'g', linestyle='-', marker='.', label="somma")

    def plotpower(self):

        xx = self.production.getTimes()
        yy = self.production.getValues()
        yy1 = np.zeros(len(yy))
        for i in range(1, len(yy)):
            yy1[i] = 3600*(yy[i] - yy[i - 1]) / (xx[i] - xx[i - 1])

        plt.plot(xx, yy1, 'b', linestyle='-', marker='.', label="pv production")

        for j in range(0, len(self.schedule)):
            xx = self.loads[j].getTimes(self.delta)

            yy = self.loads[j].getValues(xx)
            yy1 = np.zeros(len(yy))
            for i in range(1, len(yy)):
                yy1[i] = 3600*(yy[i] - yy[i - 1]) / (xx[i] - xx[i - 1])
                #print("num: %s, den: %s, res: %s, instant: %s" %((yy[i]-yy[i-1]),(xx[i] - xx[i - 1]),yy1[i],xx[i]-self.loads[j].getStartTime()))

            plt.plot(xx, yy1, 'r', linestyle='-', marker='.', label="spline" + str(j))

        if self.self_consumption.any():
            xx = self.production.getTimes()
            yy = self.self_consumption
            yy1 = np.zeros(len(yy))
            for i in range(1, len(yy)):
                yy1[i] = 3600*(yy[i] - yy[i - 1]) / (xx[i] - xx[i - 1])
            plt.plot(xx, yy1, 'y', linestyle='-', marker='.', label="self_consumption")
        if self.tot_consumption.any():
            xx = self.production.getTimes()
            yy = self.tot_consumption
            yy1 = np.zeros(len(yy))
            for i in range(1, len(yy)):
                yy1[i] = 3600*(yy[i] - yy[i - 1]) / (xx[i] - xx[i - 1])
            plt.plot(xx, yy1, 'g', linestyle='-', marker='.', label="somma")

    def getSchedule(self):
        return self.schedule

    def updatePerformance(self):
        energy_out = 0
        energy_in = 0
        xx = self.production.getTimes()
        yy = self.production.getValues()
        individual = self.getSchedule()

        self_consumption = np.zeros(len(xx))
        tot_consumption = np.zeros(len(xx))

        sp_profiles = []
        for l in self.loads:
            sp_profiles.append(l.getSPLine())

        for i in range(1, len(xx)):
            temp = yy[i] - yy[i - 1]
            tot_consumption[i] = tot_consumption[i - 1]
            for j in range(0, len(sp_profiles)):
                # bisogna usare la durata perche' sottraggo lo start time (individual[j]) all'istante attuale (xx[i])
                # quindi t va confrontato con la durata, anche se la variabile si chiama end_time
                end_time = self.loads[j].getDuration()
                t = xx[i] - individual[j]
                # se t>=0 significa che sto valutando un istante di tempo in cui il dispositivo e' gia' partito
                # l'individuo e' infatti il tempo di avvio del dispositivo j-esimo
                if t <= end_time and t >= 0:
                    # sottraggo a quello che e' stato prodotto in questo intervallo di tempo, quello che il dispositivo j-esimo ha consumato
                    val = sp_profiles[j](xx[i] - individual[j]) - sp_profiles[j](xx[i - 1] - individual[j])
                    if val < 0:
                        val = 0
                    temp = temp - (val)
                    tot_consumption[i] = tot_consumption[i] + (
                    val)


            # temp>0 significa che ho consumato meno di quanto prodotto (nell'intervallo considerato)
            if temp > 0:
                energy_out = energy_out + temp
                self_consumption[i] = self_consumption[i - 1] + yy[i] - yy[i - 1] - temp
            else:
                # in questo caso temp e' <=0 ma per come e' definita la fitness, energy_in deve essere negativa
                energy_in = energy_in + temp
                self_consumption[i] = self_consumption[i - 1] + yy[i] - yy[i - 1]

        #tot_consumption energy2power
        yy2 = np.zeros(len(tot_consumption))
        for jk in range(1, len(tot_consumption)):
            yy2[jk] = 3600 * (tot_consumption[jk] - tot_consumption[jk - 1]) / (xx[jk] - xx[jk - 1])

        max_consumption = np.amax(yy2)
        self.performance = {'energy_in': energy_in, 'energy_out': energy_out, 'pvtotal': yy[len(yy) - 1],
                            'self_consumption': self_consumption[len(self_consumption) - 1],
                            'max_consumption': max_consumption}
        self.self_consumption = self_consumption
        self.tot_consumption = tot_consumption
        self.max_consumption = max_consumption
        return self.performance

    #this function defines the performance of a subset of genes of an individual
    def partialPerformance(self, subsetindexes):
        energy_out = 0
        energy_in = 0
        xx = self.production.getTimes()
        yy = self.production.getValues()
        #xx = self.partial_prod.getTimes()
        #yy = self.partial_prod.getValues()
        #print (xx)
        #print (yy)
        individual = self.getSchedule()

        self_consumption = np.zeros(len(xx))
        tot_consumption = np.zeros(len(xx))

        sp_profiles = []
        for l in subsetindexes :
            sp_profiles.append([self.loads[l].getSPLine(), l])

        for i in range(1, len(xx)):
            temp = yy[i] - yy[i - 1]
            tot_consumption[i] = tot_consumption[i - 1]
            for j in range(0, len(sp_profiles)):
                # bisogna usare la durata perche' sottraggo lo start time (individual[j]) all'istante attuale (xx[i])
                # quindi t va confrontato con la durata, anche se la variabile si chiama end_time
                end_time = self.loads[sp_profiles[j][1]].getDuration()
                t = xx[i] - individual[sp_profiles[j][1]]
                # se t>=0 significa che sto valutando un istante di tempo in cui il dispositivo e' gia' partito
                # l'individuo e' infatti il tempo di avvio del dispositivo j-esimo
                if t <= end_time and t >= 0:
                    # sottraggo a quello che e' stato prodotto in questo intervallo di tempo, quello che il dispositivo j-esimo ha consumato
                    val = sp_profiles[j][0](xx[i] - individual[sp_profiles[j][1]]) - sp_profiles[j][0](
                        xx[i - 1] - individual[sp_profiles[j][1]])
                    if val < 0 :
                        val = 0
                    temp = temp - (val)
                    tot_consumption[i] = tot_consumption[i] + (
                    val)

            # temp>0 significa che ho consumato meno di quanto prodotto (nell'intervallo considerato)
            if temp > 0:
                energy_out = energy_out + temp
                self_consumption[i] = self_consumption[i - 1] + yy[i] - yy[i - 1] - temp
            else:
                # in questo caso temp e' <=0 ma per come e' definita la fitness, energy_in deve essere negativa
                energy_in = energy_in + temp
                self_consumption[i] = self_consumption[i - 1] + yy[i] - yy[i - 1]

        # tot_consumption energy2power
        yy2 = np.zeros(len(tot_consumption))
        for jk in range(1, len(tot_consumption)):
            yy2[jk] = 3600 * (tot_consumption[jk] - tot_consumption[jk - 1]) / (xx[jk] - xx[jk - 1])

        max_consumption = np.amax(yy2)
        performance = {'energy_in': energy_in, 'energy_out': energy_out, 'pvtotal': yy[len(yy) - 1],
                            'self_consumption': self_consumption[len(self_consumption) - 1],
                       'max_consumption': max_consumption}
        #self.self_consumption = self_consumption
        #self.tot_consumption = tot_consumption
        return performance

    def max_dev_knots(self, ts,nk):
        knots = None
        max_dev = 0
        delta = int(len(ts) / (nk+1))
        i = delta
        n = 0
        j=0
        while j < nk and i < len(ts)-delta-nk:
         max_dev = 0
         for n in range(0,delta):
             i=i+1
             temp = abs((ts[i,1]-ts[i-1,1]))
             if temp > max_dev:
                 max_dev = temp
                 temp_x = i
         if knots is None:
             knots =[ts[temp_x,0]]

         else:
             knots.append(ts[temp_x,0])
         #plot([ts[temp_x, 0]], [ts[temp_x, 1]], 'o')
         j=j+1

        return knots


if __name__ == "__main__":
    problem = GAOptimizer()
    problem.updatePrediction()
    problem.loadProfiles([(problem.production.getStartTime(), problem.production.getEndTime()),
                          (problem.production.getStartTime(), problem.production.getEndTime()),
                          (problem.production.getStartTime(), problem.production.getEndTime()),
                          (problem.production.getStartTime(), problem.production.getEndTime()),
                          (problem.production.getStartTime(), problem.production.getEndTime())])
    problem.randomSchedule()
    performance = problem.updatePerformance()
    schedule = problem.getSchedule()
    print("CIAO: ", problem.getProductionValue(180))
    print schedule
    print performance
    fitness = performance['energy_out'] - performance['energy_in']
    print fitness
    problem.plotpower()
    plt.show()