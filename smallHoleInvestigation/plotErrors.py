import os
import pandas as pd
from numpy import *
import scipy as sc
import matplotlib.pyplot as plt 
import pandas as pd
import matplotlib
matplotlib.rcParams.update({"font.size":20})

data = pd.read_csv("modifiedPressures.csv")
width, nSec, nHoles, backErr, inletErr = data["width"].values,data["nSection"].values,data["N"].values,data["MSerrorBack"].values,data["MSerrorInlet"].values
print(len(data[data["MSerrorInlet"] >-1]), (len(data)))
# Plot back pressure and inlet
"""
fig, ax = plt.subplots(1,1,figsize=(20,10))
x_multi = [backErr, inletErr]
ax.hist(x_multi, 20, histtype='bar')
ax.legend(["Pressure at closed tip", "Inlet pressure"])
ax.set_title("Relative percentage error ")
plt.savefig("allErrors.png")
plt.close()"""

fig, ax = plt.subplots(1,1,figsize=(20,10))
ax.hist(inletErr, bins=linspace(-5.25, 1,26), histtype='bar', label="External pressure $p_0$")
ax.set_ylabel("Frequency")
ax.set_xlabel("RPE")
ax.set_yticks(linspace(0,26,14))
plt.savefig("smallHolesHist.png")
plt.close()

fig, ax = plt.subplots(1,3,figsize=(30,10))

for i, err in enumerate(["MSerrorInlet"]):
    for j, xvar in enumerate([width, nSec, nHoles]):
        ax[j].scatter(xvar, data[err].values, label=err)
        ax[j].plot(xvar, [0]*len(xvar), "k")
        ax[j].set_ylabel("RPE")
        if j==0: ax[j].set_xlabel("Porous section width (mm)")
        if j==1: 
            ax[j].set_xlabel("Number of porous sections")
            ax[j].set_xticks(linspace(1,4,4))
        if j==2: ax[j].set_xlabel("Hole density")


fig.suptitle(f"Percentage relative errors")
plt.savefig("smallHolesErrs.png")
plt.close()


fig = plt.figure()
ax = fig.add_subplot(projection='3d')
sc = ax.scatter(width, nSec, nHoles,c=(inletErr))
ax.set_xlabel('Section width (mm)')
ax.set_ylabel('Number of sections')
ax.set_zlabel('Hole density')
plt.colorbar(sc)
plt.show()
plt.savefig("3Dplot.png")
