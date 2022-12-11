import pandas as pd
import numpy as np

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

    @classmethod
    def get_rank(cls, df_rank, i, born_inf=False):
        if born_inf:
            df_i = df_rank.iloc[i:, :].reset_index()
        else:
            df_i = df_rank.iloc[i, :].to_frame().transpose().reset_index()
        df_i = df_i.rename(columns={"index": "Pseudo"})
        return df_i.iloc[:, [-1, 0]].to_html(index=False), df_i.iloc[:, 1:-2].to_html(index=False)

    def set_match_res(self, match_info):
        try:
            self.__res.loc[self.__res["Pseudo"] == match_info["matches"], "Verite"] = int(match_info["res"])
        except:
            self.__res.loc[self.__res["Pseudo"] == match_info["matches"], "Verite"] = str(match_info["res"])

    def create_prono_display(self):
        df_prono = self.__res.copy().merge(self.__prono.copy(), how="right", on="Pseudo")
        df_prono = df_prono.rename(columns={"Verite": "SCORE"})
        return TransformForDisplay.transform(df_prono)

    def create_res_display(self):
        df_res = self.__res.copy().rename(columns={"Verite": "SCORE"})
        return TransformForDisplay.transform(df_res)

    def compute_ranking(self):
        return TransformForComputeRanking.transform(self.__prono, self.__res)

    def load_res(self):
        Loader.load(self.__res)
