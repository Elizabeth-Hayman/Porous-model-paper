./clean.sh
gmsh -3 fluid.geo fluid.msh -v 0
gmshToFoam fluid.msh -case . 
polyDualMesh 90 -case . -overwrite #-concaveMultiCells
combinePatchFaces 60 -overwrite -case .
checkMesh > checkMesh.txt
touch foam.foam

decomposePar
mpirun -np 4 simpleFoam -parallel
reconstructPar -latestTime
rm -rf processor*