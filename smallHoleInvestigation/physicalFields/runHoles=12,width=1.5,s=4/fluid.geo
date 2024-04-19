// Turn on labels
SetFactory("OpenCASCADE");
Mesh.Algorithm = 8;



// Initialise parameters - user coded. 
// Mesh parameters:
meshSize = 0.03;
// Catheter parameters
r=1.25;
ri = 0.75;
catheterLength = 30;

// Hole parameters updated in simulation
theta = 0.05; 
rotation = 0;
holeWidth[] = {theta,theta,theta,theta,theta,theta,theta,theta};
phi[] = {rotation, rotation+45, rotation+90, rotation+135,rotation+180, rotation+225, rotation+270, rotation+315};

nHoles = 18; 
offset[] = {}; startDist[] = {}; endDist[] = {};
For i In {0:nHoles-1:1}
	offset[] += {11.25*i};
EndFor
nSections = 4; 
width = 1.5; 
For i In {0:nSections-1:1}
	startDist[] += {9+5*i + theta};
	endDist[] += {9+width+5*i - theta};
EndFor


//Make catheter 
shuntInner = newv; Cylinder(shuntInner) = {0, 0, 0, 0, 0, catheterLength, ri, 2*Pi};

numHolesLength = #offset[];
numHolesAxial = #holeWidth[];  
interdiscs[] ={};
// Set up each of the hole wedges   
For z In {0:#startDist[]-1:1} 
	For i In {0:numHolesAxial-1:1}
		For j In {0:numHolesLength-1:1}
			zPos = startDist[z] + (j)*(endDist[z]-startDist[z])/(numHolesLength-1);
			xPos = r * Cos(Pi/180*(phi[i] + offset[j])); yPos = r * Sin(Pi/180*(phi[i] + offset[j]));
			For k In {0:4:1}
				d = news; interdiscs +={d};
				Circle(d) = {xPos, yPos, zPos + k/5*0.7, holeWidth[i]};  Curve Loop(d) = d;
			EndFor
            v = newv; ThruSections(v) = {d-4:d};
            Rotate {{-yPos, xPos, 0}, {xPos, yPos, zPos}, -Pi/2} { Volume{v};}
            Delete{Line{d-4:d};}
			BooleanUnion{Volume{shuntInner};Delete;}{Volume{v}; Delete;}
		EndFor
	EndFor
EndFor

// Identify groups of surfaces with phyiscal entities
n=numHolesLength*numHolesAxial; //shunt has 4+n surfaces
Printf("n %g", n);
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
	Printf("s[i] %g, len bdyline %g", s, k);
	bdy[] = Boundary{Line{bdyline[0]};};
	coords = Point{bdy[0]};
	If (k == 6) // Selects the tubes
		Physical Surface("walls",1) += {s};
		Printf("found k > 3 %g add to wall", i);
	ElseIf (k == 1)
		Printf("found k >==1 %g", i);
		If (coords[2]==0)
		    Physical Surface("backWall", 4) += {s};
		ElseIf (coords[2]==catheterLength)
		    Physical Surface("outlet", 4) += {s};
		Else
		    Physical Surface("inlet", 3) += {s};
		EndIf
		//surfs[] -= i;
    ElseIf (k == 3)
		Printf("found k >==1 %g", i);
        Physical Surface("inlet", 3) += {s};
	ElseIf (k == 2) // inlets on phi=0
		Printf("found k >==1 %g", i);
        Physical Surface("inlet", 3) += {s};
	Else
		Printf("unknown k = %g, s = %g", k, i);
        Physical Surface("walls",1) += {s};
	EndIf
		
EndFor


Characteristic Length{Point{:}} = 3*meshSize;
Physical Volume("fluid") = {shuntInner};
Mesh.MeshSizeFromCurvature = 10;
