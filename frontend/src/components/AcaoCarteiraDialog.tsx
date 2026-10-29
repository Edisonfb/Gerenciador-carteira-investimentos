import { useEffect, useRef, useState } from "react";
import type { FormEvent } from "react";
import { LoaderCircle } from "lucide-react";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { excluirCarteira, renomearCarteira } from "../services/configuracaoCarteiraService";
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

  useEffect(() => {
    const dialog = dialogRef.current;
    if (dialog && !dialog.open) dialog.showModal();
  }, []);

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
      setErro(falha instanceof Error ? falha.message : "Não foi possível concluir a operação.");
    } finally { requisicaoAtiva.current = false; setEnviando(false); }
  }

  return <dialog ref={dialogRef} aria-labelledby="titulo-acao-carteira" aria-describedby="descricao-acao-carteira"
    onCancel={evento => { evento.preventDefault(); fechar(); }}
    className="fixed inset-0 m-auto max-h-[90vh] w-[calc(100%_-_2rem)] max-w-md overflow-y-auto rounded-xl border bg-background p-6 text-foreground shadow-xl backdrop:bg-black/50">
    <h2 id="titulo-acao-carteira" className="mb-2 text-xl font-semibold">{excluindo ? "Excluir carteira" : "Editar carteira"}</h2>
    <p id="descricao-acao-carteira" className="mb-6 text-sm text-muted-foreground">
      {excluindo ? `Deseja excluir a carteira “${carteira.nome}” e seus vínculos com os ativos? Esta ação não pode ser desfeita.` : "Altere o nome da carteira. Os ativos, percentuais e quantidades serão mantidos."}
    </p>
    <form onSubmit={confirmar} noValidate aria-busy={enviando}>
      {!excluindo && <div className="flex flex-col gap-2">
        <label htmlFor="editar-nome-carteira" className="text-sm font-medium">Nome da carteira</label>
        <Input id="editar-nome-carteira" value={nome} maxLength={100} autoComplete="off" disabled={enviando}
          aria-invalid={!!erro} aria-describedby={erro ? "erro-acao-carteira" : undefined}
          onChange={evento => { setNome(evento.target.value); setErro(""); }} />
      </div>}
      {erro && <p id="erro-acao-carteira" role="alert" className="mt-4 text-sm text-destructive">{erro}</p>}
      <div className="mt-6 flex flex-col-reverse gap-3 sm:flex-row sm:justify-end">
        <Button type="button" variant="outline" disabled={enviando} onClick={fechar}>Cancelar</Button>
        <Button type="submit" variant={excluindo ? "destructive" : "default"} disabled={enviando}>
          {enviando && <LoaderCircle className="animate-spin" aria-hidden="true" />}
          {enviando ? (excluindo ? "Excluindo..." : "Salvando...") : (excluindo ? "Excluir carteira" : "Salvar alterações")}
        </Button>
      </div>
    </form>
  </dialog>;
}
