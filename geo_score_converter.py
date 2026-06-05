from pathlib import Path

import geopandas as gpd
import numpy as np
import pandas as pd


class GeoIntervalScorer:
    """
    Convierte columnas de un GeoDataFrame a puntajes AHP (0-5) usando
    intervalos.csv y los tipos definidos en codigo_tipos(in).csv.

    La lógica categórica replica EDA.ipynb: por cada intervalo 0..5 se
    lee df_scores.loc[code].values[interval], se hace split(';') y se
    arma un diccionario label -> intervalo para Series.replace(dic).
    """

    def __init__(
        self,
        intervalos_path: str | Path = "intervalos.csv",
        tipos_path: str | Path = "codigo_tipos(in).csv",
        encoding: str = "latin-1",
    ):
        self.df_scores = pd.read_csv(intervalos_path, sep=",", index_col=0)
        self.df_scores.index = self.df_scores.index.astype(str).str.strip()

        tipos = pd.read_csv(tipos_path, sep=";", encoding=encoding)
        tipos.columns = tipos.columns.str.strip()
        tipos["Codigo"] = tipos["Codigo"].astype(str).str.strip()
        tipos["Tipo"] = tipos["Tipo"].astype(str).str.strip().str.lower()
        self.tipos = tipos.drop_duplicates(subset="Codigo", keep="first").set_index("Codigo")

    def transform(
        self,
        gdf: gpd.GeoDataFrame,
        columns: list[str] | None = None,
        inplace: bool = False,
    ) -> gpd.GeoDataFrame:
        result = gdf if inplace else gdf.copy()
        target_cols = columns or [
            c for c in result.columns if c in self.tipos.index and c != "geometry"
        ]

        for codigo in target_cols:
            if codigo not in result.columns:
                continue
            tipo = self.tipos.loc[codigo, "Tipo"]
            result[codigo] = self._score_series(result[codigo], codigo, tipo)

        return result

    def build_label_dict(self, code: str) -> dict[str, int]:
        """
        Misma construcción que en EDA.ipynb para variables categóricas.
        """
        if code not in self.df_scores.index:
            return {}

        dic: dict[str, int] = {}
        for interval in range(0, 6):
            cell = self.df_scores.loc[code].values[interval]
            if pd.isna(cell):
                continue
            for word in str(cell).split(";"):
                dic[word] = interval
        return dic

    def _score_series(self, series: pd.Series, codigo: str, tipo: str) -> pd.Series:
        in_intervalos = codigo in self.df_scores.index

        if tipo == "categorica": 
            if not in_intervalos:
                return series
            return series.replace(self.build_label_dict(codigo))

        if tipo == "continua":
            if not in_intervalos:
                return series
            return self._score_continuous(series, codigo)

        if tipo == "binario":
            return self._score_binary(series)

        if tipo == "excluyente":
            return self._score_excluyente(series)

        return series

    def _score_continuous(self, series: pd.Series, code: str) -> pd.Series:
        ranges: list[tuple[int, float, float]] = []
        for interval in range(0, 6):
            cell = self.df_scores.loc[code].values[interval]
            if pd.isna(cell) or str(cell).strip() == "":
                continue
            parts = str(cell).split(";")
            if len(parts) != 2:
                continue
            try:
                a = float(parts[0])
                b = float(parts[1])
            except ValueError:
                continue
            low, high = min(a, b), max(a, b)
            ranges.append((interval, low, high))

        numeric = pd.to_numeric(series, errors="coerce")

        def value_to_score(value):
            if pd.isna(value):
                return np.nan
            for interval, low, high in ranges:
                if low <= value <= high:
                    return interval
            return np.nan

        return numeric.map(value_to_score)

    @staticmethod
    def _score_binary(series: pd.Series) -> pd.Series:
        numeric = pd.to_numeric(series, errors="coerce")
        scored = numeric.copy()
        scored[numeric == 0] = 0
        scored[numeric == 1] = 5
        return scored

    @staticmethod
    def _score_excluyente(series: pd.Series) -> pd.Series:
        numeric = pd.to_numeric(series, errors="coerce")
        scored = numeric.copy()
        scored[numeric == 1] = np.nan
        scored[numeric == 0] = 0
        return scored

    def _uses_label_dict(self, code: str) -> bool:
        for interval in range(0, 6):
            cell = self.df_scores.loc[code].values[interval]
            if pd.isna(cell) or str(cell).strip() == "":
                continue
            parts = str(cell).split(";")
            if len(parts) == 2:
                try:
                    float(parts[0])
                    float(parts[1])
                    continue
                except ValueError:
                    pass
            return True
        return False
