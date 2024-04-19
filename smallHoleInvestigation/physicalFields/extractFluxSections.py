import matplotlib.pyplot as plt
import matplotlib
import pandas as pd
from scipy.integrate import solve_bvp
from extractFromOpenFOAM import extractValue
from numpy import *
import os
matplotlib.rcParams.update({"font.size": 40})

resultsFile = "fullExtracted.csv"
os.system("mkdir slices")
xx = linspace(25.1,29.9,10)
rHole, numHoles, width = .05, 96, 1.5
runFolder = f"runHoles={int(numHoles/8)},width={width},s=4" 
for z in xx: extractValue(z, f"{runFolder}/foam.foam",f"slices/z={z}.csv")
z, p, w = [],[],[]
for file in os.listdir("slices"):
    z.append(float(file.replace(".csv", "=").split("=")[-2]))
    p.append(pd.read_csv(os.path.join("slices",file))["p"].values[0]/(pi*0.75**2))
    w.append(pd.read_csv(os.path.join("slices",file))["U_2"].values[0])

df = pd.DataFrame({"z":z, "p": p, "w":w})
df =df.sort_values("z")
df.to_csv("extractedSlices.csv", index=False)
df = pd.read_csv("extractedSlices.csv")
#df= df[df["z"]>1]
#centreline = df[df["U_2"] > 6.5]
Z, p, U = df["z"].values,df["p"].values,df["w"].values
rN = 1
U = convolve(U, ones(rN)/rN, mode='valid')
p = convolve(p, ones(rN)/rN, mode='valid')
Z = convolve(Z, ones(rN)/rN, mode='valid')
#Z = df["Z"].rolling(n).mean()
#U = -1* df["U_2"].rolling(n).mean()
#p = df["p"].rolling(n).mean() /(1000*pi*0.63575**2)
fig, ax = plt.subplots(1, 1,figsize=(20, 15))
ax.scatter(Z, flip(U),color="b", linewidth=5, label = "Fluid Flux")#* 6/U[2]

ax.plot([],[], "r", linewidth=5, label = "Pressure")
ax.set_ylim(0, 7)
ax.set_ylabel("Fluid flux magnitude (mm$^3$/s)")
ax.set_xlabel("Position on catheter centreline (mm)")
ax2= ax.twinx()
ax2.scatter(Z, flip(p), color="r", linewidth=5, label = "Pressure")
ax2.set_ylabel("Pressure (Pa)")

#analytics a plot for comparison 
L = 30
pscale = 6*0.75*L/(pi*0.75**4)  
def d(z, rHole, nHoles, holeCentres, width):
    holeCentres = [h/L for h in holeCentres]
    K = (68.5*sqrt(nHoles/width)*rHole**2)**2
    eps = 0.05
    res = 0
    for h in holeCentres:
        if abs(z-h)< (width+2*rHole)/(2*L): #r*t
            res += K*(tanh((z-h+width/(2*L))/eps) + tanh((-z+h+width/(2*L))/eps))/2
    return res

def pressure(z, y,params):
    rHole, nHoles, nSections, width = params[0], params[1], params[2], params[3]
    p,q = y
    D = [d(zz, rHole, nHoles, nSections, width) for zz in z]
    dydt = [q, D*(p)]
    return vstack(dydt)

def bc(ya, yb):
    return array([ya[1], yb[1]+8])

def getPresssurepL(rHole,nHoles,holeCentres, width):
    # Integrate boundary value problem and return the pressure drop
    x = linspace(0, 1, 1000)  # non-dim length
    y = zeros((2, x.size))
    params = [rHole, nHoles, holeCentres, width]
    res = solve_bvp(lambda x,y: pressure(x,y,params), bc, x, y)
    pressureData = res.sol(x)[0]
    p0 = -pressureData[-1]
    pressureData = [p +p0 for p in pressureData]
    flux = -res.sol(x)[1]/(8)
    return flux, pressureData, p0

theta, N, width = 0.05, 80, 2
xx = [L - l for l in linspace(0, L, 1000)]

holeCentres = [10.5+5*i for i in range(4)]
w, pressureData, p0 = getPresssurepL(theta, N, holeCentres, width)
pressureData = [pscale*(p - pressureData[-1]) for p in pressureData]
ax2.plot(xx, pressureData,"r",linewidth=3, label ="Pressure mPa")

#ax[0].scatter([1, 0], [pInlet, pBack], color="k")
ax.plot(xx,6*w,"b",linewidth=3, label="Fluid flux mm$^3$/s")
ax.legend(loc="center left")


fig.tight_layout()
fig.savefig("centrelineGraph.png")
#plt.show()