import { useEffect, useMemo, useRef, useState } from "react";
import type { FormEvent } from "react";
import { useLocation, useNavigate } from "react-router-dom";
import { ArrowLeftRight, LoaderCircle } from "lucide-react";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Input } from "@/components/ui/input";
import { listarAtivosDaCarteira, listarCarteirasParaTransacao, listarCatalogoTransacao, consultarCotacaoTransacao, registrarTransacao } from "../services/transacaoService";
import type { AtivoCarteiraTransacao, AtivoCatalogoTransacao, CarteiraTransacao, CotacaoTransacao } from "../services/transacaoService";

const moeda = (valor: number) => new Intl.NumberFormat("pt-BR", { style: "currency", currency: "BRL" }).format(valor);

export function TransacaoPage() {
  const navigate = useNavigate();
  const location = useLocation();
  const carteiraInicial = (location.state as { idCarteira?: number } | null)?.idCarteira;
  const [carteiras, setCarteiras] = useState<CarteiraTransacao[]>([]);
  const [catalogo, setCatalogo] = useState<AtivoCatalogoTransacao[]>([]);
  const [ativos, setAtivos] = useState<AtivoCarteiraTransacao[]>([]);
  const [carteiraId, setCarteiraId] = useState(carteiraInicial ? String(carteiraInicial) : "");
  const [ticker, setTicker] = useState("");
  const [quantidadeTexto, setQuantidadeTexto] = useState("");
  const [tipo, setTipo] = useState<"compra" | "venda" | null>(null);
  const [cotacao, setCotacao] = useState<CotacaoTransacao | null>(null);
  const [precoTexto, setPrecoTexto] = useState("");
  const [carregandoInicial, setCarregandoInicial] = useState(true);
  const [carregandoAtivos, setCarregandoAtivos] = useState(!!carteiraInicial);
  const [carregandoCotacao, setCarregandoCotacao] = useState(false);
  const [registrando, setRegistrando] = useState(false);
  const [erro, setErro] = useState("");
  const [erroCotacao, setErroCotacao] = useState("");
  const envioAtivo = useRef(false);

  useEffect(() => {
    const controller = new AbortController();
    Promise.all([listarCarteirasParaTransacao(controller.signal), listarCatalogoTransacao(controller.signal)])
      .then(([listaCarteiras, listaAtivos]) => {
        if (controller.signal.aborted) return;
        setCarteiras(listaCarteiras.filter(carteira => carteira.ativa));
        setCatalogo(listaAtivos);
      })
      .catch(falha => { if (!controller.signal.aborted) setErro(falha instanceof Error ? falha.message : "Não foi possível carregar as carteiras."); })
      .finally(() => { if (!controller.signal.aborted) setCarregandoInicial(false); });
    return () => controller.abort();
  }, []);

  useEffect(() => {
    if (!carteiraId) return;
    const controller = new AbortController();
    listarAtivosDaCarteira(Number(carteiraId), controller.signal)
      .then(lista => { if (!controller.signal.aborted) setAtivos(lista); })
      .catch(falha => { if (!controller.signal.aborted) setErro(falha instanceof Error ? falha.message : "Não foi possível consultar os ativos da carteira."); })
      .finally(() => { if (!controller.signal.aborted) setCarregandoAtivos(false); });
    return () => controller.abort();
  }, [carteiraId]);

  useEffect(() => {
    if (!ticker) return;
    const controller = new AbortController();
    consultarCotacaoTransacao(ticker, controller.signal)
      .then(dado => { if (!controller.signal.aborted) { setCotacao(dado); setPrecoTexto(atual => atual || String(dado.preco)); } })
      .catch(falha => { if (!controller.signal.aborted) setErroCotacao(falha instanceof Error ? falha.message : "Cotação indisponível."); })
      .finally(() => { if (!controller.signal.aborted) setCarregandoCotacao(false); });
    return () => controller.abort();
  }, [ticker]);

  const quantidadeAtual = ativos.find(ativo => ativo.ticker === ticker)?.quantidade;
  const quantidade = /^\d+$/.test(quantidadeTexto) ? Number(quantidadeTexto) : NaN;
  const precoUnitario = /^\d+(?:[.,]\d{1,2})?$/.test(precoTexto) ? Number(precoTexto.replace(",", ".")) : NaN;
  const valorTotal = Number.isFinite(precoUnitario) && precoUnitario > 0 && Number.isSafeInteger(quantidade) && quantidade >= 100 && quantidade % 100 === 0
    ? precoUnitario * quantidade : null;
  // A limpeza ocorre na selecao, antes de buscar os novos dados externos.
  function limparCotacao() { setCotacao(null); setPrecoTexto(""); setErroCotacao(""); }
  function selecionarCarteira(valor: string) {
    setCarteiraId(valor); setAtivos([]); setTicker(""); setTipo(null); setErro("");
    setCarregandoAtivos(!!valor); setCarregandoCotacao(false); limparCotacao();
  }
  function selecionarAtivo(valor: string) {
    setTicker(valor); setTipo(null); setErro(""); limparCotacao(); setCarregandoCotacao(!!valor);
  }
  const setor = useMemo(() => catalogo.find(ativo => ativo.ticker === ticker)?.setor ?? "", [catalogo, ticker]);

  async function enviar(evento: FormEvent<HTMLFormElement>) {
    evento.preventDefault();
    if (envioAtivo.current) return;
    setErro("");
    if (!carteiraId || !ticker) { setErro("Selecione a carteira e o ativo"); return; }
    if (!tipo) { setErro("Selecione Compra ou Venda"); return; }
    if (!quantidadeTexto.trim()) { setErro("Informe a quantidade"); return; }
    if (!Number.isSafeInteger(quantidade) || quantidade < 100 || quantidade % 100 !== 0) {
      setErro("A quantidade deve ser múltipla de 100, com mínimo de 100"); return;
    }
    if (quantidadeAtual === undefined) { setErro("O ativo não pertence à carteira selecionada"); return; }
    if (tipo === "venda" && quantidade > quantidadeAtual) {
      setErro(`Quantidade insuficiente: você possui ${quantidadeAtual} ações de ${ticker}`); return;
    }
    if (!Number.isFinite(precoUnitario) || precoUnitario <= 0) { setErro("Informe o preço unitário pago, maior que zero e com até duas casas decimais."); return; }
    envioAtivo.current = true; setRegistrando(true);
    try {
      await registrarTransacao({ id_carteira: Number(carteiraId), ticker, tipo, quantidade, preco_unitario: precoUnitario });
      navigate(`/carteiras-investidor/${carteiraId}/historico`, { replace: true, state: { mensagem: "Transação registrada e carteira atualizada." } });
    } catch (falha) {
      const mensagem = falha instanceof Error ? falha.message : "";
      if (/lotes de 100/i.test(mensagem)) setErro("A quantidade deve ser múltipla de 100, com mínimo de 100");
      else if (/quantidade insuficiente/i.test(mensagem)) setErro(`Quantidade insuficiente: você possui ${quantidadeAtual ?? 0} ações de ${ticker}`);
      else if (/ativo não encontrado nesta carteira/i.test(mensagem)) setErro("O ativo não pertence à carteira selecionada");
      else if (/conflito|erro 409|erro 5\d\d|não foi possível conectar/i.test(mensagem)) setErro("Não foi possível concluir a transação. Tente novamente");
      else setErro(mensagem || "Não foi possível concluir a transação. Tente novamente");
    } finally { envioAtivo.current = false; setRegistrando(false); }
  }

  return <section className="mx-auto w-full max-w-3xl py-4 sm:py-8" aria-labelledby="titulo-transacao">
    <Button type="button" variant="outline" className="mb-6" onClick={() => navigate(-1)}><ArrowLeftRight aria-hidden="true" />Voltar</Button>
    <Card>
      <CardHeader><CardTitle id="titulo-transacao" className="text-2xl">Transação</CardTitle><CardDescription>Registre uma compra ou venda. A carteira só será alterada após a confirmação.</CardDescription></CardHeader>
      <CardContent>
        {carregandoInicial ? <p role="status" className="flex items-center gap-2 text-sm text-muted-foreground"><LoaderCircle className="size-4 animate-spin" />Carregando carteiras...</p> : <form onSubmit={enviar} noValidate className="flex flex-col gap-6">
          {erro && <p role="alert" className="m-0 rounded-md border border-red-200 bg-red-50 p-3 text-sm text-destructive">{erro}</p>}
          <div className="grid gap-5 sm:grid-cols-2">
            <div className="flex flex-col gap-2"><label htmlFor="transacao-carteira" className="text-sm font-medium">Carteira</label><select id="transacao-carteira" className="h-10 rounded-md border border-input bg-background px-3 text-sm" value={carteiraId} onChange={evento => { selecionarCarteira(evento.target.value); }}><option value="">Selecione uma carteira</option>{carteiras.map(carteira => <option key={carteira.id_carteira} value={carteira.id_carteira}>{carteira.nome}</option>)}</select></div>
            <div className="flex flex-col gap-2"><label htmlFor="transacao-ativo" className="text-sm font-medium">Ativo</label><select id="transacao-ativo" className="h-10 rounded-md border border-input bg-background px-3 text-sm" value={ticker} disabled={!carteiraId || carregandoAtivos} onChange={evento => { selecionarAtivo(evento.target.value); }}><option value="">{carregandoAtivos ? "Carregando ativos..." : "Selecione um ativo"}</option>{ativos.map(ativo => <option key={ativo.ticker} value={ativo.ticker}>{ativo.ticker} · {catalogo.find(item => item.ticker === ativo.ticker)?.setor ?? ""} · possui {ativo.quantidade}</option>)}</select></div>
            <div className="flex flex-col gap-2"><label htmlFor="transacao-quantidade" className="text-sm font-medium">Quantidade (lotes de 100 ações)</label><Input id="transacao-quantidade" type="text" inputMode="numeric" autoComplete="off" placeholder="Ex.: 100" value={quantidadeTexto} onChange={evento => setQuantidadeTexto(evento.target.value)} /></div>
            <div className="flex flex-col gap-2"><span className="text-sm font-medium">Tipo da transação</span><div className="grid grid-cols-2 gap-2"><Button type="button" variant={tipo === "compra" ? "default" : "outline"} aria-pressed={tipo === "compra"} onClick={() => setTipo("compra")}>Compra</Button><Button type="button" variant={tipo === "venda" ? "destructive" : "outline"} aria-pressed={tipo === "venda"} onClick={() => setTipo("venda")}>Venda</Button></div></div>
          </div>
          <div className="flex flex-col gap-2"><label htmlFor="transacao-preco">Preço unitário pago (R$)</label><Input id="transacao-preco" inputMode="decimal" value={precoTexto} onChange={e => setPrecoTexto(e.target.value)} placeholder="Ex.: 40,89" /><p className="text-sm text-muted-foreground">A cotação é uma sugestão. Informe o preço efetivo da compra ou venda.</p>{cotacao && <Button type="button" variant="outline" onClick={() => setPrecoTexto(String(cotacao.preco))}>Usar cotação atual</Button>}</div>
          {ticker && <div className="rounded-lg border bg-muted/30 p-4 text-sm"><p className="mb-2">Setor: <strong>{setor || "—"}</strong></p><p className="mb-2">Quantidade atual: <strong>{quantidadeAtual ?? 0} ações</strong></p><p className="mb-2">Cotação: <strong>{carregandoCotacao ? "Consultando..." : cotacao ? moeda(cotacao.preco) : "Indisponível"}</strong></p>{erroCotacao && <p role="alert" className="mb-2 text-destructive">{erroCotacao}</p>}<p className="mb-0 text-base">{tipo ? `Total da ${tipo === "compra" ? "compra" : "venda"}` : "Valor total"}: <strong>{valorTotal === null ? "—" : moeda(valorTotal)}</strong></p></div>}
          <div className="flex justify-end"><Button type="submit" disabled={registrando || carregandoAtivos}>{registrando && <LoaderCircle className="animate-spin" aria-hidden="true" />}{registrando ? "Registrando..." : "Registrar transação"}</Button></div>
          {!carteiras.length && <p className="m-0 text-sm text-muted-foreground">Não há carteiras ativas disponíveis para transação.</p>}
        </form>}
      </CardContent>
    </Card>
  </section>;
}
