import os
import pandas as pd
from numpy import *
import pandas as pd
import matplotlib
#from extractFromOpenFOAM import extractValue
matplotlib.rcParams.update({"font.size":20})

directory = os.getcwd()
resultsfile = "testRes.csv"

def readLine(param, inFile):
    file = open(f"{inFile}","r")
    allLines = file.readlines()
    file.close()
    for i, line in enumerate(allLines): 
        if line.startswith(param + " ="): paramLine = line
    value  = paramLine.replace("=", ";").split(";")[1]
    return float(value)


for i, runFile in enumerate([d for d in os.listdir(os.getcwd()) if d.startswith("run")]):
    try:    
        components = runFile.split(",")#.replace(",", "=").replace("-", "=")
        rHole, width, numAx, numSec, numInSec = components[-5].split("=")[-1], components[-4].split("=")[-1], components[-3].split("=")[-1], components[-2].split("=")[-1], components[-1].split("=")[-1]
        width = readLine("width", f"{runFile}/fluid.geo")
        pBack = pd.read_csv(f"{runFile}/postProcessing/surfaceFieldValueBackWall/0/surfaceFieldValue.dat").iloc[-1].values[0].split("\t")[-1]
        pInlet = pd.read_csv(f"{runFile}/postProcessing/surfaceFieldValueInlet/0/surfaceFieldValue.dat").iloc[-1].values[0].split("\t")[-1]
        pOutlet = pd.read_csv(f"{runFile}/postProcessing/surfaceFieldValueOutlet/0/surfaceFieldValue.dat").iloc[-1].values[0].split("\t")[-1]
        if abs(float(pOutlet)) > 1e20: continue
        with open(resultsfile, "a") as f: f.write(f"{i},{rHole},{width},{numAx},{numSec},{numInSec},{pBack},{pInlet},{pOutlet}\n")

    except:
        print(runFile)
