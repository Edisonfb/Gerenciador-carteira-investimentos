"""Roda os testes da Sprint 1 e 2 (backend e frontend) e gera o relatorio.

Uso, na raiz do projeto:
    backend\\.venv\\Scripts\\python.exe tests\\rodar_testes.py

Gera tests/relatorios/relatorio_testes.txt com cada teste marcado como
PASSOU ou FALHOU, e mostra o resumo no terminal.
"""

import subprocess
import sys
import xml.etree.ElementTree as ET
from datetime import datetime
from pathlib import Path

RAIZ = Path(__file__).resolve().parent.parent
PASTA = RAIZ / "tests" / "relatorios"
XML_BACKEND = PASTA / "backend.xml"
XML_FRONTEND = PASTA / "frontend.xml"
RELATORIO = PASTA / "relatorio_testes.txt"


def rodar_backend():
    print("== Backend (pytest + httpx + pytest-asyncio) ==")
    subprocess.run([
        sys.executable, "-m", "pytest", "tests/backend/sprint1", "tests/backend/sprint2",
        "-q", "-p", "no:cacheprovider", f"--junitxml={XML_BACKEND}",
    ], cwd=RAIZ)


def rodar_frontend():
    print("\n== Frontend (vitest) ==")
    subprocess.run(
        "npx vitest run sprint --reporter=default --reporter=junit "
        f'--outputFile.junit="{XML_FRONTEND}"',
        cwd=RAIZ / "frontend", shell=True,
    )


def ler_resultados(arquivo, camada):
    """Le o XML no formato JUnit e devolve uma linha por teste."""
    if not arquivo.exists():
        return [{"camada": camada, "sprint": "-", "arquivo": "-", "teste": "Os testes não rodaram",
                 "situacao": "FALHOU", "detalhe": f"{arquivo.name} não foi gerado"}]
    resultados = []
    for caso in ET.parse(arquivo).iter("testcase"):
        origem = caso.get("classname", "")
        problema = caso.find("failure") if caso.find("failure") is not None else caso.find("error")
        if caso.find("skipped") is not None:
            situacao = "PULADO"
        elif problema is not None:
            situacao = "FALHOU"
        else:
            situacao = "PASSOU"
        resultados.append({
            "camada": camada,
            "sprint": "Sprint 1" if "sprint1" in origem else "Sprint 2" if "sprint2" in origem else "-",
            "arquivo": origem.replace("\\", "/").split("/")[-1].split(".")[-1 if camada == "Backend" else 0],
            "teste": caso.get("name", ""),
            "situacao": situacao,
            "detalhe": (problema.get("message") or problema.text or "") if problema is not None else "",
        })
    return resultados


def gerar_texto(resultados):
    passou = sum(r["situacao"] == "PASSOU" for r in resultados)
    falhou = sum(r["situacao"] == "FALHOU" for r in resultados)
    linhas = [
        "RELATORIO DE TESTES - SPRINT 1 E SPRINT 2",
        f"Gerado em {datetime.now():%d/%m/%Y %H:%M}",
        f"Total: {len(resultados)} | Passaram: {passou} | Falharam: {falhou}",
    ]
    grupo_atual = None
    for r in sorted(resultados, key=lambda r: (r["sprint"], r["camada"], r["arquivo"])):
        grupo = (r["sprint"], r["camada"], r["arquivo"])
        if grupo != grupo_atual:
            grupo_atual = grupo
            linhas += ["", f"== {r['sprint']} | {r['camada']} | {r['arquivo']} =="]
        linhas.append(f"[{r['situacao']}] {r['teste']}")
        if r["detalhe"]:
            linhas.append(f"    motivo: {r['detalhe'][:500]}")
    return "\n".join(linhas) + "\n"


def main():
    sys.stdout.reconfigure(encoding="utf-8", line_buffering=True)
    PASTA.mkdir(exist_ok=True)
    for arquivo in (XML_BACKEND, XML_FRONTEND):
        arquivo.unlink(missing_ok=True)
    rodar_backend()
    rodar_frontend()

    resultados = ler_resultados(XML_BACKEND, "Backend") + ler_resultados(XML_FRONTEND, "Frontend")
    RELATORIO.write_text(gerar_texto(resultados), encoding="utf-8")
    for arquivo in (XML_BACKEND, XML_FRONTEND):
        arquivo.unlink(missing_ok=True)  # so o .txt fica na pasta

    print("\n== Resumo ==")
    for camada in ("Backend", "Frontend"):
        da_camada = [r for r in resultados if r["camada"] == camada]
        passou = sum(r["situacao"] == "PASSOU" for r in da_camada)
        print(f"{camada}: {passou} de {len(da_camada)} passaram")
    falhas = [r for r in resultados if r["situacao"] == "FALHOU"]
    for r in falhas:
        print(f"  FALHOU: [{r['camada']}] {r['arquivo']} - {r['teste']}")
    print(f"\nRelatório: {RELATORIO}")
    return 1 if falhas else 0


if __name__ == "__main__":
    sys.exit(main())
