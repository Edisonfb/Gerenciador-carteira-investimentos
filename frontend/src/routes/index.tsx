import { BrowserRouter, Routes, Route } from "react-router-dom";
import { LayoutPadrao } from "../components/LayoutPadrao";
import { LayoutLogin } from "../components/LayoutLogin";
import { Dashboard } from "../pages/Dashboard";
import { Login } from "../pages/Login";
import { CadastroUsuarioPage } from "../pages/CadastroUsuarioPage";
import { CadastroInvestidorPage } from "../pages/CadastroInvestidorPage";

export const Rotas = () => {
  return (
      <Routes>
        <Route path="/dashboard" element={<LayoutPadrao />}>
          <Route index element={<Dashboard />} />   

        </Route>
        
        <Route path="/" element={<LayoutLogin/>}>
          <Route index element={<Login />} />
        </Route>

        <Route path="/cadastrar" element={<LayoutPadrao />}>
        <Route index element={<CadastroInvestidorPage />} />
        </Route>
       
      </Routes>
  );
};