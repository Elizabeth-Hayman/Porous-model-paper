import os
import pandas as pd
from scipy.integrate import solve_bvp
from numpy import *
import scipy as sc
import matplotlib.pyplot as plt 
import pandas as pd
import matplotlib
matplotlib.rcParams.update({"font.size":20})

directory = os.getcwd()
resultsfile = "results.csv"

data = pd.read_csv(resultsfile)
data=data[data["pInlet"]==0]
data = data.drop("iterations", axis=1)
for col in ["pBack", "pInlet", "pOutlet"]:    data[col] = data[col] - data["pOutlet"]
#data = data.drop("pBack", axis=1)
data = data.drop_duplicates()
#data.to_csv("resultsAdjustedOutlet.csv")
L , mu= 30, 0.75
pscale = 6*0.75*8/(pi*0.75**4) 
print(pscale, 5*pscale)
#data["NDpInlet"] = data["pInlet"]
alpha = 2.6028

def d(z, rHole, nHoles, holeCentres, width):
    eps = 0.01
    K = alpha**2*nHoles*rHole**4 #/ (2*pi*1*0.75**3)
    out = 0
    w = width/2
    for h in holeCentres:
        #out += K/pi * (arctan((z-h+w)/eps) + arctan((-z+h+w)/eps))
        if abs(z-h)< w:
            return K
    return out
   
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


analyticPBack,analyticPInlet = [], []
for id, line in data.iterrows():
    holeCentres = [9+line["width"]/2+5*i for i in range(int(line["nSection"]))]
    flux, pressureData, p0 = getPresssurepL(line["rHole"],line["N"],holeCentres,line["width"])
    analyticPBack.append(pressureData[0])
    analyticPInlet.append(p0)

#data["ApBack"] = analyticPBack
data["ApInlet"] = analyticPInlet
data["ApBack"] = analyticPBack
data["MSerrorInlet"] = [x*100 for x in (data["ApInlet"].values - data["pInlet"].values)/data["ApInlet"].values]
data["MSerrorBack"] = [x*100 for x in (data["ApBack"].values - data["pBack"].values)/data["ApBack"].values]

data = data.sort_values("MSerrorInlet") #"MSerror")
data.to_csv("modifiedPressures.csv", index=False)

#Make a plot for comparison 
fig, ax = plt.subplots(1, 3, figsize=(40,10))

rHole, numHoles, width = .05, 96, 1
l1 = 9 
l2, holeCentres = l1+width, [l1 + width/2]
xx = linspace(0, L, 1000)
w, pressureData, p0 = getPresssurepL(rHole, numHoles,  holeCentres, width)
ax[0].plot(xx, [d(x,rHole, numHoles, holeCentres, width) for x in xx])
ax[0].set_title("Porosity factor $d(z)$")
ax[1].plot(xx, pressureData,"r",linewidth=3)
ax[1].set_title("Pressure mPa")

runFile = f"runHoles={int(numHoles/12)},width={width},s={len(holeCentres)}"
pBack = pd.read_csv(f"{runFile}/postProcessing/surfaceFieldValueBackWall/0/surfaceFieldValue.dat").iloc[-1].values[0].split("\t")[-1]
pInlet = pd.read_csv(f"{runFile}/postProcessing/surfaceFieldValueInlet/0/surfaceFieldValue.dat").iloc[-1].values[0].split("\t")[-1]
pOutlet = pd.read_csv(f"{runFile}/postProcessing/surfaceFieldValueOutlet/0/surfaceFieldValue.dat").iloc[-1].values[0].split("\t")[-1]
print(pBack, pInlet, pOutlet)
ax[1].scatter([0], [float(pBack)], color="k")
ax[2].plot(xx, w,"b",linewidth=3)
ax[2].set_title("Fluid flux mm$^3$/s")
plt.savefig("paramSweep.png")
print(pressureData[0])
