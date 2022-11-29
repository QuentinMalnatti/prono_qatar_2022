import os
import pandas as pd


class Extractor(object):

    ROOT = os.path.abspath(os.path.dirname(__file__))
    DATA_PATH = os.path.abspath(os.path.join(ROOT, "..", "data"))

    FILENAME_PRONO = "Pronostics.csv"
    FILE_PATH_PRONO = os.path.abspath(os.path.join(DATA_PATH, FILENAME_PRONO))

    FILENAME_RES = "Resultats.csv"
    FILE_PATH_RES = os.path.abspath(os.path.join(DATA_PATH, FILENAME_RES))

    @classmethod
    def extract_prono(cls):
        df = pd.read_csv(cls.FILE_PATH_PRONO)
        df = df.drop(columns=["Horodateur"])
        df = df.transpose().reset_index()
        df.columns = df.iloc[0]
        df = df.iloc[1:, :]

        for col in df.columns:
            if col != "Pseudo":
                df[col] = df[col].astype('Int64')

        return df

    @classmethod
    def extract_res(cls):
        df = pd.read_csv(cls.FILE_PATH_RES, dtype='Int64')
        df = df.transpose().reset_index()
        df.columns = ["Pseudo", "Verite"]
        return df
