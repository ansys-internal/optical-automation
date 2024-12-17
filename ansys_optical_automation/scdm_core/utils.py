import math
import os
import subprocess

import numpy as np

import os

import os


def find_awp_root(version=""):
    """
    Finds the AWP_ROOT path based on the given version.

    This function searches the environmental variables for keys containing "AWP_ROOT".
    If a specific version is provided, it returns the path for that version.
    If no version is provided (i.e., an empty string is passed), it returns the path for the latest version.

    Parameters
    ----------
    version : str, optional
        The version of AWP_ROOT to search for. If an empty string is passed,
        the path for the latest version is returned. Default is an empty string.

    Returns
    -------
    str
        The path to the specified AWP_ROOT version if `version` is provided.
        If no `version` is specified, it returns the path to the latest AWP_ROOT version.

    Raises
    ------
    ValueError
        If the specified `version` does not exist or if no AWP_ROOT path is found in the environment variables.

    Notes
    -----
    The function compares the version numbers by splitting the keys containing "AWP_ROOT"
    and checking the version number after "AWP_ROOT".
    """
    try:
        if version:
            # If version is specified, return the path for that version
            awp_root_path = os.environ.get(f"AWP_ROOT{version}", "")
            if not awp_root_path:
                raise ValueError(f"AWP_ROOT path for version {version} not found in the environment variables.")
        else:
            # If no version is specified, find the latest version
            last_version = "000"
            for key in os.environ:
                if "AWP_ROOT" in key and key.split("AWP_ROOT")[1] > last_version:
                    last_version = key.split("AWP_ROOT")[1]

            awp_root_path = os.environ.get(f"AWP_ROOT{last_version}", "")
            if not awp_root_path:
                raise ValueError("AWP_ROOT path for the latest version not found in the environment variables.")

        return awp_root_path

    except Exception as e:
        raise ValueError(f"An error occurred while finding the AWP_ROOT path: {str(e)}")


print(find_awp_root("242"))
def get_scdm_install_location(version=""):
    """
    Get the SpaceClaim installation path.

    This function retrieves the installation path for SpaceClaim based on the provided version.
    It calls the `find_awp_root` function to obtain the AWP_ROOT path for the given version,
    and then appends the "scdm" directory to determine the SpaceClaim installation path.

    Parameters
    ----------
    version : str, optional
        Version of SpaceClaim in numerical format. For example, ``211`` for 2021 R1.
        If an empty string is passed, the function will use the latest version found.

    Returns
    -------
    str
        Path of the SpaceClaim installation.

    Raises
    ------
    ValueError
        If the AWP_ROOT path for the specified or latest version cannot be found,
        or if there is an issue with accessing the environment variables.

    Notes
    -----
    The `find_awp_root` function is used to retrieve the AWP_ROOT path, and the "scdm" directory
    is appended to this path to return the full path to the SpaceClaim installation.
    """
    try:
        ansys_install_dir = find_awp_root(version=version)
        scdm_install_dir = os.path.join(ansys_install_dir, "scdm")
        return scdm_install_dir
    except ValueError as e:
        raise ValueError(f"Error while getting the SpaceClaim installation path: {str(e)}")

print("####",get_scdm_install_location("242"))

def get_speos_core(version):
    """
    get speos core path for version
    Parameters
    ----------
    version : str
        Ansys Version used

    Returns
    -------
    str
        path to speos core executable

    """
    ansys_install_dir = os.environ["AWP_ROOT{}".format(version)]
    speos_core_dir = os.path.join(ansys_install_dir, r"Optical Products", r"Viewers", r"SPEOSCore.exe")
    return speos_core_dir


def run_scdm_batch(scdm_version, api_version, script_file):
    """
    Start a Speos script in batch mode via the ``subprocess.call`` method.

    Parameters
    ----------
    scdm_version : int
        SpaceClaim version.
    api_version : int
        SpaceClaim API version.
    script_file : str
        Full path to the script file.
    """
    scdm_install_dir = get_scdm_install_location(scdm_version)
    scdm_exe = os.path.join(scdm_install_dir, "SpaceClaim.exe")
    speos_path = os.path.join(
        os.path.dirname(scdm_install_dir), "Optical Products", "Speos", "Bin", "SpeosSC.Manifest.xml"
    )
    command = [
        scdm_exe,
        r"/AddInManifestFile={}".format(speos_path),
        r"/RunScript={}".format(script_file),
        r"/Headless=True",
        r"/Splash=False",
        r"/Welcome=False",
        r"/ExitAfterScript=True",
        r"/ScriptAPI={}".format(api_version),
    ]
    subprocess.call(command)


def vector_len(vector):
    """
    compute vector length
    Parameters
    ----------
    vector : list
        [x,y,z]

    Returns
    -------
    float
        length of a vector

    """
    return math.sqrt(vector[0] ** 2 + vector[1] ** 2 + vector[2] ** 2)


def vector_normalize(vector):
    """
    get normalized vector.

    Parameters
    ----------
    vector : list
        [x,y,z]

    Returns
    -------
    list
        list representing normalized vector

    """
    vector_magnitude = vector_len(vector)
    return [item / vector_magnitude for item in vector]


def vector_dot_product(vector1, vector2):
    """
    function to multiply to vectors
    Parameters
    ----------
    vector1 : list
        [x,y,z]
    vector2 : list
        [x,y,z]
    Returns
    -------
    float
    """
    return vector1[0] * vector2[0] + vector1[1] * vector2[1] + vector1[2] * vector2[2]


def degree(rad):
    """
    function to convert unit radian to degree.

    Parameters
    ----------
    rad : float

    Returns
    -------
    float

    """
    return np.rad2deg(rad)


def radiance(deg):
    """
    function to convert unit degree to radian.

    Parameters
    ----------
    deg : float

    Returns
    -------
    float

    """
    return np.deg2rad(deg)
