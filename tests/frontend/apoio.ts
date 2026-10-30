// Apoio dos testes do front: localStorage e fetch falsos (sem navegador e sem backend).
import { vi } from "vitest";

export const API = "http://127.0.0.1:8000";

export function prepararNavegador() {
  const armazenamento = new Map<string, string>();
  vi.stubGlobal("localStorage", {
    getItem: (chave: string) => armazenamento.get(chave) ?? null,
    setItem: (chave: string, valor: string) => armazenamento.set(chave, valor),
    removeItem: (chave: string) => armazenamento.delete(chave),
  });
  const fetchFalso = vi.fn();
  vi.stubGlobal("fetch", fetchFalso);
  return { armazenamento, fetchFalso };
}

export function resposta(dados: unknown, status = 200) {
  return new Response(status === 204 ? null : JSON.stringify(dados), { status });
}

// Responde conforme "METODO /caminho"; o que nao estiver na tabela vira 404.
// O valor pode ser os dados (status 200) ou uma funcao que monta a Response.
export function apiFalsa(rotas: Record<string, unknown>) {
  return async (url: string, opcoes: RequestInit = {}) => {
    const chave = `${opcoes.method ?? "GET"} ${url.replace(API, "")}`;
    if (!(chave in rotas)) return resposta({ detail: "Não encontrado" }, 404);
    const valor = rotas[chave];
    return typeof valor === "function" ? valor() : resposta(valor);
  };
}

export const semConteudo = () => resposta(null, 204);

// Lista as chamadas como "METODO /caminho" para conferir o que foi enviado.
export function chamadas(fetchFalso: ReturnType<typeof vi.fn>) {
  return fetchFalso.mock.calls.map(([url, opcoes]) => `${(opcoes as RequestInit | undefined)?.method ?? "GET"} ${String(url).replace(API, "")}`);
}

export function corpo(fetchFalso: ReturnType<typeof vi.fn>, indice: number) {
  return JSON.parse(String((fetchFalso.mock.calls[indice][1] as RequestInit).body));
}
