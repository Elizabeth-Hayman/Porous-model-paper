import os
import pandas as pd
from numpy import *
import matplotlib.pyplot as plt
import matplotlib
from scipy.optimize import curve_fit
matplotlib.rcParams.update({"font.size":30})

Q, ri, mu, L = 6, 0.75, 0.75, 30
pScale = Q*mu*8/(pi*ri**4)
print(8*mu*Q/(pi*ri**4), pScale)
directory = os.getcwd()
resultsfile = "results.csv"
data=pd.read_csv(resultsfile)
for col in ["pBack", "pInlet", "pOutlet"]:    data[col] = data[col] - data["pOutlet"]
data["B"] = data["pBack"]
data["pL"] = data["pInlet"]
data.to_csv(resultsfile, index=False)

data=pd.read_csv(resultsfile)
dataToFit = data#[data["width"]==1]
xdata = asarray(dataToFit["theta"])
xNdata = asarray(dataToFit["N"])
wdata = asarray(dataToFit["width"])
Bdata = asarray(dataToFit["B"])
pLdata = asarray(dataToFit["pL"])

## Plot data from simulations
fig, ax = plt.subplots(1, 1, figsize=(20,15))
ax.scatter(dataToFit[dataToFit["N"]==96]["theta"].values, dataToFit[dataToFit["N"]==96]["pL"].values/1000, s=100,color="b",label="CFD data, $N$=96")
ax.scatter(dataToFit[dataToFit["N"]==80]["theta"].values, dataToFit[dataToFit["N"]==80]["pL"].values/1000, s=100,color="r",label="CFD data, $N$=80")

def pLfunc(X, alpha): 
    x, numHoles, width = X
    lamSq = alpha**2 * (numHoles * x**4) #/ (2*pi*0.75**3)
    lam= lamSq**0.5
    #print(lam)
    return pScale*(L-14-width+1/(lam*tanh(lam*width)))


#FITTING THE CURVES SIMULATNAEOUSLY

initialParameters = array([2])
# curve fit the combined data to the combined function
fittedParameters, pcov = curve_fit(pLfunc, (xdata, xNdata, wdata), asarray(pLdata), initialParameters)
# values for display of fitted function
alpha = fittedParameters

xx = linspace(min(xdata), max(xdata), 30)

for width, style in zip([1],["-"]):#[0.5,1,2], ["--", "-", "-."]):
    for nHoles, color in zip([80,96], ["r", "b"]):
        xx1 = (xx, asarray([nHoles]*30), asarray([width]*30))
        yFitted = pLfunc(xx1, alpha) # second data set, second equation
        ax.plot(xx, yFitted/1000,color+style, linewidth=3,label=f"Curve fit for $p_0$, $N$={nHoles}")#, width = {width}") # plot the equation using the fitted parameters

xNVals = (data["theta"].values,data["N"].values, data["width"].values)
data["error"] = 100 * (data["pInlet"].values - pLfunc(xNVals,alpha))/pLfunc(xNVals,alpha)
data["pL"] = pLfunc(xNVals,alpha)
data=data.sort_values(["theta", "width"])
data.to_csv(resultsfile, index=False)
fig.suptitle(r"Fitted value $\alpha$"+f" = {str(alpha[0])[:6]}")#, covariance = {str(pcov[0][0])[:6]}")
ax.legend()
ax.set_xlabel("Radius of small capillary inlet tubes (mm)")
ax.set_ylabel("External pressure $p_0$ (Pa)")
plt.savefig("fittedDimensional.png")
plt.tight_layout()
#plt.show()
plt.close()
print("average error", average(abs(data["error"].values)))
print('alpha:', fittedParameters, "cov:", pcov)
