import os
import pandas as pd
from numpy import *
import scipy as sc
import matplotlib.pyplot as plt 
import pandas as pd
import matplotlib
matplotlib.rcParams.update({"font.size":25})

data = pd.read_csv("modifiedPressures.csv")
data= data[data["axial"]>1]
rHole, axial, length, config,errOne, errMult = data["rHole"].values,data["axial"].values,data["length"].values,data["config"].values,data["errOne"].values,data["errMult"].values
#print(len(data[data["MSerrorInlet"] >-1]), (len(data)))
# Plot back pressure and inlet

fig, ax = plt.subplots(1,1,figsize=(20,10))
x_multi = [errOne, errMult]
ax.hist(x_multi, 20, histtype='bar')
ax.legend(["One section", "Multiple sections"])
ax.set_ylabel("Frequency")
ax.set_xlabel("RPE")
ax.set_yticks(linspace(0,6,7))
#ax.set_title("Relative percentage error ")
plt.savefig("allErrorsLargeHoles.png")
plt.close()
"""
fig, ax = plt.subplots(1,1,figsize=(20,10))
ax.hist(inletErr, bins=linspace(-5.25, 1,26), histtype='bar', label="External pressure $p_0$")
ax.set_ylabel("Frequency")
ax.set_xlabel("RPE")
ax.set_yticks(linspace(0,26,14))
plt.savefig("smallHolesHist.png")
plt.close()"""

fig, ax = plt.subplots(1,2,figsize=(20,10))

for i, err in enumerate(["errOne", "errMult"]):
    for j, xvar in enumerate([rHole, config]):
        if err == "errOne": 
            label = "One region"
        else: 
            label = "Multiple regions"
        ax[j].scatter(xvar, data[err].values, label=label)
        ax[j].plot(xvar, [0]*len(xvar), "k")
        ax[j].legend(loc="upper left")
        if j==0: 
            ax[j].set_xlabel("Hole radius (mm)")
            ax[j].set_ylabel("RPE")
        if j==1: 
            ax[j].set_xlabel("Hole configuration")
            ax[j].set_xticks(linspace(1,4,4))


#fig.suptitle(f"Percentage relative errors")
plt.savefig("largeHolesErrs.png")
