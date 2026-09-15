const summaries = [
  { label: 'Patrimônio total', value: 'R$ 128.450,00', change: '+8,4%' },
  { label: 'Rentabilidade', value: '12,3% a.a.', change: '+1,1%' },
  { label: 'Investido', value: 'R$ 96.200,00', change: '+5,6%' },
  { label: 'Disponível', value: 'R$ 18.700,00', change: '0,0%' },
];

const portfolio = [
  { symbol: 'AAPL', name: 'Apple Inc.', shares: '25 ações', value: 'R$ 12.400,00' },
  { symbol: 'PETR4', name: 'Petrobras', shares: '80 ações', value: 'R$ 8.300,00' },
  { symbol: 'MSFT', name: 'Microsoft', shares: '18 ações', value: 'R$ 11.900,00' },
  { symbol: 'IVVB11', name: 'ETF B3', shares: '70 cotas', value: 'R$ 9.750,00' },
];

const transactions = [
  { type: 'Compra', asset: 'AAPL', date: '12 ago', value: '+ R$ 2.100,00' },
  { type: 'Venda', asset: 'PETR4', date: '10 ago', value: '- R$ 1.350,00' },
  { type: 'Dividendos', asset: 'MSFT', date: '08 ago', value: '+ R$ 420,00' },
  { type: 'Compra', asset: 'IVVB11', date: '05 ago', value: '+ R$ 950,00' },
];

export const Dashboard = () => {
  return (
    <div style={{ display: 'grid', gap: '1.5rem' }}>
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', gap: '1rem', flexWrap: 'wrap' }}>
        <div>
          <p style={{ margin: 0, color: '#64748b', fontSize: '0.875rem' }}>Visão geral</p>
          <h1 style={{ margin: '0.25rem 0 0', fontSize: '2rem' }}>Dashboard</h1>
        </div>
        <button
          type="button"
          style={{
            border: 'none',
            background: '#2563eb',
            color: '#fff',
            padding: '0.75rem 1.25rem',
            borderRadius: '10px',
            fontWeight: 600,
            cursor: 'pointer',
          }}
        >
          Nova transação
        </button>
      </div>

      <section style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(200px, 1fr))', gap: '1rem' }}>
        {summaries.map((item) => (
          <div
            key={item.label}
            style={{
              background: '#fff',
              border: '1px solid #e2e8f0',
              borderRadius: '16px',
              padding: '1.25rem',
              boxShadow: '0 2px 8px rgba(15, 23, 42, 0.04)',
            }}
          >
            <p style={{ margin: 0, color: '#64748b', fontSize: '0.85rem' }}>{item.label}</p>
            <h2 style={{ margin: '0.75rem 0 0.35rem', fontSize: '1.6rem', color: '#0f172a' }}>{item.value}</h2>
            <span style={{ color: '#16a34a', fontWeight: 700, fontSize: '0.85rem' }}>{item.change}</span>
          </div>
        ))}
      </section>

      <section style={{ display: 'grid', gridTemplateColumns: '1.6fr 1fr', gap: '1.5rem' }}>
        <div style={{ background: '#fff', borderRadius: '16px', border: '1px solid #e2e8f0', padding: '1.5rem' }}>
          <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: '1rem' }}>
            <h3 style={{ margin: 0, color: '#0f172a' }}>Carteiras</h3>
            <span style={{ color: '#64748b', fontSize: '0.85rem' }}>Últimos 30 dias</span>
          </div>

          <div style={{ height: '220px', background: 'linear-gradient(180deg, #dbeafe 0%, #eff6ff 100%)', borderRadius: '12px', padding: '1rem', display: 'flex', alignItems: 'flex-end', gap: '0.75rem' }}>
            {[40, 60, 55, 80, 72, 96, 90].map((height, index) => (
              <div key={index} style={{ flex: 1, height: `${height}%`, background: '#2563eb', borderRadius: '10px 10px 0 0', opacity: 0.7 + index * 0.04 }} />
            ))}
          </div>
        </div>

        <div style={{ background: '#fff', borderRadius: '16px', border: '1px solid #e2e8f0', padding: '1.5rem' }}>
          <h3 style={{ margin: '0 0 1rem', color: '#0f172a' }}>Ativos em destaque</h3>
          <div style={{ display: 'grid', gap: '0.9rem' }}>
            {portfolio.map((item) => (
              <div key={item.symbol} style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', paddingBottom: '0.75rem', borderBottom: '1px solid #e2e8f0' }}>
                <div>
                  <strong style={{ display: 'block', color: '#0f172a' }}>{item.symbol}</strong>
                  <span style={{ fontSize: '0.8rem', color: '#64748b' }}>{item.name}</span>
                </div>
                <div style={{ textAlign: 'right' }}>
                  <div style={{ fontSize: '0.8rem', color: '#64748b' }}>{item.shares}</div>
                  <strong style={{ color: '#0f172a' }}>{item.value}</strong>
                </div>
              </div>
            ))}
          </div>
        </div>
      </section>

      <section style={{ background: '#fff', borderRadius: '16px', border: '1px solid #e2e8f0', padding: '1.5rem' }}>
        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '1rem' }}>
          <h3 style={{ margin: 0, color: '#0f172a' }}>Transações recentes</h3>
          <a href="/" style={{ color: '#2563eb', textDecoration: 'none', fontWeight: 600 }}>Ver tudo</a>
        </div>

        <div style={{ display: 'grid', gap: '0.85rem' }}>
          {transactions.map((item) => (
            <div key={`${item.type}-${item.asset}-${item.date}`} style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', padding: '0.8rem 0', borderBottom: '1px solid #e2e8f0' }}>
              <div>
                <strong style={{ color: '#0f172a', display: 'block' }}>{item.type}</strong>
                <span style={{ color: '#64748b', fontSize: '0.85rem' }}>{item.asset} • {item.date}</span>
              </div>
              <span style={{ color: item.value.startsWith('+') ? '#16a34a' : '#dc2626', fontWeight: 700 }}>{item.value}</span>
            </div>
          ))}
        </div>
      </section>
    </div>
  );
};