import { useState } from "react";
import type { FormEvent } from "react";
import { LoaderCircle, Sparkles } from "lucide-react";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Table, TableBody, TableCaption, TableCell, TableHead, TableHeader, TableRow } from "@/components/ui/table";
import type { AtivoConfigurado } from "../types/configuracaoCarteira";
import type { ResumoFinanceiroCarteira } from "../services/configuracaoCarteiraService";
import { consultarCotacaoTransacao, registrarTransacao } from "../services/transacaoService";

interface Props {
  idCarteira: number;
  ativos: AtivoConfigurado[];
  resumo: ResumoFinanceiroCarteira | null;
  onRegistrado: () => void;
}

interface Recomendacao {
  ticker: string;
  quantidade: number;
  preco: number;
  valor: number;
}

const moeda = (valor: number) => new Intl.NumberFormat("pt-BR", { style: "currency", currency: "BRL" }).format(valor);

export function RecomendacaoCompraCarteira({ idCarteira, ativos, resumo, onRegistrado }: Props) {
  const [aporte, setAporte] = useState("");
  const [recomendacoes, setRecomendacoes] = useState<Recomendacao[]>([]);
  const [erro, setErro] = useState("");
  const [sucesso, setSucesso] = useState("");
  const [balanceada, setBalanceada] = useState(false);
  const [calculada, setCalculada] = useState(false);
  const [registrando, setRegistrando] = useState(false);
  const [calculando, setCalculando] = useState(false);

  async function gerarRecomendacao(linear = false) {
    setErro(""); setSucesso(""); setRecomendacoes([]); setCalculada(false);
    const valorAporte = Number(aporte.replace(",", "."));
    if (!Number.isFinite(valorAporte) || valorAporte <= 0) { setErro("Informe um valor de aporte maior que zero"); return; }
    if (!resumo) { setErro("O resumo financeiro está indisponível. Atualize a carteira e tente novamente."); return; }
    const posicoes = ativos.map(ativo => {
      const posicao = resumo.ativos.find(item => item.ticker === ativo.ticker);
      return posicao ? { ticker: ativo.ticker, objetivo: Number(ativo.objetivo.replace(",", ".")), atual: posicao.participacao_percentual, preco: posicao.cotacao } : null;
    }).filter((posicao): posicao is NonNullable<typeof posicao> => posicao !== null);
    if (!posicoes.length) { setErro("A carteira não possui ativos com resumo financeiro disponível."); return; }
    const deficitarios = posicoes.filter(posicao => posicao.objetivo - posicao.atual > 0.005)
      .sort((a, b) => (b.objetivo - b.atual) - (a.objetivo - a.atual) || a.ticker.localeCompare(b.ticker));
    const carteiraBalanceada = deficitarios.length === 0;
    setBalanceada(carteiraBalanceada);
    if (linear && !carteiraBalanceada) { setErro("A distribuição linear fica disponível quando a carteira está balanceada."); return; }
    if (carteiraBalanceada && !linear) { setCalculada(true); return; }
    const usarLinear = linear;
    const destinos = usarLinear ? posicoes : deficitarios.slice(0, 2);
    const pesos = usarLinear ? destinos.map(() => 1) : destinos.map(posicao => posicao.objetivo - posicao.atual);
    const somaPesos = pesos.reduce((soma, valor) => soma + valor, 0);
    setCalculando(true);
    const precos = await Promise.all(destinos.map(async posicao => {
      if (posicao.preco && posicao.preco > 0) return posicao.preco;
      try { return (await consultarCotacaoTransacao(posicao.ticker)).preco; }
      catch { return null; }
    }));
    setCalculando(false);
    if (precos.some(preco => preco === null)) { setErro("Não foi possível consultar a cotação de todos os ativos recomendados. Atualize a carteira e tente novamente."); return; }
    const proximas = destinos.flatMap((posicao, indice) => {
      const preco = precos[indice];
      if (preco === null || preco <= 0) return [];
      const alocacao = valorAporte * pesos[indice] / somaPesos;
      const quantidade = Math.floor(alocacao / (preco * 100)) * 100;
      return quantidade > 0 ? [{ ticker: posicao.ticker, quantidade, preco, valor: Number((quantidade * preco).toFixed(2)) }] : [];
    });
    setCalculando(false);
    if (!proximas.length) { setErro("O valor do aporte é insuficiente para comprar um lote de 100 ações dos ativos recomendados"); setCalculada(true); return; }
    setRecomendacoes(proximas); setCalculada(true);
  }

  function calcular(evento: FormEvent<HTMLFormElement>) {
    evento.preventDefault();
    void gerarRecomendacao();
  }

  async function registrar() {
    if (registrando || !recomendacoes.length) return;
    setRegistrando(true); setErro(""); setSucesso("");
    let concluidas = 0;
    try {
      for (const item of recomendacoes) {
        await registrarTransacao({ id_carteira: idCarteira, ticker: item.ticker, tipo: "compra", quantidade: item.quantidade, preco_unitario: item.preco });
        concluidas += 1;
      }
      setSucesso("Compras registradas. A carteira e o histórico foram atualizados.");
      setRecomendacoes([]); setCalculada(false); setBalanceada(false); onRegistrado();
    } catch (falha) {
      setErro(concluidas
        ? `${concluidas} compra(s) foram registradas antes da falha. Atualize a carteira e confira o histórico. ${falha instanceof Error ? falha.message : "Tente novamente."}`
        : (falha instanceof Error ? falha.message : "Não foi possível concluir a transação. Tente novamente"));
      if (concluidas) onRegistrado();
    } finally { setRegistrando(false); }
  }

  const valorRecomendado = recomendacoes.reduce((soma, item) => soma + item.valor, 0);
  return <section className="mt-6" aria-labelledby="titulo-recomendacoes">
    <div className="mb-4 flex items-center gap-2"><Sparkles className="size-5 text-primary" aria-hidden="true" /><h2 id="titulo-recomendacoes" className="m-0 text-xl font-semibold">Recomendações de compra</h2></div>
    <div className="rounded-xl border bg-card p-5 sm:p-6">
      <p className="mt-0 text-sm text-muted-foreground">Informe apenas o valor do novo aporte. A recomendação prioriza os dois ativos mais abaixo do objetivo e compra somente lotes de 100 ações.</p>
      <form onSubmit={evento => calcular(evento)} className="flex flex-col gap-4 sm:flex-row sm:items-end">
        <div className="flex flex-1 flex-col gap-2"><label htmlFor="aporte-carteira" className="text-sm font-medium">Novo aporte (R$)</label><Input id="aporte-carteira" inputMode="decimal" placeholder="Ex.: 3000,00" value={aporte} onChange={evento => setAporte(evento.target.value)} /></div>
        <Button type="submit" disabled={calculando}>{calculando && <LoaderCircle className="animate-spin" aria-hidden="true" />}{calculando ? "Calculando..." : "Calcular recomendação"}</Button>
        {balanceada && calculada && <Button type="button" variant="outline" disabled={calculando} onClick={() => void gerarRecomendacao(true)}>Distribuir linearmente</Button>}
      </form>
      {erro && <p role="alert" className="mb-0 mt-4 rounded-md border border-red-200 bg-red-50 p-3 text-sm text-destructive">{erro}</p>}
      {sucesso && <p role="status" className="mb-0 mt-4 rounded-md border border-emerald-200 bg-emerald-50 p-3 text-sm text-emerald-800">{sucesso}</p>}
      {!!recomendacoes.length && <>
        <Table className="mt-5"><TableCaption className="sr-only">Ativos e lotes recomendados para o aporte</TableCaption><TableHeader><TableRow><TableHead>Ativo</TableHead><TableHead className="text-right">Quantidade</TableHead><TableHead className="text-right">Cotação</TableHead><TableHead className="text-right">Valor</TableHead></TableRow></TableHeader><TableBody>{recomendacoes.map(item => <TableRow key={item.ticker}><TableCell className="font-medium">{item.ticker}</TableCell><TableCell className="text-right">{new Intl.NumberFormat("pt-BR").format(item.quantidade)}</TableCell><TableCell className="text-right">{moeda(item.preco)}</TableCell><TableCell className="text-right">{moeda(item.valor)}</TableCell></TableRow>)}</TableBody></Table>
        <div className="mt-4 flex flex-col gap-3 sm:flex-row sm:items-center sm:justify-between"><p className="m-0 text-sm">Investido: <strong>{moeda(valorRecomendado)}</strong> · Saldo não alocado: <strong>{moeda(Math.max(0, Number(aporte.replace(",", ".")) - valorRecomendado))}</strong></p><Button type="button" disabled={registrando} onClick={registrar}>{registrando && <LoaderCircle className="animate-spin" aria-hidden="true" />}{registrando ? "Registrando compras..." : "Registrar transação"}</Button></div>
      </>}
      {calculada && !recomendacoes.length && !erro && <p role="status" className="mb-0 mt-4 text-sm text-muted-foreground">A carteira está balanceada conforme os objetivos.</p>}
    </div>
  </section>;
}
