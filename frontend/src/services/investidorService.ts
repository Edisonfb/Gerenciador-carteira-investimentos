import type { Investidor } from "../types/investidor";
import { obterTokenAcesso } from "./autenticacaoService";

interface MeuPerfilInvestidorApi {
  id_investidor: number;
  id_analista_responsavel: number;
  nome: string;
  sobrenome: string;
  email: string;
  cpf: string;
  telefone: string;
  logradouro: string;
  numero: string;
  bairro: string;
  cep: string;
  cidade: string;
  uf: string;
  ativo: boolean;
}

function converterPerfilInvestidor(perfil: MeuPerfilInvestidorApi): Investidor {
  return {
    id: perfil.id_investidor,
    idAnalistaResponsavel: perfil.id_analista_responsavel,
    nome: perfil.nome,
    sobrenome: perfil.sobrenome,
    email: perfil.email,
    cpf: perfil.cpf,
    celular: perfil.telefone,
    rua: perfil.logradouro,
    numero: perfil.numero,
    bairro: perfil.bairro,
    cep: perfil.cep,
    cidade: perfil.cidade,
    uf: perfil.uf,
    perfil: "investidor",
    status: perfil.ativo ? "ativo" : "bloqueado",
  };
}

export async function buscarMeuPerfilInvestidor(): Promise<Investidor> {
  const token = obterTokenAcesso();
  const resposta = await fetch("http://127.0.0.1:8000/investors/me", {
    headers: { Authorization: `Bearer ${token}` },
  });
  if (!resposta.ok) {
    const erro = await resposta.json().catch(() => null);
    throw new Error(erro?.detail ?? "Não foi possível carregar o perfil.");
  }
  return converterPerfilInvestidor(await resposta.json());
}

export async function atualizarMeuPerfilInvestidor(
  dados: Partial<Omit<Investidor, "id" | "idAnalistaResponsavel" | "perfil" | "status" | "cpf">>,
): Promise<Investidor> {
  const token = obterTokenAcesso();
  const resposta = await fetch("http://127.0.0.1:8000/investors/me", {
    method: "PATCH",
    headers: {
      "Content-Type": "application/json",
      Authorization: `Bearer ${token}`,
    },
    body: JSON.stringify({
      nome: dados.nome,
      sobrenome: dados.sobrenome,
      email: dados.email,
      telefone: dados.celular,
      logradouro: dados.rua,
      numero: dados.numero,
      bairro: dados.bairro,
      cep: dados.cep,
      cidade: dados.cidade,
      uf: dados.uf,
    }),
  });
  if (!resposta.ok) {
    const erro = await resposta.json().catch(() => null);
    throw new Error(erro?.detail ?? "Não foi possível atualizar o perfil.");
  }
  return converterPerfilInvestidor(await resposta.json());
}

let investidoresMock: Investidor[] = [
  {
    id: 1,
    idAnalistaResponsavel: 1,
    nome: "Lucas",
    sobrenome: "Mendes",
    email: "lucas.mendes@email.com",
    cpf: "123.456.789-01",
    celular: "(11) 98765-4321",
    rua: "Av. Paulista",
    numero: "1500",
    bairro: "Bela Vista",
    cep: "01310-100",
    cidade: "São Paulo",
    uf: "SP",
    perfil: "investidor",
    status: "ativo",
  },
  {
    id: 2,
    idAnalistaResponsavel: 1,
    nome: "Camila",
    sobrenome: "Oliveira",
    email: "camila.oliveira@email.com",
    cpf: "234.567.890-12",
    celular: "(21) 99876-5432",
    rua: "Rua Visconde de Pirajá",
    numero: "250",
    bairro: "Ipanema",
    cep: "22410-000",
    cidade: "Rio de Janeiro",
    uf: "RJ",
    perfil: "investidor",
    status: "ativo",
  },
  {
    id: 3,
    idAnalistaResponsavel: 1,
    nome: "Bruno",
    sobrenome: "Ferreira",
    email: "bruno.ferreira@email.com",
    cpf: "345.678.901-23",
    celular: "(31) 97654-3210",
    rua: "Rua dos Aimorés",
    numero: "405",
    bairro: "Funcionários",
    cep: "30140-070",
    cidade: "Belo Horizonte",
    uf: "MG",
    perfil: "investidor",
    status: "bloqueado",
  },
  {
    id: 4,
    idAnalistaResponsavel: 99,
    nome: "Fernanda",
    sobrenome: "Costa",
    email: "fernanda.costa@email.com",
    cpf: "456.789.012-34",
    celular: "(41) 98888-7777",
    rua: "Av. Sete de Setembro",
    numero: "3200",
    bairro: "Batel",
    cep: "80230-010",
    cidade: "Curitiba",
    uf: "PR",
    perfil: "investidor",
    status: "ativo",
  },
];

export function buscarInvestidoresPorAnalista(
  idAnalistaResponsavel: number,
): Investidor[] {
  return investidoresMock.filter(
    (investidor) => investidor.idAnalistaResponsavel === idAnalistaResponsavel,
  );
}

export function buscarInvestidorPorId(id: number): Investidor | undefined {
  return investidoresMock.find((investidor) => investidor.id === id);
}

export async function criarInvestidor(
  novoInvestidor: Omit<Investidor, "id">,
): Promise<Investidor> {
  function somenteNumeros(valor: string){
    return valor.replace(/\D/g, "");
  }

  const resposta = await fetch("http://127.0.0.1:8000/investors", {
    method: "POST",
    headers:{
      "Content-Type": "application/json",
    },
    body: JSON.stringify({
      id_analista_responsavel: novoInvestidor.idAnalistaResponsavel,
       nome: novoInvestidor.nome,
      sobrenome: novoInvestidor.sobrenome,
      email: novoInvestidor.email,
      cpf: somenteNumeros(novoInvestidor.cpf),
      telefone: somenteNumeros(novoInvestidor.celular),
      cep: somenteNumeros(novoInvestidor.cep),
      uf: novoInvestidor.uf,
      cidade: novoInvestidor.cidade,
      bairro: novoInvestidor.bairro,
      logradouro: novoInvestidor.rua,
      numero: novoInvestidor.numero,
    })
  });

  if(!resposta.ok){
    throw new Error("Não foi possível cadastrar o investidor.");
  }

  const investidorCriado = await resposta.json();

  return{
    ...novoInvestidor,
    id: investidorCriado.id_investidor,
    cpf: investidorCriado.cpf,
    celular: investidorCriado.telefone,
  }
}

export function atualizarInvestidor(
  id: number,
  dadosAtualizados: Partial<
    Omit<Investidor, "id" | "idAnalistaResponsavel" | "perfil">
  >,
): Investidor | undefined {
  const investidorEncontrado = buscarInvestidorPorId(id);

  if (!investidorEncontrado) {
    return undefined;
  }
  const investidorAtualizado: Investidor = {
    ...investidorEncontrado,
    ...dadosAtualizados,
    id: investidorEncontrado.id,
  };

  investidoresMock = investidoresMock.map((investidor) =>
    investidor.id === id ? investidorAtualizado : investidor,
  );
  return investidorAtualizado;
}

export function excluirInvestidor(id: number): boolean {
  const quantidadeAnterior = investidoresMock.length;
  investidoresMock = investidoresMock.filter(
    (investidor) => investidor.id !== id,
  );
  return investidoresMock.length < quantidadeAnterior;
}
