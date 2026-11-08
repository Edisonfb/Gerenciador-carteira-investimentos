import { useEffect, useRef, useState } from "react";
import type { FormEvent, MouseEvent } from "react";
import { LoaderCircle, Mail, X } from "lucide-react";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { gerarConviteInvestidor, validarEmailConvite } from "../services/conviteInvestidorService";
import type { ConviteInvestidor } from "../services/conviteInvestidorService";

interface Props {
  aberto: boolean;
  onFechar: () => void;
  onGerado: (convite: ConviteInvestidor) => void;
}

export function GerarTokenInvestidorDialog({ aberto, onFechar, onGerado }: Props) {
  const dialogRef = useRef<HTMLDialogElement>(null);
  const inputRef = useRef<HTMLInputElement>(null);
  const requisicaoAtiva = useRef(false);
  const [email, setEmail] = useState("");
  const [erro, setErro] = useState("");
  const [enviando, setEnviando] = useState(false);

  useEffect(() => {
    const dialog = dialogRef.current;
    if (aberto && dialog && !dialog.open) {
      dialog.showModal();
      inputRef.current?.focus();
    } else if (!aberto && dialog?.open) {
      dialog.close();
    }
  }, [aberto]);

  async function gerar(evento: FormEvent<HTMLFormElement>) {
    evento.preventDefault();
    if (requisicaoAtiva.current) return;
    const falha = validarEmailConvite(email);
    setErro(falha ?? "");
    if (falha) { inputRef.current?.focus(); return; }
    requisicaoAtiva.current = true;
    setEnviando(true);
    try {
      const convite = await gerarConviteInvestidor(email);
      setEmail("");
      onGerado(convite);
    } catch (falha) {
      setErro(falha instanceof Error ? falha.message : "Não foi possível gerar o convite.");
    } finally {
      requisicaoAtiva.current = false;
      setEnviando(false);
    }
  }

  function fechar() {
    if (requisicaoAtiva.current) return;
    setErro(""); setEmail(""); onFechar();
  }

  function clicarFora(evento: MouseEvent<HTMLDialogElement>) {
    if (evento.target !== evento.currentTarget) return;
    const rect = evento.currentTarget.getBoundingClientRect();
    if (evento.clientX < rect.left || evento.clientX > rect.right || evento.clientY < rect.top || evento.clientY > rect.bottom) fechar();
  }

  return <dialog ref={dialogRef} aria-labelledby="titulo-gerar-token" aria-describedby="descricao-gerar-token"
    onCancel={evento => { evento.preventDefault(); fechar(); }} onClose={() => { if (aberto && !requisicaoAtiva.current) fechar(); }} onClick={clicarFora}
    className="fixed inset-0 m-auto max-h-[90vh] w-[calc(100%_-_2rem)] max-w-md overflow-y-auto rounded-xl border bg-background p-0 text-foreground shadow-xl backdrop:bg-black/50">
    <div className="p-6">
      <div className="mb-4 flex items-start justify-between gap-4">
        <div className="flex size-11 items-center justify-center rounded-xl bg-secondary"><Mail className="size-5" aria-hidden="true" /></div>
        <Button type="button" variant="ghost" size="icon" aria-label="Fechar janela de geração de token" disabled={enviando} onClick={fechar}><X aria-hidden="true" /></Button>
      </div>
      <h2 id="titulo-gerar-token" className="mb-2 text-xl font-semibold">Gerar token de acesso</h2>
      <p id="descricao-gerar-token" className="mb-6 text-sm text-muted-foreground">Informe apenas o e-mail do cliente. Ele receberá o token para realizar o primeiro acesso e concluir o próprio cadastro.</p>
      <form onSubmit={gerar} noValidate aria-busy={enviando}>
        <label htmlFor="email-cliente-token" className="mb-2 block text-sm font-medium">E-mail do cliente</label>
        <Input ref={inputRef} id="email-cliente-token" type="email" autoComplete="email" placeholder="cliente@exemplo.com" maxLength={255} disabled={enviando} value={email}
          aria-invalid={!!erro} aria-describedby={erro ? "erro-gerar-token" : undefined} onChange={evento => { setEmail(evento.target.value); setErro(""); }} />
        {erro && <p id="erro-gerar-token" role="alert" className="mb-0 mt-3 text-sm text-destructive">{erro}</p>}
        <div className="mt-6 flex flex-col-reverse gap-3 sm:flex-row sm:justify-end">
          <Button type="button" variant="outline" disabled={enviando} onClick={fechar}>Cancelar</Button>
          <Button type="submit" disabled={enviando}>{enviando && <LoaderCircle className="animate-spin" aria-hidden="true" />}{enviando ? "Gerando e enviando..." : "Gerar token e enviar"}</Button>
        </div>
      </form>
    </div>
  </dialog>;
}
