import matplotlib.pyplot as plt
import csv
import sys

def plotter(path):

	xtime=[]
	yenergy=[]
	
	with open (path,"rb") as f:
		data = csv.reader(f, delimiter=' ', quotechar='"')
		for row in data:
			#first column - time
			xtime.append(row[0])
			#second column - energy
			yenergy.append(row[1])
	
	#conversione di X
	for i in range(len(xtime)):
		if(xtime[i].isdigit()):
			xtime[i]=int(xtime[i])
		else:
			xtime[i]=float(xtime[i])

	#conversione di Y
	for j in range(len(yenergy)):
		if(yenergy[j].isdigit()):
			yenergy[j]=int(yenergy[j])
		else:
			yenergy[j]=float(yenergy[j])		

	#individuo l'elemento Max di X
	xMax=xtime[len(xtime)-1]
	for i in range(len(xtime)):
		if(xtime[i]>xMax):
			xMax=xtime[i]

	#individuo l'elemento Max di Y
	yMax=yenergy[len(yenergy)-1]
	for j in range(len(yenergy)):
		if(yenergy[j]>yMax):
			yMax=yenergy[j]
		
	fig = plt.figure()
	ax = fig.add_axes([0.1,0.1,0.8,0.8])

	ax.set_xlabel ("Time [s]")
	ax.set_ylabel ("Energy [kWh]")
	ax.set_xlim (0, xMax+1000)
	ax.set_ylim (0, yMax+1)
	ax.grid(color='black', linestyle='--', linewidth=1)
	ax.plot (xtime, yenergy, color='red', linewidth=2)

	plt.show ()
	fig.savefig ('test.png')
	

if __name__ == "__main__":

	if (len(sys.argv)<2):
		print "Missing file path!"
		sys.exit(0)

	path=sys.argv[1]

	plotter(path)

	sys.exit(1)
