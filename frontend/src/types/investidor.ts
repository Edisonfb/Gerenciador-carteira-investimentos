import type { Usuario } from "./usuario";

export interface Investidor extends Usuario {
  idAnalistaResponsavel: number;
  perfil: "investidor";
}
