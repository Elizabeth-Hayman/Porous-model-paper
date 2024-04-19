from scipy.integrate import  solve_bvp
from numpy import *
import scipy as sc
import matplotlib.pyplot as plt 
import pandas as pd
import matplotlib
matplotlib.rcParams.update({"font.size":20})


## Catheter with 10 rows, each row containing one hole radius 0.607 and 0.416 on the outer tube! 
rmin = (2.231763 - 1.7583)/2
rmax = (2.3323 - 1.67712)/2
print(rmin, rmax)
alpha = 2.6028
rHole, numHoles, width = rmax, 96, 1.5
l1 = 9
l2 = l1+width
holeCentres = [9+width/2+5*i for i in range(4)]
L, Q, a, mu = 30, 6, 0.75, 0.75
pscale = Q*mu*8/(pi*a**4)
pBack = float(pd.read_csv("postProcessing/surfaceFieldValueBackWall/0/surfaceFieldValue.dat").iloc[-1].values[0].split("\t")[-1])
pInlet = float(pd.read_csv("postProcessing/surfaceFieldValueInlet/0/surfaceFieldValue.dat").iloc[-1].values[0].split("\t")[-1])
pOutlet = float(pd.read_csv("postProcessing/surfaceFieldValueOutlet/0/surfaceFieldValue.dat").iloc[-1].values[0].split("\t")[-1])
pBack, pInlet, pOutlet = pBack - pOutlet, pInlet - pOutlet, pOutlet - pOutlet
print(pBack, pInlet, pOutlet)

def d(z, rHole, nHoles, holeCentres, width):
    eps = 0.01
    K = alpha**2*nHoles*rHole**4 #/ (2*pi*1*0.75**3)
    out = 0
    w = width/2
    #print(holeCentres, width)
    for h in holeCentres:
        #out += K/pi * (arctan((z-h+w)/eps) + arctan((-z+h+w)/eps))
        if abs(z-h)< w:
            out += K
    return out
#print([d(z, 3, 96, [14.5]) for z in linspace(0, L, 100)])
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
    return pressureData, flux, pExt


 #Make a plot
#eps = 0.05
#xx = asarray(list(linspace(0,l1-eps,20)) + list(linspace(l1,l2,20)) +list(linspace(l2+eps,L,50)))
xx = linspace(0, L, 1000)
pressureData, flux , pExt = getPresssurepL(rHole, numHoles, holeCentres, width, xx)
fig, ax = plt.subplots(1, 2, figsize=(30,10))
#ax[0].plot(xx, [d(x,rHole,numHoles, holeCentres, width) for x in xx])
#ax[0].set_title("Porosity measure")
ax[0].plot(xx, pressureData,"r",linewidth=3, label = "Porous model")
ax[0].set_ylabel("Pressure along centreline (mPa)")

#ax[0].scatter([0], [pBack-pOutlet], s=300, color="k", label = "CFD data")
ax[1].plot(xx,flux,"b",linewidth=3, label = "Porous model")
ax[1].set_ylabel("Cross section flux (mm$^3$/s)")

## One dim analytic - use if one section is present
"""
lam = alpha*sqrt(numHoles)*rHole**2
def p3(z): return pscale*((l2 - z) - 1/lam/tanh(lam*(l2-l1))) #+ pL(l)
def p2(z): return -pscale/lam*1/sinh(lam*(l2-l1)) * cosh(lam*(z-l1))# + pL(l) 
def p1(z): return -pscale/lam*1/sinh(lam*(l2-l1)) #+ pL(l)
print("CFD inlet:",pInlet, ", analytic value:", -pscale*((l2 - L) - 1/lam/tanh(lam*(l2-l1))), ", numerical integral:",pExt)
print("CFD back well:",pBack, ", analytic value:", -pscale*((l2 - L) + (1-cosh(lam*(l2-l1)))/lam/sinh(lam*(l2-l1))), ", numerical integral:",pressureData[0])
p = zeros(xx.shape)
for i, z in enumerate(xx):
    if z > l2: p[i] = p3(z)
    elif z< l1: p[i] = p1(z)
    else: p[i] = p2(z)

flux= -1/(8*mu)*diff(p)/diff(xx)

ax[1].scatter(xx, [pr - p[-1] for pr in p],color="r", label = "Analytic")#,linewidth=3)
ax[2].scatter(xx[1:],flux,color="b",  label="Analytic")#,linewidth=3)
"""
#-----------------------

### If centreline data is present
from outletFromOpenFOAM import extractValueOutlet
extractValueOutlet("foam.foam", "outlet.csv")
centreLineData = pd.read_csv("extractedSlices.csv")
z, p, w = centreLineData["z"].values,centreLineData["p"].values, centreLineData["w"].values
pext = pd.read_csv("outlet.csv")["p"].values/pd.read_csv("outlet.csv")["Area"].values
p = [pp - pext[0] for pp in p]
#ax[1].plot(z, p,"k--", label = "CFD")#,linewidth=3))
ax[1].plot(z, w,"k--", label = "CFD",linewidth=5)
centreLineData = pd.read_csv("centreLineFine.csv")
z, p, w = centreLineData["Points_2"].values,centreLineData["p"].values, centreLineData["U_2"].values*pi*a**2/2
p = [pp - pext[0] for pp in p]
ax[0].plot(z, p,"k--", label = "CFD",linewidth=5)

for a in ax.flatten():
    a.legend()
    a.set_xlabel("Centreline z co-ordinate (mm)")
#ApInlet, ApBack = -pscale*((l2 - L) - 1/lam/tanh(lam*(l2-l1))), -pscale*((l2 - L) + (1-cosh(lam*(l2-l1)))/lam/sinh(lam*(l2-l1)))
ApInlet, ApBack = pExt, pressureData[0]
errorInlet, errorBack = 100 * (pInlet - ApInlet)/ApInlet,100 * (pBack - ApBack)/ApBack
fig.suptitle(f"External pressure $p_0$: CFD: {str(pInlet)[:7]}, numerical integral: {str(pExt)[:7]}, RPE: {str(errorInlet)[:7]} %\n \
             BACK WALL - CFD {str(pBack)[:7]}, analytic value: {str(ApBack)[:7]}, numerical integral: {str(pressureData[0])[:7]}, % error: {str(errorBack)[:7]}")
plt.savefig("multSectionsExample.png")
#plt.show()
