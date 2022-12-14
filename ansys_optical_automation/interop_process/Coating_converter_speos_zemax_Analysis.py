import math

import clr, os, winreg
from itertools import islice
import shutil
import numpy as np
import io

from ansys_optical_automation.zemax_process.base import BaseZOS
from comtypes.client import CreateObject

def main():

    zos = BaseZOS()
    
    # load local variables
    zosapi = zos.zosapi
    the_application = zos.the_application
    the_system = zos.the_system
    
    # Insert Code Here
 
    
    #-------------------------------------------------------------------------------------------------
    # USER INPUT
    coatingfilename = "Meopta_CoatingFileExample.dat"
    coatingfolder = r"C:\Data\PROJECTS\MEOPTA_COATING\COATINGS"
    user_wavelength_min = 0.31
    user_wavelength_max = 0.9
    nb_wavelength = 5
    # Wavelength unit in Speos in um
    speos_wavelength_units_um = 1000
    # AngleOfIncidence_min = 0
    # AngleOfIncidence_max = 90
    # nb_angle_of_incidence = 91

    #Coating substrates
    #We could also read a Zemax file and extract coatings directly with the substrates
    #Here we extract two coatings per substrates: Substrate -> AIR and AIR -> SubstrateN-SK16
    substrate_catalog = "HOYA"
    #substrate_name = ("N-SK16", "N-SF56", "SF4")
    #substrate_name = ("N-SK16")
    substrate_name = ("TAF1","E-F1")

    #Number of digits
    nb_digits = 6
    skip_lines = 4
    
    #-------------------------------------------------------------------------------------------------

    myformat = '{:.'+str(nb_digits)+'f}'
    coatingfullfilename = coatingfolder+'\\'+ coatingfilename
    print(coatingfullfilename)

    # Set up primary optical system
    the_system = the_application.PrimarySystem;
    sample_dir = the_application.SamplesDir;
    coating_dir = the_application.CoatingDir;
    destination_file=coating_dir+'\\'+coatingfilename
    #print(destination_file)
    shutil.copy(coatingfullfilename,destination_file)
    # Make new file
    test_file = sample_dir + '\coating.zos'
    #print(test_file)
    the_system.New(False)
    the_system.SaveAs(test_file)
    # Coating catalog
    the_system.SystemData.Files.CoatingFile = coatingfilename
    # Aperture
    the_system_data = the_system.SystemData
    the_system_data.Aperture.ApertureValue = 1
    the_lde = the_system.LDE
    surface_0 = the_lde.GetSurfaceAt(0)
    surface_1 = the_lde.GetSurfaceAt(1)
    # Check the material catalog
    if not the_system.SystemData.MaterialCatalogs.IsCatalogInUse(substrate_catalog):
        the_system.SystemData.MaterialCatalogs.AddCatalog(substrate_catalog)
    coating_list = surface_1.CoatingData.GetAvailableCoatings()
    coating_list_length = coating_list.Length
    wave = 1
    the_system.Save()
    
    # % TABLE coating? Can be checked with number of layers
    # % TestSurface.CoatingData.NumberOfLayers = 0 --> TABLE
    # % TestSurface.CoatingData.NumberOfLayers <> 0 --> COAT
    # % If it is a TABLE coating --> direct conversion
    # % If it is a COAT coating --> need to use a method to convert

    for j in range(len(substrate_name)):
        material_1 = substrate_name[j]
        material_2_name = "AIR"
        material_2 = ''

        # Open the material catalog and check the wavelength ranges
        my_material_catalog = the_system.Tools.OpenMaterialsCatalog()
        my_material_catalog.SelectedCatalog = substrate_catalog
        my_material_catalog.SelectedMaterial = material_1
        material_1_minwave = my_material_catalog.MinimumWavelength
        material_1_maxwave = my_material_catalog.MaximumWavelength
        my_material_catalog.Close()

        if material_1_minwave > user_wavelength_min:
            wavelength_min = material_1_minwave
        else:
            wavelength_min = user_wavelength_min
        if user_wavelength_max > material_1_maxwave:
            wavelength_max = material_1_maxwave
        else:
            wavelength_max = user_wavelength_max
        wavelength_delta = (wavelength_max - wavelength_min) / (nb_wavelength - 1)

        for i in range(coating_list_length):
            # print(coating_list[i])
            coating_name = coating_list[i]
            if not coating_name == 'None':
                name1 = str(coating_name) + '_' + str(material_2_name) + '_' + str(material_1)
                name2 = str(coating_name) + '_' + str(material_1) + '_' + str(material_2_name)
                coatingfilename1 = name1 + '.coated'
                coatingfilename2 = name2 + '.coated'
                coatingfullfilename1 = coatingfolder + '\\' + coatingfilename1
                coatingfullfilename2 = coatingfolder + '\\' + coatingfilename2
                file_id1 = open(coatingfullfilename1,'w')
                file_id2 = open(coatingfullfilename2, 'w')

                coating_data = list()

                # From AIR TO SUBSTRATE
                surface_0.Material = material_2  # AIR
                surface_1.Material = material_1
                surface_1.Coating = coating_name

                # Need to loop for all wavelength
                for wavelength_index in range(nb_wavelength):
                    wavelength = round(wavelength_min + wavelength_index * (wavelength_max - wavelength_min) / (
                            nb_wavelength - 1), 3)
                    the_system.SystemData.Wavelengths.GetWavelength(wave).Wavelength = wavelength
                    #--------------------------------------------------------------------------------------------------
                    # Reading from the analysis
                    # No access to the settings so:
                    # - the incident angles should be set by default from 0 to 90
                    # - the surface should be set to 1
                    # --------------------------------------------------------------------------------------------------
                    # the_system.Save()

                    my_transmission_vs_angle = the_system.Analyses.New_Analysis(
                        zosapi.Analysis.AnalysisIDM.TransmissionvsAngle)
                    my_transmission_vs_angle.ApplyAndWaitForCompletion()
                    my_transmission_vs_angle_results = my_transmission_vs_angle.GetResults()
                    resultfullfilename = coatingfolder + '\\My_Transmission_vs_angle_' + name1 + '.txt'
                    bool_result = my_transmission_vs_angle_results.GetTextFile(resultfullfilename)
                    # if bool_result == False:
                        # print("The result file was not created!")
                    my_transmission_vs_angle.Close()

                    # Reading the transmission file
                    bfile = io.open(resultfullfilename, 'r', encoding='utf-16-le')
                    header_line = bfile.readline()
                    while header_line[1:10].strip() != 'Angle':
                        header_line = bfile.readline()
                    # Now reading the content
                    # Angle S - Reflect P - Reflect S - Transmit    P - Transmit
                    index_angle_of_incidence = 0
                    data_line = 'start'
                    while not len(data_line) == 1:
                        data_line = bfile.readline()
                        data_line = data_line.split('\t')
                        data_line = data_line[0:5] #only keeping the first 5 values
                        #Miss 3 lines
                        for index_line in range(skip_lines):
                            bfile.readline()
                        coating_data.append(data_line)
                        index_angle_of_incidence = index_angle_of_incidence + 1
                        # print(index_angle_of_incidence)
                        # nb_angle_of_incidence = len(coating_data)
                    nb_angle_of_incidence = index_angle_of_incidence - 1
                    bfile.close()

                # Writing the file
                file_id1.write('OPTIS - Coated surface file v1.0\n')
                file_id1.write(name1 + "\n")
                file_id1.write(str(nb_angle_of_incidence) + " " + str(nb_wavelength) + "\n")

                #1st line
                for wavelength_index in range(nb_wavelength):
                    wavelength = round(wavelength_min + wavelength_index * (wavelength_max - wavelength_min) / (
                            nb_wavelength - 1), 3)
                    file_id1.write("\t" + " " + myformat.format(speos_wavelength_units_um * wavelength) + " " + "\t")
                file_id1.write("\n")
                #Loop to read the data
                for angle_index in range(nb_angle_of_incidence):
                    #1st column: angle of incidence
                    angleofincidence = float(coating_data[angle_index][0])
                    file_id1.write(myformat.format(angleofincidence) + ' \t')
                    for wavelength_index in range(nb_wavelength):
                        offset = angle_index+wavelength_index*(nb_angle_of_incidence+1)
                        reflectance_ppol_1 = float(coating_data[offset][2])
                        transmittance_ppol_1 = float(coating_data[offset][4])
                        file_id1.write(myformat.format(100 * reflectance_ppol_1) + '\t' + myformat.format(
                            100 * transmittance_ppol_1) + '\t')
                    file_id1.write("\n\t")
                    for wavelength_index in range(nb_wavelength):
                        offset = angle_index+wavelength_index*(nb_angle_of_incidence+1)
                        reflectance_spol_1 = float(coating_data[offset][1])
                        transmittance_spol_1 = float(coating_data[offset][3])
                        file_id1.write(myformat.format(100 * reflectance_spol_1) + "\t" + myformat.format(
                            100 * transmittance_spol_1) + "\t")
                    file_id1.write("\n")
                file_id1.close()
                print("File " + coatingfilename1 + " created")
                coating_data.clear()
                os.remove(resultfullfilename)

                # from SUBSTRATE to AIR
                surface_0.Material = material_1
                surface_1.Material = material_2 #AIR
                surface_1.Coating = coating_name

                for wavelength_index in range(nb_wavelength):
                    wavelength = round(wavelength_min + wavelength_index * (wavelength_max - wavelength_min) / (
                            nb_wavelength - 1), 3)
                    the_system.SystemData.Wavelengths.GetWavelength(wave).Wavelength = wavelength
                    # --------------------------------------------------------------------------------------------------
                    # Reading from the analysis
                    # No access to the settings so:
                    # - the incident angles should be set by default from 0 to 90
                    # - the surface should be set to 1
                    # --------------------------------------------------------------------------------------------------
                    # From AIR TO SUBSTRATE
                    # Need to loop for all wavelength
                    my_transmission_vs_angle = the_system.Analyses.New_Analysis(
                        zosapi.Analysis.AnalysisIDM.TransmissionvsAngle)
                    my_transmission_vs_angle.ApplyAndWaitForCompletion()
                    my_transmission_vs_angle_results = my_transmission_vs_angle.GetResults()
                    resultfullfilename2 = coatingfolder + '\\My_Transmission_vs_angle_' + name2 + '.txt'
                    bool_result = my_transmission_vs_angle_results.GetTextFile(resultfullfilename2)
                    # if bool_result == False:
                    #    print("The result file was not created!")
                    my_transmission_vs_angle.Close()

                    # Reading the transmission file
                    # bfile = open(resultfullfilename, 'r')
                    bfile = io.open(resultfullfilename2, 'r', encoding='utf-16-le')
                    header_line = bfile.readline()
                    while header_line[1:10].strip() != 'Angle':
                        header_line = bfile.readline()
                    # Now reading the content
                    # Angle S - Reflect P - Reflect S - Transmit    P - Transmit
                    index_angle_of_incidence = 0
                    data_line = 'start'
                    while not len(data_line) == 1:
                        data_line = bfile.readline()
                        data_line = data_line.split('\t')
                        data_line = data_line[0:5]  # only keeping the first 5 values
                        # Miss 3 lines
                        for index_line in range(skip_lines):
                            bfile.readline()
                        coating_data.append(data_line)
                        index_angle_of_incidence = index_angle_of_incidence + 1
                    nb_angle_of_incidence = index_angle_of_incidence - 1
                    bfile.close()

                # Writing the file
                file_id2.write('OPTIS - Coated surface file v1.0\n')
                file_id2.write(name2 + "\n")
                file_id2.write(str(nb_angle_of_incidence) + " " + str(nb_wavelength) + "\n")
                for wavelength_index in range(nb_wavelength):
                    wavelength = round(wavelength_min + wavelength_index * (wavelength_max - wavelength_min) / (
                            nb_wavelength - 1), 3)
                    file_id2.write("\t" + " " + myformat.format(speos_wavelength_units_um * wavelength) + " " + "\t")
                file_id2.write("\n")

                for angle_index in range(nb_angle_of_incidence):
                    # 1st column: angle of incidence
                    angleofincidence = float(coating_data[angle_index][0])
                    file_id2.write(myformat.format(angleofincidence) + ' \t')
                    for wavelength_index in range(nb_wavelength):
                        offset = angle_index + wavelength_index * (nb_angle_of_incidence + 1)
                        reflectance_ppol_1 = float(coating_data[offset][2])
                        transmittance_ppol_1 = float(coating_data[offset][4])
                        file_id2.write(myformat.format(100 * reflectance_ppol_1) + '\t' + myformat.format(
                            100 * transmittance_ppol_1) + '\t')
                    file_id2.write("\n\t")
                    for wavelength_index in range(nb_wavelength):
                        offset = angle_index + wavelength_index * (nb_angle_of_incidence + 1)
                        reflectance_spol_1 = float(coating_data[offset][1])
                        transmittance_spol_1 = float(coating_data[offset][3])
                        file_id2.write(myformat.format(100 * reflectance_spol_1) + "\t" + myformat.format(
                            100 * transmittance_spol_1) + "\t")
                    file_id2.write("\n")
                file_id2.close()
                print("File " + coatingfilename2 + " created")
                coating_data.clear()
                os.remove(resultfullfilename2)

                # Create the BSDF180 that combines the two coatings
                bsdf_viewer = CreateObject("SimpleBSDFSurfaceViewer.Application")
                # Builds BSDF 180
                bsdf_viewer.BuildBSDF180(coatingfullfilename1, coatingfullfilename2)
                bsdf180filename = str(coating_name) + '_' + str(material_2_name) + '_' + str(material_1) + '.bsdf180'
                bsdf180fullfilename = coatingfolder + '\\' + bsdf180filename
                # Save BSDF180
                bsdf_viewer.SaveFile(bsdf180fullfilename)
                print("File " + bsdf180filename + " created\n")


    os.remove(destination_file)
    os.remove(test_file)
    # This will clean up the connection to OpticStudio.
    # Note that it closes down the server instance of OpticStudio, so you for maximum performance do not do
    # this until you need to.
    del zos
    zos = None


main()