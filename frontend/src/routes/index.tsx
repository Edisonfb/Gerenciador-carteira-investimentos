import { Navigate, Route, Routes } from "react-router-dom";
import { LayoutLogin } from "../components/LayoutLogin";
import { LayoutPadrao } from "../components/LayoutPadrao";
import { InvestidoresPage } from "../pages/InvestidoresPage";
import { EdicaoInvestidorPage } from "../pages/EdicaoInvestidorPage";
import { CadastroInvestidorPage } from "../pages/CadastroInvestidorPage";
import { AcessoSenhaPage } from "../pages/AcessoSenhaPage";
import { MinhaContaPage } from "../pages/MinhaContaPage";
import { CarteirasInvestidorPage } from "../pages/CarteirasInvestidorPage";
import { CadastroCarteiraPage } from "../pages/CadastroCarteiraPage";

import { Login } from "../pages/Login";
import { MinhaContaInvestidorPage } from "../pages/MinhaContaInvestidorPage";
import { RotaProtegida } from "./RotaProtegida";

export const Rotas = () => (
  <Routes>
    <Route path="/" element={<LayoutLogin />}>
      <Route index element={<Login />} />
      <Route path="esqueci-senha" element={<AcessoSenhaPage />} />
      <Route path="primeiro-acesso" element={<AcessoSenhaPage primeiroAcesso />} />
      <Route path="primeiro-acesso/definir-senha" element={<AcessoSenhaPage primeiroAcesso definirSenha />} />
      <Route path="definir-senha" element={<AcessoSenhaPage definirSenha />} />
    </Route>

    <Route element={<RotaProtegida perfisPermitidos={["investidor"]} />}>
      <Route path="/minha-conta" element={<LayoutPadrao />}>
        <Route index element={<MinhaContaInvestidorPage />} />
      </Route>
      <Route path="/carteiras-investidor" element={<LayoutPadrao />}>
        <Route index element={<CarteirasInvestidorPage />} />
      </Route>
      <Route path="/carteiras-nova" element={<LayoutPadrao />}>
        <Route index element={<CadastroCarteiraPage />} />
      </Route>
    </Route>

    <Route element={<RotaProtegida perfisPermitidos={["analista"]} />}>

      <Route path="/minha-conta-analista" element={<LayoutPadrao />}>
        <Route index element={<MinhaContaPage />} />
      </Route>
      <Route path="/dashboard" element={<Navigate to="/minha-conta-analista" replace />} />

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