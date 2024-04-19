import os
import pandas as pd
import numpy as np
import itertools

directory = os.getcwd()
resultsfile = "results.csv"
paramValues = {"theta": [0.05], "nHoles":[12,10,8,6],  "nSections": [1, 2, 3, 4], "width": [0.5, 1, 1.5, 2, 3]} 
paramFile = "fluid.geo"
pCombos = list(itertools.product(*[paramValues[p] for p in paramValues.keys()]))

def changeLine(param, newValue, inFile):
    file = open(f"{inFile}","r")
    allLines = file.readlines()
    file.close()
    for i, line in enumerate(allLines): 
        if line.startswith(param + " ="): allLines[i]= f"{param} = {newValue}; \n"
    file = open(f"{inFile}","w")
    file.writelines(allLines)
    file.close()

for i, p in enumerate(pCombos):
	try: 
		theta, nHoles, nSections, width = p[0],p[1],p[2],p[3]
		runFile = os.path.join(directory, f"runHoles={nHoles},width={width},s={nSections}")#f"runN={nHoles*8}t={theta}s={nSections}")
		os.system(f"rm -rf {runFile}; cp -r template/ {runFile}")
		changeLine("theta", p[0], os.path.join(runFile, "fluid.geo"))
		changeLine("nHoles", int(p[1] * p[3]), os.path.join(runFile, "fluid.geo"))  #same hole density
		changeLine("nSections", p[2], os.path.join(runFile, "fluid.geo"))
		changeLine("width", p[3], os.path.join(runFile, "fluid.geo"))
		os.system(f"cd {runFile}; ./config.sh")
		pBack = pd.read_csv(f"{runFile}/postProcessing/surfaceFieldValueBackWall/0/surfaceFieldValue.dat").iloc[-1].values[0].split("\t")[-1]
		pInlet = pd.read_csv(f"{runFile}/postProcessing/surfaceFieldValueInlet/0/surfaceFieldValue.dat").iloc[-1].values[0].split("\t")[-1]
		pOutlet = pd.read_csv(f"{runFile}/postProcessing/surfaceFieldValueOutlet/0/surfaceFieldValue.dat").iloc[-1].values[0].split("\t")[-1]
		with open(resultsfile, "a") as f: f.write(f"{i},{p[0]},{p[1]*8},{p[2]},{p[3]},{pBack},{pInlet},{pOutlet}\n")
	except:
		print(p)
        
