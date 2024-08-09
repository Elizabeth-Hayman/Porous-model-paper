
import matplotlib
import matplotlib.pyplot as plt 
from numpy import *
import os
import pandas as pd
from scipy.integrate import  solve_bvp

from extractFromOpenFOAM import extractValue
matplotlib.rcParams.update({"font.size":35})


#rHole, numAx, numSec = .039, 4, 1
rHole, numAx, numSec = .332, 2, 10
#rHole, numAx, numSec = .31, 1, 3
runFolder = "ventricular" #f"runrh={rHole},numAx={int(numAx)},numSec={numSec}" 

alpha = 1.05 * sqrt(60)
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


fig, ax = plt.subplots(1, 3, figsize=(40,20))
xx = linspace(0, 1, integralStep)
## Plot analytic model
numAxial, numLength, rmin, rmax, a = 2, 10, 0.3, 0.18, 0.75
ORfactor = (20 + 2*0.3)/L # one or less - how much of the catheter the one region model encompasses
holeCentres = [(5 + (20)*i/(numLength-1))/L for i in range(numLength)]
print([(5 + (20)*i/(numLength-1)) for i in range(numLength)])
xx = linspace(0, 1, integralStep)
porosityMult = [d(zz, rmin / a, 1/(2*rmin) * L, holeCentres, 2*rmin / L)+d(zz, rmax / a, 1/(2*rmax) * L, holeCentres, 2*rmax / L) for zz in xx]
porosityOne = [d(zz, rmin / a, numLength /ORfactor, [1/2], ORfactor) + d(zz, rmax / a, numLength / ORfactor, [1/2], ORfactor) for zz in xx] 


flux, pressureData, p0 = getPresssurepL(porosityMult)
ax[0].plot(xx, porosityMult, "b", linewidth=4,label="Multiple regions")
ax[1].plot(xx, pressureData, "b", linewidth=4,label="Multiple regions")
ax[2].plot(xx, flux, "b", linewidth=4,label="Multiple regions")

flux, pressureData, p0 = getPresssurepL(porosityOne)
ax[0].plot(xx, porosityOne, "r", linewidth=4,label="One region")
ax[1].plot(xx, pressureData, "r", linewidth=4,label="One region")
ax[2].plot(xx, flux, "r", linewidth=4,label="One region")

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
ax[2].plot(CFDdata["z"].values/L, CFDdata["w"].values/Q,"k", label = "CFD",linewidth=4)

pext = pd.read_csv(f"outlet.csv")["p"].values/pd.read_csv(f"outlet.csv")["Area"].values
p = [(pp - pext[0])/pscale for pp in CFDdata["p"].values]
ax[1].plot(CFDdata["z"].values/L, p,"k", label = "CFD",linewidth=4)
pBack = float(pd.read_csv(f"{runFolder}/postProcessing/surfaceFieldValueBackWall/0/surfaceFieldValue.dat").iloc[-1].values[0].split("\t")[-1])
pInlet = float(pd.read_csv(f"{runFolder}/postProcessing/surfaceFieldValueInlet/0/surfaceFieldValue.dat").iloc[-1].values[0].split("\t")[-1])
pOutlet = float(pd.read_csv(f"{runFolder}/postProcessing/surfaceFieldValueOutlet/0/surfaceFieldValue.dat").iloc[-1].values[0].split("\t")[-1])
pBack, pInlet, pOutlet = pBack - pOutlet, pInlet - pOutlet, pOutlet - pOutlet
ax[1].scatter([0, 1], [pBack/pscale, pOutlet/pscale], color="k", s=30)

#clineData = pd.read_csv("centreLine.csv")
#p = [(pp - pext[0])/pscale for pp in clineData["p"].values]
#ax[2].plot(clineData["Points_2"].values/L, clineData["U_2"].values * (pi*ri**2)/ (2*Q),"y", label = "CFD",linewidth=4)
#ax[1].plot(clineData["Points_2"].values/L, p, "y", label = "CFD",linewidth=4)

fig.suptitle(f"{rHole,numAx,numSec}")
for a in ax:
    a.legend()
    a.set_xlabel("$z$ coordinate")
plt.savefig(f"venticularCyl.png")
plt.show()
plt.close()

intMult = trapz(porosityMult,xx)
intOne = trapz(porosityOne,xx)
print("porosity integrals", intMult, intOne)

os.system("rm -rf slices centreLine.csv outlet.csv")