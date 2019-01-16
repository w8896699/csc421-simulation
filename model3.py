from SimPy.Simulation import *
from random import expovariate, seed
import matplotlib.pyplot as plt
from matplotlib.colors import colorConverter as cc
import statistics
import math

## Model components ------------------------
vip_total = 0.0
total_time_in_system = 0.0
total_cus_events=[]
international_individual = []
ubw = []
lbw = []
Larray = []
ubl = []
lbl = []
Wqarray = []
ubwq = []
lbwq = []
Lqarray = []
ublq = []
lblq = []
class Source(Process):
    """ Source generates customers randomly """

    def generate(self,number,interval,resource):
        global total_time_in_system       
        for i in range(number):
            c = Customer(name = "Customer%02d"%(i,))
            TimeInService=expovariate(1.0/4)
            activate(c,c.visit(TimeInService,
                               res=resource,P=0))
            total_time_in_system += TimeInService           
            t = expovariate(1.0/interval)
            yield hold,self,t
class vipSource(Process):
    def generatevip(self,number,interval,resource): 
        global total_time_in_system      
        for i in range(number):
            c = Customer(name = "vips%02d"%(i,))
            #print "I am here"
            TimeInService=expovariate(1.0/4)
            activate(c,c.visit(TimeInService,
                               res=resource,P=100)) 
            total_time_in_system += TimeInService          
            t = expovariate(1.0/interval)
            yield hold,self,t
class Customer(Process):

    """ Customer arrives, is served and  leaves """
        
    def visit(self,TimeInService=0,res=None,P=0):              
        count=0.0
        
        total_time = 0.0
        global vip_total
        global total_time_in_system
        global international_individual
        arrive = now()       # arrival time
        
        Nwaiting = len(res.waitQ)
        print "%8.3f %s: Queue is %d on arrival"%(now(),self.name,Nwaiting)
        print "avg # of customer in queue:", Nwaiting

        yield request,self,res,P                            
        wait = now()-arrive  # waiting time   
        wM.observe(wait); 
                   
        print "%8.3f %s: Waited %6.3f"%(now(),self.name,wait)
        international_individual.append(wait + TimeInService)
        #Wqarray.append(wait)
        if 'vips' in self.name:
            count += wait
            
        vip_total += count
        if 'Customer' in self.name:
            Wqarray.append(wait)
            
        total_time_in_system += wait
        #print "vip total",vip_total

        yield hold,self,TimeInService
        yield release,self,res                              
        
        print "%8.3f %s: Completed"%(now(),self.name)


def plot_mean_and_CI(mean, lb, ub, color_mean=None, color_shading=None):
    # plot the shaded range of the confidence intervals
    plt.fill_between(range(188), ub, lb,
                     color=color_shading, alpha=0.5)
    # plot the mean on top
    plt.xlabel('Time')
    plt.ylabel('L(t)')
    plt.plot(mean)

## Experiment data -------------------------

maxTime = 4000.0  # minutes                                
k = Resource(name="Counter",unitName="Karen",               
             qType=PriorityQ,capacity=6)                               

NumVIP = 90
NumCustomer = 98
customer_inter_arrival = 60.0/NumCustomer
vip_inter_arrivial = 60.0/NumVIP
## Model/Experiment ------------------------------
seed(123221)
initialize()
s = Source('Source')
wM = Monitor()
wMvip = Monitor()
svip = vipSource('Sourcevip')
activate(s,s.generate(number=NumCustomer, interval=customer_inter_arrival,              
                      resource=k),at=0.0)                   
  
activate(svip, svip.generatevip(number=NumVIP, interval=vip_inter_arrivial,
                        resource=k), at=0.0)               
simulate(until=maxTime)
totalw = 0
for a in range(188):
    ubw.append (international_individual[a] + 1.96* (statistics.stdev(international_individual)/ math.sqrt(188)))
    lbw.append (international_individual[a] - 1.96* (statistics.stdev(international_individual)/ math.sqrt(188)))
    totalw += international_individual[a]

total = 0
for i in range(98):
    ubwq.append (Wqarray[i] + 1.96* (statistics.stdev(Wqarray)/ math.sqrt(98)))
    lbwq.append (Wqarray[i] - 1.96* (statistics.stdev(Wqarray)/ math.sqrt(98)))
    #total+=international_individual[i]
    #Larray.append(international_individual[i] * customer_inter_arrival)


for i in range(98):
    Lqarray.append(Wqarray[i] * customer_inter_arrival)

for k in range(98):
    #ubl.append (Larray[k] + 1.96* (statistics.stdev(Larray)/ math.sqrt(98)))
    #lbl.append (Larray[k] - 1.96* (statistics.stdev(Larray)/ math.sqrt(98)))
    #ubwq.append (Wqarray[k] + 1.96* (statistics.stdev(Wqarray)/ math.sqrt(98)))
    #lbwq.append (Wqarray[k] - 1.96* (statistics.stdev(Wqarray)/ math.sqrt(98)))
    ublq.append(Lqarray[k] + 1.96* (statistics.stdev(Lqarray)/ math.sqrt(90)))
    lblq.append(Lqarray[k] - 1.96* (statistics.stdev(Lqarray)/ math.sqrt(90)))

for j in range(98):
    total+=Wqarray[j]
AvgW = totalw / 188
    
Avgwq = total / 98

fig = plt.figure(1, figsize=(9, 6.5))
plot_mean_and_CI(international_individual,ubw,lbw,color_mean='r',color_shading='r')
plt.title('International:Mean and Confidence Interval of Lq parameter for Single Queue with Priority')
plt.show()

result = wM.count(),wM.mean()
print "totalW:",AvgW
print "Avgwq:" ,Avgwq
#print Lqarray
print "totalL:",AvgW * (188/60)
print len(international_individual)
print "Wq:", AvgW - (1/0.25)
print "Lq:", (188/60) * (result[1] - (1/0.25))
print "Average wait for %3d completions was %5.3f minutes."% result
print "Average wait for VIP customer: ", vip_total/NumVIP ,"minutes"
