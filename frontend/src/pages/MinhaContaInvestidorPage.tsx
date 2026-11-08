import { useEffect, useRef, useState } from "react";
import { LoaderCircle, Pencil, UserRound } from "lucide-react";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { FormularioContaInvestidor } from "../components/FormularioContaInvestidor";
import { buscarContaInvestidor, salvarContaInvestidor } from "../services/contaInvestidorService";
import type { ContaInvestidor, EdicaoContaInvestidor } from "../types/contaInvestidor";

function DadoConta({ titulo, valor }: { titulo: string; valor: string }) {
  return <div className="min-w-0 space-y-1">
    <dt className="text-sm text-muted-foreground">{titulo}</dt>
    <dd className="m-0 break-words text-sm font-medium text-foreground">{valor || "Não informado"}</dd>
  </div>;
}

export function MinhaContaInvestidorPage() {
  const [investidor, setInvestidor] = useState<ContaInvestidor | null>(null);
  const [estaEditando, setEstaEditando] = useState(false);
  const [carregando, setCarregando] = useState(true);
  const [salvando, setSalvando] = useState(false);
  const requisicaoAtiva = useRef(false);
  const [mensagemErro, setMensagemErro] = useState("");
  const [erroEdicao, setErroEdicao] = useState("");
  const [mensagemSucesso, setMensagemSucesso] = useState("");

  useEffect(() => {
    let ativo = true;
    buscarContaInvestidor()
      .then(dados => { if (ativo) setInvestidor(dados); })
      .catch((erro: unknown) => {
        if (ativo) setMensagemErro(erro instanceof Error ? erro.message : "Não foi possível carregar o perfil.");
      })
      .finally(() => { if (ativo) setCarregando(false); });
    return () => { ativo = false; };
  }, []);

  async function salvarMinhaConta(dados: EdicaoContaInvestidor) {
    if (requisicaoAtiva.current) return;
    requisicaoAtiva.current = true;
    setSalvando(true);
    setErroEdicao("");
    try {
      const atualizado = await salvarContaInvestidor(dados);
      setInvestidor(atualizado);
      setEstaEditando(false);
      setMensagemSucesso("Conta atualizada com sucesso.");
    } catch (erro) {
      setErroEdicao(erro instanceof Error ? erro.message : "Não foi possível atualizar sua conta.");
    } finally { requisicaoAtiva.current = false; setSalvando(false); }
  }

  if (carregando) {
    return <section className="mx-auto w-full max-w-5xl py-4 sm:py-8" aria-busy="true">
      <Card><CardContent className="flex items-center gap-3 p-6">
        <LoaderCircle className="size-5 animate-spin text-muted-foreground" aria-hidden="true" />
        <p className="m-0 text-sm text-muted-foreground" role="status">Carregando sua conta...</p>
      </CardContent></Card>
    </section>;
  }

  if (mensagemErro || !investidor) {
    return <section className="mx-auto w-full max-w-5xl py-4 sm:py-8">
      <Card><CardHeader>
        <CardTitle><h1 className="m-0 text-xl">Não foi possível abrir sua conta</h1></CardTitle>
        <CardDescription role="alert">{mensagemErro || "Perfil de investidor não encontrado."}</CardDescription>
      </CardHeader><CardContent>
        <Button variant="outline" onClick={() => window.location.reload()}>Tentar novamente</Button>
      </CardContent></Card>
    </section>;
  }

  return <section className="mx-auto w-full max-w-5xl py-4 sm:py-8" aria-labelledby="titulo-conta">
    <header className="mb-8 flex flex-col gap-4 sm:flex-row sm:items-center sm:justify-between">
      <div>
        <h1 id="titulo-conta" className="mb-2 text-3xl font-semibold tracking-tight text-foreground">
          {estaEditando ? "Editar Minha Conta" : "Minha Conta"}
        </h1>
        <p className="m-0 text-sm text-muted-foreground">Consulte e atualize seu usuário, e-mails e senha.</p>
      </div>
      {!estaEditando && <Button onClick={() => { setEstaEditando(true); setErroEdicao(""); setMensagemSucesso(""); }}>
        <Pencil aria-hidden="true" /> Editar dados
      </Button>}
    </header>

    {mensagemSucesso && <p role="status" className="mb-6 rounded-lg border border-emerald-200 bg-emerald-50 p-4 text-sm text-emerald-800">{mensagemSucesso}</p>}

    {estaEditando ? <Card>
      <CardHeader>
        <CardTitle>Dados da conta</CardTitle>
        <CardDescription>Atualize seu usuário e seus e-mails. Para trocar a senha, preencha também a nova senha e a confirmação.</CardDescription>
      </CardHeader>
      <CardContent>
        {erroEdicao && <p role="alert" className="mb-4 rounded-md border border-red-200 bg-red-50 p-3 text-sm text-destructive">{erroEdicao}</p>}
        <FormularioContaInvestidor key={investidor.id} conta={investidor} onSalvar={salvarMinhaConta}
          onCancelar={() => { setEstaEditando(false); setErroEdicao(""); }} salvando={salvando} />
      </CardContent>
    </Card> : <div className="grid gap-6">
      <Card>
        <CardHeader className="flex flex-col gap-4 sm:flex-row sm:items-center sm:justify-between">
          <div className="flex items-center gap-3">
            <div className="flex size-11 items-center justify-center rounded-xl bg-secondary text-muted-foreground"><UserRound aria-hidden="true" className="size-5" /></div>
            <div><CardTitle>Dados da conta</CardTitle><CardDescription className="mb-0 mt-1">Perfil de investidor</CardDescription></div>
          </div>
          <span className={investidor.ativo ? "w-fit rounded-full bg-emerald-50 px-3 py-1 text-xs font-medium text-emerald-800" : "w-fit rounded-full bg-red-50 px-3 py-1 text-xs font-medium text-red-800"}>
            {investidor.ativo ? "Conta ativa" : "Conta bloqueada"}
          </span>
        </CardHeader>
        <CardContent><dl className="m-0 grid gap-6 sm:grid-cols-2 lg:grid-cols-3">
          <DadoConta titulo="Usuário" valor={investidor.nomeUsuario} />
          <DadoConta titulo="E-mail comunicação" valor={investidor.emailComunicacao} />
          <DadoConta titulo="E-mail recuperação" valor={investidor.emailRecuperacao} />
          <DadoConta titulo="Senha" valor="**************" />
        </dl></CardContent>
      </Card>
    </div>}
  </section>;
}
