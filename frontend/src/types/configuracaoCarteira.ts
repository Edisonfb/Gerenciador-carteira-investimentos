export interface AtivoDisponivel {
  ticker: string;
  setor: string;
  ativo: boolean;
}

export interface AtivoConfigurado extends AtivoDisponivel {
  objetivo: string;
  readonly quantidade: 0;
}
