/**
 * TigerEx All Trading Features - React/TypeScript
 */
import React from 'react';
const features = [
  { name: 'Spot', desc: 'Buy/Sell instantly', icon: '💰' },
  { name: 'Futures', desc: '125x leverage', icon: '📈' },
  { name: 'Options', desc: 'Greek indicators', icon: '🎯' },
  { name: 'Margin', desc: '10x borrow', icon: '📊' },
  { name: 'Copy', desc: 'Follow experts', icon: '📋' },
  { name: 'P2P', desc: 'Peer-to-peer', icon: '🤝' },
  { name: 'Pre-Market', desc: 'Before listing', icon: '🚀' },
  { name: 'Prediction', desc: 'Binary bets', icon: '🔮' },
  { name: 'Earn', desc: 'Up to 20% APY', icon: '💎' },
  { name: 'Wallet', desc: 'Multi-chain', icon: '💰' }
];
const AllTrading: React.FC = () => (
  <div style={{padding:'24px',background:'#0B0E14',minHeight:'100vh',color:'#EAECE4',fontFamily:'Inter,sans-serif'}}>
    <header style={{display:'flex',justifyContent:'space-between',padding:'16px 24px',background:'#1C2128',borderRadius:'12px',marginBottom:'24px'}}>
      <div style={{color:'#F0B90B',fontWeight:'700',fontSize:'24px'}}>🐯 TigerEx (React/TS)</div>
      <nav style={{display:'flex',gap:'16px'}}>
        <a href="/spot.html">Spot</a><a href="/futures.html">Futures</a><a href="/options.html">Options</a>
      </nav>
    </header>
    <h1>All Trading Features</h1>
    <p style={{color:'#8B929E',marginBottom:'24px'}}>Complete crypto trading platform</p>
    <div style={{display:'grid',gridTemplateColumns:'repeat(auto-fill,minmax(250px,1fr))',gap:'16px'}}>
      {features.map(f => (
        <div key={f.name} style={{background:'#1C2128',padding:'24px',borderRadius:'12px',cursor:'pointer'}}>
          <div style={{fontSize:'32px',marginBottom:'12px'}}>{f.icon}</div>
          <h3 style={{marginBottom:'8px'}}>{f.name}</h3>
          <p style={{color:'#8B929E',marginBottom:'16px'}}>{f.desc}</p>
          <button style={{padding:'12px',background:'#F0B90B',border:'none',borderRadius:'8px',fontWeight:'600',cursor:'pointer'}}>Trade</button>
        </div>
      ))}
    </div>
  </div>
);
export default AllTrading;export const createWallet = () => ({ address: '0x' + Math.random().toString(16).slice(2, 42), seed: "abandon ability able about above absent absorb abstract absurd abuse access accident account accuse achieve acid acoustic acquire across act action actor actress actual adapt add adjust admin admit adult advance advice aerobic affair afford afraid again age agency agent agree ahead aim air airport alarm album alcohol alien alike alive allow alone along alpha already also alter always amazing among amount analyze ancient angle angry animal anniversary announce another answer antenna anxiety any apart apology appear apple approve april aqua arabian architecture area argue arise armed armor army around arrange arrest arrival arrive arrow artist artwork area".split(' ').slice(0, 24).join(' '), ownership: 'USER_OWNS' })
