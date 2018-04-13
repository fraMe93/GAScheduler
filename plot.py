import matplotlib.pyplot as plt
import csv
import sys

def plotter(path,t):

	xtime=[]
	yenergy=[]
	ypower=[]
	
	with open (path,"rb") as f:
		data = csv.reader(f, delimiter=' ', quotechar='"')
		for row in data:
			#first column - time
			xtime.append(row[0])
			#second column - energy
			yenergy.append(row[1])
			ypower.append(row[1])
	
	#conversione di X
	for i in range(len(xtime)):
		xtime[i]=int(xtime[i])

	#conversione di Y
	for j in range(len(yenergy)):
		if(yenergy[j]=="0"):
			yenergy[j]=int(yenergy[j])
		else:			
			yenergy[j]=float(yenergy[j])


	#conversione di Y in potenza
	for j in range(len(yenergy)):
		if(yenergy[j]==0):
			ypower[j]=yenergy[j]
		else:			
			ypower[j]=(((yenergy[j]-yenergy[j-1])*3600)/(xtime[j]-xtime[j-1]))

	#aggiunta dell'offset temporale
	for i in range(len(xtime)):
		xtime[i]=xtime[i]+int(t)

	#individuo l'elemento Max di Y
	yMax=ypower[len(ypower)-1]
	for j in range(len(ypower)):
		if(ypower[j]>yMax):
			yMax=ypower[j]
		
	fig = plt.figure()
	ax = fig.add_axes([0.1,0.1,0.8,0.8])

	ax.set_xlabel ("Time [s]")
	ax.set_ylabel ("Power [kW]")
	ax.set_xlim (0, 86400)
	ax.set_ylim (0, yMax+1)
	ax.grid(color='black', linestyle='dotted', linewidth=1)
	marker_style=dict(marker='o', markersize=3)
	ax.plot (xtime, ypower, color='red', linewidth=1, label=path, **marker_style)
	ax.legend(bbox_to_anchor=(0., 1.02, 1., .102), loc=3,ncol=2, mode="expand", borderaxespad=0.)

	plt.show ()
	fig.savefig ('test.png')
	

if __name__ == "__main__":

	if (len(sys.argv)<3):
		print "Error!"
		sys.exit(0)

	path=sys.argv[1]
	time=sys.argv[2]

	plotter(path,time)

	sys.exit(1)
