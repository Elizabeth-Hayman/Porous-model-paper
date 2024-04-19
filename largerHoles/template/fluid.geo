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
theta = .4; 
numAxial = 4; 
nHoles = 12;
holeWidth[] = {}; phi[] = {};
For i In {0:numAxial-1:1}
	holeWidth[] += {theta};
	phi[] += {360/numAxial*i};
EndFor


offset[] = {};
twist = 90;//11.25;
For i In {0:nHoles-1:1}
	offset[] += {twist*i};
EndFor

startDist[] = {5};
endDist[] = {25};



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
				Circle(d) = {xPos, yPos, zPos + k/5, holeWidth[i]};  Curve Loop(d) = d;
	            //Rotate {{-yPos, xPos, 0}, {xPos, yPos, zPos}, -Pi/2} { Curve{d};}
			EndFor
			//Rotate {{-yPos, xPos, 0}, {xPos, yPos, zPos}, -Pi/2} {Curve{d}; Curve{d-1}; Curve{d-2}; Curve{d-3}; Curve{d-4};}
            v = newv; ThruSections(v) = {d-4:d};
            Delete{Line{d-4:d};}
	        Rotate {{-yPos, xPos, 0}, {xPos, yPos, zPos}, -Pi/2} { Volume{v};}
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
Mesh.MeshSizeFromCurvature = 100*theta;
