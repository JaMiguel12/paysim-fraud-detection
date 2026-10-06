import pandas as pd
import pytest

from fraude.evaluation import choisir_seuil
from fraude.features import FEATURES, construire_variables, preparer_xy


def test_construire_variables_filtre_et_cree_les_colonnes():
    donnees = pd.DataFrame(
        {
            "step": [1, 2, 25],
            "type": ["TRANSFER", "PAYMENT", "CASH_OUT"],
            "amount": [100.0, 20.0, 50.0],
            "oldbalanceOrg": [100.0, 40.0, 50.0],
            "newbalanceOrig": [0.0, 20.0, 0.0],
            "oldbalanceDest": [0.0, 0.0, 10.0],
            "newbalanceDest": [100.0, 0.0, 60.0],
            "isFraud": [1, 0, 1],
        }
    )

    resultat = construire_variables(donnees)
    X, y = preparer_xy(resultat)

    assert len(resultat) == 2
    assert resultat["heure"].tolist() == [0, 0]
    assert resultat["type_transfer"].tolist() == [1, 0]
    assert tuple(X.columns) == FEATURES
    assert "isFraud" not in X.columns
    assert y.tolist() == [1, 1]


def test_choisir_seuil_respecte_le_rappel_minimum():
    vrais = [0, 0, 0, 1, 1]
    probabilites = [0.1, 0.2, 0.3, 0.8, 0.9]

    seuil = choisir_seuil(vrais, probabilites, rappel_minimum=1.0)

    assert seuil == pytest.approx(0.8)


def test_choisir_seuil_refuse_un_rappel_hors_intervalle():
    with pytest.raises(ValueError, match="compris entre 0 et 1"):
        choisir_seuil([0, 1], [0.1, 0.9], rappel_minimum=1.1)
