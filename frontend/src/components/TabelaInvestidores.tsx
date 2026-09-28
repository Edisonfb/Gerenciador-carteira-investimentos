import type { Investidor } from "../types/investidor";
import "../styles/usuarios.css";

interface TabelaInvestidoresProps {
  investidores: Investidor[];
  onEditarInvestidor: (id: number) => void;
  onExcluirInvestidor: (id: number) => void;
}

export function TabelaInvestidores({
  investidores,
  onEditarInvestidor,
  onExcluirInvestidor,
}: TabelaInvestidoresProps) {
  return (
    <div className="tabela-container">
      <table className="tabela-usuarios">
        <thead>
          <tr>
            <th>Nome</th>
            <th>E-mail</th>
            <th>CPF</th>
            <th>Celular</th>
            <th>Status</th>
            <th>Ações</th>
          </tr>
        </thead>

        <tbody>
          {investidores.map((investidor) => (
            <tr key={investidor.id}>
              <td>
                {investidor.nome} {investidor.sobrenome}
              </td>

              <td>{investidor.email}</td>

              <td>{investidor.cpf}</td>

              <td>{investidor.celular}</td>

              <td>
                <span
                  className={`status ${
                    investidor.status === "ativo"
                      ? "status-ativo"
                      : "status-bloqueado"
                  }`}
                >
                  {investidor.status}
                </span>
              </td>

              <td>
                <div className="acoes-tabela">
                  <button
                    className="botao botao-secundario"
                    onClick={() => onEditarInvestidor(investidor.id)}
                  >
                    Editar
                  </button>

                  <button
                    className="botao botao-perigo"
                    onClick={() => onExcluirInvestidor(investidor.id)}
                  >
                    Excluir
                  </button>
                </div>
              </td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}
