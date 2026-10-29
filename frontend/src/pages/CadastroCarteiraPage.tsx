import { useEffect, useRef, useState } from "react";
import type { FormEvent } from "react";
import { useNavigate } from "react-router-dom";
import { Check, LoaderCircle, Plus, Search, X } from "lucide-react";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Table, TableBody, TableCaption, TableCell, TableHead, TableHeader, TableRow } from "@/components/ui/table";
import { filtrarAtivos, formatarPercentual, percentualEmCentesimos, validarConfiguracao, validarInclusao } from "../lib/configuracaoCarteira";
import { consultarAtivosAceitos, consultarNomesCarteiras } from "../services/configuracaoCarteiraService";
import type { AtivoConfigurado, AtivoDisponivel } from "../types/configuracaoCarteira";

export const CadastroCarteiraPage = () => {
  const navigate = useNavigate();
  const objetivoRef = useRef<HTMLInputElement>(null);
  const [nome, setNome] = useState("");
  const [codigo, setCodigo] = useState("");
  const [objetivoInicial, setObjetivoInicial] = useState("");
  const [setor, setSetor] = useState("");
  const [catalogo, setCatalogo] = useState<AtivoDisponivel[]>([]);
  const [ativos, setAtivos] = useState<AtivoConfigurado[]>([]);
  const [nomesExistentes, setNomesExistentes] = useState<string[]>([]);
  const [carregando, setCarregando] = useState(true);
  const [conferindo, setConferindo] = useState(false);
  const [tentativa, setTentativa] = useState(0);
  const [erroCatalogo, setErroCatalogo] = useState("");
  const [avisoNomes, setAvisoNomes] = useState("");
  const [erroInclusao, setErroInclusao] = useState("");
  const [erroFormulario, setErroFormulario] = useState("");
  const [validado, setValidado] = useState(false);

  useEffect(() => {
    const controller = new AbortController();
    Promise.allSettled([consultarAtivosAceitos(controller.signal), consultarNomesCarteiras(controller.signal)])
      .then(([resultadoAtivos, resultadoNomes]) => {
        if (controller.signal.aborted) return;
        if (resultadoAtivos.status === "fulfilled") {
          setCatalogo(resultadoAtivos.value);
          setErroCatalogo("");
        } else {
          setErroCatalogo(resultadoAtivos.reason instanceof Error ? resultadoAtivos.reason.message : "Não foi possível consultar os ativos.");
        }
        if (resultadoNomes.status === "fulfilled") {
          setNomesExistentes(resultadoNomes.value);
          setAvisoNomes("");
        } else {
          setAvisoNomes("Não foi possível conferir os nomes já utilizados. A conferência será tentada novamente ao confirmar.");
        }
        setCarregando(false);
      });
    return () => controller.abort();
  }, [tentativa]);

  const setores = [...new Set(catalogo.map(ativo => ativo.setor))].sort((a, b) => a.localeCompare(b, "pt-BR"));
  const encontrados = filtrarAtivos(catalogo, codigo, setor);
  const soma = ativos.reduce((total, ativo) => total + (percentualEmCentesimos(ativo.objetivo) ?? 0), 0);
  const todosValidos = ativos.length > 0 && ativos.every(ativo => percentualEmCentesimos(ativo.objetivo) !== null);
  const totalCorreto = todosValidos && soma === 10000;

  function limparValidacao() { setErroFormulario(""); setValidado(false); }

  function incluirAtivo() {
    const erro = validarInclusao(codigo, objetivoInicial, catalogo, ativos);
    setErroInclusao(erro ?? "");
    if (erro) return;
    const ativo = catalogo.find(item => item.ticker.toUpperCase() === codigo.toUpperCase())!;
    setAtivos(anteriores => [...anteriores, { ...ativo, objetivo: objetivoInicial, quantidade: 0 }]);
    setCodigo(""); setObjetivoInicial(""); limparValidacao();
  }

  async function confirmar(evento: FormEvent<HTMLFormElement>) {
    evento.preventDefault();
    if (conferindo) return;
    setValidado(false);
    const erro = validarConfiguracao(nome, ativos, nomesExistentes);
    setErroFormulario(erro ?? "");
    if (erro) return;
    setConferindo(true);
    try {
      const nomes = await consultarNomesCarteiras();
      setNomesExistentes(nomes); setAvisoNomes("");
      const falha = validarConfiguracao(nome, ativos, nomes);
      if (falha) { setErroFormulario(falha); return; }
      // Não envia POST /portfolios: o contrato atual não aceita a composição.
      setValidado(true);
    } catch (falha) {
      setErroFormulario(falha instanceof Error ? falha.message : "Não foi possível conferir as carteiras existentes.");
    } finally { setConferindo(false); }
  }

  return (
    <section className="mx-auto w-full max-w-5xl rounded-xl border bg-card p-4 text-card-foreground shadow-sm sm:p-6" aria-labelledby="cadastro-carteira-titulo">
      <header className="mb-8 text-center">
        <h1 id="cadastro-carteira-titulo" className="mb-2 text-3xl font-semibold tracking-tight">Defina o objetivo da sua carteira</h1>
        <p className="m-0 text-sm text-muted-foreground">Dê um nome ao seu objetivo e distribua 100% entre os ativos escolhidos.</p>
      </header>
      <p className="mb-6 rounded-md border border-amber-200 bg-amber-50 p-3 text-sm text-amber-900" role="note">
        Você já pode configurar os ativos e conferir os objetivos. O salvamento da composição ainda não está disponível; confirmar não criará uma carteira nesta etapa.
      </p>
      <form onSubmit={confirmar} noValidate aria-busy={conferindo}>
        <fieldset disabled={conferindo} className="m-0 min-w-0 border-0 p-0">
          <div className="mb-8 flex flex-col gap-2">
            <label htmlFor="nome-carteira" className="text-sm font-medium">Nome da carteira</label>
            <Input id="nome-carteira" value={nome} maxLength={100} placeholder="Ex.: Aposentadoria" autoComplete="off" onChange={evento => { setNome(evento.target.value); limparValidacao(); }} />
          </div>
          <h2 className="mb-2 text-xl font-semibold">Configure os Ativos</h2>
          <p className="mb-5 text-sm text-muted-foreground">Busque um código, selecione o ativo e informe seu objetivo (%). O setor é preenchido pelo cadastro do ativo.</p>
          <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-4">
            <div className="flex flex-col gap-2 lg:col-span-2">
              <label htmlFor="busca-ativo" className="text-sm font-medium">Código do ativo</label>
              <div className="relative">
                <Search aria-hidden="true" className="absolute left-3 top-1/2 size-4 -translate-y-1/2 text-muted-foreground" />
                <Input id="busca-ativo" placeholder="Busque por código, ex.: ITUB" className="pl-9" autoComplete="off" value={codigo} onChange={evento => { setCodigo(evento.target.value.toUpperCase()); setErroInclusao(""); }} />
              </div>
            </div>
            <div className="flex flex-col gap-2">
              <label htmlFor="setor-ativo" className="text-sm font-medium">Setor</label>
              <select id="setor-ativo" className="h-9 w-full rounded-md border border-input bg-background px-3 text-sm" value={setor} onChange={evento => setSetor(evento.target.value)}>
                <option value="">Todos os setores</option>
                {setores.map(item => <option key={item} value={item}>{item}</option>)}
              </select>
            </div>
            <div className="flex flex-col gap-2">
              <label htmlFor="objetivo-inicial" className="text-sm font-medium">Objetivo (%)</label>
              <Input ref={objetivoRef} id="objetivo-inicial" inputMode="decimal" placeholder="Ex.: 20" value={objetivoInicial} onChange={evento => { setObjetivoInicial(evento.target.value); setErroInclusao(""); }} />
            </div>
          </div>
          <div className="my-4 flex justify-end">
            <Button type="button" onClick={incluirAtivo} disabled={carregando || !!erroCatalogo}><Plus aria-hidden="true" />Incluir ativo</Button>
          </div>
          {erroInclusao && <p role="alert" className="mb-4 text-sm text-destructive">{erroInclusao}</p>}
          <div className="mb-6 rounded-md border bg-muted/30 p-3" aria-label="Lista de ativos aceitos" aria-busy={carregando}>
            {carregando ? <p role="status" className="m-0 flex items-center gap-2 text-sm text-muted-foreground"><LoaderCircle className="size-4 animate-spin" aria-hidden="true" />Carregando ativos...</p>
              : erroCatalogo ? <div><p role="alert" className="mb-3 text-sm text-destructive">{erroCatalogo}</p><Button type="button" variant="outline" onClick={() => { setCarregando(true); setTentativa(t => t + 1); }}>Tentar novamente</Button></div>
              : encontrados.length === 0 ? <p role="status" className="m-0 text-sm text-muted-foreground">Nenhum ativo encontrado</p>
              : <><p className="mb-3 text-xs text-muted-foreground">Selecione um código abaixo e informe o objetivo para incluí-lo.</p><ul className="m-0 grid list-none gap-2 p-0 sm:grid-cols-2">
                {encontrados.slice(0, 8).map(ativo => <li key={ativo.ticker}>
                  <Button type="button" variant="outline" className="h-auto w-full justify-start whitespace-normal py-2 text-left" aria-label={`Selecionar ${ativo.ticker}, setor ${ativo.setor}`} onClick={() => { setCodigo(ativo.ticker); setErroInclusao(""); objetivoRef.current?.focus(); }}>
                    <span className="font-semibold">{ativo.ticker}</span><span className="text-xs text-muted-foreground">{ativo.setor}</span>
                  </Button>
                </li>)}
              </ul>{encontrados.length > 8 && <p className="mb-0 mt-3 text-xs text-muted-foreground">Mostrando 8 de {encontrados.length} ativos. Refine a busca ou selecione um setor.</p>}</>}
          </div>
          <div className="overflow-hidden rounded-md border">
            <Table>
              <TableCaption className="sr-only">Ativos configurados para a nova carteira</TableCaption>
              <TableHeader><TableRow className="bg-muted"><TableHead>Ativo</TableHead><TableHead>Setor</TableHead><TableHead>Objetivo (%)</TableHead><TableHead className="text-right">Remover</TableHead></TableRow></TableHeader>
              <TableBody>
                {ativos.map(ativo => <TableRow key={ativo.ticker} className="even:bg-muted/30">
                  <TableCell className="font-medium">{ativo.ticker}</TableCell><TableCell>{ativo.setor}</TableCell>
                  <TableCell><Input className="w-28" inputMode="decimal" aria-label={`Objetivo de ${ativo.ticker} (%)`} aria-invalid={percentualEmCentesimos(ativo.objetivo) === null} value={ativo.objetivo} onChange={evento => { setAtivos(itens => itens.map(item => item.ticker === ativo.ticker ? { ...item, objetivo: evento.target.value } : item)); limparValidacao(); }} /></TableCell>
                  <TableCell className="text-right"><Button type="button" size="icon" variant="ghost" aria-label={`Remover ${ativo.ticker} da carteira`} onClick={() => { setAtivos(itens => itens.filter(item => item.ticker !== ativo.ticker)); limparValidacao(); }}><X aria-hidden="true" /></Button></TableCell>
                </TableRow>)}
                {!ativos.length && <TableRow><TableCell colSpan={4} className="py-8 text-center text-muted-foreground">Nenhum ativo incluído na carteira.</TableCell></TableRow>}
              </TableBody>
            </Table>
          </div>
          <div className="my-4 flex flex-col gap-2 sm:flex-row sm:items-center sm:justify-between">
            <p className="m-0 text-xs text-muted-foreground">A quantidade inicial será zero. Incluir ou remover ativos aqui não registra compras ou vendas.</p>
            <p role="status" className={`m-0 whitespace-nowrap text-sm font-semibold ${totalCorreto ? "text-emerald-700" : "text-muted-foreground"}`}>Objetivo total: {formatarPercentual(soma)}% de 100%</p>
          </div>
        </fieldset>
        {avisoNomes && <p className="my-4 text-sm text-amber-800">{avisoNomes}</p>}
        {erroFormulario && <p role="alert" className="my-4 rounded-md border border-red-200 bg-red-50 p-3 text-sm text-destructive">{erroFormulario}</p>}
        {validado && <p role="status" className="my-4 flex items-start gap-2 rounded-md border border-amber-200 bg-amber-50 p-3 text-sm text-amber-900"><Check className="size-4 shrink-0" aria-hidden="true" />Configuração válida. Nenhuma carteira foi salva: o salvamento dos ativos e objetivos ainda precisa ser habilitado.</p>}
        <div className="mt-6 flex flex-col-reverse gap-3 border-t pt-6 sm:flex-row sm:justify-end">
          <Button type="button" variant="outline" disabled={conferindo} onClick={() => navigate("/carteiras-investidor")}>Cancelar</Button>
          <Button type="submit" disabled={conferindo}>{conferindo ? "Conferindo..." : "Confirmar"}</Button>
        </div>
      </form>
    </section>
  );
};
