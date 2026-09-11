/** Configuracao de rotas do frontend. */

import { Navigate, Route, Routes } from 'react-router-dom'
import { AppLayout } from '../components/AppLayout'
import { ProtectedRoute } from '../components/ProtectedRoute'
import { AssetsPage } from '../pages/AssetsPage'
import { HomePage } from '../pages/HomePage'
import { InvestorsPage } from '../pages/InvestorsPage'
import { LoginPage } from '../pages/LoginPage'
import { PortfolioSummaryPage } from '../pages/PortfolioSummaryPage'
import { PortfoliosPage } from '../pages/PortfoliosPage'
import { RegisterPage } from '../pages/RegisterPage'
import { TransactionsPage } from '../pages/TransactionsPage'

/** Define rotas publicas e autenticadas da aplicacao. */
export function AppRoutes() {
  return (
    <Routes>
      <Route path="/login" element={<LoginPage />} />
      <Route path="/register" element={<RegisterPage />} />
      <Route element={<ProtectedRoute />}>
        <Route element={<AppLayout />}>
          <Route path="/" element={<HomePage />} />
          <Route path="/investors" element={<InvestorsPage />} />
          <Route path="/portfolios" element={<PortfoliosPage />} />
          <Route
            path="/portfolios/:portfolioId/summary"
            element={<PortfolioSummaryPage />}
          />
          <Route path="/assets" element={<AssetsPage />} />
          <Route path="/transactions" element={<TransactionsPage />} />
        </Route>
      </Route>
      <Route path="*" element={<Navigate to="/" replace />} />
    </Routes>
  )
}
