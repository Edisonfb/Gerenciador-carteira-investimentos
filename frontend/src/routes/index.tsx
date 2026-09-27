import { Routes, Route } from "react-router-dom";
import { LayoutPadrao } from "../components/LayoutPadrao";
import { LayoutLogin } from "../components/LayoutLogin";
import { Dashboard } from "../pages/Dashboard";
import { Login } from "../pages/Login";

export const Rotas = () => {
  return (
    <Routes>
      <Route path="/" element={<LayoutLogin />}>
        <Route index element={<Login />} />
      </Route>

      <Route path="/" element={<LayoutPadrao />}>
        <Route path="Dashboard" element={<Dashboard />} />
      </Route>
    </Routes>
  );
};
