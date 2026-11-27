import { useEffect, useState } from "react";
import { Link, useLocation, useParams } from "react-router-dom";
import { ArrowLeft, LoaderCircle, RefreshCw } from "lucide-react";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Table, TableBody, TableCaption, TableCell, TableHead, TableHeader, TableRow } from "@/components/ui/table";
import { consultarConfiguracaoCarteira } from "../services/configuracaoCarteiraService";
import { listarCatalogoTransacao, listarHistoricoTransacoes } from "../services/transacaoService";
import type { AtivoCatalogoTransacao, TransacaoHistorico } from "../services/transacaoService";

const moeda = (valor: number) => new Intl.NumberFormat("pt-BR", { style: "currency", currency: "BRL" }).format(valor);
const dataUtc = (valor: string) => new Date(/(?:Z|[+-]\d{2}:?\d{2})$/i.test(valor) ? valor : `${valor}Z`);

export function HistoricoTransacoesPage() {
  const { id } = useParams();
  return <HistoricoTransacoes key={id} idCarteira={Number(id)} />;
}

// Reinicia os dados ao navegar para o historico de outra carteira.
function HistoricoTransacoes({ idCarteira }: { idCarteira: number }) {
  const id = idCarteira;
  const location = useLocation();
  const mensagem = (location.state as { mensagem?: string } | null)?.mensagem;
  const [nomeCarteira, setNomeCarteira] = useState("");
  const [transacoes, setTransacoes] = useState<TransacaoHistorico[]>([]);
  const [catalogo, setCatalogo] = useState<AtivoCatalogoTransacao[]>([]);
  const [carregando, setCarregando] = useState(true);
  const [erro, setErro] = useState("");
  const [tentativa, setTentativa] = useState(0);

  useEffect(() => {
    const controller = new AbortController();
    async function carregar() {
      try {
        // A leitura da carteira valida propriedade antes da consulta do histórico.
        const configuracao = await consultarConfiguracaoCarteira(idCarteira, controller.signal);
        const [historico, ativos] = await Promise.all([
          listarHistoricoTransacoes(idCarteira, controller.signal),
          listarCatalogoTransacao(controller.signal),
        ]);
        if (controller.signal.aborted) return;
        setNomeCarteira(configuracao.carteira.nome); setTransacoes(historico); setCatalogo(ativos);
      } catch (falha) {
        if (!controller.signal.aborted) setErro(falha instanceof Error ? falha.message : "Não foi possível carregar o histórico.");
      } finally { if (!controller.signal.aborted) setCarregando(false); }
    }
    void carregar();
    return () => controller.abort();
  }, [idCarteira, tentativa]);

  return <section className="mx-auto w-full max-w-6xl py-4 sm:py-8" aria-labelledby="titulo-historico-transacoes">
    <div className="mb-6 flex flex-wrap items-center justify-between gap-3">
      <Button asChild variant="outline"><Link to={`/carteiras-investidor/${id}`} className="no-underline hover:no-underline"><ArrowLeft aria-hidden="true" />Voltar à carteira</Link></Button>
      <Button type="button" variant="outline" disabled={carregando} onClick={() => { setCarregando(true); setErro(""); setTentativa(valor => valor + 1); }}><RefreshCw className={carregando ? "animate-spin" : undefined} aria-hidden="true" />Atualizar</Button>
    </div>
    <Card>
      <CardHeader><CardTitle id="titulo-historico-transacoes" className="text-2xl">Histórico de transações</CardTitle><CardDescription>{nomeCarteira ? `Movimentações da carteira ${nomeCarteira}.` : "Consulta somente leitura das compras e vendas desta carteira."}</CardDescription></CardHeader>
      <CardContent>
        {mensagem && <p role="status" className="mb-5 rounded-md border border-emerald-200 bg-emerald-50 p-3 text-sm text-emerald-800">{mensagem}</p>}
        {erro && <p role="alert" className="mb-5 rounded-md border border-red-200 bg-red-50 p-3 text-sm text-destructive">{erro}</p>}
        {carregando ? <p role="status" className="flex items-center gap-2 text-sm text-muted-foreground"><LoaderCircle className="size-4 animate-spin" aria-hidden="true" />Carregando histórico...</p>
          : !erro && <Table><TableCaption className="sr-only">Histórico de compras e vendas, da mais recente para a mais antiga.</TableCaption><TableHeader><TableRow><TableHead>Data</TableHead><TableHead>Tipo</TableHead><TableHead>Ativo</TableHead><TableHead>Setor</TableHead><TableHead className="text-right">Quantidade</TableHead><TableHead className="text-right">Valor</TableHead></TableRow></TableHeader>
            <TableBody>{transacoes.map(transacao => {
              const data = dataUtc(transacao.data_transacao);
              const setor = catalogo.find(ativo => ativo.ticker === transacao.ticker)?.setor ?? "—";
              return <TableRow key={transacao.id_transacao}><TableCell>{Number.isNaN(data.getTime()) ? "—" : new Intl.DateTimeFormat("pt-BR", { dateStyle: "short" }).format(data)}</TableCell><TableCell><span className={transacao.tipo === "compra" ? "rounded-full bg-emerald-50 px-2.5 py-1 text-xs font-medium text-emerald-800" : "rounded-full bg-amber-50 px-2.5 py-1 text-xs font-medium text-amber-900"}>{transacao.tipo === "compra" ? "Compra" : "Venda"}</span></TableCell><TableCell className="font-medium">{transacao.ticker}</TableCell><TableCell>{setor}</TableCell><TableCell className="text-right">{new Intl.NumberFormat("pt-BR").format(transacao.quantidade)}</TableCell><TableCell className="text-right">{moeda(transacao.valor_total)}</TableCell></TableRow>;
            })}
              {!transacoes.length && <TableRow><TableCell colSpan={6} role="status" className="py-10 text-center text-muted-foreground">Nenhuma transação registrada nesta carteira.</TableCell></TableRow>}
            </TableBody></Table>}
        <p className="mb-0 mt-4 text-xs text-muted-foreground">O histórico é somente leitura e está ordenado da transação mais recente para a mais antiga.</p>
      </CardContent>
    </Card>
  </section>;
}
