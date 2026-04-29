/**
 * TigerEx Futures Trading - React/TypeScript
 */
import React from 'react';
const contracts = [
  { symbol: 'BTC/USDT', price: 42500, change: 2.5, funding: 0.01, leverage: 125 },
  { symbol: 'ETH/USDT', price: 2250, change: 3.2, funding: 0.01, leverage: 100 },
  { symbol: 'SOL/USDT', price: 98.5, change: -1.5, funding: -0.01, leverage: 50 }
];
const Futures: React.FC = () => (
  <div style={{padding:'24px',background:'#0B0E14',minHeight:'100vh',color:'#EAECE4',fontFamily:'Inter,sans-serif'}}>
    <header style={{display:'flex',justifyContent:'space-between',padding:'16px 24px',background:'#1C2128',marginBottom:'24px',borderRadius:'12px'}}>
      <div style={{color:'#F0B90B',fontWeight:700,fontSize:'22px'}}>🐯 TigerEx Futures (React/TS)</div>
      <nav style={{display:'flex',gap:'20px'}}><a href="/spot.html" style={{color:'#8B929E'}}>Spot</a><a href="/futures.html" style={{color:'#F0B90B'}}>Futures</a></nav>
    </header>
    <h1>Futures Trading</h1>
    <p style={{color:'#8B929E',marginBottom:'24px'}}>USDT-M & COIN-M perpetual futures with up to 125x leverage</p>
    <div style={{display:'flex',gap:'8px',marginBottom:'24px'}}>
      <button style={{padding:'12px 24px',background:'#F0B90B',border:'none',borderRadius:'8px',fontWeight:600,cursor:'pointer'}}>USDT-M</button>
      <button style={{padding:'12px 24px',background:'#1C2128',border:'1px solid #2A303C',borderRadius:'8px',color:'#8B929E'}}>COIN-M</button>
    </div>
    <div style={{display:'grid',gridTemplateColumns:'repeat(auto-fill,minmax(280px,1fr))',gap:'16px'}}>
      {contracts.map(c => (
        <div key={c.symbol} style={{background:'#1C2128',padding:'20px',borderRadius:'12px'}}>
          <div style={{display:'flex',justifyContent:'space-between',marginBottom:'12px'}}>
            <span style={{fontWeight:700}}>{c.symbol}</span>
            <span style={{background:'#F0B90B',color:'#000',padding:'2px 8px',borderRadius:'4px',fontSize:'12px'}}>{c.leverage}x</span>
          </div>
          <div style={{fontSize:'24px',fontWeight:700,color:c.change>=0?'#00C087':'#F6465D',marginBottom:'12px'}}>${c.price.toLocaleString()}</div>
          <div style={{fontSize:'12px',color:'#8B929E',marginBottom:'12px'}}>Funding: {c.funding}%</div>
          <div style={{display:'grid',gridTemplateColumns:'1fr 1fr',gap:'8px'}}>
            <button style={{padding:'12px',background:'#00C087',border:'none',borderRadius:'8px',fontWeight:600,cursor:'pointer'}}>Long</button>
            <button style={{padding:'12px',background:'#F6465D',border:'none',borderRadius:'8px',fontWeight:600,color:'#fff'}}>Short</button>
          </div>
        </div>
      ))}
    </div>
  </div>
);
export default Futures;