import os
import pandas as pd
from numpy import *
import scipy as sc
import matplotlib.pyplot as plt 
import pandas as pd
import matplotlib
matplotlib.rcParams.update({"font.size":35})

data = pd.read_csv("errorsalphaOne.csv")
rHole, axial, length, errOne, errMult = data["rHole"].values,data["numAx"].values,data["numSec"].values,data["errOne"].values,data["errMult"].values
print(errMult.min())

def plotErrorHist(data, nbins, saveFileName):
    rHole, axial, length, errOne, errMult = data["rHole"].values,data["numAx"].values,data["numSec"].values,data["errOne"].values,data["errMult"].values
    fig, ax = plt.subplots(1,1,figsize=(20,10))
    x_multi = [errOne, errMult]
    ax.hist(x_multi, bins=nbins, histtype='bar')
    ax.legend(["One section", "Multiple sections"])
    ax.set_ylabel("Frequency")
    ax.set_xlabel("RPE")
    #ax.set_yticks(linspace(0,6,7))
    #ax.set_title("Relative percentage error ")
    plt.savefig(f"{saveFileName}.png")
    plt.savefig(f"{saveFileName}.eps")
    plt.close()

plotErrorHist(data, 80, "allErrors")
#plotErrorHist(data[data["rHole"] < 0.1], 80, "smallHoleErrors")
#plotErrorHist(data[data["rHole"] > 0.1], 80, "largeHoleErrors")
#plotErrorHist(data[data["numAx"] == 1], 80, "numAx=1")
#plotErrorHist(data[data["numSec"] <= 10], 80, "numSec=10")


for col in ["numSec", "numAx", "numHoles", "ratio"]:
    for err in ["errOne", "errMult"]:
        fig, ax = plt.subplots(1, 1, figsize=(15,15))
        if col=="numHoles":sc = ax.scatter(data["rHole"].values / 0.75, data[err].values, c=data["numSec"].values*data["numAx"].values)
        elif col=="ratio":sc = ax.scatter(data["rHole"].values / 0.75, data[err].values, c=log(data["numAx"].values/data["numSec"].values))
        else: sc = ax.scatter(data["rHole"].values / 0.75, data[err].values, c=data[col].values)
        ax.set_xlabel("Inlet hole radius $r_h$")
        ax.set_ylabel("RPE")
        cbar = plt.colorbar(sc)
        #cbar.set_label(col, rotation=270, labelpad=50)
        if col=="numSec": cbar.set_label('numLength', rotation=270, labelpad=50)
        elif col=="numAx": cbar.set_label('numAxial', rotation=270, labelpad=50)
        fig.savefig(f"{col}-{err}.eps")
"""
fig, ax = plt.subplots(1,1,figsize=(20,10))
ax.hist(inletErr, bins=linspace(-5.25, 1,26), histtype='bar', label="External pressure $p_0$")
ax.set_ylabel("Frequency")
ax.set_xlabel("RPE")
ax.set_yticks(linspace(0,26,14))
plt.savefig("smallHolesHist.png")
plt.close()"""

"""
for j, xvar in enumerate([rHole, configsList]):
    fig, ax = plt.subplots(1,1,figsize=(20,20))
    for i, err in enumerate(["errOne", "errMult"]):
        if err == "errOne": 
            label = "One region"
        else: 
            label = "Multiple regions"
        ax.scatter(xvar, data[err].values, s=200,label=label)
        ax.plot(xvar, [0]*len(xvar), "k")
        ax.legend(loc="upper left")
        if j==0: 
            ax.set_xlabel("Hole radius (mm)")
            ax.set_ylabel("RPE")
        if j==1: 
            ax.set_xlabel("Hole configuration")
            ax.set_xticks(linspace(1,4,4))

        fig.tight_layout()
#fig.suptitle(f"Percentage relative errors")
        fig.savefig(f"largeHolesErrs{j}.eps")
        fig.savefig(f"largeHolesErrs{j}.png")
"""
