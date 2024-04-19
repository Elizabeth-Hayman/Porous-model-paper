import os
import pandas as pd
from scipy.integrate import solve_bvp
from numpy import *
import scipy as sc
import matplotlib.pyplot as plt 
import pandas as pd
import matplotlib
matplotlib.rcParams.update({"font.size":20})

#os.system("python3 extract.py")
directory = os.getcwd()
resultsfile = "results.csv"

data = pd.read_csv(resultsfile)
#data=data[data["pInlet"]==0]
data = data.drop("iterations", axis=1)
for col in ["pBack", "pInlet", "pOutlet"]:    data[col] = data[col] - data["pOutlet"]
data = data.drop_duplicates()
data.to_csv("resultsAdjustedOutlet.csv")
L, mu= 30, 0.75
pscale = 6*0.75*8/(pi*0.75**4)
alpha = 2.6028

def d(z, rHole, nHoles, holeCentres, width):
    K = alpha**2*nHoles*rHole**4
    w = width/2
    for h in holeCentres:
        if abs(z-h)< w:
            return K
    return 0
def pressure(z, y,params):
    rHole, nHoles, nSections, width = params[0], params[1], params[2], params[3]
    p,q = y
    D = [d(zz, rHole, nHoles, nSections, width) for zz in z]
    dydt = [q, D*(p)]
    return vstack(dydt)

def bc(ya, yb):
    return array([ya[1], yb[1]+pscale])

def getPresssurepL(rHole,nHoles,holeCentres, width, x = linspace(0, L, 1000)):
    y = zeros((2, x.size))
    params = [rHole, nHoles, holeCentres, width]
    res = solve_bvp(lambda x,y: pressure(x,y,params), bc, x, y)
    pressureData = res.sol(x)[0]
    pExt = -pressureData[-1]
    pressureData = [p + pExt for p in pressureData]
    flux = -res.sol(x)[1]/(8*mu)
    return flux, pressureData, pExt

"""
oneRegion,multRegion = [], []
for id, line in data.iterrows():
    holeCentres, width, numHoles =   [5+20* i/(int(line["length"])-1) for i in range(int(line["length"]))], 2*line["rHole"], line["axial"]/(2*line["rHole"])
    flux, pressureData, p0 = getPresssurepL(line["rHole"],numHoles,holeCentres, width)
    multRegion.append(p0)
for id, line in data.iterrows():
    holeCentres, width, numHoles =  [15], 20+2*line["rHole"], line["axial"]*line["length"]/(20+2*line["rHole"])
    flux, pressureData, p0 = getPresssurepL(line["rHole"],numHoles,holeCentres, width)
    oneRegion.append(p0)

data["oneRegion"] = oneRegion
data["multRegion"] = multRegion
data["errOne"] = [x*100 for x in (data["oneRegion"].values - data["pInlet"].values)/data["oneRegion"].values]
data["errMult"] = [x*100 for x in (data["multRegion"].values - data["pInlet"].values)/data["multRegion"].values]

data = data.sort_values("errMult") #"MSerror")
data.to_csv("modifiedPressures.csv", index=False)"""

#Make a plot for comparison 

fig, ax = plt.subplots(1, 3, figsize=(40,10))

rHole, numAxial, numLength = .4, 2, 12

## We can either model this as 12 distinct porous regions comprised of all the axial holes on a specific z coord.
holeCentres, width, numHoles =   [5 +20* i/(numLength-1) for i in range(numLength)], 2*rHole, numAxial/(2*rHole) # [5 +rHole+(20-2*rHole)
print(holeCentres, width, numHoles)
xx = linspace(0, L, 1000)
w, pressureData, p0 = getPresssurepL(rHole, numHoles,  holeCentres, width)
ax[0].plot(xx, [d(x,rHole, numHoles, holeCentres, width) for x in xx],"k",label="Multiple regions")
ax[0].set_title("Porosity factor $\Lambda(z)$")
ax[1].plot(xx, pressureData,"r",linewidth=3,label="Multiple regions")
ax[1].set_title("Pressure mPa")
ax[2].plot(xx, w,"b",linewidth=3,label="Multiple regions")
ax[2].set_title("Fluid flux mm$^3$/s")
pBackMult, pExtMult = pressureData[0], p0


## Or the model could say all the catheter is porous 
holeCentres, width, numHoles =  [15], 20+2*rHole, numAxial*numLength/(20 + 2*rHole)
print(holeCentres, width, numHoles)
w, pressureData, p0 = getPresssurepL(rHole, numHoles,  holeCentres, width)
ax[0].plot(xx, [d(x,rHole, numHoles, holeCentres, width) for x in xx], "k--",label="One region")
ax[0].set_title("Porosity factor $\Lambda(z)$")
ax[1].plot(xx, pressureData,"r--",linewidth=3,label="One region")
ax[1].set_title("Pressure mPa")
ax[2].plot(xx, w,"b--",linewidth=3,label="One region")
ax[2].set_title("Fluid flux mm$^3$/s")
pBackOne, pExtOne = pressureData[0], p0

"""
## Or the model could say ALL the catheter is porous along te tip to outlet 
holeCentres, width, numHoles =  [15], 30, numAxial*numLength/(30)
print(holeCentres, width, numHoles)
w, pressureData, p0 = getPresssurepL(rHole, numHoles,  holeCentres, width)
ax[0].plot(xx, [d(x,rHole, numHoles, holeCentres, width) for x in xx], "k--",label="One region")
ax[0].set_title("Porosity factor $\Lambda(z)$")
ax[1].plot(xx, pressureData,"r-.",linewidth=3,label="Whole region")
ax[1].set_title("Pressure mPa")
ax[2].plot(xx, w,"b-.",linewidth=3,label="Whole region")
ax[2].set_title("Fluid flux mm$^3$/s")
pExtMult = p0#pressureData[0]
"""

runFile = f"runrHole={rHole}-{numAxial}x{numLength}"
pBack = pd.read_csv(f"{runFile}/postProcessing/surfaceFieldValueBackWall/0/surfaceFieldValue.dat").iloc[-1].values[0].split("\t")[-1]
pOutlet = pd.read_csv(f"{runFile}/postProcessing/surfaceFieldValueOutlet/0/surfaceFieldValue.dat").iloc[-1].values[0].split("\t")[-1]
pDrop = -float(pOutlet)#float(pBack)-float(pOutlet)
print(pDrop, pExtMult, pExtOne)
#ax[1].scatter([0], [float(pBack)-float(pOutlet)], color="k")
errorMult, errorOne = 100 * (pDrop - pExtMult)/pExtMult,100 * (pDrop - pExtOne)/pExtOne
fig.suptitle(f"RPE with multiple porous regions: {str(errorMult)[:5]}, RPE with one porous region: {str(errorOne)[:5]} ")

from outletFromOpenFOAM import extractValueOutlet
extractValueOutlet(f"{runFile}/foam.foam", "outlet.csv")
centreLineData = pd.read_csv("extractedSlices.csv")
z, p, w = centreLineData["z"].values,centreLineData["p"].values, centreLineData["w"].values
pext = pd.read_csv("outlet.csv")["p"].values/pd.read_csv("outlet.csv")["Area"].values
p = [pp - pext[0] for pp in p]
#ax[1].plot(z, p,"k--", label = "CFD")#,linewidth=3))
ax[2].plot(z, w,"k--", label = "CFD",linewidth=5)
centreLineData = pd.read_csv("centreLine.csv")
z, p, w = centreLineData["Points_2"].values,centreLineData["p"].values, centreLineData["U_2"].values*pi*0.75**2/2
p = [pp - pext[0] for pp in p]
ax[1].plot(z, p,"k--", label = "CFD",linewidth=5)

for a in ax:
    a.legend()
    a.set_xlabel("$z$ coordinate (mm)")
    a.set_xlabel("$z$ coordinate (mm)")
plt.tight_layout()
plt.savefig("largeHoleFields.png")
