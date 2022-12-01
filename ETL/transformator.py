import pandas as pd
import numpy as np


class TransformForDisplay(object):

    @staticmethod
    def __groupby_func(x):
        res_match = list()
        for col in x.columns:
            res_match.append(' - '.join(map(str, list(x[col]))))

        return pd.Series(res_match, index=x.columns)

    @classmethod
    def transform(cls, df):
        df["Pseudo"] = df["Pseudo"].str.split('[', expand=True)[0]
        df = df.groupby("Pseudo")[list(df.columns)[1:]].apply(cls.__groupby_func).reset_index()
        return df.to_html(index=False)


class TransformForComputeRanking(object):

    @classmethod
    def transform(cls, df_prono, df_res):
        df_ranking = cls.__add_res(df_prono, df_res)
        df_ranking = cls.__compute_score(df_ranking)
        return df_ranking.to_html()

    @staticmethod
    def __add_res(df_prono, df_res):
        df = df_prono.merge(df_res, how="left", on="Pseudo")
        return df.set_index("Pseudo")

    @staticmethod
    def __compute_score(df_ranking):
        df_score = pd.DataFrame(columns=["Ecart_score", "score_exact", "resultat_correct", "nombre_buts_corrects", "ratio_reussite"], index=df_ranking.drop(columns=["Verite"]).columns)

        for col in df_ranking.columns:
            if col != "Verite":
                reponse = (df_ranking[col].replace("", np.nan).dropna()).index
                passe = (df_ranking["Verite"].dropna()).index
                idx_to_consider = passe.intersection(reponse)

                ligne_paire = [2 * k for k in range(int(len(idx_to_consider) / 2))]
                ligne_impaire = [x + 1 for x in ligne_paire]

                df_score.loc[col, "nombre_buts_corrects"] = sum(df_ranking.loc[idx_to_consider, col].astype(int) == df_ranking.loc[idx_to_consider, "Verite"])
                pred = (df_ranking.loc[idx_to_consider, col].astype(int) - df_ranking.loc[idx_to_consider, col].astype(int).shift(1)).iloc[ligne_impaire]

                truth = (df_ranking.loc[idx_to_consider, "Verite"].astype(int) - df_ranking.loc[idx_to_consider, "Verite"].astype(int).shift(1)).iloc[ligne_impaire]
                df_score.loc[col, "Ecart_score"] = sum(pred == truth)

                df_score.loc[col, "resultat_correct"] = sum(pred * truth > 0) + sum((truth == 0) & (pred == 0))

                df_score.loc[col, "score_exact"] = sum((df_ranking.loc[idx_to_consider, col].astype(int).iloc[ligne_paire] == df_ranking.loc[idx_to_consider, "Verite"].iloc[ligne_paire]).reset_index(drop=True) &
                                                       (df_ranking.loc[idx_to_consider, col].astype(int).iloc[ligne_impaire] == df_ranking.loc[idx_to_consider, "Verite"].iloc[ligne_impaire]).reset_index(drop=True))

                df_score.loc[col, "ratio_reussite"] = df_score.loc[col, "resultat_correct"] / (len(idx_to_consider) / 2)
                df_score.loc[col, "score"] = df_score.loc[col, "resultat_correct"] * 3 + df_score.loc[col, "Ecart_score"] + df_score.loc[col, "score_exact"] + df_score.loc[col, "nombre_buts_corrects"] * 0.5
                df_score.loc[col, "score_normalise"] = df_score.loc[col, "score"] / (len(idx_to_consider) / 2)
        df_score["rang"] = df_score.score_normalise.sort_values(ascending=False).rank(ascending=False)
        return df_score.sort_values(by="rang", ascending=True)
