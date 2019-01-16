#Several counters two queues
from SimPy.Simulation import *
from random import expovariate, seed
import matplotlib.pyplot as plt
from matplotlib.colors import colorConverter as cc
import statistics
import math

## Model components ------------------------           
vip_total = 0.0
Warray = []
ubw = []
lbw = []
Wqarray = []
ubwq = []
lbwq = []

class Source(Process):
    """ Source generates customers randomly """

    def generate(self,number,meanTBA,resource):      
        for i in range(number):
            c = Customer(name = "Customer%02d"%(i,))
            activate(c,c.visit(b=resource))            
            t = expovariate(1/meanTBA)              
            yield hold,self,t
class vipSource(Process):
    def vipgenerate(self,number,meanTBA,resource):      
        for i in range(number):
            c = Customer(name = "vip%02d"%(i,))
            activate(c,c.visit(b=resource))            
            t = expovariate(1/meanTBA)              
            yield hold,self,t

class Customer(Process):
    """ Customer arrives, is served and leaves """
        
    def visit(self,b):                                
        arrive = now()
        count = 0.0
        global vip_total
        global Warray

        print "%8.4f %s: Here I am     "%(now(),self.name)
        yield request,self,b                          
        wait = now()-arrive
        wM.observe(wait);
        print "%8.4f %s: Waited %6.3f"%(now(),self.name,wait)
        
        tib = expovariate(1.0/timeInBank)
        Warray.append(wait + tib)
        Wqarray.append(wait)
        if 'vip' in self.name:
            count += wait
        vip_total += count
        #print "tib: ", tib            
        yield hold,self,tib                          
        yield release,self,b                         
        print "%8.4f %s: Finished      "%(now(),self.name)

def plot_mean_and_CI(mean, lb, ub, color_mean=None, color_shading=None):
    # plot the shaded range of the confidence intervals
    plt.fill_between(range(188), ub, lb,
                     color=color_shading, alpha=0.5)
    # plot the mean on top
    plt.xlabel('Xth Customer')
    plt.ylabel('Time in system')
    plt.plot(mean)

## Experiment data -------------------------         

maxNumber = 126
maxTime = 6700.0 # minutes                                      
timeInBank = 4 # mean, minutes                      
ARRint = 60.0/maxNumber   # mean, minutes    

theseed = 212121

vipNumber = 62
vipARRint = 60.0/vipNumber            

## Model/Experiment ------------------------------

seed(theseed)                                        
k = Resource(capacity=4,name="Counter",unitName="Clerk")
#print k
vipk = Resource(capacity=2,name="vip_Counter",unitName="vip_Clerk")
wM = Monitor()





initialize()
s = Source('Source')
svip = vipSource('vipSource')
activate(s, s.generate(number=maxNumber,meanTBA=ARRint, resource=k),at=0.0)    
activate(svip, svip.vipgenerate(number = vipNumber, meanTBA=vipARRint,resource = vipk), at=20.0)       
simulate(until=maxTime)

total = 0
totalwq = 0
for m in range(188):
    #ubw.append (Warray[m] + 1.96* (statistics.stdev(Warray)/ math.sqrt(188)))
    #lbw.append (Warray[m] - 1.96* (statistics.stdev(Warray)/ math.sqrt(188)))
    ubwq.append (Wqarray[m] + 1.96* (statistics.stdev(Wqarray)/ math.sqrt(188)))
    lbwq.append (Wqarray[m] - 1.96* (statistics.stdev(Wqarray)/ math.sqrt(188)))
    total += Warray[m]
    totalwq += Wqarray[m]
Avg = total / 188
Avgq = totalwq /188
fig = plt.figure(1, figsize=(9, 6.5))
plot_mean_and_CI(Wqarray,ubwq,lbwq,color_mean='g',color_shading='g')
plt.title('All Time:Mean and Confidence Interval of Wq parameter')
plt.show()

print "AvgW:",Avg
print "AvgWQ:", Avgq
print "L:", Avg * (188/60)
print "Lq:", (188/60) * (Avgq - (1/0.25))
result = wM.count(),wM.mean()
print "Average wait for %3d completions was %5.3f minutes."% result 
print "Average wait for VIP customer: ", vip_total/vipNumber ,"minutes" 
