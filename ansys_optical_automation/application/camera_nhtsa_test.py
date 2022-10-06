import os
import sys

from ansys_optical_automation.speos_process.speos_sensors import Camera
from ansys_optical_automation.speos_process.speos_simulations import Simulation


def import_car(path, position_value):
    param = GetActiveWindow().Groups[0]
    param.SetDimensionValue(MM(position_value))
    name = "Placement_position"
    target = Selection.CreateByNames(name).Filter[ICoordinateSystem]()
    target.SetActive()
    DocumentInsert.Execute(path)


def define_camera(
    my_cam,
    position,
    focal_length=0.8,
    imager_distance=10,
    f_number=20,
    distortion="OPTIS_Distortion_150deg.OPTDistortion",
    transmittance="ANSYS_Transmittance.spectrum",
    horz_pixel=1280,
    vert_pixel=1280,
    width=1.8,
    height=1.8,
    sensitivity=[
        "ANSYS_Sensitivity_Red.spectrum",
        "ANSYS_Sensitivity_Green.spectrum",
        "ANSYS_Sensitivity_Blue.spectrum",
    ],
):
    """
    function to define the camera
    Parameters
    ----------
    my_cam
    position
    focal_length
    imager_distance
    f_number
    distortion
    transmittance
    horz_pixel
    vert_pixel
    width
    height
    sensitivity

    Returns
    -------


    """
    my_cam.set_position(
        False,
        False,
        position.Items[0],
        [
            position.Items[0].GetDescendants[ICoordinateAxis]()[0],
            position.Items[0].GetDescendants[ICoordinateAxis]()[1],
        ],
    )
    my_cam.speos_object.FocalLength = focal_length
    my_cam.speos_object.ImagerDistance = imager_distance
    my_cam.speos_object.FNumber = f_number
    my_cam.set_distortion(distortion)
    my_cam.set_transmittance(transmittance)
    my_cam.speos_object.HorzPixel = horz_pixel
    my_cam.speos_object.VertPixel = vert_pixel
    my_cam.speos_object.Width = width
    my_cam.speos_object.Height = height
    my_cam.set_sensitivity("red", sensitivity[0])
    my_cam.set_sensitivity("green", sensitivity[1])
    my_cam.set_sensitivity("blue", sensitivity[2])


def main():
    try:
        argsDict
        mode = 1
    except Exception:
        if len(args) == 0:
            mode = 0
        else:
            mode = 2

    if mode == 1:
        camera_model = argsDict["camera_model"]
        car_model = argsDict["car_model"]
        print(car_model + camera_model)
    elif mode == 2:
        # This section defines the inputs which might be replaced by Optislang or the user on usage
        repo_path = os.path.join(os.getcwd(), r"Reference\optical-automation-main")
        sys.path.append(repo_path)
        camera_model = 1
        car_model = "SUV_22R2"
        Ansys_SPEOS_file = os.path.join(os.getcwd(), "Scene_22R2.scdocx")
        if "Berline_22R2" in car_model:
            position_value = 682.2  # Berline =682.2mm
            car_path = os.path.join(os.getcwd(), "ANSYS_Berline/Berline_22R2.scdocx")
        if "SUV_22R2" in car_model:
            position_value = 546.123  # SUV=546.123mm
            car_path = os.path.join(os.getcwd(), "ANSYS_SUV/SUV_22R2.scdocx")
        # this section is the normal script part
        partnames = []
        # Open File
        importOptions = ImportOptions.Create()
        DocumentOpen.Execute(Ansys_SPEOS_file, importOptions)

        import_car(car_path, position_value)
        for part in GetRootPart().Components:
            partnames.append(part.GetName())
        ###
        # Get Camera position
        ###
        name = "Cam_pos_1"  # Axis system in Berline and in SUV
        target = Selection.CreateByNames(name).Filter[ICoordinateSystem]()
        Cam_1 = Camera("Camera", SpeosSim, SpaceClaim)

        if camera_model == 1:  # Based on Camera model V1
            parameters = [
                0.8,
                10,
                20,
                "OPTIS_Distortion_150deg.OPTDistortion",
                "ANSYS_Transmittance.spectrum",
                1280,
                1280,
                1.8,
                1.8,
                [
                    "ANSYS_Sensitivity_Red.spectrum",
                    "ANSYS_Sensitivity_Green.spectrum",
                    "ANSYS_Sensitivity_Blue.spectrum",
                ],
            ]
            define_camera(
                Cam_1,
                target,
                parameters[0],
                parameters[1],
                parameters[2],
                parameters[3],
                parameters[4],
                parameters[5],
                parameters[6],
                parameters[7],
                parameters[8],
                parameters[9],
            )

        if camera_model == 2:  # Based on Camera model V1
            parameters = [
                0.8,
                10,
                20,
                "OPTIS_Distortion_190deg.OPTDistortion",
                "ANSYS_Transmittance.spectrum",
                1280,
                1280,
                1.8,
                1.8,
                [
                    "ANSYS_Sensitivity_Red.spectrum",
                    "ANSYS_Sensitivity_Green.spectrum",
                    "ANSYS_Sensitivity_Blue.spectrum",
                ],
            ]
            define_camera(
                Cam_1,
                target,
                parameters[0],
                parameters[1],
                parameters[2],
                parameters[3],
                parameters[4],
                parameters[5],
                parameters[6],
                parameters[7],
                parameters[8],
                parameters[9],
            )

        Sim_Cam = Simulation("Cam_Sim", SpeosSim, SpaceClaim, "inverse")
        Sim_Cam.select_geometries(partnames)  # new
        Sim_Cam.define_geometries()  # new
        Sim_Cam.object.Sensors.Set(Cam_1.speos_object)

        # Save File
        options = ExportOptions.Create()
        DocumentSave.Execute(Ansys_SPEOS_file, options)
        # This section is added to export an additonal SOlution nfile for compuatiuon on HPC or GPU
        # Export speos-file
        speos_path = os.path.join(os.getcwd(), "SPEOS isolated files")
        if not os.path.isdir(speos_path):
            os.mkdir(speos_path)
        Sim_Cam.object.Export(os.path.join(speos_path, "Cam_Sim.speos"))

    elif mode == 0:
        ###
        # Input Camera model number
        ###
        camera_model = 1

        InputHelper.PauseAndGetInput("Please provide a camera model number (2 models availables)", camera_model)
        partnames = []  # new
        car_model = "SUV_22R2"

        if "Berline_22R2" in car_model:
            position_value = 682.2  # Berline =682.2mm
            car_path = os.path.join(os.getcwd(), "ANSYS_Berline/Berline_22R2.scdocx")
        if "SUV_22R2" in car_model:
            position_value = 546.123  # SUV=546.123mm
            car_path = os.path.join(os.getcwd(), "ANSYS_SUV/SUV_22R2.scdocx")

        import_car(car_path, position_value)
        for part in GetRootPart().Components:
            partnames.append(part.GetName())
        ###
        # Get Camera position
        ###
        name = "Cam_pos_1"  # Axis system in Berline and in SUV
        target = Selection.CreateByNames(name).Filter[ICoordinateSystem]()
        Cam_1 = Camera("Camera", SpeosSim, SpaceClaim)

        if camera_model == 1:  # Based on Camera model V1
            parameters = [
                0.8,
                10,
                20,
                "OPTIS_Distortion_150deg.OPTDistortion",
                "ANSYS_Transmittance.spectrum",
                1280,
                1280,
                1.8,
                1.8,
                [
                    "ANSYS_Sensitivity_Red.spectrum",
                    "ANSYS_Sensitivity_Green.spectrum",
                    "ANSYS_Sensitivity_Blue.spectrum",
                ],
            ]
            define_camera(
                Cam_1,
                target,
                parameters[0],
                parameters[1],
                parameters[2],
                parameters[3],
                parameters[4],
                parameters[5],
                parameters[6],
                parameters[7],
                parameters[8],
                parameters[9],
            )

        if camera_model == 2:  # Based on Camera model V1
            parameters = [
                0.8,
                10,
                20,
                "OPTIS_Distortion_190deg.OPTDistortion",
                "ANSYS_Transmittance.spectrum",
                1280,
                1280,
                1.8,
                1.8,
                [
                    "ANSYS_Sensitivity_Red.spectrum",
                    "ANSYS_Sensitivity_Green.spectrum",
                    "ANSYS_Sensitivity_Blue.spectrum",
                ],
            ]
            define_camera(
                Cam_1,
                target,
                parameters[0],
                parameters[1],
                parameters[2],
                parameters[3],
                parameters[4],
                parameters[5],
                parameters[6],
                parameters[7],
                parameters[8],
                parameters[9],
            )

        Sim_Cam = Simulation("Cam_Sim", SpeosSim, SpaceClaim, "inverse")
        Sim_Cam.select_geometries(partnames)  # new
        Sim_Cam.define_geometries()  # new
        Sim_Cam.object.Sensors.Set(Cam_1.speos_object)

        # Save File
        options = ExportOptions.Create()

        DocumentSave.Execute(GetActivePart().Document.Path, options)

        Sim_Cam.object.Compute()


main()
