import { Plus, Wallet } from "lucide-react";
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

      <div className="mb-4 flex justify-end">
        <Button type="button" aria-describedby="disponibilidade-carteiras">
          <Plus aria-hidden="true" />
          Adicionar Carteira
        </Button>
      </div>

      <div className="overflow-hidden rounded-xl border bg-card shadow-sm">
        <Table>
          <TableCaption className="sr-only">Carteiras do investidor</TableCaption>
          <TableHeader>
            <TableRow className="bg-muted hover:bg-muted">
              <TableHead className="px-6">Carteira</TableHead>
            </TableRow>
          </TableHeader>
          <TableBody>
            <TableRow className="hover:bg-transparent">
              <TableCell className="px-6 py-16 text-center">
                <div className="mx-auto mb-4 flex size-12 items-center justify-center rounded-xl bg-secondary text-muted-foreground">
                  <Wallet className="size-6" aria-hidden="true" />
                </div>
                <p className="mb-2 text-base font-medium text-foreground">Suas carteiras em um só lugar</p>
                <p id="disponibilidade-carteiras" className="mx-auto mb-0 max-w-sm text-sm text-muted-foreground">
                  A consulta e o cadastro de carteiras ainda não estão disponíveis.
                </p>
              </TableCell>
            </TableRow>
          </TableBody>
        </Table>
      </div>
    </section>
  );
};
