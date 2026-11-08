import type { ContaInvestidorConsulta } from "../services/consultaInvestidoresService";
import { Table, TableBody, TableCaption, TableCell, TableHead, TableHeader, TableRow } from "@/components/ui/table";

interface TabelaInvestidoresProps {
  investidores: ContaInvestidorConsulta[];
  buscaAtiva?: boolean;
}

export function TabelaInvestidores({ investidores, buscaAtiva = false }: TabelaInvestidoresProps) {
  return <Table>
    <TableCaption className="sr-only">Consulta de contas de investidores</TableCaption>
    <TableHeader><TableRow className="bg-muted/50">
      <TableHead className="pl-6">E-mail</TableHead><TableHead>Situação da conta</TableHead><TableHead>Convite</TableHead><TableHead className="pr-6">Cadastro</TableHead>
    </TableRow></TableHeader>
    <TableBody>
      {!investidores.length && <TableRow><TableCell colSpan={4} className="py-12 text-center text-muted-foreground">{buscaAtiva ? "Nenhum investidor encontrado para os filtros informados." : "Nenhum investidor cadastrado."}</TableCell></TableRow>}
      {investidores.map(investidor => <TableRow key={investidor.id_usuario}>
        <TableCell className="pl-6 font-medium"><span className="break-all">{investidor.email}</span></TableCell>
        <TableCell>{investidor.ativo === null ? <span className="text-sm text-muted-foreground">Não informada</span> : <span className={investidor.ativo ? "whitespace-nowrap rounded-full bg-emerald-50 px-3 py-1 text-xs font-medium text-emerald-800" : "whitespace-nowrap rounded-full bg-red-50 px-3 py-1 text-xs font-medium text-red-800"}>{investidor.ativo ? "Ativa" : "Inativa"}</span>}</TableCell>
        <TableCell>{investidor.convite === null ? <span className="text-sm text-muted-foreground">Não informado</span> : <span className={investidor.convite === "enviado" ? "whitespace-nowrap rounded-full bg-emerald-50 px-3 py-1 text-xs font-medium text-emerald-800" : "whitespace-nowrap rounded-full bg-amber-50 px-3 py-1 text-xs font-medium text-amber-800"}>{investidor.convite === "enviado" ? "Envio confirmado na geração" : "Envio não confirmado"}</span>}</TableCell>
        <TableCell className="pr-6">{investidor.cadastro === null ? <span className="text-sm text-muted-foreground">Não informado</span> : <span className="text-sm">{investidor.cadastro === "concluido" ? "Concluído na geração" : "Pendente na geração"}</span>}</TableCell>
      </TableRow>)}
    </TableBody>
  </Table>;
}
