import { useEffect, useState } from "react";
import { LoaderCircle, Pencil, UserRound } from "lucide-react";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { FormularioInvestidor, type DadosFormularioInvestidor } from "../components/FormularioInvestidor";
import { atualizarMeuPerfilInvestidor, buscarMeuPerfilInvestidor } from "../services/investidorService";
import type { Investidor } from "../types/investidor";

function DadoConta({ titulo, valor }: { titulo: string; valor: string }) {
  return <div className="min-w-0 space-y-1">
    <dt className="text-sm text-muted-foreground">{titulo}</dt>
    <dd className="m-0 break-words text-sm font-medium text-foreground">{valor || "Não informado"}</dd>
  </div>;
}

export function MinhaContaInvestidorPage() {
  const [investidor, setInvestidor] = useState<Investidor | null>(null);
  const [estaEditando, setEstaEditando] = useState(false);
  const [carregando, setCarregando] = useState(true);
  const [salvando, setSalvando] = useState(false);
  const [mensagemErro, setMensagemErro] = useState("");
  const [erroEdicao, setErroEdicao] = useState("");
  const [mensagemSucesso, setMensagemSucesso] = useState("");

  useEffect(() => {
    let ativo = true;
    buscarMeuPerfilInvestidor()
      .then(dados => { if (ativo) setInvestidor(dados); })
      .catch((erro: unknown) => {
        if (ativo) setMensagemErro(erro instanceof Error ? erro.message : "Não foi possível carregar o perfil.");
      })
      .finally(() => { if (ativo) setCarregando(false); });
    return () => { ativo = false; };
  }, []);

  async function salvarMinhaConta(dados: DadosFormularioInvestidor) {
    if (salvando) return;
    setSalvando(true);
    setErroEdicao("");
    try {
      const atualizado = await atualizarMeuPerfilInvestidor(dados);
      setInvestidor(atualizado);
      setEstaEditando(false);
      setMensagemSucesso("Conta atualizada com sucesso.");
    } catch (erro) {
      setErroEdicao(erro instanceof Error ? erro.message : "Não foi possível atualizar sua conta.");
    } finally { setSalvando(false); }
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
        <p className="m-0 text-sm text-muted-foreground">Consulte e atualize seus dados pessoais e de contato.</p>
      </div>
      {!estaEditando && <Button onClick={() => { setEstaEditando(true); setErroEdicao(""); setMensagemSucesso(""); }}>
        <Pencil aria-hidden="true" /> Editar dados
      </Button>}
    </header>

    {mensagemSucesso && <p role="status" className="mb-6 rounded-lg border border-emerald-200 bg-emerald-50 p-4 text-sm text-emerald-800">{mensagemSucesso}</p>}

    {estaEditando ? <Card>
      <CardHeader>
        <CardTitle>Dados cadastrais</CardTitle>
        <CardDescription>O CPF permanece vinculado à sua conta e não pode ser alterado aqui.</CardDescription>
      </CardHeader>
      <CardContent>
        {erroEdicao && <p role="alert" className="mb-4 rounded-md border border-red-200 bg-red-50 p-3 text-sm text-destructive">{erroEdicao}</p>}
        <FormularioInvestidor key={investidor.id} investidor={investidor} onSalvar={salvarMinhaConta}
          onCancelar={() => { setEstaEditando(false); setErroEdicao(""); }} permitirAlterarCpf={false}
          textoBotaoSalvar="Salvar alterações" usarShadcn salvando={salvando} />
      </CardContent>
    </Card> : <div className="grid gap-6">
      <Card>
        <CardHeader className="flex flex-col gap-4 sm:flex-row sm:items-center sm:justify-between">
          <div className="flex items-center gap-3">
            <div className="flex size-11 items-center justify-center rounded-xl bg-secondary text-muted-foreground"><UserRound aria-hidden="true" className="size-5" /></div>
            <div><CardTitle>Dados pessoais</CardTitle><CardDescription className="mb-0 mt-1">Perfil de investidor</CardDescription></div>
          </div>
          <span className={investidor.status === "ativo" ? "w-fit rounded-full bg-emerald-50 px-3 py-1 text-xs font-medium text-emerald-800" : "w-fit rounded-full bg-red-50 px-3 py-1 text-xs font-medium text-red-800"}>
            {investidor.status === "ativo" ? "Conta ativa" : "Conta bloqueada"}
          </span>
        </CardHeader>
        <CardContent><dl className="m-0 grid gap-6 sm:grid-cols-2 lg:grid-cols-3">
          <DadoConta titulo="Nome" valor={investidor.nome} />
          <DadoConta titulo="Sobrenome" valor={investidor.sobrenome} />
          <DadoConta titulo="CPF" valor={investidor.cpf} />
          <DadoConta titulo="E-mail" valor={investidor.email} />
          <DadoConta titulo="Celular" valor={investidor.celular} />
        </dl></CardContent>
      </Card>
      <Card>
        <CardHeader><CardTitle>Endereço</CardTitle><CardDescription>Endereço informado no seu cadastro.</CardDescription></CardHeader>
        <CardContent><dl className="m-0 grid gap-6 sm:grid-cols-2 lg:grid-cols-3">
          <DadoConta titulo="Rua" valor={investidor.rua} />
          <DadoConta titulo="Número" valor={investidor.numero} />
          <DadoConta titulo="Bairro" valor={investidor.bairro} />
          <DadoConta titulo="CEP" valor={investidor.cep} />
          <DadoConta titulo="Cidade" valor={investidor.cidade} />
          <DadoConta titulo="UF" valor={investidor.uf} />
        </dl></CardContent>
      </Card>
    </div>}
  </section>;
}
