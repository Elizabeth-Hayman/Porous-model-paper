
import matplotlib
import matplotlib.pyplot as plt 
from numpy import *
import os
import pandas as pd
from scipy.integrate import  solve_bvp

from extractFromOpenFOAM import extractValue
matplotlib.rcParams.update({"font.size":35})

exId = 1
rHole, numAx, numSec = .2, 4, 10
#exId = 2
#rHole, numAx, numSec = .3, 1, 3
runFolder = f"runrh={rHole},numAx={int(numAx)},numSec={numSec}" 

alpha = 1.0 * sqrt(60)
L, Q, ri, mu = 30, 6, 0.75, 0.75
pscale = Q*mu*L/(pi*ri**4)
integralStep = 5000

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


fig0, ax0 = plt.subplots(1, 1, figsize=(15,15))
fig1, ax1 = plt.subplots(1, 1, figsize=(15,15))
fig2, ax2 = plt.subplots(1, 1, figsize=(15,15))
xx = linspace(0, 1, integralStep)
## Plot analytic model
holeCentres = [(i+1)/(numSec+1) for i in range(int(numSec))]

porosityMult = [d(zz, rHole / ri, numAx  * L / (2 * rHole), holeCentres, 2 * rHole / L)for zz in xx]

flux, pressureData, p0Mult = getPresssurepL(porosityMult)
ax0.plot(xx, porosityMult, "r", linewidth=4,label="Multiple regions")
ax1.plot(xx, pressureData, "r", linewidth=4,label="Multiple regions")
ax2.plot(xx, flux, "r", linewidth=4,label="Multiple regions")

porosityOne = [d(zz, rHole / ri, numAx * numSec, [1/2], 1)  for zz in xx] 
flux, pressureData, p0One = getPresssurepL(porosityOne)
ax0.plot(xx, porosityOne, "b", linewidth=4,label="One region")
ax1.plot(xx, pressureData, "b", linewidth=4,label="One region")
ax2.plot(xx, flux, "b", linewidth=4,label="One region")

## Plot CFD data
# Extract physical fields from CFD
os.system("rm -rf slices; mkdir slices")
extractValue(f"{runFolder}/foam.foam",linspace(0.05,29.95,100))

z, p, w = [],[],[]
for file in os.listdir("slices"):
    z.append(float(file.replace(".csv", "=").split("=")[-2]))
    p.append(pd.read_csv(os.path.join("slices",file))["p"].values[0]/(pi*ri**2))
    w.append(pd.read_csv(os.path.join("slices",file))["U_2"].values[0])

CFDdata = pd.DataFrame({"z": z, "p": p, "w": w}).sort_values("z")
ax2.plot(CFDdata["z"].values/L, CFDdata["w"].values/Q,"k", label = "CFD",linewidth=4)

pext = pd.read_csv(f"outlet.csv")["p"].values/pd.read_csv(f"outlet.csv")["Area"].values
p = [(pp - pext[0])/pscale for pp in CFDdata["p"].values]
ax1.plot(CFDdata["z"].values/L, p,"k", label = "CFD",linewidth=4)
pBack = float(pd.read_csv(f"{runFolder}/postProcessing/surfaceFieldValueBackWall/0/surfaceFieldValue.dat").iloc[-1].values[0].split("\t")[-1])
pInlet = float(pd.read_csv(f"{runFolder}/postProcessing/surfaceFieldValueInlet/0/surfaceFieldValue.dat").iloc[-1].values[0].split("\t")[-1])
pOutlet = float(pd.read_csv(f"{runFolder}/postProcessing/surfaceFieldValueOutlet/0/surfaceFieldValue.dat").iloc[-1].values[0].split("\t")[-1])
pBack, pInlet, pOutlet = pBack - pOutlet, pInlet - pOutlet, pOutlet - pOutlet
ax1.scatter([0, 1], [pBack/pscale, pOutlet/pscale], color="k", s=30)

#clineData = pd.read_csv("centreLine.csv")
#p = [(pp - pext[0])/pscale for pp in clineData["p"].values]
#ax2.plot(clineData["Points_2"].values/L, clineData["U_2"].values * (pi*ri**2)/ (2*Q),"y", label = "CFD",linewidth=4)
#ax1.plot(clineData["Points_2"].values/L, p, "y", label = "CFD",linewidth=4)

for a in [ax0, ax1, ax2]:
    a.legend()
    a.set_xlabel("$z$ coordinate")

ax0.set_ylabel("Porosity factor ")
ax1.set_ylabel("Pressure")
ax2.set_ylabel("Fluid flux")
for i, fig in enumerate([fig0, fig1, fig2]):
    fig.savefig(f"example{exId}{i}.eps")
    fig.savefig(f"example{exId}{i}.png")
#plt.savefig(f"runrh={rHole},numAx={int(numAx)},numSec={numSec}.png")
#plt.show()
plt.close()

intMult = trapz(porosityMult,xx)
intOne = trapz(porosityOne,xx)
print("porosity integrals", intMult, intOne)
print((p0Mult * pscale- pInlet)/pInlet * 100, (p0One * pscale- pInlet)/pInlet * 100)
os.system("rm -rf slices centreLine.csv outlet.csv")