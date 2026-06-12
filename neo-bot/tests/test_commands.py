"""Tests del parser de comandos. No requieren red ni credenciales."""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from neo.commands import Kind, parse  # noqa: E402


def test_no_es_para_neo():
    assert parse("hola equipo").kind is Kind.NONE
    assert parse("").kind is Kind.NONE


def test_ayuda_y_alias():
    assert parse("!neo").kind is Kind.HELP
    assert parse("!neo ayuda").kind is Kind.HELP
    assert parse("!neo help").kind is Kind.HELP


def test_status_y_repos():
    assert parse("!neo status").kind is Kind.STATUS
    assert parse("!neo estado").kind is Kind.STATUS
    assert parse("!neo repos").kind is Kind.REPOS


def test_implement_basico():
    cmd = parse("!neo uko-vue: agregá un botón de exportar a CSV")
    assert cmd.kind is Kind.IMPLEMENT
    assert cmd.repo == "uko-vue"
    assert cmd.request == "agregá un botón de exportar a CSV"


def test_implement_con_owner_repo_y_dos_puntos_en_pedido():
    cmd = parse("!neo mi-org/api: arreglá el endpoint /login: devuelve 500")
    assert cmd.kind is Kind.IMPLEMENT
    assert cmd.repo == "mi-org/api"
    # solo se parte en el primer ':'
    assert cmd.request == "arreglá el endpoint /login: devuelve 500"


def test_teardown_formatos():
    for text in ["!neo bajar pr-12", "!neo bajar pr 12", "!neo bajar PR-12"]:
        cmd = parse(text)
        assert cmd.kind is Kind.TEARDOWN, text
        assert cmd.pr_number == 12, text
        assert cmd.repo is None


def test_teardown_con_repo():
    cmd = parse("!neo bajar pr-7 en uko-vue")
    assert cmd.kind is Kind.TEARDOWN
    assert cmd.pr_number == 7
    assert cmd.repo == "uko-vue"


def test_prefijo_case_insensitive():
    assert parse("!NEO status").kind is Kind.STATUS


def test_unknown():
    assert parse("!neo blablabla sin dos puntos").kind is Kind.UNKNOWN
    assert parse("!neo bajar algo").kind is Kind.UNKNOWN


if __name__ == "__main__":
    # Permite correr sin pytest: python tests/test_commands.py
    fns = [v for k, v in sorted(globals().items()) if k.startswith("test_") and callable(v)]
    for fn in fns:
        fn()
        print(f"ok  {fn.__name__}")
    print(f"\n{len(fns)} tests OK")
