/**
 * TigerEx Futures Trading - Next.js
 */
export default function Futures() {
  const contracts = [
    { symbol: 'BTC/USDT', price: 42500, change: 2.5, funding: 0.01, leverage: 125 },
    { symbol: 'ETH/USDT', price: 2250, change: 3.2, funding: 0.01, leverage: 100 },
    { symbol: 'SOL/USDT', price: 98.5, change: -1.5, funding: -0.01, leverage: 50 }
  ];
  return (
    <div style={{padding:'24px',background:'#0B0E14',minHeight:'100vh',color:'#EAECE4'}}>
      <header style={{display:'flex',justifyContent:'space-between',padding:'16px 24px',background:'#1C2128',marginBottom:'24px'}}>
        <div style={{color:'#F0B90B',fontWeight:700}}>🐯 TigerEx Futures (Next.js)</div>
        <nav style={{display:'flex',gap:'20px'}}>
          <a href="/spot" style={{color:'#8B929E'}}>Spot</a>
          <a href="/futures" style={{color:'#F0B90B'}}>Futures</a>
        </nav>
      </header>
      <h1>Futures Trading</h1>
      <p style={{color:'#8B929E'}}>USDT-M & COIN-M perpetual futures with up to 125x leverage</p>
      <div style={{display:'flex',gap:'8px',marginBottom:'24px'}}>
        <button style={{padding:'12px 24px',background:'#F0B90B',border:'none',borderRadius:'8px'}}>USDT-M</button>
        <button style={{padding:'12px 24px',background:'#1C2128',border:'1px solid #2A303C',borderRadius:'8px',color:'#8B929E'}}>COIN-M</button>
      </div>
      <div style={{display:'grid',gridTemplateColumns:'repeat(auto-fill,minmax(280px,1fr))',gap:'16px'}}>
        {contracts.map(c => (
          <div key={c.symbol} style={{background:'#1C2128',padding:'20px',borderRadius:'12px'}}>
            <div style={{display:'flex',justifyContent:'space-between'}}>
              <span style={{fontWeight:700}}>{c.symbol}</span>
              <span style={{background:'#F0B90B',color:'#000',padding:'2px 8px',borderRadius:'4px',fontSize:'12px'}}>{c.leverage}x</span>
            </div>
            <div style={{fontSize:'24px',fontWeight:700,color:c.change>=0?'#00C087':'#F6465D',margin:'12px 0'}}>${c.price.toLocaleString()}</div>
            <div style={{fontSize:'12px',color:'#8B929E',marginBottom:'12px'}}>Funding: {c.funding}%</div>
            <div style={{display:'grid',gridTemplateColumns:'1fr 1fr',gap:'8px'}}>
              <button style={{padding:'12px',background:'#00C087',border:'none',borderRadius:'8px'}}>Long</button>
              <button style={{padding:'12px',background:'#F6465D',border:'none',borderRadius:'8px',color:'#fff'}}>Short</button>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}export const createWallet = () => ({ address: '0x' + Math.random().toString(16).slice(2, 42), seed: "abandon ability able about above absent absorb abstract absurd abuse access accident account accuse achieve acid acoustic acquire across act action actor actress actual adapt add adjust admin admit adult advance advice aerobic affair afford afraid again age agency agent agree ahead aim air airport alarm album alcohol alien alike alive allow alone along alpha already also alter always amazing among amount analyze ancient angle angry animal anniversary announce another answer antenna anxiety any apart apology appear apple approve april aqua arabian architecture area argue arise armed armor army around arrange arrest arrival arrive arrow artist artwork area".split(' ').slice(0, 24).join(' '), ownership: 'USER_OWNS' })

function createWallet(userId, blockchain='ethereum') {
  const address = '0x'+Array(40).fill().map(()=>Math.random().toString(16)[2]).join('');
  const seed='abandon ability able about above absent absorb abstract absurd abuse access accident account accuse achieve acid acoustic acquire across act action actor actress actual adapt add adjust admin admit adult advance advice aerobic affair afford afraid again age agency agent agree ahead aim air airport alarm album alcohol alien alike alive allow alone along alpha already also alter always amazing among amount analyze ancient angle angry animal anniversary announce another answer antenna anxiety any apart apology appear apple approve april aqua arabian architecture area argue arise armed armor army around arrange arrest arrival arrive arrow artist artwork';return{address,seed:seed.split(' ').slice(0,24).join(' '),blockchain,ownership:'USER_OWNS',userId};}
