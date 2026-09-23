import type { Investidor } from "../types/investidor";

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

export function criarInvestidor(
  novoInvestidor: Omit<Investidor, "id">,
): Investidor {
  const investidorCriado: Investidor = {
    ...novoInvestidor,
    id: Date.now(),
  };
  investidoresMock = [...investidoresMock, investidorCriado];
  return investidorCriado;
}
