import os
import pandas as pd
from scipy.integrate import solve_bvp, trapz
from numpy import *
import matplotlib.pyplot as plt 
import pandas as pd
import matplotlib
matplotlib.rcParams.update({"font.size":45})

#os.system("python3 extract.py")
directory = os.getcwd()

L, mu, Q, a= 30, 0.75, 6, 0.75
pscale = 6*0.75*L/(pi*0.75**4)
alpha = 1.0 * sqrt(60)
integralStep = 5000
ORfactor = 1 # (20 + 2*0.3)/L # one or less - how much of the catheter the one region model encompasses

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
    #params = [rHole, nHoles, holeCentres, width,flag]
    res = solve_bvp(lambda x,y: pressure(x,y,porosity), bc, x, y)
    pressureData = res.sol(x)[0]
    pExt = -pressureData[-1]
    pressureData = [p + pExt for p in pressureData]
    flux = -res.sol(x)[1]/(8)
    return flux, pressureData, pExt

#Make a plot for comparison 

fig1, ax1 = plt.subplots(1, 1, figsize=(15,15))
fig2, ax2 = plt.subplots(1, 1, figsize=(15,15))
fig3, ax3 = plt.subplots(1, 1, figsize=(15,15))

numAxial, numLength, rmin, rmax = 2, 10, 0.3, 0.18
holeCentres = [(5 + (20)*i/(numLength-1))/L for i in range(numLength)]
xx = linspace(0, 1, integralStep)
porosityMult = [d(zz, rmin / a, 1/(2*rmin) * L, holeCentres, 2*rmin / L)+d(zz, rmax / a, 1/(2*rmax) * L, holeCentres, 2*rmax / L) for zz in xx]
porosityOne = [d(zz, rmin / a, numLength /ORfactor, [1/2], ORfactor) + d(zz, rmax / a, numLength / ORfactor, [1/2], ORfactor) for zz in xx] 

## Add porous model data
w, pressureData, p0 = getPresssurepL(porosityMult, x=xx)
pBackMult, pExtMult = pressureData[0], p0
ax1.plot(xx, porosityMult,"r",label="Multiple regions",linewidth=5)
ax1.plot(xx, porosityOne,"b",label="One region",linewidth=5)
ax2.plot(xx, pressureData,"r",linewidth=5,label="Multiple regions")
ax3.plot(xx, w,"r",linewidth=5,label="Multiple regions")
w, pressureData, p0 = getPresssurepL(porosityOne, x=xx)
pBackOne, pExtOne = pressureData[0], p0
ax2.plot(xx, pressureData,"b",linewidth=5,label="One region")
ax3.plot(xx, w,"b",linewidth=5,label="One region")




## Check integrals are roughly equal
intMult = trapz(porosityMult,xx)
intOne = trapz(porosityOne,xx)
print("porosity integrals", intMult, intOne)


## Getting data from simulation
centreLineData = pd.read_csv("centreLine.csv")
zz = list(centreLineData["Points_2"].values/L)
zz = [1-z for z in zz]
ax2.plot(zz, centreLineData["p"].values/ pscale, "k", linewidth=5, label="CFD")
fluxData = pd.read_csv("extractedSlices.csv")
zz = list(fluxData["z"].values/L)
zz = [1-z for z in zz]
ax3.plot(zz, -fluxData["w"].values/Q, "k", linewidth=5, label="CFD")
pBack = float(pd.read_csv(f"postProcessing/surfaceFieldValueBackWall/0/surfaceFieldValue.dat").iloc[-1].values[0].split("\t")[-1]) / pscale
pOutlet = float(pd.read_csv(f"postProcessing/surfaceFieldValueOutlet/0/surfaceFieldValue.dat").iloc[-1].values[0].split("\t")[-1]) / pscale
pInlet = float(pd.read_csv(f"postProcessing/surfaceFieldValueInlet/0/surfaceFieldValue.dat").iloc[-1].values[0].split("\t")[-1]) / pscale
pDrop = float(pBack)-float(pOutlet)
ax2.scatter([0], [float(pBack)-float(pOutlet)], color="k")

#errorMult, errorOne = 100 * (pDrop - pExtMult)/pExtMult,100 * (pDrop - pExtOne)/pExtOne
#errorBackMult, errorBackOne = 100 * (float(pInlet) - pBackMult)/pBackMult,100 * (float(pInlet)  - pBackOne)/pBackOne

for a in [ax1, ax2, ax3]:
    a.legend()
    a.set_xlabel("$z$ coordinate")
#plt.tight_layout()

ax1.set_ylabel("Porosity factor ")
ax2.set_ylabel("Pressure")
ax3.set_ylabel("Fluid flux")
for i, fig in enumerate([fig1, fig2, fig3]):
    fig.savefig(f"ventricleCatheter{i}.eps")
    fig.savefig(f"ventricleCatheter{i}.png")
