import { useEffect, useState } from "react";

interface HealthResponse {
  status: string;
  app: string;
}

export const DashboardAnalista = () => {
  const [mensagemApi, setMensagemApi] = useState("Carregando API...");

  useEffect(() => {
    async function testarApi() {
      try {
        const resposta = await fetch("http://127.0.0.1:8000/health");
        const dados: HealthResponse = await resposta.json();

        setMensagemApi(`API conectada: ${dados.app}`);
      } catch {
        setMensagemApi("Não foi possível conectar com a API.");
      }
    }

    testarApi();
  }, []);

  return (
    <div>
      <h1>Dashboard/Home do Analista</h1>
      <p>{mensagemApi}</p>
    </div>
  );
};