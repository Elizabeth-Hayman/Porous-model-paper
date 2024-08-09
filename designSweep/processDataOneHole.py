import os
import pandas as pd
from scipy.integrate import solve_bvp
from numpy import *
import matplotlib.pyplot as plt 
import pandas as pd
import matplotlib
matplotlib.rcParams.update({"font.size":25})

#os.system("python3 extract.py")
directory = os.getcwd()
resultsfile = "results.csv" #"resultsFull.csv"

data = pd.read_csv(resultsfile)
#data=data[data["pInlet"]==0]
data = data.drop("iteration", axis=1)
data = data.drop_duplicates()
data = data[data["rHole"] > 0.05]
for col in ["pBack", "pInlet", "pOutlet"]:    data[col] = data[col] - data["pOutlet"]
data = data.drop_duplicates()
L, mu, Q, a= 30, 0.75, 6, 0.75
pscale = 6*0.75*L/(pi*0.75**4) 
alpha = 1.0 * sqrt(60)
integralStep = 2000

def d(z, rHole, nHoles, holeCentres, width):
    K = alpha**2*nHoles*rHole**4
    w = width/2
    out = 0
    for h in holeCentres:
        if abs(z-h)< w:
            out += K
    return out

def pressure(z, y, porosity: list):
    #porosity needs to be list the same length as z
    if len(porosity) != len(z): porosity = [(porosity[i]+porosity[i+1])/2 for i in range(len(porosity)-1)]
    p,q = y
    dydt = [q, list(porosity)*(p)]
    return vstack(dydt)

def bc(ya, yb):
    return array([ya[1], yb[1]+8])

def getPresssurepL(porosity,x = linspace(0, 1, integralStep)):
    y = zeros((2, x.size))
    res = solve_bvp(lambda x,y: pressure(x,y,porosity), bc, x, y)
    pressureData = res.sol(x)[0]
    pExt = -pressureData[-1]
    pressureData = [p + pExt for p in pressureData]
    flux = -res.sol(x)[1]/(8)
    return flux, pressureData, pExt


oneRegion,multRegion = [], []
xx = linspace(0, 1, integralStep)
for id, line in data.iterrows():
    #break
    rHole,numAx,numSec = line["rHole"], int(line["numAx"]), int(line["numSec"])
    holeCentres = [(i+1)/(numSec+1) for i in range(int(numSec))]
    porosityMult = [d(zz, rHole / a, numAx  * L / (2 * rHole), holeCentres, 2 * rHole / L)for zz in xx]
    flux, pressureData, p0 = getPresssurepL(porosityMult)
    multRegion.append(p0)
    intMult = trapz(porosityMult,xx)
    fig, ax = plt.subplots(1, 3)
    ax[0].plot(porosityMult, "b")
    ax[1].plot(pressureData, "b")
    ax[2].plot(flux, "b")

    porosityOne = [d(zz, line["rHole"] / a, numAx * numSec, [1/2], 1)  for zz in xx] 
    flux, pressureData, p0 = getPresssurepL(porosityOne)
    ax[0].plot(porosityOne, "r")
    ax[1].plot(pressureData, "r")
    ax[2].plot(flux, "r")
    fig.suptitle(f"{rHole,numAx,numSec}")
    #plt.savefig(f"")
    #plt.show()
    plt.close()
    oneRegion.append(p0)
    intOne = trapz(porosityOne,xx)
    print("porosity integrals", intMult, intOne)

data["oneRegion"] = oneRegion
data["multRegion"] = multRegion
data["errOne"] = [x*100 for x in (data["oneRegion"].values * pscale- data["pInlet"].values)/data["pInlet"].values]
data["errMult"] = [x*100 for x in (data["multRegion"].values * pscale- data["pInlet"].values)/data["pInlet"].values]

data = data.sort_values("errOne") #"MSerror")
print(data)
data.to_csv("errorsalphaOne.csv", index=False)