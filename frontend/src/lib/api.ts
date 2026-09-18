const API=process.env.NEXT_PUBLIC_API_URL||"http://localhost:8000";
async function j(path:string,init?:RequestInit){const r=await fetch(API+path,{...init,headers:{"Content-Type":"application/json",...(init?.headers||{})}});if(!r.ok)throw new Error(await r.text());return r.json()}
export const api={entities:()=>j("/api/entities"),detail:(id:string)=>j("/api/entities/"+id),research:(query:string)=>j("/api/research",{method:"POST",body:JSON.stringify({query})}),job:(id:string)=>j("/api/research/"+id),
enrich:(ids:string[],operation:string)=>j("/api/enrichments",{method:"POST",body:JSON.stringify({target_company_ids:ids,operation})}),
runEnrich:(id:string)=>j("/api/enrichments/"+id+"/run",{method:"POST"}),enrichJob:(id:string)=>j("/api/enrichments/"+id),
exportCsv:()=>API+"/api/export/csv"};
