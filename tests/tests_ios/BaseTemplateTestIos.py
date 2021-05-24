import unittest
import pathlib
import yaml
from tests import BaseTemplateTest
from netcm.models.BaseModels import BaseNetCmModel

class BaseTemplateTestIos(BaseTemplateTest):

    VENDOR = 'ios'
    TEMPLATE_NAME = ''
    RESOURCE_DIR = pathlib.Path(__file__).resolve().parent.parent.joinpath("resources").joinpath(VENDOR)
    ENVIRONMENT = BaseTemplateTest.get_vendor_environment(vendor=VENDOR)

    def common_testbase(self, test_cases: list):

        template = self.ENVIRONMENT.get_template(name=f"{self.TEMPLATE_NAME}.j2")

        for test_case in test_cases:
            with self.subTest(msg=test_case["test_name"]):
                want = test_case["result"]

                dict_params = None
                if "dict_params" in test_case.keys():
                    dict_params = dict_params

                if isinstance(test_case["data"], BaseNetCmModel):
                    if dict_params:
                        test_case["data"] = test_case["data"].dict(**dict_params)
                    else:
                        test_case["data"] = test_case["data"].dict()
                elif isinstance(test_case["data"], dict):
                    for k in test_case["data"].keys():
                        if isinstance(test_case["data"][k], BaseNetCmModel):
                            if dict_params:
                                test_case["data"][k] = test_case["data"][k].dict(**dict_params)
                            else:
                                test_case["data"][k] = test_case["data"][k].dict()

                have = template.render(**test_case["data"])
                print(f"! Template: {self.TEMPLATE_NAME}\tTest: {test_case['test_name']}\n<< BEGIN >>\n{have}<< END >>")

                self.assertEqual(want, have)

    def get_test_cases_from_resources(self):
        test_cases = []
        data_files = [x for x in self.RESOURCE_DIR.joinpath("data").iterdir() if x.is_file and x.suffix == ".yml" and x.stem.split("-")[0].startswith(self.TEMPLATE_NAME)]
        results_files = [x for x in self.RESOURCE_DIR.joinpath("results").iterdir() if x.is_file and x.suffix == ".txt" and x.stem.split("-")[0].startswith(self.TEMPLATE_NAME)]
        data_file_names = [x.stem for x in data_files]
        results_file_names = [x.stem for x in results_files]
        assert set(data_file_names) == set(results_file_names)

        test_cases = [{"test_name": x, "data": None, "result": None} for x in data_file_names]



        for test_case in test_cases:
            test_case["data"] = yaml.safe_load([x for x in data_files if x.stem == test_case["test_name"]][0].read_text())
            test_case["result"] = [x for x in results_files if x.stem == test_case["test_name"]][0].read_text()
        print(test_cases)
        return test_cases

