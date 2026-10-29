import { useRef, useState } from "react";
import type { FormEvent } from "react";
import { Link, useLocation, useNavigate } from "react-router-dom";
import { LoaderCircle } from "lucide-react";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { realizarLogin } from "../services/autenticacaoService";

export const Login = () => {
  const navigate = useNavigate();
  const location = useLocation();
  const mensagemSucesso = (location.state as { mensagemSucesso?: string } | null)?.mensagemSucesso;
  const [nomeUsuario, setNomeUsuario] = useState("");
  const [senha, setSenha] = useState("");
  const [mensagemErro, setMensagemErro] = useState("");
  const [carregando, setCarregando] = useState(false);
  const requisicaoAtiva = useRef(false);

  async function enviarLogin(evento: FormEvent<HTMLFormElement>) {
    evento.preventDefault();
    if (requisicaoAtiva.current) return;
    requisicaoAtiva.current = true;
    setCarregando(true);
    setMensagemErro("");
    try {
      const usuario = await realizarLogin(nomeUsuario.trim(), senha);
      navigate(usuario.perfil === "analista" ? "/minha-conta-analista" : "/minha-conta", { replace: true });
    } catch (erro) {
      setMensagemErro(erro instanceof Error ? erro.message : "Não foi possível realizar o login.");
    } finally {
      requisicaoAtiva.current = false;
      setCarregando(false);
    }
  }

  return (
    <section className="mx-auto my-8 w-full max-w-md sm:my-12" aria-labelledby="titulo-login">
      <Card>
        <CardHeader className="text-center">
          <CardTitle><h1 id="titulo-login" className="m-0 text-2xl font-semibold tracking-tight">Login</h1></CardTitle>
        </CardHeader>
        <CardContent>
          {mensagemSucesso && <p role="status" className="mb-5 rounded-md border border-emerald-200 bg-emerald-50 p-3 text-sm text-emerald-800">{mensagemSucesso}</p>}
          <form onSubmit={enviarLogin} className="flex flex-col gap-6" aria-busy={carregando} aria-describedby={mensagemErro ? "erro-login" : undefined}>
            <fieldset disabled={carregando} className="m-0 flex min-w-0 flex-col gap-5 border-0 p-0">
              <div className="flex flex-col gap-2.5">
                <label htmlFor="nome-usuario" className="text-sm font-medium">Nome de usuário</label>
                <Input type="text" id="nome-usuario" name="nome_usuario" autoComplete="username" autoCapitalize="none" spellCheck={false} required value={nomeUsuario} onChange={evento => setNomeUsuario(evento.target.value)} />
              </div>
              <div className="flex flex-col gap-2.5">
                <label htmlFor="senha" className="text-sm font-medium">Senha</label>
                <Input type="password" id="senha" name="senha" autoComplete="current-password" required value={senha} onChange={evento => setSenha(evento.target.value)} />
              </div>
            </fieldset>
            <div className="flex flex-wrap items-center justify-center gap-x-8 gap-y-3">
              <Button asChild variant="link" className="h-auto p-0 text-sm"><Link to="/primeiro-acesso">Primeiro acesso</Link></Button>
              <Button asChild variant="link" className="h-auto p-0 text-sm"><Link to="/esqueci-senha">Esqueci minha senha</Link></Button>
            </div>
            {mensagemErro && <p id="erro-login" role="alert" className="m-0 rounded-md border border-destructive/30 bg-destructive/5 p-3 text-sm text-destructive">{mensagemErro}</p>}
            <Button id="botao_login" type="submit" className="w-full" disabled={carregando}>
              {carregando && <LoaderCircle className="animate-spin" aria-hidden="true" />}
              {carregando ? "Entrando..." : "Entrar"}
            </Button>
          </form>
        </CardContent>
      </Card>
    </section>
  );
};
