/** Exibe mensagens de erro da interface. */

type Props = {
  message: string | null
}

/** Banner simples para erros de formularios e listas. */
export function ErrorBanner({ message }: Props) {
  if (!message) {
    return null
  }

  return <div className="error-banner">{message}</div>
}
