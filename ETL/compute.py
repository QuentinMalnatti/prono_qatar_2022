from ETL.extractor import Extractor
from ETL.transformator import TransformForDisplay, TransformForComputeRanking
from ETL.loader import Loader


class Compute(object):

    def __init__(self):
        self.__prono = None
        self.__res = None

        self.__extract_prono()
        self.__extract_res()

    def __extract_prono(self):
        self.__prono = Extractor.extract_prono()

    def __extract_res(self):
        self.__res = Extractor.extract_res()

    def get_matches(self):
        return list(self.__res["Pseudo"])

    def set_match_res(self, match_info):
        try:
            self.__res.loc[self.__res["Pseudo"] == match_info["matches"], "Verite"] = int(match_info["res"])
        except:
            self.__res.loc[self.__res["Pseudo"] == match_info["matches"], "Verite"] = str(match_info["res"])

    def create_prono_display(self):
        return TransformForDisplay.transform(self.__prono.copy())

    def create_res_display(self):
        return TransformForDisplay.transform(self.__res.copy())

    def compute_ranking(self):
        return TransformForComputeRanking.transform(self.__prono, self.__res)

    def load_res(self):
        Loader.load(self.__res)
