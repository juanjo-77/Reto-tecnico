import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "src"))
from clasif_ia import validar  # noqa: E402
from dias import dias_habiles  # noqa: E402
from enmascarar import enmascarar  # noqa: E402
from revision import evaluar_revision  # noqa: E402

FESTIVOS = {"2026-12-08", "2026-12-25"}


@pytest.mark.parametrize("ini,fin,esperado", [
    ("2026-12-14", "2026-12-18", 5),  # S01
    ("2026-12-07", "2026-12-11", 4),  # S05: 8-dic festivo
    ("2026-12-21", "2026-12-31", 8),  # S06: 25-dic festivo
])
def test_dias_habiles(ini, fin, esperado):
    assert dias_habiles(ini, fin, FESTIVOS) == esperado


def test_enmascarar_datos_personales():
    r = enmascarar("Mi cédula 1067890123, cel 3001234567, correo a.p@correo-ficticio.com")
    assert "1067890123" not in r and "3001234567" not in r and "@" not in r
    assert "[DOCUMENTO]" in r and "[CELULAR]" in r and "[CORREO]" in r


def test_revision_dias_mayores_al_saldo():
    emp = {"dias_vacaciones": 0}
    assert evaluar_revision(emp, "VACACIONES", 0.95, 8, False)
    assert not evaluar_revision({"dias_vacaciones": 12}, "VACACIONES", 0.95, 5, True)


def test_revision_empleado_inexistente_y_sin_fechas():
    assert evaluar_revision(None, "CERTIFICADO_LABORAL", 0.9, None, False)
    assert evaluar_revision({"dias_vacaciones": 3}, "VACACIONES", 0.9, None, False)


def test_json_invalido_del_modelo_se_rechaza():
    with pytest.raises(ValueError):
        validar({"categoria": "INVENTADA", "confianza": 0.9})
