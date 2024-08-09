
#### import the simple module from the paraview
from paraview.simple import *
paraview.simple._DisableFirstRenderCameraReset()

def extractValue(inputFile, Zrange):
    #outFile = f"slices/outfileZ={Z}.csv"
    # create a new 'OpenFOAMReader'
    fluid2foam = OpenFOAMReader(registrationName='foam.foam', FileName=inputFile)
    fluid2foam.MeshRegions = ['internalMesh']
    fluid2foam.CellArrays = ['C', 'Cx', 'Cy', 'Cz', 'U', 'force', 'moment', 'p', 'static(p)', 'stressTensor', 'wallShearStress']

    # create a new 'Clip'
    clip1 = Clip(registrationName='Clip1', Input=fluid2foam)
    clip1.ClipType = 'Cylinder'

    # Properties modified on clip1.ClipType
    clip1.ClipType.Center = [0,0, 15.0]
    clip1.ClipType.Axis = [0.0, 0.0, 1.0]
    clip1.ClipType.Radius = 0.75

    for Z in Zrange:
        # create a new 'Slice'
        slice1 = Slice(registrationName='Slice1', Input=clip1)
        slice1.SliceType = 'Plane'
        slice1.SliceOffsetValues = [0.0]
        slice1.SliceType.Origin = [0,0, Z]
        slice1.HyperTreeGridSlicer.Origin = [0,0, Z]
        slice1.SliceType.Normal = [0.0, 0.0, 1.0]
        # create a new 'Integrate Variables'
        integrateVariables1 = IntegrateVariables(registrationName='IntegrateVariables1', Input=slice1)

        # Create a new 'SpreadSheet View'
        spreadSheetView1 = CreateView('SpreadSheetView')
        spreadSheetView1.ColumnToSort = ''
        spreadSheetView1.BlockSize = 1024
        spreadSheetView1.FieldAssociation = 'Cell Data'

        # Properties modified on spreadSheetView1
        #spreadSheetView1.FieldAssociation = 'Cell Data'
        spreadSheetView1.HiddenColumnLabels = ['Block Name', 'Block Number', 'Cell ID', 'C_Magnitude', 'Cell Type', 'Cx', 'Cy', 'Cz', 'U_Magnitude', 'force', 
                                            'force_Magnitude', 'moment', 'moment_Magnitude', 'static(p)', 'stressTensor', 'stressTensor_Magnitude', 
                                            'wallShearStress', 'wallShearStress_Magnitude']

        integrateVariables1Display = Show(integrateVariables1, spreadSheetView1, 'SpreadSheetRepresentation')
        ExportView(f"slices/z={Z}.csv", view=spreadSheetView1)

    """
    ## ---------------------------------------------------
    ## Extract centreline data
    plotOverLine1 = PlotOverLine(registrationName='PlotOverLine1', Input=fluid2foam)
    plotOverLine1.Point1 = [0, 0, 0.0]
    plotOverLine1.Point2 = [0, 0, 30.0]

    integrateVariables1 = IntegrateVariables(registrationName='IntegrateVariables1', Input=plotOverLine1)

    # Create a new 'SpreadSheet View'
    spreadSheetView3 = CreateView('SpreadSheetView')
    spreadSheetView3.ColumnToSort = ''
    spreadSheetView3.BlockSize = 1024
    #spreadSheetView3.FieldAssociation = 'Cell Data'
    spreadSheetView3.HiddenColumnLabels = ['Point ID', 'Points_Magnitude', 'U_Magnitude', 'arc_length', 'static(p)', 'stressTensor', 
                                           'stressTensor_Magnitude', 'vtkValidPointMask', 'Block Number']
    integrateVariables1Display = Show(integrateVariables1, spreadSheetView3, 'SpreadSheetRepresentation')
    plotOverLine1Display_2 = Show(plotOverLine1, spreadSheetView3, 'SpreadSheetRepresentation')
    ExportView('centreLine.csv', view=spreadSheetView3)
    """



    ## ---------------------------------------------------
    ## Extract outlet surface
    fluid2foam.MeshRegions = ['patch/outlet']
    fluid2foam.CellArrays = ['C', 'Cx', 'Cy', 'Cz', 'U', 'force', 'moment', 'p', 'static(p)', 'stressTensor', 'wallShearStress']

    integrateVariables2 = IntegrateVariables(registrationName='IntegrateVariables2', Input=fluid2foam)

    # Create a new 'SpreadSheet View'
    spreadSheetView2 = CreateView('SpreadSheetView')
    spreadSheetView2.ColumnToSort = ''
    spreadSheetView2.BlockSize = 1024

    # Properties modified on spreadSheetView1
    spreadSheetView2.FieldAssociation = 'Cell Data'
    spreadSheetView2.HiddenColumnLabels = ['Block Name', 'Block Number', 'Cell ID', 'C_Magnitude', 'Cell Type', 'Cx', 'Cy', 'Cz', 'U_Magnitude', 'force', 
                                        'force_Magnitude', 'moment', 'moment_Magnitude', 'static(p)', 'stressTensor', 'stressTensor_Magnitude', 
                                        'wallShearStress', 'wallShearStress_Magnitude']

    integrateVariables1Display = Show(integrateVariables2, spreadSheetView2, 'SpreadSheetRepresentation')
    ExportView("outlet.csv", view=spreadSheetView2)


