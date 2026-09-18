"use client";
import {useState} from "react"; import {ChevronDown,Play} from "lucide-react"; import {api} from "../lib/api";
export default function Composer({onDone}:{onDone:()=>void}){
 const [q,setQ]=useState("Find B2B SaaS companies in North America with 100–1000 employees showing buying intent"); const [plan,setPlan]=useState<any>(); const [busy,setBusy]=useState(false);
 async function run(){setBusy(true);try{const r=await api.research(q);setPlan(r.plan);onDone()}finally{setBusy(false)}}
 return <section className="border border-slate-800 bg-slate-950/70 rounded-xl p-5">
  <div className="flex justify-between"><div><h1 className="text-lg font-semibold">Research composer</h1><p className="text-xs text-slate-400 mt-1">Turn a commercial hypothesis into a bounded, evidence-backed research run.</p></div><span className="text-xs px-2 py-1 rounded bg-slate-900 border border-slate-800">12 Units est.</span></div>
  <textarea value={q} onChange={e=>setQ(e.target.value)} className="w-full h-24 mt-4 bg-slate-900 border border-slate-800 rounded-lg p-3 text-sm outline-none focus:border-slate-600"/>
  <div className="flex gap-2 mt-3 flex-wrap">{["B2B SaaS in North America, 100–1000 employees","Cloud companies hiring security leaders","FinTech SaaS with expansion signals"].map(x=><button key={x} onClick={()=>setQ(x)} className="text-xs px-3 py-1.5 rounded-full bg-slate-900 border border-slate-800 hover:border-slate-600">{x}</button>)}</div>
  <div className="flex items-center gap-3 mt-4"><button disabled={busy} onClick={run} className="inline-flex items-center gap-2 bg-white text-black px-4 py-2 rounded-lg text-sm font-medium"><Play size={14}/>{busy?"Planning…":"Run research"}</button>{plan&&<details className="text-xs text-slate-400"><summary className="cursor-pointer flex items-center gap-1">Inspect plan <ChevronDown size={13}/></summary><pre className="mt-2 p-3 bg-black rounded-lg max-w-2xl overflow-auto">{JSON.stringify(plan,null,2)}</pre></details>}</div>
 </section>
}
