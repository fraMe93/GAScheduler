import spade
import xmpp
import time
import sys
import os
import csv
import shutil
import smart_scheduler as sched

host="ubuntu.local"
database="./web/behaviours/allData"
dirName=None
fileName=None
dirResults="./results"

def getData1(b): #funzione per l'estrazione delle informazioni dal body dei messaggi

	d = []
	l=len(b)
	for i in range(l):
		if (b[i] == '['):
			j=1
			temp = b[i+j]
			while (b[i+j+1] != ']'):
				temp = temp+b[i+j+1]
				j=j+1
			d.append(temp)
	return d

def getData2(b): #funzione per l'estrazione delle informazioni dal body dei messaggi

	d = []
	l=len(b)
	for i in range(l):
		if (b[i] == '['):
			j=1
			temp = b[i+j]
			while (b[i+j+1] != ']'):
				temp = temp+b[i+j+1]
				j=j+1
			d.append(temp)
		if (b[i] == 'T'):
			j=2
			temp=b[i+j]
			while (b[i+j+1] != ' '):
				temp = temp+b[i+j+1]
				j=j+1
			d.append(temp)
	return d

'''class ProducerAgent(spade.Agent.Agent):

	class ReceiveUP(spade.Behaviour.Behaviour):
		#This behaviour will receive only UPDATE_PREDICTION messages
	
		#def onStart(self):
			#print "Starting receiving UPDATE_PREDICTION messages . . ."

		def _process(self):
			msg = None
			msg = self._receive(True)
			if msg is not None:
				if (msg.getSubject() == "PREDICTION_UPDATE"):
					print "I got an UPDATE_PREDICTION message!"
				else:
					print "I got no UPDATE_PREDICTION message!"	
			else:
				print "I waited but got no message!"				

	def _setup(self):
		print "Producer starting . . ."

		# XMPP message generic template
		mt = spade.Behaviour.MessageTemplate(xmpp.Message()) 

		# Add the RECEIVE_UPDATE_PREDICTION behaviour
		rup = self.ReceiveUP() 
		self.addBehaviour(rup, mt)'''	


class ReceiverAgent(spade.Agent.Agent):
	
	class ReceiveCP(spade.Behaviour.Behaviour):
		#This behaviour will receive only CREATE_PRODUCER messages
	
		#def onStart(self):
			#print "Starting receiving CREATE_PRODUCER messages . . ."

		def _process(self):
			msg = None
			msg = self._receive(True)
			if msg is not None:
				if (msg.getSubject() == "CREATE_PRODUCER"):
					print "I got a CREATE_PRODUCER message!"
					body = msg.getBody()
					print "Body is:",body
					data = getData1(body)
					pH=data[0]
					pID=data[1]
					print "Producer House:",pH+",","Producer ID:",pID

					#Binding
					with open("producers_bind.csv", "rb") as f:
						binding = csv.reader(f)
						for row in binding:
							if ((row[0]==pH) and (row[1]==pID)):
								csvName=row[2]

					if (os.path.isfile(dirName+"/production/"+fileName+".constraints.csv")==False):
						with open (dirName+"/production/"+fileName+".constraints.csv","wb") as f:
							writer=csv.writer(f, delimiter=',', quotechar='"', quoting=csv.QUOTE_MINIMAL)
							writer.writerow([csvName,'1'])
					else:
						with open (dirName+"/production/"+fileName+".constraints.csv","rb") as f:
							l = list(csv.reader(f))
						os.remove(dirName+"/production/"+fileName+".constraints.csv")
						with open (dirName+"/production/"+fileName+".constraints.csv","ab") as f:
							writer=csv.writer(f, delimiter=',', quotechar='"', quoting=csv.QUOTE_MINIMAL)
							permit=True
							for row in l:
								if (row[0]==csvName):
									temp=int(row[1])+1
									writer.writerow([csvName,str(temp)])
									permit=False
								else:
									writer.writerow(row)
							if (permit):
								writer.writerow([csvName,'1'])
					
					#p = ProducerAgent("taskscheduler@ubuntu.local", resource="pv_producer", password="secret")
					#p.start()
					#p.stop()
				else:
					print "I got no CREATE_PRODUCER message!"	
			else:
				print "I waited but got no message!"	

	class ReceiveCL(spade.Behaviour.Behaviour):
		#This behaviour will receive only CREATE_LOAD messages
	
		#def onStart(self):
			#print "Starting receiving CREATE_LOAD messages . . ."

		def _process(self):
			msg = None
			msg = self._receive(True)
			if msg is not None:
				if (msg.getSubject() == "LOAD"):
					print "I got a CREATE_LOAD message!"

					# ACK
					#ack = xmpp.Message()
					#ack.setTo(msg.getFrom())
					#ack.setSubject("ACK_CL")
					#self.myAgent.send(ack)

					body = msg.getBody()
					print "Body is:",body
					data = getData2(body)
					lH=data[0]
					lID=data[1]
					lT=data[2]
					est=data[3]
					lst=data[4]
					print "Load House:",lH+",","Load ID:",lID+",","Load Task:",lT+",","EST:",est+",","LST:",lst

					#Binding
					with open("consumers_bind.csv", "rb") as f:
						binding = csv.reader(f)
						for row in binding:
							if ((row[0]==lH) and (row[1]==lID) and (row[2]==lT)):
								csvName=row[3]

					if (os.path.isfile(dirName+"/consumption/"+fileName+".constraints.csv")==False):
						with open (dirName+"/consumption/"+fileName+".constraints.csv","wb") as f:
							writer=csv.writer(f, delimiter=',', quotechar='"', quoting=csv.QUOTE_MINIMAL)
							writer.writerow([csvName,est,lst])
					else:
						with open (dirName+"/consumption/"+fileName+".constraints.csv","ab") as f:
							writer=csv.writer(f, delimiter=',', quotechar='"', quoting=csv.QUOTE_MINIMAL)
							writer.writerow([csvName,est,lst])

					sched.main(dirName,fileName,dirResults)

				else:
					print "I got no CREATE_LOAD message!"	
			else:
				print "I waited but got no message!"

	class ReceiveDL(spade.Behaviour.Behaviour):
		#This behaviour will receive only DELETE_LOAD messages
	
		#def onStart(self):
			#print "Starting receiving DELETE_LOAD messages . . ."

		def _process(self):
			msg = None
			msg = self._receive(True)
			if msg is not None:
				if (msg.getSubject() == "DELETE_LOAD"):
					print "I got a DELETE_LOAD message!"
					body = msg.getBody()
					print "Body is:",body
					data = getData1(body)
					lH=data[0]
					lID=data[1]
					lT=data[2]
					print "Load House:",lH+",","Load ID:",lID+",","Load Task:",lT

					#Binding
					with open("consumers_bind.csv", "rb") as f:
						binding = csv.reader(f)
						for row in binding:
							if ((row[0]==lH) and (row[1]==lID) and (row[2]==lT)):
								csvName=row[3]
						
					if (os.path.isfile(dirName+"/consumption/"+fileName+".constraints.csv")==False):
						print "There is no Constraints file!"

					else:

						print "Updating file . . ."

						with open(dirName+"/consumption/"+fileName+".constraints.csv", "rb") as f:
							l = list(csv.reader(f))

						os.remove(dirName+"/consumption/"+fileName+".constraints.csv")

						with open(dirName+"/consumption/"+fileName+".constraints.csv", "ab") as f:
							writer = csv.writer(f, delimiter=',', quotechar='"', quoting=csv.QUOTE_MINIMAL)
							for row in l:
								if (row[0]!=csvName):
									writer.writerow(row)

						print "Update successfully!"

				else:
					print "I got no DELETE_LOAD message!"	
			else:
				print "I waited but got no message!"	

	def _setup(self):
		print "Receiver starting . . ."

		# XMPP message generic template
		mt = spade.Behaviour.MessageTemplate(xmpp.Message()) 

		# Add the RECEIVE_CREATE_PRODUCER behaviour
		rcp = self.ReceiveCP() 
		self.addBehaviour(rcp, mt)

		# Add the RECEIVE_CREATE_LOAD behaviour
		rcl = self.ReceiveCL() 
		self.addBehaviour(rcl, mt)

		# Add the RECEIVE_DELETE_LOAD behaviour
		rdl = self.ReceiveDL() 
		self.addBehaviour(rdl, mt)
			

if __name__ == "__main__":

	if (len(sys.argv)<2):
		print "Missing agent username!"
		sys.exit(0)

	global dirName
	global fileName

	username=sys.argv[1]
	JID=username+'@'+host
	dirName="./web/behaviours/"+username
	fileName=username

	if not os.path.exists(dirName):
    		os.makedirs(dirName)

	shutil.copytree(database+"/production",dirName+"/production")
	shutil.copytree(database+"/consumption",dirName+"/consumption")

	r = ReceiverAgent(JID, resource="actormanager", password="secret")
	r.start()

alive = True
while alive:
    try:
        time.sleep(1)
    except KeyboardInterrupt:
        alive=False
r.stop()

'''if (os.path.isfile(dirName+"/production/"+fileName+".constraints.csv")==True): 
	os.remove(dirName+"/production/"+fileName+".constraints.csv")
if (os.path.isfile(dirName+"/consumption/"+fileName+".constraints.csv")==True): 
	os.remove(dirName+"/consumption/"+fileName+".constraints.csv")'''

shutil.rmtree(dirName)
sys.exit(0)
