"""Construction des caractéristiques utilisées par les modèles."""

import pandas as pd

TYPES_TRANSACTIONS = ("TRANSFER", "CASH_OUT")
FEATURES = (
    "heure",
    "amount",
    "oldbalanceOrg",
    "oldbalanceDest",
    "type_transfer",
)


def construire_variables(df: pd.DataFrame) -> pd.DataFrame:
    """Filtre le périmètre étudié et crée les variables pré-transaction."""
    df_modele = df.loc[df["type"].isin(TYPES_TRANSACTIONS)].copy()
    df_modele["heure"] = ((df_modele["step"] - 1) % 24).astype("int8")
    df_modele["type_transfer"] = (
        df_modele["type"] == "TRANSFER"
    ).astype("int8")
    return df_modele


def preparer_xy(df_modele: pd.DataFrame) -> tuple[pd.DataFrame, pd.Series]:
    """Sépare les caractéristiques X de la cible isFraud dans y."""
    return df_modele[list(FEATURES)].copy(), df_modele["isFraud"].copy()
