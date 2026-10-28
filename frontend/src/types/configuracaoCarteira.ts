export interface AtivoDisponivel {
  id_ativo: number;
  codigo: string;
  setor: string;
  ativo: boolean;
}

export interface AtivoConfigurado extends AtivoDisponivel {
  objetivo: string;
  readonly quantidade: 0;
}
