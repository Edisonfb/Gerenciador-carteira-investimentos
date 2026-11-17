import { useEffect, useState } from "react";
import { Link, useNavigate, useParams } from "react-router-dom";
import { ArrowLeft, Eye, LoaderCircle, Pencil, Plus, RefreshCw, Search, Trash2 } from "lucide-react";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Card, CardHeader, CardTitle, CardDescription, CardContent } from "@/components/ui/card";
import { Table, TableBody, TableCaption, TableCell, TableHead, TableHeader, TableRow } from "@/components/ui/table";
import { AcaoCarteiraDialog } from "../components/AcaoCarteiraDialog";
import { consultarConfiguracaoCarteira, consultarResumoFinanceiroCarteira } from "../services/configuracaoCarteiraService";
import type { ConfiguracaoCarteira, ResumoFinanceiroCarteira } from "../services/configuracaoCarteiraService";
import { distribuicaoObjetivos, filtrarAtivosCarteira } from "../lib/detalheCarteira";

const percentual = (valor: number) => `${new Intl.NumberFormat("pt-BR", { maximumFractionDigits: 2 }).format(valor)}%`;
const moeda = (valor: number) => new Intl.NumberFormat("pt-BR", { style: "currency", currency: "BRL" }).format(valor);
const dataCotacao = (valor: string) => new Date(/(?:Z|[+-]\d{2}:?\d{2})$/i.test(valor) ? valor : `${valor}Z`);

export function DetalheCarteiraPage() {
  const { id } = useParams();
  return <DetalheCarteira key={id} id={Number(id)} />;
}

function DetalheCarteira({ id }: { id: number }) {
  const navigate = useNavigate();
  const [dados, setDados] = useState<ConfiguracaoCarteira | null>(null);
  const [resumo, setResumo] = useState<ResumoFinanceiroCarteira | null>(null);
  const [erroResumo, setErroResumo] = useState("");
  const [carregando, setCarregando] = useState(true);
  const [erro, setErro] = useState("");
  const [tentativa, setTentativa] = useState(0);
  const [busca, setBusca] = useState("");
  const [setor, setSetor] = useState("");
  const [excluindo, setExcluindo] = useState(false);
  useEffect(() => {
    const controller = new AbortController();
    setErroResumo("");
    Promise.allSettled([
      consultarConfiguracaoCarteira(id, controller.signal),
      consultarResumoFinanceiroCarteira(id, controller.signal),
    ]).then(([resultadoCarteira, resultadoResumo]) => {
      if (controller.signal.aborted) return;
      if (resultadoCarteira.status === "fulfilled") { setDados(resultadoCarteira.value); setErro(""); }
      else setErro(resultadoCarteira.reason instanceof Error ? resultadoCarteira.reason.message : "Não foi possível carregar a carteira.");
      if (resultadoResumo.status === "fulfilled") { setResumo(resultadoResumo.value); setErroResumo(""); }
      else { setResumo(null); setErroResumo(resultadoResumo.reason instanceof Error ? resultadoResumo.reason.message : "Não foi possível carregar o resumo financeiro."); }
    }).finally(() => { if (!controller.signal.aborted) setCarregando(false); });
    return () => controller.abort();
  }, [id, tentativa]);
  function atualizar() { setCarregando(true); setTentativa(t => t + 1); }
  const ativos = dados?.ativos ?? [];
  const setores = [...new Set(ativos.map(a => a.setor))].sort((a, b) => a.localeCompare(b, "pt-BR"));
  const filtrados = filtrarAtivosCarteira(ativos, busca, setor);
  const { fatias, total } = distribuicaoObjetivos(ativos);
  const objetivoCompleto = Math.abs(total - 100) < 0.000001;
  const fundo = fatias.length && objetivoCompleto ? `conic-gradient(${fatias.map(f => `${f.cor} ${f.inicio}% ${f.fim}%`).join(", ")})` : undefined;

  return <section className="mx-auto w-full max-w-6xl py-4 sm:py-8" aria-labelledby="titulo-detalhe-carteira">
    <div className="mb-6 flex flex-wrap items-center justify-between gap-3">
      <Button asChild variant="outline"><Link to="/carteiras-investidor" className="no-underline hover:no-underline"><ArrowLeft aria-hidden="true" />Voltar às carteiras</Link></Button>
      <Button type="button" variant="outline" disabled={carregando || excluindo} onClick={atualizar}><RefreshCw aria-hidden="true" />Atualizar</Button>
    </div>
    <header className="mb-8 text-center"><p className="mb-1 text-sm text-muted-foreground">Carteira</p><h1 id="titulo-detalhe-carteira" className="mb-2 text-3xl font-semibold tracking-tight">{dados?.carteira.nome ?? "Detalhes da carteira"}</h1>{dados && <p className="m-0 text-sm text-muted-foreground">{dados.carteira.ativa ? "Carteira ativa" : "Carteira desativada"}</p>}</header>
    {carregando ? <Card><CardContent className="flex items-center gap-2 p-6" role="status"><LoaderCircle className="size-4 animate-spin" aria-hidden="true" />Carregando carteira...</CardContent></Card>
      : erro || !dados ? <Card><CardContent className="p-6"><p role="alert" className="text-destructive">{erro || "Carteira não encontrada."}</p><Button variant="outline" onClick={atualizar}>Tentar novamente</Button></CardContent></Card>
      : <>
        <div className="mb-6 grid gap-4 sm:grid-cols-3">
          <Card><CardContent className="p-5"><p className="mb-2 text-sm text-muted-foreground">Ativos na carteira</p><p className="m-0 text-2xl font-semibold">{ativos.length}</p></CardContent></Card>
          <Card><CardContent className="p-5"><p className="mb-2 text-sm text-muted-foreground">Objetivo total</p><p className="m-0 text-2xl font-semibold">{percentual(total)}</p></CardContent></Card>
          <Card><CardContent className="p-5"><p className="mb-2 text-sm text-muted-foreground">Patrimônio total</p>{resumo ? <p className="m-0 text-2xl font-semibold">{moeda(resumo.patrimonio_total)}</p> : <p className="m-0 text-sm text-muted-foreground">Resumo financeiro indisponível.</p>}</CardContent></Card>
        </div>
        {erroResumo && <div role="alert" className="mb-6 rounded-md border border-amber-200 bg-amber-50 p-4 text-sm text-amber-900">Não foi possível carregar os valores financeiros. {erroResumo} Use “Atualizar” para tentar novamente.</div>}
        <div className="grid items-start gap-6 lg:grid-cols-[280px_minmax(0,1fr)]">
          <Card><CardHeader><CardTitle>Distribuição dos objetivos</CardTitle><CardDescription>Percentuais definidos para cada ativo.</CardDescription></CardHeader><CardContent>
            {fundo ? <div className="mx-auto mb-5 size-44 rounded-full" style={{ background: fundo }} role="img" aria-label={`Distribuição dos objetivos: ${fatias.map(f => `${f.ticker} ${percentual(f.percentual)}`).join(", ")}`} /> : <p role="status" className="text-sm text-muted-foreground">{ativos.length ? "Redistribua os objetivos para somar 100% e visualizar o gráfico." : "Inclua ativos para visualizar a distribuição."}</p>}
            <ul className="m-0 flex list-none flex-col gap-3 p-0">{fatias.map(f => <li key={f.ticker} className="flex items-center justify-between gap-3 text-sm"><span className="flex items-center gap-2"><span className="size-3 shrink-0 rounded-full" style={{ background: f.cor }} aria-hidden="true" />{f.ticker}</span><span>{percentual(f.percentual)}</span></li>)}</ul>
          </CardContent></Card>
          <Card className="min-w-0"><CardHeader><div className="flex flex-wrap items-center justify-between gap-3"><CardTitle>Ativos da carteira</CardTitle><div className="flex gap-2">
            <Button asChild variant="outline" size="sm"><Link to={`/carteiras-investidor/${id}/historico`} className="no-underline hover:no-underline"><Eye aria-hidden="true" />Histórico de transação</Link></Button>
            <Button asChild variant="outline" size="sm"><Link to="/transacoes-investidor" state={{ idCarteira: id }} className="no-underline hover:no-underline"><Plus aria-hidden="true" />Registrar transação</Link></Button>
            <Button asChild variant="outline" size="sm"><Link to={`/carteiras-investidor/${id}/editar`} className="no-underline hover:no-underline"><Pencil aria-hidden="true" />Editar</Link></Button>
            <Button variant="destructive" size="sm" onClick={() => setExcluindo(true)}><Trash2 aria-hidden="true" />Excluir</Button>
          </div></div><CardDescription>Consulte a composição e filtre os ativos abaixo.</CardDescription></CardHeader><CardContent>
            <div className="mb-5 grid gap-4 sm:grid-cols-2">
              <div className="flex flex-col gap-2"><label htmlFor="busca-ativo-carteira" className="text-sm font-medium">Buscar ativo</label><div className="relative"><Search className="absolute left-3 top-1/2 size-4 -translate-y-1/2 text-muted-foreground" aria-hidden="true" /><Input id="busca-ativo-carteira" className="pl-9" placeholder="Ex.: ITUB" value={busca} onChange={e => setBusca(e.target.value)} /></div></div>
              <div className="flex flex-col gap-2"><label htmlFor="setor-detalhe-carteira" className="text-sm font-medium">Filtrar por setor</label><select id="setor-detalhe-carteira" className="h-9 w-full rounded-md border border-input bg-background px-3 text-sm" value={setor} onChange={e => setSetor(e.target.value)}><option value="">Todos os setores</option>{setores.map(s => <option key={s} value={s}>{s}</option>)}</select></div>
            </div>
            <Table><TableCaption className="sr-only">Composição e valores financeiros da carteira {dados.carteira.nome}.</TableCaption><TableHeader><TableRow><TableHead>Ativo</TableHead><TableHead>Setor</TableHead><TableHead className="text-right">Quantidade</TableHead><TableHead className="text-right">Cotação</TableHead><TableHead className="text-right">Patrimônio</TableHead><TableHead className="text-right">Atual (%)</TableHead><TableHead className="text-right">Objetivo (%)</TableHead><TableHead className="text-right">Distância</TableHead></TableRow></TableHeader>
              <TableBody>{filtrados.map(ativo => {
                const posicao = resumo?.ativos.find(item => item.ticker === ativo.ticker);
                const distancia = posicao ? Number(ativo.objetivo.replace(",", ".")) - posicao.participacao_percentual : null;
                return <TableRow key={ativo.ticker}><TableCell className="font-medium">{ativo.ticker}{!ativo.ativo && <span className="mt-1 block text-xs text-muted-foreground">Desativado</span>}</TableCell><TableCell>{ativo.setor}</TableCell><TableCell className="text-right">{new Intl.NumberFormat("pt-BR").format(ativo.quantidade)}</TableCell><TableCell className="text-right">{posicao?.cotacao === null ? "—" : posicao ? moeda(posicao.cotacao) : "—"}</TableCell><TableCell className="text-right">{posicao ? moeda(posicao.valor_atual) : "—"}</TableCell><TableCell className="text-right">{posicao ? percentual(posicao.participacao_percentual) : "—"}</TableCell><TableCell className="text-right">{percentual(Number(ativo.objetivo.replace(",", ".")))}</TableCell><TableCell className="text-right">{distancia === null ? "—" : `${distancia > 0 ? "+" : ""}${percentual(distancia)}`}</TableCell></TableRow>;
              })}
                {!filtrados.length && <TableRow><TableCell colSpan={8} role="status" className="py-8 text-center text-muted-foreground">{ativos.length ? "Nenhum ativo encontrado" : "Nenhum ativo incluído nesta carteira."}</TableCell></TableRow>}
              </TableBody></Table>
            <p role="status" className="mb-0 mt-4 text-xs text-muted-foreground">{filtrados.length} de {ativos.length} ativo(s). O gráfico e os totais representam a carteira completa.{resumo?.ativos.some(posicao => posicao.data_atualizacao) && <> Cotações atualizadas até {new Intl.DateTimeFormat("pt-BR", { dateStyle: "short", timeStyle: "short" }).format(new Date(Math.max(...resumo.ativos.flatMap(posicao => posicao.data_atualizacao ? [dataCotacao(posicao.data_atualizacao).getTime()] : []))))}.</>}</p>
          </CardContent></Card>
        </div>
        {excluindo && <AcaoCarteiraDialog carteira={dados.carteira} acao="excluir" onFechar={() => setExcluindo(false)} onConcluido={() => navigate("/carteiras-investidor", { replace: true })} />}
      </>}
  </section>;
}
