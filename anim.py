import numpy as np
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation
import matplotlib.animation as an
plt.rcParams['animation.ffmpeg_path']='/home/1/17B00082/_mac/Desktop/ffmpeg-20200131-62d92a8-macos64-static/bin/ffmpeg'

#Assume a total of 1100000 people susceptible to the virus
N = 1100000
#actual infection number
#source (seen at 17:24 Feb 2): https://gisanddata.maps.arcgis.com/apps/opsdashboard/index.html#/bda7594740fd40299423467b48e9ecf6

actual = [278,326,547,639,916,2000,2700,6000,7700,9700,11200,11900,14326]

#hyper parameter initialize at random
gamma = np.random.rand()/100
beta = 2.24*gamma

I_inf = (beta-gamma)*N/beta #endemic infected population
V = I_inf/44-1 #Assume initial cases = 44

dt = 0.01 #unit time: 1/100 day
states = 20000 #number of instant that we consider
time = np.arange(0,states*dt,dt) #the range to plot


I = []

#Analytic solution:
# I = I_inf / (1 + V*e^((gamma-beta)*t))

for t in time:
	#actual solution:
	i = (I_inf)/(V*np.exp(gamma*t-beta*t)+1)
	I.append(np.minimum(i,N))
	
S = [N-i for i in I]

epochs = range(200) #number of trainings

froms =22
to=31
fig,(ax,ax1) = plt.subplots(2,1)
#error befor training happen
#error function: mean absolute error 

error= 0
for i in range(22,35):
	print("Day", i, ":", abs(actual[i-22]-I[i*100]), "different")
	error += abs(actual[i-22] - I[i*100])
print("Error before: ", error/12)

errors = []

lr = 1e-12
def animation(epoch):
	global gamma, beta,N,V,I_inf
		#changing the learning-rate for faster learning speed
		#------------------------------------------------------
	if epoch < 10:
		lr = 2*1e-12
	elif epoch < 30:
		lr = 1e-12
	elif epoch < 60:
		lr = 6*1e-13
	elif epoch < 200:
		lr = 3*1e-13
	else:
		lr = 1e-13
	
	print(gamma,beta)
	
	#------------------------------------------------------
	#Here we train the model, minimize the difference between predicted values and actual 	values 
	#for several random days using gradient descent
	#------------------------------------------------------
	t = np.array([22,23,24,25,27,30,32])
	m = np.array([I[i*100] for i in t])
	n = np.array([actual[i-22] for i in t])

	#---differential of I wrt gamma and beta---------------

	dI_infdgamma = -N/beta                                     # I_inf = (beta-gamma)*N/beta
	dVdgamma = dI_infdgamma/44								   # V = I_inf/44 - 1
	dexpdgamma = t.dot(np.exp((gamma-beta)*t))				   # exp((gamma-beta)*t)
	denom = 1+V*np.exp(gamma*t-beta*t)					 	   # denom = 1 + V*exp((gamma-beta)*t)
	ddenomdgamma = V*dexpdgamma+dVdgamma*np.exp(gamma*t-beta*t) 
	dI_infdbeta = gamma*N/beta**2							   # I_inf = (beta-gamma)*N/beta
	dVdbeta = dI_infdbeta/44								   # V = I_inf/44 - 1
	dexpdbeta = -t.dot(np.exp((gamma-beta)*t))				   # exp((gamma-beta)*t)
	ddenomdbeta = V*dexpdbeta+dVdbeta*np.exp(gamma*t-beta*t)

	dIdgamma = (dI_infdgamma*denom-ddenomdgamma*I_inf)/denom**2    # I = I_inf/denom
	dIdbeta = (dI_infdbeta*denom-ddenomdbeta*I_inf)/denom**2	   # I = I_inf/denom

	#-----update gamma and beta----------------------------
	#Update rule: gradient descent
	gamma -= lr*(m-n).dot(dIdgamma)
	beta -= lr*(m-n).dot(dIdbeta) 

	#-----update errors array------------------------------
	error= 0
	for i in t:
		error += abs(actual[i-22] - I[i*100])
	errors.append(error/len(t))

	#update the solution due to change of gamma and beta
	I_inf = (beta-gamma)*N/beta 
	V = I_inf/44-1
	for ts in t:
		I[ts*100] = np.minimum((I_inf)/(V*np.exp(gamma*ts-beta*ts)+1),N)

	#----------------------------------------------------
	#take the instant at several epochs to see learning steps

	Is = []
	for t in time:
		Is.append(np.minimum(N,(I_inf)/(V*np.exp(gamma*t-beta*t)+1)))
	ax.clear()
	ax1.clear()
	ax.plot(time,Is,label='analytical')
	ax.plot(range(22,35),actual,label="actual")
	ax.set_xlim(22,35)
	ax.set_ylim(0,15000)
	ax.legend(loc='best')
	ax.set_title('epoch #'+str(epoch))
	ax1.plot(errors)
	
	return ax,ax1
animation = FuncAnimation(fig, animation, frames=epochs,interval=70)
#plt.show()
Writer = an.writers['ffmpeg']
writer = Writer(fps=15, metadata=dict(artist='Me'), bitrate=1800)
animation.save("test.mp4",writer=writer)