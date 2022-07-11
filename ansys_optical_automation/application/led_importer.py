import os
import sys

appdata_path = os.getenv("AppData")
repo_path = os.path.join(appdata_path, "SpaceClaim", "Published Scripts")
sys.path.append(repo_path)

from ansys_optical_automation.scdm_process.scdm_io import ScdmIO


def selection_dialog_window():
    """
    Asks for a file selection.

    Returns
    -------
    str
        File directory selected, otherwise ``False``.
    """
    open_dialog = OpenFileDialog()
    open_dialog.Filter = "ANSYS SPEOS files (*.scdoc;*.scdocx)|*.scdoc;*scdocx|All Files (*.*)|*.*"
    open_dialog.Show()
    if open_dialog.FileName == "":
        MessageBox.Show("You did not select a file.")
        return False
    return open_dialog.FileName


def check_visual_status_dialog():
    """
    Check whether visual parts are correct for a later operation.

    Returns
    -------
    bool
        ``True`` if successful, ``False`` otherwise.
    """
    response = InputHelper.PauseAndGetInput("Only show coordinates where you would like to import LEDs.")
    if not response.Success:
        MessageBox.Show("You canceled the operation.")
        return False
    return True


def import_by_visual_status():
    """Import a part based on the visual axis systems."""
    if not check_visual_status_dialog():
        return
    led_file = selection_dialog_window()
    if not led_file:
        return
    led_importer = ScdmIO(SpaceClaim)
    for component in GetRootPart().GetAllComponents():
        component_name = component.GetName()
        axis_system_list = led_importer.get_axis_systems_under_component(component)
        if len(axis_system_list) == 0:
            continue
        led_importer.import_part_at_axis_system(led_file, axis_system_list, component_name, True, True, True, True)


def import_by_selection():
    """Import a SCDM project on the selected axis."""
    led_file = selection_dialog_window()
    if not led_file:
        return

    axis_system_selection = Selection.GetActive()
    if len(axis_system_selection.GetItems[ICoordinateSystem]()) == 0:
        while True:
            input_return = InputHelper.PauseAndGetInput("Select the axis that you want to import the part onto.")
            if not input_return.Success:
                return
            axis_system_selection = input_return.PrimarySelection
            if len(axis_system_selection.GetItems[ICoordinateSystem]()) == 0:
                MessageBox.Show("To import the part, the selection must contain at least one axis system.")
                continue
            break
    axis_system_list = axis_system_selection.GetItems[ICoordinateSystem]()
    led_importer = ScdmIO(SpaceClaim)
    led_importer.import_part_at_axis_system(led_file, axis_system_list, anchor=True, lock=True, internalize=True)


# Select one of the following methods preferred for import
# import_by_selection()
# import_by_visual_status()
