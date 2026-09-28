import { Navigate, Route, Routes } from "react-router-dom";
import { CadastroUsuarioPage } from "../pages/CadastroUsuarioPage";
import { EdicaoUsuarioPage } from "../pages/EdicaoUsuarioPage";
import { MinhaContaPage } from "../pages/MinhaContaPage";
import { UsuariosPage } from "../pages/UsuariosPage";
import { buscarUsuarioAutenticado } from "../services/autenticacaoService";
import { InvestidoresPage } from "../pages/InvestidoresPage";
import { CadastroInvestidorPage } from "../pages/CadastroInvestidorPage";
import { EdicaoInvestidorPage } from "../pages/EdicaoInvestidorPage";
import { MinhaContaInvestidorPage } from "../pages/MinhaContaInvestidorPage";

export function RotasApp() {
  const usuarioAutenticado = buscarUsuarioAutenticado();

  if (usuarioAutenticado.perfil === "analista") {
    return (
      <Routes>
        <Route path="/minha-conta" element={<MinhaContaPage />} />

        <Route path="/investidores" element={<InvestidoresPage />} />

        <Route path="/investidores/novo" element={<CadastroInvestidorPage />} />

        <Route
          path="/investidores/:id/editar"
          element={<EdicaoInvestidorPage />}
        />

        <Route path="*" element={<Navigate to="/investidores" replace />} />
      </Routes>
    );
  }

  if (usuarioAutenticado.perfil === "administrador") {
    return (
      <Routes>
        <Route path="/usuarios" element={<UsuariosPage />} />

        <Route path="/usuarios/novo" element={<CadastroUsuarioPage />} />

        <Route path="/usuarios/:id/editar" element={<EdicaoUsuarioPage />} />

        <Route path="*" element={<Navigate to="/usuarios" replace />} />
      </Routes>
    );
  }

  if (usuarioAutenticado.perfil === "investidor") {
    return (
      <Routes>
        <Route path="/minha-conta" element={<MinhaContaInvestidorPage />} />

        <Route path="*" element={<Navigate to="/minha-conta" replace />} />
      </Routes>
    );
  }

  return (
    <main>
      <h1>Acesso não disponível</h1>
      <p>Não há uma área configurada para este perfil.</p>
    </main>
  );
}
