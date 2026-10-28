import { Navigate } from "react-router-dom";

// Mantém compatibilidade com os endereços antigos de convite.
export const GerarTokenInvestidorPage = () => <Navigate to="/investidores" replace state={{ abrirConvite: true }} />;
