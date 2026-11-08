import { useEffect, useState } from "react";
import { consultarCarteiras } from "../services/configuracaoCarteiraService";
import type { CarteiraResumo } from "../services/configuracaoCarteiraService";
import { Link, useLocation } from "react-router-dom";
import { Eye, Pencil, Plus, RefreshCw, Trash2, Wallet } from "lucide-react";
import { AcaoCarteiraDialog } from "../components/AcaoCarteiraDialog";
import { Button } from "@/components/ui/button";
import {
  Table,
  TableBody,
  TableCaption,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from "@/components/ui/table";

export const CarteirasInvestidorPage = () => {
  const location = useLocation();
  const [carteiras, setCarteiras] = useState<CarteiraResumo[]>([]);
  const [carregando, setCarregando] = useState(true);
  const [erro, setErro] = useState("");
  const [tentativa, setTentativa] = useState(0);
  const [selecionada, setSelecionada] = useState<{ carteira: CarteiraResumo; acao: "editar" | "excluir" } | null>(null);
  const [aviso, setAviso] = useState(() => location.state?.carteiraCriada ? "Carteira e ativos cadastrados com sucesso." : location.state?.carteiraEditada ? "Carteira atualizada com sucesso." : "");
  useEffect(() => {
    const controller = new AbortController();
    consultarCarteiras(controller.signal).then(dados => {
      if (!controller.signal.aborted) { setCarteiras(dados); setErro(""); }
    }).catch(falha => {
      if (!controller.signal.aborted) setErro(falha instanceof Error ? falha.message : "Não foi possível consultar as carteiras.");
    }).finally(() => { if (!controller.signal.aborted) setCarregando(false); });
    return () => controller.abort();
  }, [tentativa]);
  return (
    <section className="mx-auto w-full max-w-5xl py-4 sm:py-8" aria-labelledby="titulo-carteiras">
      <header className="mb-8 text-center">
        <h1 id="titulo-carteiras" className="mb-2 text-3xl font-semibold tracking-tight text-foreground">
          Carteiras
        </h1>
        <p className="text-sm text-muted-foreground">
          Organize seus investimentos de acordo com seus objetivos.
        </p>
      </header>

      {aviso && <p role="status" className="mb-4 rounded-md border border-emerald-200 bg-emerald-50 p-3 text-sm text-emerald-800">{aviso}</p>}
      <div className="mb-4 flex flex-wrap justify-end gap-3">
        <Button type="button" variant="outline" disabled={carregando || !!selecionada} onClick={() => { setCarregando(true); setTentativa(t => t + 1); }}><RefreshCw aria-hidden="true" />Atualizar</Button>
        <Button asChild>
          <Link to="/carteiras-nova" className="no-underline hover:no-underline">
            <Plus aria-hidden="true" />
            Adicionar Carteira
          </Link>
        </Button>
      </div>

      <div className="overflow-hidden rounded-xl border bg-card shadow-sm">
        <Table>
          <TableCaption className="sr-only">Carteiras do investidor</TableCaption>
          <TableHeader>
            <TableRow className="bg-muted hover:bg-muted">
              <TableHead className="px-6">Carteira</TableHead>
              <TableHead className="px-6 text-right">Ações</TableHead>
            </TableRow>
          </TableHeader>
          <TableBody>
            {carregando ? <TableRow><TableCell colSpan={2} className="py-8 text-center" role="status">Carregando carteiras...</TableCell></TableRow>
              : erro ? <TableRow><TableCell colSpan={2} className="p-6"><p role="alert" className="text-destructive">{erro}</p><Button variant="outline" onClick={() => { setCarregando(true); setTentativa(t => t + 1); }}>Tentar novamente</Button></TableCell></TableRow>
              : carteiras.length ? carteiras.map(carteira => <TableRow key={carteira.id_carteira}><TableCell className="px-6 py-4">{carteira.nome}{!carteira.ativa && <span className="ml-3 text-xs text-muted-foreground">Desativada</span>}</TableCell>
                <TableCell className="px-6 py-4"><div className="flex flex-wrap justify-end gap-2">
                  <Button asChild variant="outline" size="sm"><Link className="no-underline hover:no-underline" aria-label={`Visualizar carteira ${carteira.nome}`} to={`/carteiras-investidor/${carteira.id_carteira}`}><Eye aria-hidden="true" />Visualizar</Link></Button>
                  <Button asChild variant="outline" size="sm"><Link className="no-underline hover:no-underline" aria-label={`Editar carteira ${carteira.nome}`} to={`/carteiras-investidor/${carteira.id_carteira}/editar`}><Pencil aria-hidden="true" />Editar</Link></Button>
                  <Button type="button" variant="destructive" size="sm" aria-label={`Excluir carteira ${carteira.nome}`} onClick={() => setSelecionada({ carteira, acao: "excluir" })}><Trash2 aria-hidden="true" />Excluir</Button>
                </div></TableCell></TableRow>) : (
            <TableRow className="hover:bg-transparent">
              <TableCell colSpan={2} className="px-6 py-16 text-center">
                <div className="mx-auto mb-4 flex size-12 items-center justify-center rounded-xl bg-secondary text-muted-foreground">
                  <Wallet className="size-6" aria-hidden="true" />
                </div>
                <p className="mb-2 text-base font-medium text-foreground">Suas carteiras em um só lugar</p>
                <p id="disponibilidade-carteiras" className="mx-auto mb-0 max-w-sm text-sm text-muted-foreground">
                  Nenhuma carteira cadastrada. Clique em Adicionar Carteira para começar.
                </p>
              </TableCell>
            </TableRow>
            )}
          </TableBody>
        </Table>
      </div>
      {selecionada && <AcaoCarteiraDialog key={`${selecionada.acao}-${selecionada.carteira.id_carteira}`} carteira={selecionada.carteira} acao={selecionada.acao}
        onFechar={() => setSelecionada(null)} onConcluido={nome => {
          const { carteira, acao } = selecionada;
          setCarteiras(itens => acao === "excluir" ? itens.filter(item => item.id_carteira !== carteira.id_carteira) : itens.map(item => item.id_carteira === carteira.id_carteira ? { ...item, nome } : item));
          setAviso(acao === "excluir" ? "Carteira excluída com sucesso." : "Nome da carteira atualizado com sucesso.");
          setSelecionada(null);
        }} />}
    </section>
  );
};
