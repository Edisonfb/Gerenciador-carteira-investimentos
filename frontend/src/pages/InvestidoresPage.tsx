import { useEffect, useState } from "react";
import { useLocation, useNavigate } from "react-router-dom";
import { LoaderCircle, MailPlus, RefreshCw, Search } from "lucide-react";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Card, CardContent } from "@/components/ui/card";
import { TabelaInvestidores } from "../components/TabelaInvestidores";
import { GerarTokenInvestidorDialog } from "../components/GerarTokenInvestidorDialog";
import { buscarUsuarioAutenticado } from "../services/autenticacaoService";
import { combinarContasEConvites, filtrarContasInvestidores, listarContasInvestidores } from "../services/consultaInvestidoresService";
import type { ContaInvestidorConsulta } from "../services/consultaInvestidoresService";
import type { ConviteInvestidor } from "../services/conviteInvestidorService";

export function InvestidoresPage() {
  const navigate = useNavigate();
  const location = useLocation();
  const usuarioAutenticado = buscarUsuarioAutenticado();
  const analista = usuarioAutenticado?.perfil === "analista";
  const idUsuario = usuarioAutenticado?.id;
  const deveAbrir = (location.state as { abrirConvite?: boolean } | null)?.abrirConvite === true;
  const [popupAberto, setPopupAberto] = useState(deveAbrir);
  const [investidores, setInvestidores] = useState<ContaInvestidorConsulta[]>([]);
  const [convites, setConvites] = useState<ConviteInvestidor[]>([]);
  const [ultimoConvite, setUltimoConvite] = useState<ConviteInvestidor | null>(null);
  const [busca, setBusca] = useState("");
  const [situacao, setSituacao] = useState("todas");
  const [carregando, setCarregando] = useState(true);
  const [carregou, setCarregou] = useState(false);
  const [erroConsulta, setErroConsulta] = useState("");
  const [consulta, setConsulta] = useState(0);

  useEffect(() => {
    if (deveAbrir) navigate(location.pathname, { replace: true, state: null });
  }, [deveAbrir, location.pathname, navigate]);

  useEffect(() => {
    if (!analista) return;
    const controller = new AbortController();
    listarContasInvestidores(controller.signal)
      .then(contas => {
        if (controller.signal.aborted) return;
        setInvestidores(contas); setCarregou(true); setErroConsulta("");
      })
      .catch(erro => {
        if (!controller.signal.aborted) setErroConsulta(erro instanceof Error ? erro.message : "Não foi possível consultar os investidores.");
      })
      .finally(() => { if (!controller.signal.aborted) setCarregando(false); });
    return () => controller.abort();
  }, [analista, idUsuario, consulta]);

  if (!analista) return <section className="mx-auto max-w-5xl py-8"><Card><CardContent className="p-6"><h1 className="text-xl font-semibold">Acesso não permitido</h1><p className="mb-0 text-sm text-muted-foreground">Esta página é destinada à consulta de investidores pelo analista.</p></CardContent></Card></section>;

  function conviteGerado(convite: ConviteInvestidor) {
    setConvites(anteriores => [...anteriores.filter(item => item.id_usuario !== convite.id_usuario), convite]);
    setUltimoConvite(convite); setPopupAberto(false);
  }

  function atualizar() {
    setCarregando(true); setErroConsulta("");
    // A consulta não fornece estes status; evita manter um retrato antigo como se fosse atual.
    setConvites([]); setUltimoConvite(null);
    setConsulta(versao => versao + 1);
  }

  const contas = combinarContasEConvites(investidores, convites);
  const filtrados = filtrarContasInvestidores(contas, busca, situacao);

  return <section className="mx-auto w-full max-w-6xl py-4 sm:py-8" aria-labelledby="titulo-investidores">
    <header className="mb-8 flex flex-col gap-4 sm:flex-row sm:items-center sm:justify-between">
      <div><h1 id="titulo-investidores" className="mb-2 text-3xl font-semibold tracking-tight">Investidores</h1><p className="m-0 text-sm text-muted-foreground">Localize contas pelo e-mail e consulte sua situação.</p></div>
      <Button type="button" onClick={() => { setUltimoConvite(null); setPopupAberto(true); }}><MailPlus aria-hidden="true" />Gerar token de acesso</Button>
    </header>
    {ultimoConvite && <p role="status" className={`mb-6 rounded-lg border p-4 text-sm ${ultimoConvite.email_acesso_enviado ? "border-emerald-200 bg-emerald-50 text-emerald-900" : "border-amber-200 bg-amber-50 text-amber-900"}`}>
      {ultimoConvite.email_acesso_enviado ? `Convite gerado e encaminhado para ${ultimoConvite.email}.` : `Convite criado para ${ultimoConvite.email}. O servidor não confirmou o envio do e-mail. Confira o recebimento antes de tentar gerar outro convite.`}
    </p>}
    <Card className="overflow-hidden">
      <CardContent className="p-0">
        <div className="flex flex-col gap-4 border-b p-4 sm:flex-row sm:items-end sm:p-6">
          <div className="flex flex-1 flex-col gap-2"><label htmlFor="busca-investidor" className="text-sm font-medium">Buscar por e-mail</label><div className="relative"><Search className="absolute left-3 top-1/2 size-4 -translate-y-1/2 text-muted-foreground" aria-hidden="true" /><Input id="busca-investidor" type="search" className="pl-9" placeholder="Digite o e-mail ou parte dele" value={busca} onChange={evento => setBusca(evento.target.value)} /></div></div>
          <div className="flex flex-col gap-2"><label htmlFor="situacao-investidor" className="text-sm font-medium">Situação da conta</label><select id="situacao-investidor" className="h-9 rounded-md border border-input bg-background px-3 text-sm" value={situacao} onChange={evento => setSituacao(evento.target.value)}><option value="todas">Todas</option><option value="ativas">Ativas</option><option value="inativas">Inativas</option></select></div>
          <Button type="button" variant="outline" disabled={carregando} onClick={atualizar}><RefreshCw aria-hidden="true" className={carregando ? "animate-spin" : undefined} />Atualizar</Button>
        </div>
        {erroConsulta && <div role="alert" className="m-4 rounded-md border border-red-200 bg-red-50 p-3 text-sm text-destructive">{erroConsulta}{carregou && " Os dados da consulta anterior continuam sendo exibidos."}</div>}
        {carregando && <p role="status" className="m-0 flex items-center gap-2 p-6 text-sm text-muted-foreground"><LoaderCircle className="size-4 animate-spin" aria-hidden="true" />Consultando investidores...</p>}
        {(carregou || convites.length > 0) && <div aria-busy={carregando}><TabelaInvestidores investidores={filtrados} buscaAtiva={!!busca.trim() || situacao !== "todas"} /><p role="status" className="m-0 border-t px-6 py-3 text-xs text-muted-foreground">{filtrados.length} de {contas.length} conta(s) de investidor</p></div>}
      </CardContent>
    </Card>
    <GerarTokenInvestidorDialog aberto={popupAberto} onFechar={() => setPopupAberto(false)} onGerado={conviteGerado} />
  </section>;
}
