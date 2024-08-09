
// Turn on openCascade
SetFactory("OpenCASCADE");
Mesh.Algorithm = 8;

// Initialise parameters - user coded. 
// Mesh parameters:
meshSize = 0.1;
// Box parameters
Lx = 8; 
Ly = 6;
Lz = 35;
flapWidth = .2;
flapHeight = 3.5;
flapBase = flapWidth;
flapStart = 0;
flapLength = Lz;
// Catheter parameters
xc = 2;
yc = 2.5;
r = 1.25;
ri = 0.75;
catheterLength = 30;

// Hole parameters updated in simulation
theta = 20;
rotation = 0;
t[] = {0.5,0.3};
phi[] = {rotation+0.4, rotation+180.4};
offset[] = {0, -90,0, -90,0, -90,0, -90,0, -90};
startDist = {5};
endDist = {25};


// Make box 
boxR = newp; Point(boxR) = {flapBase/2, 0, 0, meshSize}; 
p = newp; Point(p) = {Lx/2, Ly/2, 0, meshSize}; 
p = newp; Point(p) = {flapBase/2, Ly, 0, meshSize}; 
p = newp; Point(p) = {-flapBase/2, Ly, 0, meshSize}; 
p = newp; Point(p) = {-Lx/2, Ly/2, 0, meshSize}; 
boxL = newp; Point(boxL) = {-flapBase/2, 0, 0, meshSize}; 
ls1 = newl; Spline(ls1)={boxR:boxL:1}; 
base = newl; Line(base) = {boxL, boxR};
cl = newcl; Curve Loop(cl) = {ls1, base};
boxS = news; Plane Surface(boxS) = {cl}; 

boxFull[] = Extrude { 0,0, Lz }{Surface{boxS};};
box = boxFull[1];

// Make CP
baseR = newp; Point(baseR) = {flapBase/2, 0, flapStart, meshSize}; 
p = newp; Point(p) = {3/4*flapWidth, 1/4*flapHeight, flapStart, meshSize}; 
p = newp; Point(p) = {3/4*flapWidth, 3/4*flapHeight, flapStart, meshSize}; 
p = newp; Point(p) = {flapWidth/2, flapHeight, flapStart, meshSize}; 
p = newp; Point(p) = {-flapWidth/2, flapHeight, flapStart, meshSize}; 
p = newp; Point(p) = {-3/4*flapWidth, 3/4*flapHeight, flapStart, meshSize}; 
p = newp; Point(p) = {-3/4*flapWidth, 1/4*flapHeight, flapStart, meshSize}; 
baseL = newp; Point(baseL) = {-flapBase/2, 0, flapStart, meshSize}; 
ls1 = newl; Spline(ls1)={baseR:baseL:1}; 
base = newl; Line(base) = {baseL, baseR};
cl = newcl; Curve Loop(cl) = {ls1, base};
flapS = news; Plane Surface(flapS) = {cl};

If (flapStart + flapLength > Lz)
    flapLength = Lz - flapStart;
EndIf
flapFull[] = Extrude { 0, 0, flapLength }{Surface{flapS};};
flap = flapFull[1];
BooleanDifference{Volume{box};Delete;}{Volume{flap}; Delete;}


//Make catheter 
shuntOuter = newv;
Cylinder(shuntOuter) = {xc, yc, 0, 0, 0, catheterLength, r, 2*Pi};
shuntTip = newv;
Sphere(shuntTip) = {xc, yc, catheterLength, r};
BooleanUnion{Volume{shuntOuter};Delete;}{Volume{shuntTip};Delete;}
shuntInner = newv;
Cylinder(shuntInner) = {xc, yc, 0, 0, 0, catheterLength, ri, 2*Pi};
shuntOuter = 2;
BooleanDifference{Volume{shuntOuter};Delete;}{Volume{shuntInner};Delete;}


numHolesLength = #offset[];
numHolesAxial = #t[]; 
holesEnd = catheterLength - endDist;
holesLength = endDist - startDist;


// Set up each of the hole wedges    
For i In {0:numHolesAxial-1:1}
    For j In {1:numHolesLength:1}
    	zPos = holesEnd + (j-1)*holesLength/(numHolesLength-1);
        Printf("zpos %g", zPos);
        xPos =  xc + r * Cos(Pi/180*(phi[i] + offset[j-1])); yPos = yc + r * Sin(Pi/180*(phi[i] + offset[j-1])); rHole = t[i];
        xAxis = xPos - xc; yAxis = yPos - yc;
        v = newv; 
        If (t[i] < .10)
	        Cylinder(v) = {xPos, yPos, zPos, -xAxis, -yAxis, 0, rHole};
        Else
	        Cone(v) = {xPos, yPos, zPos, -xAxis, -yAxis, 0, rHole, 0};
        EndIf
	    BooleanDifference{Volume{shuntOuter};Delete;}{Volume{v}; Delete;}
    EndFor
EndFor
BooleanDifference{Volume{box}; Delete;}{Volume{shuntOuter}; Delete;}


// Identify groups of surfaces with phyiscal entities
surfs[]=Surface "*";
Physical Surface("walls") = {};
n= #surfs[];
For i In {0:n-7:1}
    Physical Surface("walls") += {surfs(i)};
EndFor

Physical Surface("backWall") = {surfs(n-6)};
Physical Surface("domainInlet") = {surfs(n-4)};
Physical Surface("domainOutlet") = {surfs(n-3)};
Physical Surface("walls") += {surfs(n-2)};
Physical Surface("walls") += {surfs(n-5)};
Physical Surface("outlet") = {surfs(n-1)};

Physical Volume("fluid") = {1};


Characteristic Length{Point{:}} = meshSize;
Mesh.MeshSizeFromCurvature = 10;

