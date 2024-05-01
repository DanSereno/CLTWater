"""
SYNOPSIS

    clt_water_create_geometry.py
    This script to be run as a stand alone script.

DESCRIPTION

    This script iterates a list of point  and line feature classes, in the target database, and
        1. Determine if there is a corresponding table in the source database.
        2. If a corresponding table exists, then iterate each row of the source database table and
            a. Get the PARENTID, then
            b. Parse the PARENTID to determine which target database feature class record we should
                get the centroid XY coordinates from.
        3. If the target feature class has no records or does not exist,
            a. Get the PlantName
            b. Determine which plant polygon we should get the centroid XY coordinates from.
        4. Inside the target database's point feature class create a new record using the XY coordinates from step 2 or 3.
        5. Inside the target database's line feature class create a new records using the XY coordinates from step 2 or 3, as the
            starting vertex, then add ~14 feet to create the ending vertex.
        6. Poplate other required fields when creating new points or lines.
    
REQUIREMENTS

    Python 3.5 or higher

AUTHOR

    Dan Sereno, AximGeoSpatial, 2024
    
UPDATES

    TODO - If this script was modified, indicate when it was modified, what
           modifications were performed, and by whom.
"""

import os, sys
import logging
import traceback


exit_status = 0

# import arcpy
# below is code to try to catch arcpy import errors
try:
    import arcpy
    arcpy_imported = True
except:
    arcpy_imported = False
    exit_status = 1

# Create feature at centroid of the YARD
def create_yard_geometry(target_fc, plantID, yard, assetID, name, parentID, tag = None):
    #print(fr"Processing {target_fc}, {plantID}, {yard}, {assetID}, {name}, {tag}, {parentID}")
    with arcpy.da.SearchCursor(yard, ['PlantName', 'PlantID', 'SHAPE@XY']) as yard_cursor:
        for yard_row in yard_cursor:
            yard_name = yard_row[0]
            yard_id = yard_row[1]
            if yard_name.lower() == plantID.lower():
            
                # Get the centroid XY of the plant
                x = yard_row[2][0]
                y = yard_row[2][1]

                # Create global offset variable
                global xOffset
                global yOffset
                xOffset = 10
                yOffset = 10

                #Create a point, in the target fc at the centroid of the Yard
                #print(fr"{os.path.basename(target_fc)}")
                if os.path.basename(target_fc) in point_no_tag:
                    insert_field_list = ['SHAPE@XY', 'PlantName', 'PlantID', 'ASSETID', 'Name', 'ParentID']
                elif os.path.basename(target_fc) in line_no_tag:
                    insert_field_list = ['SHAPE@', 'PlantName', 'PlantID', 'ASSETID', 'Name', 'ParentID']
                else:
                    insert_field_list = ['SHAPE@XY', 'PlantName', 'PlantID', 'ASSETID', 'Name', 'TagNumber', 'ParentID']
                with arcpy.da.InsertCursor(target_fc, insert_field_list) as target_insert_cursor:
                    xy = (x, y)
                    if os.path.basename(target_fc) in point_no_tag:
                        insert_row_list = [xy, yard_name, yard_id, assetID, name, parentID]
                        target_insert_cursor.insertRow(insert_row_list)
                    elif os.path.basename(target_fc) in line_no_tag:
                        array = arcpy.Array(
                            [arcpy.Point(x, y), arcpy.Point(x + xOffset, y + yOffset)])
                        polyline = arcpy.Polyline(array)
                        target_insert_cursor.insertRow([polyline, yard_name, yard_id, assetID, name, parentID])
                    else:   
                        #print(fr"insert_field_list: {insert_field_list}")
                        #print(fr"insert_row_list: {insert_row_list}")
                        insert_row_list = [xy, yard_name, yard_id, assetID, name, tag, parentID]
                        target_insert_cursor.insertRow(insert_row_list)
                    break

def main():
    """
    Main execution code
    """
    try:
        # if arcpy did not import, log the message and quit
        if arcpy_imported == False:
            raise ValueError("Could not import arcpy.  Check licensing or the Python executable.")
        
        # # # # Put your code below here # # # # #
        # Define data source and target locations
        sdb = r'C:\Temp\CLT_Plant\wam_emd_plants_sd_clientdata.gdb' #arcpy.GetParametersAsText[0] # Source database
        tdb = r'C:\Temp\CLT_Plant\CLT_WW_Treatment_Plant_Assets_Relationships.gdb' #arcpy.GetParametersAsText[1] # Target database
        
        # Point fc list
        fc_list = ['Aerator',
                     'AirCompressor',
                     'BarScreen',
                     'BeltFilterPress',
                     'BlowerUnit',
                     'Boiler',
                     'CentrifugeUnit',
                     'Compactor',
                     'Disinfectors',
                     'Electrical',
                     'ElectricalSwitchgear',
                     'Filter',
                     'FlowElement',
                     'Generator',
                     'Grinder',
                     'HeatExchanger',
                     'HVAC',
                     'LiftEquipment',
                     'Mixer',
                     'PumpUnit',
                     'SludgeHeater',
                     'Tank',
                     'UVDisinfectionUnit',
                     'Valve',
                     'Vault',
                     'WetWell',
                     'UVChannel',
                     'Pipe',
                     'AirPipe'
                     ]
        
        # Polygons feature classes in target database
        target_polys = {'WWBAS':'Basin',
                        'WWABUNT':'Basin',
                        'WWAER':'Basin',
                        'WWBASIN':'Basin',
                        'WWBGF':'Buildings',
                        'WWCB':'Buildings',
                        'WWCFPS':'Buildings',
                        'WWEBRPS':'Buildings',
                        'WWEFF':'Buildings',
                        'WWFAC':'Buildings',
                        'WWFEPS':'Buildings',
                        'WWFEQE':'Buildings',
                        'WWFWPS':'Buildings',
                        'WWGB':'Buildings',
                        'WWGTPS':'Buildings',
                        'WWHEAD':'Buildings',
                        'WWHFPS':'Buildings',
                        'WWIPS':'Buildings',
                        'WWLLPS':'Buildings',
                        'WWMFB':'Buildings',
                        'WWNPS':'Buildings',
                        'WWNPWPS':'Buildings',
                        'WWOCA':'Buildings',
                        'WWOCF':'Buildings',
                        'WWPS':'Buildings',
                        'WWPSPS':'Buildings',
                        'WWRAS':'Buildings',
                        'WWRPS':'Buildings',
                        'WWRWPS':'Buildings',
                        'WWSBC':'Buildings',
                        'WWSFE':'Buildings',
                        'WWSFF':'Buildings',
                        'WWSGF':'Buildings',
                        'WWSPS':'Buildings',
                        'WWSS':'Buildings',
                        'WWSUS':'Buildings',
                        'WWTWF':'Buildings',
                        'WWWF':'Buildings',
                        'WWWPB':'Buildings',
                        'WWWPS':'Buildings',
                        'WWWWGF':'Buildings',
                        'WWCLR':'Clarifier',
                        'WWFCLAR':'Clarifier',
                        'WWPCLAR':'Clarifier',
                        'WWAD':'Digestor',
                        'WWDIG':'Digestor',
                        'WWENC':'Enclosure',
                        'WWSDB':'SludgeDryingBed',
                        'WWGT':'Thickener',
                        'WWDISBX':'Thickener',
                        'WWYARD':'Yard'
                        }
        
        # Define feature classes with no Tag attribute
        global point_no_tag
        global line_no_tag
        point_no_tag = ['FlowElement', 'Filter', 'Tank', 'UVDisinfectionUnit', 'Vault', 'WetWell', 'Electrical']
        line_no_tag = ['AirPipe', 'Pipe', 'UVChannel']

        # Define the YARD feature class
        yard = os.path.join(tdb, 'YARD')

        # Iterate a list of point feature classes, in the target database, and
        #   determine if there is a corresponding table in the source database.
        for fc in fc_list:

            source_table = os.path.join(sdb, fc)
            target_fc = os.path.join(tdb, fc)
            
            # Check if source table exists, if no table exits skip the iteration
            if not arcpy.Exists(source_table):
                continue

            # If a corresponding table exists, then iterate each row of the source database table and
            #   get the PARENTID
            # Iterate each row of the source table to get the PLANTID
            if os.path.basename(target_fc) in point_no_tag or os.path.basename(target_fc) in line_no_tag:
                field_list = ['PARENTID', 'PLANTID', 'ASSETID', 'Name']    
            else:
                field_list = ['PARENTID', 'PLANTID', 'ASSETID', 'Name', 'TAG']
            with arcpy.da.SearchCursor(source_table, field_list) as source_cursor:
                for row in source_cursor:
                    parentID = row[0]
                    plantID = row[1]
                    assetID = row[2]
                    name = row[3]
                    if 'Filter' or 'Tank' in source_table:
                        tag = ''
                    else:
                        tag = row[4]

                    # If the record has no ParentID or PlantID, do not process it
                    if not parentID and not plantID:
                        continue

                    # Parse the PARENTID to determine which target database polygon feature class 
                    #   record we should get the centroid XY coordinates from.
                    if row[0]:
                        parentID_prefix = row[0].split('-')[0]
                    else:
                        create_yard_geometry(target_fc, plantID, yard, assetID, name, parentID, tag)
                        continue

                    # Check if target database polygon feature class exists
                    if parentID_prefix in target_polys:
                        polygon_source = os.path.join(tdb, target_polys[parentID_prefix])

                        # Check if polygon_source has records.
                        polygon_count = arcpy.GetCount_management(polygon_source)
                        if int(polygon_count[0]) > 0:

                            # Get the correct polygon feature to create a point in
                            with arcpy.da.SearchCursor(polygon_source, ['AssetID', 'SHAPE@XY']) as poly_cursor:
                                for poly in poly_cursor:
                                    if parentID == poly[0]:

                                        # Get the centroid XY of the plant
                                        x = poly[1][0]
                                        y = poly[1][1]

                                        #Create a point, in the target fc at the centroid of the polygon_source
                                        if os.path.basename(target_fc) in point_no_tag:
                                            insert_field_list = ['SHAPE@XY', 'PlantID', 'PlantName', 'ASSETID', 'Name', 'ParentID']
                                        elif os.path.basename(target_fc) in line_no_tag:
                                            insert_field_list = ['SHAPE@', 'PlantName', 'ASSETID', 'Name', 'ParentID']
                                        else:
                                            insert_field_list = ['SHAPE@XY', 'PlantID', 'PlantName', 'ASSETID', 'Name', 'TagNumber', 'ParentID']
                                        with arcpy.da.InsertCursor(target_fc, insert_field_list) as insert_cursor:
                                            xy = (x, y)
                                            if os.path.basename(target_fc) in point_no_tag:
                                                insert_row_list = [xy, parentID, plantID, assetID, name, parentID]
                                                insert_cursor.insertRow(insert_row_list)
                                            
                                            # Process line feature classes
                                            elif os.path.basename(target_fc) in line_no_tag:
                                                array = arcpy.Array(
                                                    [arcpy.Point(x, y), arcpy.Point(x + xOffset, y + yOffset)])
                                                polyline = arcpy.Polyline(array)
                                                insert_cursor.insertRow([polyline, plantID, assetID, name, parentID])
                                            else:
                                                insert_row_list = [xy, parentID, plantID, assetID, name, tag, parentID]
                                                insert_cursor.insertRow(insert_row_list)
                                            break

                        # If the polygon_source has no records or does not exist,
                        #    get XYs from Yard fc        
                        else:
                            create_yard_geometry(target_fc, plantID, yard, assetID, name, parentID, tag)

                    # If a target polygon feature class is not found, get XYs from Yard fc
                    else:
                        create_yard_geometry(target_fc, plantID, yard, assetID, name, parentID, tag)  

        exit_status = "SUCCESS"
        # # # # End your code above here # # # #
            
    except ValueError as e:
        exit_status = 1
        exc_traceback = sys.exc_info()[2]
        error_text = 'Line: {0} --- {1}'.format(exc_traceback.tb_lineno, e)
        try:
            print(error_text)
        except NameError:
            print(error_text)       
    
    except Exception:
        exit_status = 1
        exc_traceback = sys.exc_info()[2]
        tbinfo = traceback.format_exc()
        error_text = 'Line: {0} --- {1}'.format(exc_traceback.tb_lineno, tbinfo)
        try:
            print(error_text)
        except NameError:
            print(tbinfo)
    
    finally:
        # shut down logging
        try:
            print("--- Script Execution Completed ---")
            logging.shutdown()
        except NameError:
            pass
        if exit_status == "SUCCESS":
            sys.exit(0)
        else:
            print(str(exit_status))
            sys.exit(exit_status)
    
if __name__ == '__main__':
    main()
