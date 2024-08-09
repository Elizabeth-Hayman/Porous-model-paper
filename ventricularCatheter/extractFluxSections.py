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
xx = linspace(0.1,29.9,100)
rHole, numHoles, width = .05, 96, 1.5
extractValue(xx, "foam.foam")
z, p, w = [],[],[]
for file in os.listdir("slices"):
    z.append(float(file.replace(".csv", "=").split("=")[-2]))
    p.append(pd.read_csv(os.path.join("slices",file))["p"].values[0]/(pi*0.75**2))
    w.append(pd.read_csv(os.path.join("slices",file))["U_2"].values[0])

df = pd.DataFrame({"z":z, "p": p, "w":w})
df =df.sort_values("z")
df.to_csv("extractedSlices.csv", index=False)
df = pd.read_csv("extractedSlices.csv")
