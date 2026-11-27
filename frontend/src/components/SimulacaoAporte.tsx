import { useEffect, useRef, useState } from "react";
import type { FormEvent } from "react";
import { useNavigate } from "react-router-dom";
import { Button } from "./ui/button";
import { Input } from "./ui/input";
import { Card, CardHeader, CardTitle, CardDescription, CardContent } from "./ui/card";
import { Table, TableHeader, TableRow, TableHead, TableBody, TableCell } from "./ui/table";
import { consultarMinimosAporte, registrarRecomendacao, simularAporte } from "../services/simulacaoAporteService";
import type { Distribuicao, Simulacao, ValoresPagos } from "../types/simulacaoAporte";

const moeda = (valor: string) => new Intl.NumberFormat("pt-BR", { style: "currency", currency: "BRL" }).format(Number(valor));
const percentual = (valor: string) => `${Number(valor).toLocaleString("pt-BR", { maximumFractionDigits: 2 })}%`;

/** Consulta sugestoes da API e exige confirmacao explicita antes de registrar compras. */
export function SimulacaoAporte({ idCarteira, ativa }: { idCarteira: number; ativa: boolean }) {
  const navigate = useNavigate();
  const [aporte, setAporte] = useState("");
  const [distribuicao, setDistribuicao] = useState<Distribuicao>("balanceamento");
  const [resultado, setResultado] = useState<Simulacao | null>(null);
  const [minimos, setMinimos] = useState<Simulacao | null>(null);
  const [erroMinimos, setErroMinimos] = useState("");
  const [ocupado, setOcupado] = useState(false);
  const [erro, setErro] = useState("");
  const [registroIniciado, setRegistroIniciado] = useState(false);
  const [conferindo, setConferindo] = useState(false);
  const [valoresPagos, setValoresPagos] = useState<ValoresPagos>({});
  const emAndamento = useRef(false);

  useEffect(() => {
    if (!ativa) return;
    const controller = new AbortController();
    consultarMinimosAporte(idCarteira, distribuicao, controller.signal)
      .then(dados => { if (!controller.signal.aborted) { setMinimos(dados); setErroMinimos(""); } })
      .catch(falha => { if (!controller.signal.aborted) setErroMinimos(falha instanceof Error ? falha.message : "Não foi possível consultar os mínimos."); });
    return () => controller.abort();
  }, [idCarteira, distribuicao, ativa]);

  async function simular(evento: FormEvent) {
    evento.preventDefault();
    if (emAndamento.current) return;
    setErro(""); setResultado(null); setConferindo(false);
    const valor = aporte.trim().replace(",", ".");
    if (!/^\d+(?:\.\d{1,2})?$/.test(valor) || Number(valor) <= 0) {
      setErro("Informe um valor de aporte maior que zero"); return;
    }
    emAndamento.current = true; setOcupado(true);
    try { const dados = await simularAporte(idCarteira, valor, distribuicao); setResultado(dados); setMinimos(dados); setErroMinimos(""); }
    catch (falha) { setErro(falha instanceof Error ? falha.message : "Não foi possível simular o aporte."); }
    finally { emAndamento.current = false; setOcupado(false); }
  }

  // Abre uma etapa editavel; esse botao nunca grava compras.
  function conferirCompras() {
    if (!resultado) return;
    setValoresPagos(Object.fromEntries(resultado.ativos.filter(a => a.quantidade_sugerida > 0)
      .map(a => [a.ticker, a.custo_sugerido.replace(".", ",")])));
    setConferindo(true); setErro("");
  }

  async function registrar() {
    if (!resultado || emAndamento.current || registroIniciado) return;
    const confirmados: ValoresPagos = {};
    for (const ativo of resultado.ativos.filter(a => a.quantidade_sugerida > 0)) {
      const valor = (valoresPagos[ativo.ticker] ?? "").trim().replace(",", ".");
      if (!/^\d+(?:\.\d{1,2})?$/.test(valor) || Number(valor) <= 0) {
        setErro(`Informe o valor total pago por ${ativo.ticker}, maior que zero e com até duas casas decimais.`); return;
      }
      confirmados[ativo.ticker] = valor;
    }
    emAndamento.current = true; setOcupado(true); setRegistroIniciado(true); setErro("");
    try {
      await registrarRecomendacao(resultado, confirmados);
      navigate(`/carteiras-investidor/${idCarteira}/historico`, { state: { mensagem: "Compras recomendadas registradas e carteira atualizada." } });
    } catch (falha) {
      setErro(falha instanceof Error ? falha.message : "Não foi possível concluir as compras.");
    } finally { emAndamento.current = false; setOcupado(false); }
  }

  const compras = resultado?.ativos.filter(a => a.quantidade_sugerida > 0) ?? [];
  const referencia = resultado ?? minimos;
  const centavosPagos = compras.map(a => {
    const texto = (valoresPagos[a.ticker] ?? "").trim().replace(",", ".");
    return /^\d+(?:\.\d{1,2})?$/.test(texto) && Number(texto) > 0 ? Math.round(Number(texto) * 100) : NaN;
  });
  const totalPago = centavosPagos.reduce((soma, valor) => soma + valor, 0);
  return <Card className="mt-6">
    <CardHeader><CardTitle>Recomendações de Compra</CardTitle><CardDescription>Simule seu novo aporte. Nenhuma compra é registrada até a confirmação.</CardDescription></CardHeader>
    <CardContent>
      <form onSubmit={simular} className="flex flex-col gap-4">
        <fieldset disabled={!ativa || ocupado || registroIniciado} className="flex flex-wrap items-end gap-4">
          <div><label htmlFor="novo-aporte" className="mb-2 block">Novo aporte (R$)</label><Input id="novo-aporte" inputMode="decimal" placeholder="Ex.: 3000,00" value={aporte} onChange={e => { setAporte(e.target.value); setResultado(null); setErro(""); }} /></div>
          <div><label htmlFor="distribuicao-aporte" className="mb-2 block">Distribuição</label><select id="distribuicao-aporte" className="h-9 rounded-md border px-3" value={distribuicao} onChange={e => { setDistribuicao(e.target.value as Distribuicao); setResultado(null); setMinimos(null); setErroMinimos(""); setErro(""); }}><option value="balanceamento">Balancear: dois ativos mais abaixo da meta</option><option value="linear">Distribuir proporcionalmente às metas</option></select></div>
          <Button type="submit">{ocupado ? "Aguarde..." : "Simular aporte"}</Button>
        </fieldset>
      </form>
      {ativa && <div className="mt-4 rounded-md border bg-muted/30 p-4">
        <h3 className="mb-2 font-medium">Quanto preciso para começar?</h3>
        {referencia ? <>
          <p role="status">{referencia.aporte_minimo !== null ? <>Aporte mínimo para gerar uma compra nesta distribuição: <strong>{moeda(referencia.aporte_minimo)}</strong>.</> : "A carteira está balanceada. Selecione a distribuição proporcional às metas para investir um novo valor."}</p>
          <Table><TableHeader><TableRow><TableHead>Ativo</TableHead><TableHead>Preço por ação</TableHead><TableHead>Custo de 100 ações</TableHead><TableHead>Aporte mínimo para este ativo</TableHead></TableRow></TableHeader><TableBody>{referencia.ativos.map(a => <TableRow key={a.ticker}><TableCell>{a.ticker}</TableCell><TableCell>{moeda(a.cotacao)}</TableCell><TableCell>{moeda(a.custo_lote)}</TableCell><TableCell>{a.aporte_minimo_ativo !== null ? moeda(a.aporte_minimo_ativo) : "Fora da recomendação atual"}</TableCell></TableRow>)}</TableBody></Table>
          <p className="mb-0 mt-2 text-sm text-muted-foreground">O aporte é dividido entre os ativos conforme a distribuição escolhida. Por isso, ele pode precisar ser maior que o custo de um lote. Valores estimados pelas cotações consultadas; a simulação atualiza essas referências.</p>
        </> : <p role="status">{erroMinimos ? "Não foi possível consultar os custos mínimos. Tente simular novamente ou atualize a carteira." : "Consultando o custo dos lotes..."}</p>}
      </div>}
      {!ativa && <p role="status">A carteira está desativada.</p>}
      {erro && <p role="alert" className="mt-4 text-destructive">{erro}</p>}
      {registroIniciado && !ocupado && <p className="mt-4">Confira o histórico antes de iniciar outra recomendação. <Button variant="outline" onClick={() => navigate(`/carteiras-investidor/${idCarteira}/historico`)}>Ver histórico</Button></p>}
      {resultado && <div className="mt-5">
        {!compras.length ? <p role="status">{distribuicao === "balanceamento" && resultado.ativos.every(a => Number(a.distancia_atual) >= 0) ? "A carteira está balanceada. Use a distribuição proporcional às metas para investir um novo valor." : "O valor do aporte é insuficiente para comprar um lote de 100 ações dos ativos recomendados"}</p> : <>
          <Table><TableHeader><TableRow><TableHead>Ativo</TableHead><TableHead>Quantidade</TableHead><TableHead>Valor sugerido</TableHead><TableHead>Atual</TableHead><TableHead>Projetado</TableHead><TableHead>Distância projetada</TableHead></TableRow></TableHeader><TableBody>{compras.map(a => <TableRow key={a.ticker}><TableCell>{a.ticker}</TableCell><TableCell>{a.quantidade_sugerida}</TableCell><TableCell>{moeda(a.custo_sugerido)}</TableCell><TableCell>{percentual(a.participacao_atual)}</TableCell><TableCell>{percentual(a.participacao_projetada)}</TableCell><TableCell>{percentual(a.distancia_projetada)}</TableCell></TableRow>)}</TableBody></Table>
          {!conferindo && <Button className="mt-4" disabled={ocupado || registroIniciado} onClick={conferirCompras}>Conferir valores e registrar</Button>}
          {conferindo && <section className="mt-4 rounded-md border p-4" aria-labelledby="titulo-confirmar-compras">
            <h3 id="titulo-confirmar-compras" className="font-medium">Confira o que você realmente pagou</h3>
            <p className="text-sm text-muted-foreground">Os valores abaixo são sugestões. Antes de confirmar, ajuste o total efetivamente pago por cada ativo. A quantidade continua sendo a da recomendação.</p>
            <fieldset disabled={ocupado || registroIniciado} className="space-y-4">
              {compras.map(a => <div key={a.ticker}><label className="mb-1 block" htmlFor={`pago-${a.ticker}`}>Total pago por {a.quantidade_sugerida} ações de {a.ticker} (R$)</label><Input id={`pago-${a.ticker}`} inputMode="decimal" value={valoresPagos[a.ticker] ?? ""} onChange={e => { setValoresPagos(valores => ({ ...valores, [a.ticker]: e.target.value })); setErro(""); }} /><p className="mt-1 text-xs text-muted-foreground">Valor sugerido: {moeda(a.custo_sugerido)}.</p></div>)}
              <div className="flex flex-wrap gap-3"><Button variant="outline" onClick={() => { setConferindo(false); setErro(""); }}>Voltar à simulação</Button><Button onClick={registrar}>Confirmar e registrar compras</Button></div>
            </fieldset>
            {Number.isFinite(totalPago) && <p className="mt-3 font-medium">Total a registrar no histórico: {moeda((totalPago / 100).toFixed(2))}.{totalPago > Math.round(Number(resultado.aporte) * 100) && " O custo informado supera o aporte simulado."}</p>}
            <p className="mt-3 text-sm">O histórico guarda o total pago exato. O patrimônio e os percentuais atuais usam as cotações de mercado. Os valores projetados acima são estimativas da simulação.</p>
          </section>}
        </>}
        <p className="mt-4">Valor a investir: <strong>{moeda(resultado.valor_investido)}</strong> · Saldo restante: <strong>{moeda(resultado.saldo_restante)}</strong> · Patrimônio projetado: <strong>{moeda(resultado.patrimonio_projetado)}</strong></p>
        <p className="text-sm text-muted-foreground">Quantidades em lotes de 100 ações. Os valores sugeridos usam as cotações desta simulação; o saldo restante não é redistribuído. Confira o total efetivamente pago antes de registrar.</p>
      </div>}
    </CardContent>
  </Card>;
}
