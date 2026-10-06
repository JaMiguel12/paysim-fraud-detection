"""Chargement compact du jeu de données PaySim."""

from pathlib import Path
from typing import Sequence

import pandas as pd

COLONNES_PAYSIM = (
    "step",
    "type",
    "amount",
    "oldbalanceOrg",
    "newbalanceOrig",
    "oldbalanceDest",
    "newbalanceDest",
    "isFraud",
)

DTYPES_PAYSIM = {
    "step": "int16",
    "type": "category",
    "amount": "float32",
    "oldbalanceOrg": "float32",
    "newbalanceOrig": "float32",
    "oldbalanceDest": "float32",
    "newbalanceDest": "float32",
    "isFraud": "int8",
}


def charger_paysim(
    chemin_csv: str | Path,
    colonnes: Sequence[str] | None = None,
) -> pd.DataFrame:
    """Lit les colonnes choisies avec des types économes en mémoire."""
    colonnes_a_lire = list(colonnes) if colonnes is not None else list(COLONNES_PAYSIM)
    colonnes_inconnues = set(colonnes_a_lire) - set(COLONNES_PAYSIM)
    if colonnes_inconnues:
        raise ValueError(f"Colonnes PaySim inconnues : {sorted(colonnes_inconnues)}")

    types_a_lire = {
        colonne: dtype
        for colonne, dtype in DTYPES_PAYSIM.items()
        if colonne in colonnes_a_lire
    }
    return pd.read_csv(
        chemin_csv,
        usecols=colonnes_a_lire,
        dtype=types_a_lire,
    )
