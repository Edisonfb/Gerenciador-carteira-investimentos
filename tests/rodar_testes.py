"""Roda os testes da Sprint 1 e 2 (backend e frontend) e gera o relatorio.

Uso, na raiz do projeto:
    backend\\.venv\\Scripts\\python.exe tests\\rodar_testes.py

Gera tests/relatorios/relatorio_testes.html com cada teste marcado como
PASSOU ou FALHOU, e mostra o resumo no terminal.
"""

import html
import subprocess
import sys
import xml.etree.ElementTree as ET
from datetime import datetime
from pathlib import Path

RAIZ = Path(__file__).resolve().parent.parent
PASTA = RAIZ / "tests" / "relatorios"
XML_BACKEND = PASTA / "backend.xml"
XML_FRONTEND = PASTA / "frontend.xml"
RELATORIO = PASTA / "relatorio_testes.html"


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


def gerar_html(resultados):
    total = len(resultados)
    passou = sum(r["situacao"] == "PASSOU" for r in resultados)
    falhou = sum(r["situacao"] == "FALHOU" for r in resultados)
    linhas = []
    for r in sorted(resultados, key=lambda r: (r["sprint"], r["camada"], r["arquivo"])):
        cor = {"PASSOU": "#15803d", "FALHOU": "#b91c1c"}.get(r["situacao"], "#a16207")
        linhas.append(
            f"<tr><td>{r['sprint']}</td><td>{r['camada']}</td><td>{html.escape(r['arquivo'])}</td>"
            f"<td>{html.escape(r['teste'])}</td><td style='color:{cor};font-weight:bold'>{r['situacao']}</td>"
            f"<td><pre>{html.escape(r['detalhe'][:500])}</pre></td></tr>"
        )
    return f"""<!doctype html>
<html lang="pt-BR"><head><meta charset="utf-8"><title>Relatório de testes</title>
<style>
  body {{ font-family: Arial, sans-serif; margin: 2rem; color: #0f172a; }}
  table {{ border-collapse: collapse; width: 100%; font-size: 14px; }}
  th, td {{ border: 1px solid #cbd5e1; padding: 6px 8px; text-align: left; vertical-align: top; }}
  th {{ background: #1e293b; color: #fff; }}
  pre {{ margin: 0; white-space: pre-wrap; font-size: 12px; }}
  .resumo span {{ margin-right: 1.5rem; font-size: 18px; }}
</style></head><body>
<h1>Relatório de testes - Sprint 1 e Sprint 2</h1>
<p>Gerado em {datetime.now():%d/%m/%Y %H:%M}</p>
<p class="resumo"><span>Total: <b>{total}</b></span>
<span style="color:#15803d">Passaram: <b>{passou}</b></span>
<span style="color:#b91c1c">Falharam: <b>{falhou}</b></span></p>
<table><tr><th>Sprint</th><th>Camada</th><th>Arquivo</th><th>Teste</th><th>Resultado</th><th>Detalhe da falha</th></tr>
{''.join(linhas)}
</table></body></html>"""


def main():
    sys.stdout.reconfigure(encoding="utf-8", line_buffering=True)
    PASTA.mkdir(exist_ok=True)
    for arquivo in (XML_BACKEND, XML_FRONTEND):
        arquivo.unlink(missing_ok=True)
    rodar_backend()
    rodar_frontend()

    resultados = ler_resultados(XML_BACKEND, "Backend") + ler_resultados(XML_FRONTEND, "Frontend")
    RELATORIO.write_text(gerar_html(resultados), encoding="utf-8")

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
