import pandas as pd
import numpy as np
import re


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
        df["sort_col"] = df["Pseudo"].str.extract(r"^.* ([a-zA-Z\u00C0-\u00FF\-]* - [a-zA-Z\u00C0-\u00FF\-]*)")
        df = df.sort_values(by="sort_col", ascending=True).drop(columns=["sort_col"])
        return df.to_html(index=False)


class TransformForComputeRanking(object):

    @classmethod
    def transform(cls, df_prono, df_res):
        df_ranking = cls.__add_res(df_prono, df_res)
        df_ranking = cls.__compute_score(df_ranking)
        return df_ranking

    @staticmethod
    def __add_res(df_prono, df_res):
        df = df_prono.merge(df_res, how="left", on="Pseudo")
        return df.set_index("Pseudo")

    @staticmethod
    def __compute_score(df_ranking):
        df_score = pd.DataFrame(columns=["Ecart_score", "score_exact", "resultat_correct", "nombre_buts_corrects", "ratio_reussite", "point_par_match", "qualif_correcte", "score"], index=df_ranking.drop(columns=["Verite"]).columns)

        for col in df_ranking.columns:
            if col != "Verite":
                score_matchs = [col for col in df_ranking.index if "Score" in col]
                df_results_matchs = df_ranking.loc[score_matchs]
                reponse = (df_results_matchs[col].replace("", np.nan).dropna()).index
                passe = (df_results_matchs["Verite"].dropna()).index
                idx_to_consider = passe.intersection(reponse)

                ligne_paire = [2 * k for k in range(int(len(idx_to_consider) / 2))]
                ligne_impaire = [x + 1 for x in ligne_paire]

                df_score.loc[col, "nombre_buts_corrects"] = sum(df_results_matchs.loc[idx_to_consider, col].astype(int) == df_results_matchs.loc[idx_to_consider, "Verite"])
                pred = (df_results_matchs.loc[idx_to_consider, col].astype(int) - df_results_matchs.loc[idx_to_consider, col].astype(int).shift(1)).iloc[ligne_impaire]

                truth = (df_results_matchs.loc[idx_to_consider, "Verite"].astype(int) - df_results_matchs.loc[idx_to_consider, "Verite"].astype(int).shift(1)).iloc[ligne_impaire]
                df_score.loc[col, "Ecart_score"] = sum(pred == truth)
                df_score.loc[col, "nb_matchs"] = len(idx_to_consider)/2

                df_score.loc[col, "resultat_correct"] = sum(pred * truth > 0) + sum((truth == 0) & (pred == 0))

                df_score.loc[col, "score_exact"] = sum((df_results_matchs.loc[idx_to_consider, col].astype(int).iloc[ligne_paire] == df_results_matchs.loc[idx_to_consider, "Verite"].iloc[ligne_paire]).reset_index(drop=True) &
                                                       (df_results_matchs.loc[idx_to_consider, col].astype(int).iloc[ligne_impaire] == df_results_matchs.loc[idx_to_consider, "Verite"].iloc[ligne_impaire]).reset_index(drop=True))

                df_score.loc[col, "ratio_reussite"] = df_score.loc[col, "resultat_correct"] / (len(idx_to_consider) / 2)

                qualif_matchs = [col for col in df_ranking.index if "Score" not in col]
                df_qualif = df_ranking.loc[qualif_matchs]
                df_score.loc[col, "qualif_correcte"] = sum(df_qualif.index.map(lambda x: re.split(" match | - ", x)[int(df_ranking.fillna(0).loc[x, "Verite"])]) == df_qualif[col])/len(df_qualif[col].dropna())

                df_score.loc[col, "score"] = df_score.loc[col, "resultat_correct"] * 3 + df_score.loc[col, "Ecart_score"] + df_score.loc[col, "score_exact"] + df_score.loc[col, "nombre_buts_corrects"] * 0.5
                df_score.loc[col, "point_par_match"] = df_score.loc[col, "score"] / (len(idx_to_consider) / 2)
                df_score.loc[col, "score"] = df_score.loc[col, "point_par_match"] + df_score.loc[col, "qualif_correcte"]
        df_score["rang"] = df_score.score.sort_values(ascending=False).rank(ascending=False)
        return df_score.sort_values(by="rang", ascending=True)
