// Turn on labels
SetFactory("OpenCASCADE");
Mesh.Algorithm = 5;



// Initialise parameters - user coded. 
// Mesh parameters:
meshSize = 0.05;
// Catheter parameters
rOuter=1.25;
ri = 0.75;
L = 30;

// Hole parameters updated in simulation
rh = 0.051572827066605924;
width = 1.0;
numAxial = 5.0;
numSection = 10.0;
numInSection = 1;



holeWidth[] = {}; phi[]={}; offset[] = {}; startDist[] = {}; endDist[] = {};
For i In {0:numAxial-1:1}
	holeWidth[] += {rh};
	phi[] += {360*i / numAxial};
EndFor

// Offset changes orientation 
For i In {0:(numSection )-1:1}
	offset[] += {360 * i / numAxial};
EndFor

For i In {1:numSection:1}
	startDist[] += {(i)/(numSection+1) * L - width/2 + rh};
	endDist[] += {(i)/(numSection+1) * L + width /2 - rh};
EndFor


//Make catheter 
shuntInner = newv; Cylinder(shuntInner) = {0, 0, 0, 0, 0, L, ri, 2*Pi};
// Set up each of the hole wedges   
For z In {0:#startDist[]-1:1} 
	For i In {0:numAxial-1:1}
		For j In {0:numInSection-1:1}
			If (numInSection == 1)
				zPos = (endDist[z] + startDist[z])/2;
			Else
				zPos = startDist[z] + (j)*(endDist[z]-startDist[z])/(numInSection-1);
			EndIf
			xPos = rOuter * Cos(Pi/180*(phi[i] + offset[z])); yPos = rOuter * Sin(Pi/180*(phi[i] + offset[z]));
			For k In {0:4:1}
				d = news; Circle(d) = {xPos, yPos, zPos + k/5*1.7, holeWidth[i]};  Curve Loop(d) = d;
			EndFor
            v = newv; ThruSections(v) = {d-4:d};
            Rotate {{-yPos, xPos, 0}, {xPos, yPos, zPos}, -Pi/2} { Volume{v};}
            Delete{Line{d-4:d};}
			BooleanUnion{Volume{shuntInner};Delete;}{Volume{v}; Delete;}
		EndFor
	EndFor
EndFor

// Identify groups of surfaces with phyiscal entities

surfs[]=Surface "*";
Physical Surface("walls") = {};
Physical Surface("backWall") = {};
Physical Surface("inlet") = {};
Physical Surface("outlet") = {};

// Identify back and front walls
For i In {0:#surfs[]-1:1}
    s = surfs(i);
	bdyline() = Boundary{Surface{s};};
	k=#bdyline();
	bdy[] = Boundary{Line{bdyline[0]};};
	coords = Point{bdy[0]};
	If (k == 6) // Selects the tubes
		Physical Surface("walls",1) += {s};
	ElseIf (k == 1)
		Printf("found k >==1 %g", i);
		If (coords[2]==0)
		    Physical Surface("backWall", 4) += {s};
		ElseIf (coords[2]==L)
		    Physical Surface("outlet", 4) += {s};
		Else
		    Physical Surface("inlet", 3) += {s};
		EndIf
    ElseIf (k == 3)
        Physical Surface("inlet", 3) += {s};
	ElseIf (k == 2) // inlets on phi=0
        Physical Surface("inlet", 3) += {s};
	Else
        Physical Surface("walls",1) += {s};
	EndIf
		
EndFor


Characteristic Length{Point{:}} = 3*meshSize;
Physical Volume("fluid") = {shuntInner};
Mesh.MeshSizeFromCurvature = 10;
