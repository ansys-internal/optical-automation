import os

from .workflows.run_test_11_brdf_viewer import unittest_run


class TestBrdfStructAPI:
    """
    Defines conditions for running unit tests in PyTest.
    """

    def setup_class(self):
        self.local_path = os.path.dirname(os.path.realpath(__file__))
        self.reference_file_speos = os.path.join(
            self.local_path, "workflows", "example_models", "test_11_brdf_viewer_reference.brdf"
        )

        self.results_file_speos = os.path.join(self.local_path, "workflows", "example_models", "export_brdfstruct.brdf")

        self.clean_results(self)  # no idea why but you have to pass there self

        print("Start BRDFStruct to generate file for tests.")
        unittest_run()

    def teardown_class(self):
        """
        Called after all tests are completed to clean the results file.

        On fail will report traceback with lines where the code failed.
        """
        self.clean_results(self)

    def clean_results(self):
        """
        Delete results file to avoid confusion.
        Returns:
        """
        if os.path.isfile(self.results_file_speos):
            os.remove(self.results_file_speos)

    def test_01_speos_brdf_generated(self):
        """
        Verify brdf content is loaded and file generated
        Returns:
        -------
        None
        """
        assert os.path.exists(self.results_file_speos)

    def test_02_verify_generated_speos_coated_file(self):
        """
        Verify brdf file is corrected generated via comparing to a reference
        Returns
        -------
        None
        """

        res_file = open(self.results_file_speos, "r")
        ref_file = open(self.reference_file_speos, "r")
        res = res_file.read()
        ref = ref_file.read()
        res_file.close()
        ref_file.close()
        assert res == ref
