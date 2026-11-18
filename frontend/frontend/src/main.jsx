import React from 'react';
import {createRoot} from 'react-dom/client';
import './style.css';

function App(){
 const [tab,setTab]=React.useState('vpn');
 const [regions,setRegions]=React.useState([]);
 const [region,setRegion]=React.useState('us-east');
 const [ipType,setIpType]=React.useState('shared');
 const [device,setDevice]=React.useState('Meu dispositivo');
 const [notice,setNotice]=React.useState('');
 React.useEffect(()=>{fetch('http://localhost:8000/api/regions').then(r=>r.json()).then(d=>setRegions(d.regions||[])).catch(()=>setNotice('Inicie a API para carregar as regiões.'));},[]);
 async function config(){
  setNotice('Solicitação demonstrativa: o provisionamento real será conectado aos servidores WireGuard.');
  try{const r=await fetch('http://localhost:8000/api/wireguard/config',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({region_id:region,device_name:device,ip_type:ipType})});const d=await r.json();if(!r.ok)setNotice(d.detail||'Não foi possível solicitar a configuração.');}catch{setNotice('API indisponível.');}
 }
 return <div className="shell"><header><a className="brand">🥭 MANGA VPN</a><nav><a href="#recursos">Recursos</a><a href="#conta">Minha conta</a><button>Entrar</button></nav></header><main>
 <section className="hero"><small>PRIVACIDADE E CONTROLE</small><h1>Sua conexão.<br/><em>Seu IP. Seu controle.</em></h1><p>Gerencie conexões WireGuard e navegação por proxy em uma única plataforma.</p><div className="pills"><span>Windows</span><span>macOS</span><span>Android</span><span>iPhone</span></div></section>
 <section className="workspace" id="recursos"><div className="tabs"><button className={tab==='vpn'?'active':''} onClick={()=>setTab('vpn')}>VPN WireGuard</button><button className={tab==='proxy'?'active':''} onClick={()=>setTab('proxy')}>Proxy no navegador</button></div>
 {tab==='vpn'?<div className="panel"><small>CONEXÃO VPN</small><h2>Escolha sua localização</h2><label>Localização</label><select value={region} onChange={e=>setRegion(e.target.value)}>{regions.map(r=><option key={r.id} value={r.id}>{r.name}</option>)}</select><label>Tipo de IP</label><div className="choices"><button className={ipType==='shared'?'selected':''} onClick={()=>setIpType('shared')}><b>IP compartilhado</b><small>Saída compartilhada entre clientes.</small></button><button className={ipType==='dedicated'?'selected':''} onClick={()=>setIpType('dedicated')}><b>IP dedicado</b><small>Endereço reservado para sua conta.</small></button></div><label>Nome do dispositivo</label><input value={device} onChange={e=>setDevice(e.target.value)}/><button className="primary" onClick={config}>Solicitar configuração WireGuard</button><p className="hint">Importe o perfil no cliente oficial WireGuard do seu dispositivo.</p></div>:<div className="panel"><small>NAVEGAÇÃO PELO SITE</small><h2>Proxy web</h2><label>Endereço do site</label><input placeholder="https://exemplo.com"/><button className="primary" onClick={()=>setNotice('Proxy ainda em desenvolvimento. Será implementado com destinos permitidos e proteção contra acesso a redes internas.')}>Abrir pelo proxy</button><p className="hint">O proxy encaminhará somente sessões compatíveis dentro do Manga VPN. Não altera o IP de outros aplicativos.</p></div>}
 {notice&&<div className="notice">{notice}</div>}</section>
 <section className="features"><article><b>01</b><h3>Escolha a localização</h3><p>Selecione um servidor disponível conforme seu plano.</p></article><article><b>02</b><h3>Gerencie seus IPs</h3><p>Use endereços compartilhados ou dedicados.</p></article><article><b>03</b><h3>Controle sua conta</h3><p>Gerencie dispositivos e configurações em um só lugar.</p></article></section></main><footer>© 2026 Manga VPN · Protótipo de desenvolvimento</footer></div>
}
createRoot(document.getElementById('root')).render(<App/>);