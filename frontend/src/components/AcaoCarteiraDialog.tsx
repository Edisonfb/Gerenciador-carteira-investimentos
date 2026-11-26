import { useEffect, useRef, useState } from "react";
import type { FormEvent } from "react";
import { LoaderCircle } from "lucide-react";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { carteiraPossuiAtivoComQuantidade, excluirCarteira, MENSAGEM_CARTEIRA_COM_QUANTIDADE, renomearCarteira } from "../services/configuracaoCarteiraService";
import type { CarteiraResumo } from "../services/configuracaoCarteiraService";

interface Props {
  carteira: CarteiraResumo;
  acao: "editar" | "excluir";
  onFechar: () => void;
  onConcluido: (nome: string) => void;
}

export function AcaoCarteiraDialog({ carteira, acao, onFechar, onConcluido }: Props) {
  const dialogRef = useRef<HTMLDialogElement>(null);
  const requisicaoAtiva = useRef(false);
  const [nome, setNome] = useState(carteira.nome);
  const [enviando, setEnviando] = useState(false);
  const [erro, setErro] = useState("");
  const excluindo = acao === "excluir";
  // US 8.3 cenario 2.1: carteira com ativo(s) com quantidade nao pode ser excluida.
  const [conferindo, setConferindo] = useState(excluindo);
  const [bloqueada, setBloqueada] = useState(false);

  useEffect(() => {
    const dialog = dialogRef.current;
    if (dialog && !dialog.open) dialog.showModal();
  }, []);

  useEffect(() => {
    if (!excluindo) return;
    const controller = new AbortController();
    carteiraPossuiAtivoComQuantidade(carteira.id_carteira, controller.signal)
      .then(possui => { if (!controller.signal.aborted) setBloqueada(possui); })
      .catch(() => { /* sem a conferencia, o backend continua bloqueando a exclusao */ })
      .finally(() => { if (!controller.signal.aborted) setConferindo(false); });
    return () => controller.abort();
  }, [excluindo, carteira.id_carteira]);

  function fechar() {
    if (!requisicaoAtiva.current) onFechar();
  }

  async function confirmar(evento: FormEvent<HTMLFormElement>) {
    evento.preventDefault();
    if (requisicaoAtiva.current) return;
    requisicaoAtiva.current = true;
    setEnviando(true); setErro("");
    try {
      if (excluindo) await excluirCarteira(carteira.id_carteira);
      else await renomearCarteira(carteira.id_carteira, nome);
      onConcluido(nome.trim());
    } catch (falha) {
      const mensagem = falha instanceof Error ? falha.message : "";
      if (excluindo && mensagem === MENSAGEM_CARTEIRA_COM_QUANTIDADE) setBloqueada(true);
      else setErro(mensagem || "Não foi possível concluir a operação.");
    } finally { requisicaoAtiva.current = false; setEnviando(false); }
  }

  return <dialog ref={dialogRef} aria-labelledby="titulo-acao-carteira" aria-describedby="descricao-acao-carteira"
    onCancel={evento => { evento.preventDefault(); fechar(); }}
    className="fixed inset-0 m-auto max-h-[90vh] w-[calc(100%_-_2rem)] max-w-md overflow-y-auto rounded-xl border bg-background p-6 text-foreground shadow-xl backdrop:bg-black/50">
    <h2 id="titulo-acao-carteira" className="mb-2 text-xl font-semibold">{excluindo ? "Excluir carteira" : "Editar carteira"}</h2>
    <p id="descricao-acao-carteira" className="mb-6 text-sm text-muted-foreground">
      {bloqueada ? MENSAGEM_CARTEIRA_COM_QUANTIDADE : excluindo ? `Deseja excluir a carteira “${carteira.nome}” e seus vínculos com os ativos? Esta ação não pode ser desfeita.` : "Altere o nome da carteira. Os ativos, percentuais e quantidades serão mantidos."}
    </p>
    {bloqueada ? <div className="flex justify-end">
      <Button type="button" onClick={onFechar}>Confirmar</Button>
    </div> : <form onSubmit={confirmar} noValidate aria-busy={enviando}>
      {!excluindo && <div className="flex flex-col gap-2">
        <label htmlFor="editar-nome-carteira" className="text-sm font-medium">Nome da carteira</label>
        <Input id="editar-nome-carteira" value={nome} maxLength={100} autoComplete="off" disabled={enviando}
          aria-invalid={!!erro} aria-describedby={erro ? "erro-acao-carteira" : undefined}
          onChange={evento => { setNome(evento.target.value); setErro(""); }} />
      </div>}
      {erro && <p id="erro-acao-carteira" role="alert" className="mt-4 text-sm text-destructive">{erro}</p>}
      <div className="mt-6 flex flex-col-reverse gap-3 sm:flex-row sm:justify-end">
        <Button type="button" variant="outline" disabled={enviando} onClick={fechar}>Cancelar</Button>
        <Button type="submit" variant={excluindo ? "destructive" : "default"} disabled={enviando || conferindo}>
          {enviando && <LoaderCircle className="animate-spin" aria-hidden="true" />}
          {enviando ? (excluindo ? "Excluindo..." : "Salvando...") : (excluindo ? "Excluir carteira" : "Salvar alterações")}
        </Button>
      </div>
    </form>}
  </dialog>;
}
