import os


class Loader(object):

    ROOT = os.path.abspath(os.path.dirname(__file__))
    DATA_PATH = os.path.abspath(os.path.join(ROOT, "..", "data"))

    FILENAME_RES = "Resultats.csv"
    FILE_PATH_RES = os.path.abspath(os.path.join(DATA_PATH, FILENAME_RES))

    @classmethod
    def load(cls, df):
        df = df.set_index("Pseudo")
        df = df.transpose()
        df_str = df.to_csv(index=False, lineterminator="\n").encode()

        with open(cls.FILE_PATH_RES, mode='wb') as f:
            f.write(df_str)
