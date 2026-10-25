import { Navigate, Route, Routes } from "react-router-dom";
import { LayoutLogin } from "../components/LayoutLogin";
import { LayoutPadrao } from "../components/LayoutPadrao";
import { CadastroInvestidorPage } from "../pages/CadastroInvestidorPage";
import { DashboardAnalista } from "../pages/DashboardAnalista";
import { InvestidoresPage } from "../pages/InvestidoresPage";
import { EdicaoInvestidorPage } from "../pages/EdicaoInvestidorPage";

import { Login } from "../pages/Login";
import { MinhaContaInvestidorPage } from "../pages/MinhaContaInvestidorPage";
import { RotaProtegida } from "./RotaProtegida";

export const Rotas = () => (
  <Routes>
    <Route path="/" element={<LayoutLogin />}>
      <Route index element={<Login />} />
    </Route>

    <Route element={<RotaProtegida perfisPermitidos={["investidor"]} />}>
      <Route path="/minha-conta" element={<LayoutPadrao />}>
        <Route index element={<MinhaContaInvestidorPage />} />
      </Route>
    </Route>

    <Route element={<RotaProtegida perfisPermitidos={["analista"]} />}>

      <Route path="/dashboard" element={<LayoutPadrao />}>
        <Route index element={<DashboardAnalista />} />
      </Route>

      <Route path="/investidores" element={<LayoutPadrao />}>
        <Route index element={<InvestidoresPage />} />
      </Route>

      <Route path="/investidores/novo" element={<LayoutPadrao />}>
        <Route index element={<CadastroInvestidorPage />} />
      </Route>

      <Route path="/investidores/:id/editar" element={<LayoutPadrao />}>
        <Route index element={<EdicaoInvestidorPage />} />
      </Route>
      
      <Route path="/cadastrar" element={<LayoutPadrao />}>
        <Route index element={<CadastroInvestidorPage />} />
      </Route>

    </Route>

    <Route path="*" element={<Navigate to="/" replace />} />
  </Routes>
);