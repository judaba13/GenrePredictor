from numpy import *
from matplotlib import pyplot as plt
import csv

data = csv.reader(open('famhot.csv'))
data = array([ x for x in data]).astype('float')
fam = [d[0] for d in data]
hot = [d[1] for d in data]
plt.figure()
plt.title("hotttnesss vs familiarity")
plt.xlabel("familiarity")
plt.ylabel("hotttnesss")
plt.plot(fam, hot, '.')
fThreshx = [0.65,0.65]
fThreshy = [0, 1]
hThreshx = [0, 1]
hThreshy = [0.4, 0.4]

plt.plot(fThreshx, fThreshy, 'r-')
plt.plot(hThreshx, hThreshy, 'r-')
plt.savefig("famhotgraph.png")
plt.show()
