import os
import pandas as pd
from scipy.integrate import solve_bvp, trapz
from numpy import *
import matplotlib.pyplot as plt 
import pandas as pd
import matplotlib
matplotlib.rcParams.update({"font.size":20})

#os.system("python3 extract.py")
directory = os.getcwd()

L, mu= 30, 0.75
pscale = 6*0.75*8/(pi*0.75**4)
alpha = 2.6028

def d(z, rHole, nHoles, holeCentres, width):
    K = alpha**2*nHoles*rHole**4
    w = width/2
    out = 0
    for h in holeCentres:
        if abs(z-h)< w:
            out += K
    return out
def pressure(z, y,params):
    rHole, nHoles, nSections, width, flag = params[0], params[1], params[2], params[3], params[4]
    p,q = y
    if flag == "Mult":
        D = [d(zz, 0.4, 1/0.8, nSections, 0.4)+d(zz, 0.6, 1/1.2, nSections, 0.4) for zz in z]
    else:
        D = [d(zz, rHole, nHoles, nSections, width) for zz in z]
    dydt = [q, D*(p)]
    return vstack(dydt)

def bc(ya, yb):
    return array([ya[1], yb[1]+pscale])

def getPresssurepL(rHole,nHoles,holeCentres, width, flag="One",x = linspace(0, L, 1000)):
    y = zeros((2, x.size))
    params = [rHole, nHoles, holeCentres, width,flag]
    res = solve_bvp(lambda x,y: pressure(x,y,params), bc, x, y)
    pressureData = res.sol(x)[0]
    pExt = -pressureData[-1]
    pressureData = [p + pExt for p in pressureData]
    flux = -res.sol(x)[1]/(8*mu)
    return flux, pressureData, pExt

#Make a plot for comparison 

fig, ax = plt.subplots(1, 3, figsize=(40,10))
rmin, rmax = 0.4, 0.6
print(rmin, rmax)
rHole, numAxial, numLength = rmax, 2, 10

## We can either model this as 12 distinct porous regions comprised of all the axial holes on a specific z coord.
holeCentres, width, numHoles = [5 +rmax+(20-2*rmax)* i/(numLength-1) for i in range(numLength)], 2*rHole, (rmin**2+rmax**2)/rmax**2 * 1/(2*rHole)
print(holeCentres, width, numHoles, (rmin**2+rmax**2)/rmax**2,(rmin**2+rmax**2)/rmax**2 * 1/(2*rHole), numAxial/(2*rmax))
xx = linspace(0, L, 1000)
w, pressureData, p0 = getPresssurepL(rHole, numHoles,  holeCentres, width,flag="Mult")
porosity = [d(zz, 0.4, 1/0.8, holeCentres, 0.8)+d(zz, 0.6, 1/1.2, holeCentres, 1.2) for zz in xx]
ax[0].plot(xx, porosity,"k",label="Multiple regions")
ax[0].set_title("Porosity factor $\Lambda(z)$")
ax[1].plot(xx, pressureData,"r",linewidth=3,label="Multiple regions")
ax[1].set_title("Pressure mPa")
ax[2].plot(xx, w,"b",linewidth=3,label="Multiple regions")
ax[2].set_title("Fluid flux mm$^3$/s")
pBackMult, pExtMult = pressureData[0], p0
intOne = trapz(porosity,xx)


## Or the model could say all the catheter is porous 
holeCentres, width, numHoles =  [15], 20, 1 * numLength/(20)
print(holeCentres, width, numHoles)
w, pressureData, p0 = getPresssurepL(rHole, numHoles,  holeCentres, width)
porosity= [d(x,0.6, numHoles, holeCentres, width) + d(x,0.4, numHoles, holeCentres, width) for x in xx]
ax[0].plot(xx, porosity, "k--",label="One region")
ax[0].set_title("Porosity factor $\Lambda(z)$")
ax[1].plot(xx, pressureData,"r--",linewidth=3,label="One region")
ax[1].set_title("Pressure mPa")
ax[2].plot(xx, w,"b--",linewidth=3,label="One region")
ax[2].set_title("Fluid flux mm$^3$/s")
pBackOne, pExtOne = pressureData[0], p0
intMult = trapz(porosity,xx)


## Getting data from simulation
centreLineData = pd.read_csv("centreLine.csv")
zz = list(centreLineData["Points_2"].values)
zz = [L-z for z in zz]
ax[1].plot(zz, centreLineData["p"].values, "k--", linewidth=3, label="CFD")
fluxData = pd.read_csv("extractedSlices.csv")
zz = list(fluxData["z"].values)
zz = [L-z for z in zz]
ax[2].plot(zz, -fluxData["w"].values, "k--", linewidth=3, label="CFD")
pBack = pd.read_csv(f"postProcessing/surfaceFieldValueBackWall/0/surfaceFieldValue.dat").iloc[-1].values[0].split("\t")[-1]
pOutlet = pd.read_csv(f"postProcessing/surfaceFieldValueOutlet/0/surfaceFieldValue.dat").iloc[-1].values[0].split("\t")[-1]
pInlet = pd.read_csv(f"postProcessing/surfaceFieldValueInlet/0/surfaceFieldValue.dat").iloc[-1].values[0].split("\t")[-1]
pDrop = float(pBack)-float(pOutlet)
print(pDrop, pExtMult, pExtOne)
print(intOne, intMult)
ax[1].scatter([0], [float(pBack)-float(pOutlet)], color="k")
ax[1].legend()
ax[2].legend()
errorMult, errorOne = 100 * (pDrop - pExtMult)/pExtMult,100 * (pDrop - pExtOne)/pExtOne
print(float(pInlet) , pBackMult, pBackOne)
errorBackMult, errorBackOne = 100 * (float(pInlet) - pBackMult)/pBackMult,100 * (float(pInlet)  - pBackOne)/pBackOne
fig.suptitle(f"RPE on external pressure with multiple porous regions: {str(errorMult)[:5]}, RPE with one porous region: {str(errorOne)[:5]} ")#\n \
             #RPE on $z=0$ pressure with multiple porous regions: {str(errorBackMult)[:5]}, RPE with one porous region: {str(errorBackOne)[:5]} ")

plt.savefig("ventricularCatheter.png")
