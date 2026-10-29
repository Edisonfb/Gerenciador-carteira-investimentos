import { useRef, useState } from "react";
import type { FormEvent } from "react";
import { Link, useLocation, useNavigate } from "react-router-dom";
import { LoaderCircle } from "lucide-react";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from "@/components/ui/card";
import { validarCadastroPrimeiroAcesso } from "../lib/primeiroAcesso";
import type { CadastroPrimeiroAcesso } from "../lib/primeiroAcesso";
import { concluirCadastroPrimeiroAcesso } from "../services/primeiroAcessoService";

export function CadastroPrimeiroAcessoPage() {
  const location = useLocation();
  const navigate = useNavigate();
  const estado = location.state as { tokenDefinicao?: string; emailConvite?: string } | null;
  const token = typeof estado?.tokenDefinicao === "string" ? estado.tokenDefinicao : "";
  const [dados, setDados] = useState<CadastroPrimeiroAcesso>({ nomeUsuario: "", emailComunicacao: estado?.emailConvite ?? "", emailRecuperacao: "", senha: "", confirmacaoSenha: "" });
  const [erro, setErro] = useState("");
  const [enviando, setEnviando] = useState(false);
  const requisicaoAtiva = useRef(false);
  function alterar(campo: keyof CadastroPrimeiroAcesso, valor: string) {
    setDados(anteriores => ({ ...anteriores, [campo]: valor })); setErro("");
  }
  async function salvar(evento: FormEvent<HTMLFormElement>) {
    evento.preventDefault();
    if (requisicaoAtiva.current || !token) return;
    const falha = validarCadastroPrimeiroAcesso(dados);
    setErro(falha ?? "");
    if (falha) return;
    requisicaoAtiva.current = true; setEnviando(true);
    try {
      await concluirCadastroPrimeiroAcesso(token, dados);
      navigate("/", { replace: true, state: { mensagemSucesso: "Cadastro concluído com sucesso. Entre com seu nome de usuário e sua senha." } });
    } catch (falha) {
      setErro(falha instanceof Error ? falha.message : "Não foi possível concluir o cadastro.");
    } finally { requisicaoAtiva.current = false; setEnviando(false); }
  }
  return <section className="mx-auto my-8 w-full max-w-lg" aria-labelledby="titulo-cadastro-primeiro-acesso">
    <Card>
      <CardHeader>
        <CardTitle><h1 id="titulo-cadastro-primeiro-acesso" className="m-0 text-2xl font-semibold">Complete seu cadastro</h1></CardTitle>
        <CardDescription>Defina seu usuário, os e-mails de contato e a senha para acessar sua conta.</CardDescription>
      </CardHeader>
      <CardContent>
        {!token && <p role="alert" className="mb-5 rounded-md border border-destructive/30 p-3 text-sm text-destructive">Valide seu e-mail e token na <Link to="/primeiro-acesso" className="underline">tela de primeiro acesso</Link> antes de continuar.</p>}
        <form onSubmit={salvar} className="flex flex-col gap-5" aria-busy={enviando}>
          <fieldset disabled={enviando || !token} className="m-0 flex min-w-0 flex-col gap-5 border-0 p-0">
            <div className="flex flex-col gap-2"><label htmlFor="cadastro-usuario" className="text-sm font-medium">Usuário</label><Input id="cadastro-usuario" name="nome_usuario" autoComplete="username" autoCapitalize="none" spellCheck={false} required maxLength={50} value={dados.nomeUsuario} onChange={e => alterar("nomeUsuario", e.target.value)} /></div>
            <div className="flex flex-col gap-2"><label htmlFor="cadastro-email-comunicacao" className="text-sm font-medium">E-mail de comunicação</label><Input id="cadastro-email-comunicacao" type="email" autoComplete="email" required maxLength={255} value={dados.emailComunicacao} onChange={e => alterar("emailComunicacao", e.target.value)} /><p className="m-0 text-xs text-muted-foreground">Usado para as comunicações da sua conta.</p></div>
            <div className="flex flex-col gap-2"><label htmlFor="cadastro-email-recuperacao" className="text-sm font-medium">E-mail de recuperação</label><Input id="cadastro-email-recuperacao" type="email" required maxLength={255} value={dados.emailRecuperacao} onChange={e => alterar("emailRecuperacao", e.target.value)} /><p className="m-0 text-xs text-muted-foreground">Informe um endereço diferente do e-mail de comunicação para recuperar sua senha.</p></div>
            <div className="flex flex-col gap-2"><label htmlFor="cadastro-senha" className="text-sm font-medium">Senha</label><Input id="cadastro-senha" type="password" autoComplete="new-password" required minLength={8} maxLength={72} aria-describedby="cadastro-regra-senha" value={dados.senha} onChange={e => alterar("senha", e.target.value)} /><p id="cadastro-regra-senha" className="m-0 text-xs text-muted-foreground">No mínimo 8 caracteres e no máximo 72 bytes.</p></div>
            <div className="flex flex-col gap-2"><label htmlFor="cadastro-confirmacao" className="text-sm font-medium">Confirmação de senha</label><Input id="cadastro-confirmacao" type="password" autoComplete="new-password" required minLength={8} maxLength={72} value={dados.confirmacaoSenha} onChange={e => alterar("confirmacaoSenha", e.target.value)} /></div>
          </fieldset>
          {erro && <p role="alert" className="m-0 rounded-md border border-destructive/30 p-3 text-sm text-destructive">{erro}</p>}
          <div className="flex flex-col-reverse gap-3 sm:flex-row sm:justify-end">
            <Button type="button" variant="outline" disabled={enviando} onClick={() => navigate("/", { replace: true })}>Cancelar</Button>
            <Button type="submit" disabled={enviando || !token}>{enviando && <LoaderCircle className="animate-spin" aria-hidden="true" />}{enviando ? "Salvando..." : "Concluir cadastro"}</Button>
          </div>
        </form>
      </CardContent>
    </Card>
  </section>;
}
