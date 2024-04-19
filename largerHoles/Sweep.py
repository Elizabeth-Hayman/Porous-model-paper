import os
import pandas as pd
import numpy as np
import itertools

directory = os.getcwd()
#os.system("rm -rf run*")
resultsfile = "results.csv"
paramValues = {"theta": [0.6],# [0.1, 0.2,0.25,0.3,0.4,0.5,0.6],#np.linspace(0.1, 0.6, 6)} 
				"numLength" : [3]}#[12, 12, 24, 8, 3]}
numAxial = [2, 4, 2, 6, 1] * len(paramValues["theta"]) # corresponds to the num length above
numAxial = [1]
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

## nholes = 6 so 48 holes total. Across 5-25mm of catheter. 

for i, p in enumerate(pCombos):
	try: 
		theta = p[0]
		ax = numAxial[paramValues["numLength"].index(p[1])]
		runFile = os.path.join(directory, f"runrHole={theta}-{numAxial[i]}x{p[1]}")#f"runN={nHoles*8}t={theta}s={nSections}")
		os.system(f"rm -rf {runFile}; cp -r template/ {runFile}")
		changeLine("theta", p[0], os.path.join(runFile, "fluid.geo"))
		changeLine("nHoles", p[1], os.path.join(runFile, "fluid.geo"))
		changeLine("numAxial", numAxial[i], os.path.join(runFile, "fluid.geo"))
		os.system(f"cd {runFile}; ./config.sh")
		pBack = pd.read_csv(f"{runFile}/postProcessing/surfaceFieldValueBackWall/0/surfaceFieldValue.dat").iloc[-1].values[0].split("\t")[-1]
		pInlet = pd.read_csv(f"{runFile}/postProcessing/surfaceFieldValueInlet/0/surfaceFieldValue.dat").iloc[-1].values[0].split("\t")[-1]
		pOutlet = pd.read_csv(f"{runFile}/postProcessing/surfaceFieldValueOutlet/0/surfaceFieldValue.dat").iloc[-1].values[0].split("\t")[-1]
		with open(resultsfile, "a") as f: f.write(f"{i},{p[0]},{numAxial[i]},{p[1]},{pBack},{pInlet},{pOutlet}\n")
	except:
		print(p)
        
        