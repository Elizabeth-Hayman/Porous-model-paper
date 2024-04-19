
#### import the simple module from the paraview
from paraview.simple import *
paraview.simple._DisableFirstRenderCameraReset()

def extractValueOutlet(inputFile, outCSV):
    #outFile = f"slices/outfileZ={Z}.csv"
    # create a new 'OpenFOAMReader'
    fluid2foam = OpenFOAMReader(registrationName='foam.foam', FileName=inputFile)
    fluid2foam.MeshRegions = ['patch/outlet']
    fluid2foam.CellArrays = ['C', 'Cx', 'Cy', 'Cz', 'U', 'force', 'moment', 'p', 'static(p)', 'stressTensor', 'wallShearStress']

    integrateVariables1 = IntegrateVariables(registrationName='IntegrateVariables1', Input=fluid2foam)

    # Create a new 'SpreadSheet View'
    spreadSheetView1 = CreateView('SpreadSheetView')
    spreadSheetView1.ColumnToSort = ''
    spreadSheetView1.BlockSize = 1024

    # Properties modified on spreadSheetView1
    spreadSheetView1.FieldAssociation = 'Cell Data'
    spreadSheetView1.HiddenColumnLabels = ['Block Name', 'Block Number', 'Cell ID', 'C_Magnitude', 'Cell Type', 'Cx', 'Cy', 'Cz', 'U_Magnitude', 'force', 
                                        'force_Magnitude', 'moment', 'moment_Magnitude', 'static(p)', 'stressTensor', 'stressTensor_Magnitude', 
                                        'wallShearStress', 'wallShearStress_Magnitude']

    integrateVariables1Display = Show(integrateVariables1, spreadSheetView1, 'SpreadSheetRepresentation')
    ExportView(outCSV, view=spreadSheetView1)
