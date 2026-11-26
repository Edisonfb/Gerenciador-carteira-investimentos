import { useEffect, useRef } from "react";
import { Button } from "@/components/ui/button";

interface Props {
  titulo: string;
  mensagem: string;
  onFechar: () => void;
}

/** Aviso simples com um botao Confirmar que apenas fecha a janela. */
export function AvisoDialog({ titulo, mensagem, onFechar }: Props) {
  const dialogRef = useRef<HTMLDialogElement>(null);

  useEffect(() => {
    const dialog = dialogRef.current;
    if (dialog && !dialog.open) dialog.showModal();
  }, []);

  return <dialog ref={dialogRef} role="alertdialog" aria-labelledby="titulo-aviso" aria-describedby="mensagem-aviso"
    onCancel={evento => { evento.preventDefault(); onFechar(); }}
    className="fixed inset-0 m-auto max-h-[90vh] w-[calc(100%_-_2rem)] max-w-md overflow-y-auto rounded-xl border bg-background p-6 text-foreground shadow-xl backdrop:bg-black/50">
    <h2 id="titulo-aviso" className="mb-2 text-xl font-semibold">{titulo}</h2>
    <p id="mensagem-aviso" className="mb-6 text-sm text-muted-foreground">{mensagem}</p>
    <div className="flex justify-end">
      <Button type="button" onClick={onFechar}>Confirmar</Button>
    </div>
  </dialog>;
}
