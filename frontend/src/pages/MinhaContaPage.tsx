import { useEffect, useState } from "react";
import type { FormEvent } from "react";
import { LoaderCircle, Pencil, UserRound } from "lucide-react";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { atualizarMinhaContaAnalista, buscarMinhaContaAnalista } from "../services/contaAnalistaService";
import type { ContaAnalista } from "../services/contaAnalistaService";

export function MinhaContaPage() {
  const [conta, setConta] = useState<ContaAnalista | null>(null);
  const [carregando, setCarregando] = useState(true);
  const [editando, setEditando] = useState(false);
  const [salvando, setSalvando] = useState(false);
  const [nome, setNome] = useState("");
  const [email, setEmail] = useState("");
  const [erro, setErro] = useState("");
  const [sucesso, setSucesso] = useState("");

  useEffect(() => {
    let ativo = true;
    buscarMinhaContaAnalista().then(dados => {
      if (ativo) { setConta(dados); setNome(dados.nome); setEmail(dados.email); }
    }).catch(falha => { if (ativo) setErro(falha instanceof Error ? falha.message : "Não foi possível carregar sua conta."); })
      .finally(() => { if (ativo) setCarregando(false); });
    return () => { ativo = false; };
  }, []);

  async function salvar(evento: FormEvent<HTMLFormElement>) {
    evento.preventDefault();
    if (salvando) return;
    setErro(""); setSucesso("");
    if (!nome.trim()) { setErro("Informe seu nome."); return; }
    if (!/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(email.trim())) { setErro("Informe um e-mail válido."); return; }
    setSalvando(true);
    try {
      const atualizada = await atualizarMinhaContaAnalista({ nome: nome.trim(), email: email.trim() });
      setConta(atualizada); setNome(atualizada.nome); setEmail(atualizada.email); setEditando(false);
      setSucesso("Conta atualizada com sucesso.");
    } catch (falha) { setErro(falha instanceof Error ? falha.message : "Não foi possível atualizar sua conta."); }
    finally { setSalvando(false); }
  }

  return <section className="mx-auto w-full max-w-5xl py-4 sm:py-8" aria-labelledby="titulo-conta-analista">
    <header className="mb-8 flex flex-col gap-4 sm:flex-row sm:items-center sm:justify-between">
      <div><h1 id="titulo-conta-analista" className="mb-2 text-3xl font-semibold tracking-tight">Minha Conta</h1><p className="m-0 text-sm text-muted-foreground">Consulte e atualize os dados da sua conta de analista.</p></div>
      {conta && !editando && <Button onClick={() => { setEditando(true); setSucesso(""); setErro(""); }}><Pencil aria-hidden="true" />Editar dados</Button>}
    </header>
    {erro && <p role="alert" className="mb-6 rounded-md border border-red-200 bg-red-50 p-4 text-sm text-destructive">{erro}</p>}
    {sucesso && <p role="status" className="mb-6 rounded-md border border-emerald-200 bg-emerald-50 p-4 text-sm text-emerald-800">{sucesso}</p>}
    <Card>
      <CardHeader><div className="mb-3 flex size-11 items-center justify-center rounded-xl bg-secondary"><UserRound className="size-5 text-muted-foreground" aria-hidden="true" /></div><CardTitle>Dados do analista</CardTitle><CardDescription>Informações vinculadas à sua conta de acesso.</CardDescription></CardHeader>
      <CardContent>
        {carregando ? <p role="status" className="m-0 flex items-center gap-2 text-sm text-muted-foreground"><LoaderCircle className="size-4 animate-spin" aria-hidden="true" />Carregando sua conta...</p>
          : !conta ? <Button variant="outline" onClick={() => window.location.reload()}>Tentar novamente</Button>
          : editando ? <form onSubmit={salvar} noValidate aria-busy={salvando}>
            <fieldset disabled={salvando} className="m-0 grid min-w-0 gap-5 border-0 p-0 sm:grid-cols-2">
              <div className="flex flex-col gap-2"><label htmlFor="nome-analista" className="text-sm font-medium">Nome</label><Input id="nome-analista" maxLength={50} value={nome} onChange={evento => setNome(evento.target.value)} /></div>
              <div className="flex flex-col gap-2"><label htmlFor="email-analista" className="text-sm font-medium">E-mail</label><Input id="email-analista" type="email" maxLength={255} autoComplete="email" value={email} onChange={evento => setEmail(evento.target.value)} /></div>
            </fieldset>
            <div className="mt-6 flex justify-end gap-3 border-t pt-6"><Button type="button" variant="outline" disabled={salvando} onClick={() => { setEditando(false); setNome(conta.nome); setEmail(conta.email); setErro(""); }}>Cancelar</Button><Button disabled={salvando} type="submit">{salvando ? "Salvando..." : "Salvar alterações"}</Button></div>
          </form>
          : <dl className="m-0 grid gap-6 sm:grid-cols-2">
            <div><dt className="mb-1 text-sm text-muted-foreground">Nome</dt><dd className="m-0 break-words font-medium">{conta.nome}</dd></div>
            <div><dt className="mb-1 text-sm text-muted-foreground">E-mail</dt><dd className="m-0 break-words font-medium">{conta.email}</dd></div>
            <div><dt className="mb-1 text-sm text-muted-foreground">Perfil</dt><dd className="m-0 font-medium">Analista</dd></div>
            <div><dt className="mb-1 text-sm text-muted-foreground">Status</dt><dd className={`m-0 font-medium ${conta.ativo ? "text-emerald-700" : "text-destructive"}`}>{conta.ativo ? "Ativo" : "Inativo"}</dd></div>
          </dl>}
      </CardContent>
    </Card>
  </section>;
}
