"""Fonctions d'évaluation et de sélection du seuil de fraude."""

import numpy as np
from sklearn.metrics import precision_recall_curve


def choisir_seuil(
    y_vrai,
    probabilites,
    rappel_minimum: float = 0.90,
) -> float:
    """Maximise la précision parmi les seuils atteignant le rappel demandé."""
    if not 0 <= rappel_minimum <= 1:
        raise ValueError("Le rappel minimum doit être compris entre 0 et 1.")

    precisions, rappels, seuils = precision_recall_curve(y_vrai, probabilites)
    precisions = precisions[:-1]
    rappels = rappels[:-1]
    admissibles = rappels >= rappel_minimum

    if not admissibles.any():
        raise ValueError("Aucun seuil n'atteint le rappel minimum demandé.")

    indices = np.flatnonzero(admissibles)
    meilleur_indice = indices[np.argmax(precisions[indices])]
    return float(seuils[meilleur_indice])
