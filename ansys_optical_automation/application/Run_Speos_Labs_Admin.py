"""
Requirements: administrative privileges.
-----------------------------------------------------------------------
This module launches with administrator privileges all executables in:
`C:\\Program Files\\ANSYS Inc\\vXXX\\Optical Products\\Viewers`

Many users lack administrative rights, so this module can be executed right after the installation
while the user still has admin rights.

Upon launching each application, the module registers the associated COM server used to call each application, 
with the path to each executable appropriately registered.

Class
-----------------------------------------------------------------------
2. **LabsAdmin**
   - This class offers methods to open or close one or multiple applications simultaneously.
   - By default, if no specific applications are specified, it will launch all applications found.

"""

import subprocess, os, time, sys
# Get the absolute path to the scdm_core directory
current_dir = os.path.dirname(os.path.abspath(__file__))
scdm_core_path = os.path.join(current_dir, '..', 'scdm_core')
# Add the scdm_core path to sys.path if it's not already there
if scdm_core_path not in sys.path:
    sys.path.append(scdm_core_path)
# Try importing the function from utils
try:
    from utils import find_awp_root
    print("get_scdm_install_location imported.")
except ModuleNotFoundError as e:
    print(f"Error: {e}")
    print(f"sys.path: {sys.path}")

# If pygetwindow is not installed, do it
third_party_package = "pygetwindow"
try: 
    gw =  __import__(third_party_package)
    print(f"{third_party_package} is already installed.")
except ImportError:
    print(f"{third_party_package} not found. Installing...")
    subprocess.check_call([sys.executable, "-m", "pip", "install", third_party_package])
    import pygetwindow as gw


import numpy as np

class LabsAdmin:
    '''
    Class with methods to:
    - Run one specific application.
    - Kill one specific application.
    - Run all applications as admin.
    - Kill all applications.
    - Run and Kill one application.
    - Run and Kill all applications.
    '''

    def __init__(self, ThreeDigitCode=""):
        """
        Initializes the LabsAdmin class with a given ThreeDigitCode or derives it from the installation path.

        Parameters
        ----------
        ThreeDigitCode : str, optional
            A 3-digit version code (default is an empty string, which causes the code to be derived from the installation path).
        Path_Installation_Root: str
            Path to Ansys installation, format C:\Program Files\ANSYS Inc\v242.
            Uses find_awp_root, imported from utils. If no ThreeDigitCode is given as input, the function will return
            the latest installed Ansys installation path.
        """
        if not ThreeDigitCode:
            self.Path_Installation_Root = find_awp_root(version="")
            version_part = self.Path_Installation_Root.split("\\")[-1]
            self.ThreeDigitCode = version_part[1:]
        else:
            self.ThreeDigitCode = ThreeDigitCode
            self.Path_Installation_Root = find_awp_root(version=self.ThreeDigitCode)

        if not self.Path_Installation_Root:
            raise ValueError(f"AWP_ROOT path for version {self.ThreeDigitCode} not found.")

    def RunSingleApp(self, exe_name):
        """
        Runs a single application as an administrator.

        Parameters
        ----------
        exe_name : str
            The name of the executable to run.
        """
        exe_path = os.path.join(self.Path_Installation_Root, 'Optical Products', 'Viewers', exe_name)
        print("Application Executed: " + exe_path)
        subprocess.Popen(["powershell", "-Command", f"Start-Process '{exe_path}' -Verb RunAs"])

    def RunAll(self):
        """
        Runs all applications as administrators.
        """
        print("\n\n#### Run all Viewer as admin STARTED: \n")
        Dictionary_Labs = self.Applications()
        for App in Dictionary_Labs.keys():
            self.RunSingleApp(App)

    def Applications(self):
        """
        Returns a dictionary of applications with the names of the applications to run as key, and the title visible
        for each application after running the viewer without input files, as items.

        Returns
        -------
        dict
            A dictionary where the keys are executable names and the values are titles.
        """
        if len(self.ThreeDigitCode) != 3:
            raise ValueError("\n\nThe code must be of 3 characters long to derive the version.")
        self.Version = "20" + self.ThreeDigitCode[0] + self.ThreeDigitCode[1] + " R" + self.ThreeDigitCode[2]
        self.Labs_Applications = {
            "XmpViewer.exe": "Speos " + self.Version + " - Extended map [No Name]",
            "VRLab.exe": "Speos " + self.Version + " - Empty view",
            "Xm3Viewer.exe": "Speos " + self.Version + " - Virtual 3D Photometric Lab [No file loaded]",
            "VisionLabViewer.exe": "Speos " + self.Version + " - Spectral map [No Name]",
            "TextureMappingViewer.exe": "Texture Mapping Viewer",
            "VMPViewer.exe": "Speos " + self.Version + " - 3D Energy Density Lab [No Name]",
            "SimpleScatteringViewer.exe": "Speos " + self.Version + " - Scattering surface [No Name]",
            "VPLab.exe": "Speos " + self.Version + " - Photometric Calc",
            "SPEOSCore.exe": "Speos Core " + self.Version,
            "SpectrumViewer.exe": "Speos " + self.Version + " - Spectrum [No Name]",
            "RoughMirrorViewer.exe": "Speos " + self.Version + " - Mirror surface [No Name]",
            "FluorescentSurfaceViewer.exe": "Speos " + self.Version + " - Fluorescent surface [No Name]",
            "BSDF_BRDF_Anisotropic_Viewer.exe": "Speos " + self.Version + " - Bsdf surface [No Name]",
            "PolarizerSurfaceEditor.exe": "Speos " + self.Version + " - Polarizer surface [No Name]",
            "RetroReflectingSurfaceViewer.exe": "Speos " + self.Version + " - Retro-reflecting surface [No Name]",
            "IESViewer.exe": "Speos " + self.Version + " - Iesna LM-63 []",
            "CoatedSurfaceViewer.exe": "Speos " + self.Version + " - Coated surface [No Name]",
            "EulumdatViewer.exe": "Speos " + self.Version + " - Eulumdat [No Name]",
            "VirtualLightingAnimation.exe": "Virtual Lighting Animation [BETA] " + self.Version,
            "AdvancedScatteringViewer.exe": "Speos " + self.Version + " - Scattering surface (Advanced model) [No Name]",
            "DoeSurfaceViewer.exe": "Speos " + self.Version + " - Thin lens surface [No Name]",
            "GratingSurfaceViewer.exe": "Speos " + self.Version + " - Grating surface [No Name]",
            "RayEditor.exe": "Speos " + self.Version + " -  [No Name]",
            "UserMaterialViewer.exe": "Speos " + self.Version + " - User Material (Advanced Model) [No Name]"
        }
        return self.Labs_Applications

    def KillApp(self, exe_name):
        """
        Kills a specific running application.

        Parameters
        ----------
        exe_name : str
            The name of the executable to kill.
        """
        Dictionary_Labs = self.Applications()
        open_windows = gw.getAllTitles()
        app_opened = False
        Expected_title = Dictionary_Labs[exe_name]
        while not app_opened:
            open_windows = gw.getAllTitles()
            for title in open_windows:
                if Expected_title in title:
                    app_opened = True
                    print("Trying to find: " + exe_name)
                    subprocess.run(["taskkill", "/f", "/im", exe_name])
                    break
            time.sleep(0.2)

    def KillAll(self):
        """
        Kills all running applications.
        """
        Dictionary_Labs = self.Applications()
        print("\n\n#### Kill all process: \n")
        for App in Dictionary_Labs.keys():
            self.KillApp(App)

    def RunAndKillApp(self, exe_name):
        """
        Runs and then kills a specific application.

        Parameters
        ----------
        exe_name : str
            The name of the executable to run and kill.
        """
        self.RunSingleApp(exe_name)
        self.KillApp(exe_name)

    def RunAndKillAll(self):
        """
        Runs all applications and then kills all of them.
        """
        self.RunAll()
        self.KillAll()

# Example usage of LabsAdmin with the new integration
try:
    LabsAdmin("242").RunAndKillAll()
except Exception as err:
    print("Unexpected error: "+str(err)+", "+str(type(err)))