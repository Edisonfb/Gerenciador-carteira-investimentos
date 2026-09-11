/** Componente raiz da aplicacao. */

import { BrowserRouter } from 'react-router-dom'
import { AuthProvider } from './hooks/AuthProvider'
import { AppRoutes } from './routes/AppRoutes'
import './styles/app.css'

/** Monta providers e rotas do frontend. */
function App() {
  return (
    <BrowserRouter>
      <AuthProvider>
        <AppRoutes />
      </AuthProvider>
    </BrowserRouter>
  )
}

export default App
