import { useState } from "react";
import type { FormEvent } from "react";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { validarEdicaoConta } from "../types/contaInvestidor";
import type { ContaInvestidor, EdicaoContaInvestidor } from "../types/contaInvestidor";

interface Props {
  conta: ContaInvestidor;
  salvando: boolean;
  onSalvar: (dados: EdicaoContaInvestidor) => Promise<void>;
  onCancelar: () => void;
}

export function FormularioContaInvestidor({ conta, salvando, onSalvar, onCancelar }: Props) {
  const [dados, setDados] = useState<EdicaoContaInvestidor>({ nomeUsuario: conta.nomeUsuario, emailComunicacao: conta.emailComunicacao, emailRecuperacao: conta.emailRecuperacao, senhaAtual: "", novaSenha: "", confirmacaoSenha: "" });
  const [erro, setErro] = useState("");
  function alterar(campo: keyof EdicaoContaInvestidor, valor: string) { setDados(anteriores => ({ ...anteriores, [campo]: valor })); setErro(""); }
  async function salvar(evento: FormEvent<HTMLFormElement>) {
    evento.preventDefault();
    if (salvando) return;
    const falha = validarEdicaoConta(dados); setErro(falha ?? "");
    if (!falha) await onSalvar(dados);
  }
  return <form onSubmit={salvar} className="flex flex-col gap-6" aria-busy={salvando}>
    <fieldset disabled={salvando} className="m-0 grid min-w-0 gap-5 border-0 p-0 sm:grid-cols-2">
      <div className="flex flex-col gap-2 sm:col-span-2"><label htmlFor="conta-usuario" className="text-sm font-medium">Usuário</label><Input id="conta-usuario" autoComplete="username" autoCapitalize="none" spellCheck={false} required maxLength={50} value={dados.nomeUsuario} onChange={e => alterar("nomeUsuario", e.target.value)} /></div>
      <div className="flex flex-col gap-2"><label htmlFor="conta-comunicacao" className="text-sm font-medium">E-mail de comunicação</label><Input id="conta-comunicacao" type="email" autoComplete="email" required maxLength={255} value={dados.emailComunicacao} onChange={e => alterar("emailComunicacao", e.target.value)} /></div>
      <div className="flex flex-col gap-2"><label htmlFor="conta-recuperacao" className="text-sm font-medium">E-mail de recuperação</label><Input id="conta-recuperacao" type="email" required maxLength={255} value={dados.emailRecuperacao} onChange={e => alterar("emailRecuperacao", e.target.value)} /></div>
      <div className="flex flex-col gap-2 sm:col-span-2"><label htmlFor="conta-senha-atual" className="text-sm font-medium">Senha atual</label><Input id="conta-senha-atual" type="password" autoComplete="current-password" required value={dados.senhaAtual} onChange={e => alterar("senhaAtual", e.target.value)} /><p className="m-0 text-xs text-muted-foreground">Confirme sua senha atual para salvar as alterações.</p></div>
      <div className="flex flex-col gap-2"><label htmlFor="conta-nova-senha" className="text-sm font-medium">Nova senha (opcional)</label><Input id="conta-nova-senha" type="password" autoComplete="new-password" minLength={8} maxLength={72} value={dados.novaSenha} onChange={e => alterar("novaSenha", e.target.value)} /></div>
      <div className="flex flex-col gap-2"><label htmlFor="conta-confirmacao" className="text-sm font-medium">Confirmar nova senha</label><Input id="conta-confirmacao" type="password" autoComplete="new-password" minLength={8} maxLength={72} value={dados.confirmacaoSenha} onChange={e => alterar("confirmacaoSenha", e.target.value)} /></div>
    </fieldset>
    <p className="m-0 text-sm text-muted-foreground">Deixe a nova senha em branco para manter a atual. Se alterar, use pelo menos 8 caracteres.</p>
    {erro && <p role="alert" className="m-0 text-sm text-destructive">{erro}</p>}
    <div className="flex flex-col-reverse gap-3 sm:flex-row sm:justify-end"><Button type="button" variant="outline" disabled={salvando} onClick={onCancelar}>Cancelar</Button><Button type="submit" disabled={salvando}>{salvando ? "Salvando..." : "Salvar alterações"}</Button></div>
  </form>;
}
