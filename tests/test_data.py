import pandas as pd

from fraude.data import charger_paysim


def test_charger_paysim_lit_seulement_les_colonnes_demandees(tmp_path):
    chemin_csv = tmp_path / "paysim_test.csv"
    donnees = pd.DataFrame(
        {
            "step": [1, 2],
            "type": ["TRANSFER", "PAYMENT"],
            "amount": [100.0, 25.0],
            "nameOrig": ["C1", "C2"],
            "oldbalanceOrg": [100.0, 50.0],
            "newbalanceOrig": [0.0, 25.0],
            "nameDest": ["C3", "M1"],
            "oldbalanceDest": [0.0, 0.0],
            "newbalanceDest": [100.0, 0.0],
            "isFraud": [1, 0],
            "isFlaggedFraud": [0, 0],
        }
    )
    donnees.to_csv(chemin_csv, index=False)

    resultat = charger_paysim(
        chemin_csv,
        colonnes=["step", "type", "amount", "isFraud"],
    )

    assert resultat.shape == (2, 4)
    assert resultat["step"].dtype == "int16"
    assert str(resultat["type"].dtype) == "category"
    assert resultat["amount"].dtype == "float32"
    assert resultat["isFraud"].dtype == "int8"
    assert "isFlaggedFraud" not in resultat.columns
