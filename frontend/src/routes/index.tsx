import { BrowserRouter, Routes, Route } from "react-router-dom";
import { LayoutPadrao } from "../components/LayoutPadrao";
import { Login } from "../components/Login";
import { Dashboard } from "../pages/Dashboard";
import { LoginAnalista } from "../pages/LoginAnalista";

export const Rotas = () => {
  return (
    <BrowserRouter>
      <Routes>
        <Route path="/" element={<Login />}>
          <Route index element={<LoginAnalista />} />
        </Route>

        
       
      </Routes>
    </BrowserRouter>
  );
};