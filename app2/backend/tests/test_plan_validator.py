from copy import deepcopy

import pytest


@pytest.fixture
def three_books():
    selection = {"objeto": "diamond_sword", "encantamientos": [
        {"nombre": "sharpness", "nivel": 5}, {"nombre": "mending", "nivel": 1}, {"nombre": "unbreaking", "nivel": 3},
    ]}
    result = {"resultado": {"pasos": [
        {"orden": 1, "izquierda": "objeto", "derecha": "libro_1", "coste_niveles": 5},
        {"orden": 2, "izquierda": "paso_1", "derecha": "libro_2", "coste_niveles": 3},
        {"orden": 3, "izquierda": "paso_2", "derecha": "libro_3", "coste_niveles": 6},
    ], "coste_total_niveles": 14, "advertencias": []}}
    return selection, result


@pytest.mark.parametrize("case", [
    "empty", "missing", "short", "reused", "invented", "future", "same", "object_right",
    "negative", "decimal", "boolean", "sum", "order", "extra", "wrong_type", "warning_type",
])
def test_invalid_proposal_is_rejected_completely(api_client, token_factory, ai_mock, three_books, case):
    selection, original = three_books
    result = deepcopy(original)
    steps = result["resultado"]["pasos"]
    if case == "empty": result = None
    elif case == "missing": result = {}
    elif case == "short": steps.pop()
    elif case == "reused": steps[1]["izquierda"] = "objeto"
    elif case == "invented": steps[0]["derecha"] = "libro_4"
    elif case == "future": steps[0]["derecha"] = "paso_3"
    elif case == "same": steps[0]["derecha"] = "objeto"
    elif case == "object_right": steps[0].update(izquierda="libro_1", derecha="objeto")
    elif case == "negative": steps[0]["coste_niveles"] = -1
    elif case == "decimal": steps[0]["coste_niveles"] = 1.5
    elif case == "boolean": steps[0]["coste_niveles"] = True
    elif case == "sum": result["resultado"]["coste_total_niveles"] = 99
    elif case == "order": steps[1]["orden"] = 7
    elif case == "extra": steps[0]["extra"] = "dato inventado"
    elif case == "wrong_type": result["resultado"]["coste_total_niveles"] = "14"
    elif case == "warning_type": result["resultado"]["advertencias"] = "no es una lista"
    ai_mock.return_value = result
    response = api_client.post("/api/procesar", json=selection, headers={"Authorization": f"Bearer {token_factory()}"})
    assert response.status_code == 502
    assert response.json()["error"]["codigo"] == "RESPUESTA_INVALIDA"
    assert "resultado" not in response.json()
    ai_mock.assert_awaited_once()
