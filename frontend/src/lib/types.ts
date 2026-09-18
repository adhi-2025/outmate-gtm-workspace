export type Company={id:string;name:string;domain:string;location:string;employee_range:string;industry:string;score:number|null;score_breakdown:Record<string,any>;evidence_count:number;evidence_status:string;top_decision_maker:string|null};
export type Evidence={id:string;entity_id:string;claim_field:string;observed_value:string;source_url:string;retrieved_at:string;evidence_type:string;confidence_score:number;conflict_note?:string|null};
export type Detail={company:Company;evidence:Evidence[];people:any[];signals:any[]};
export type Enrichment={id:string;status:string;progress_pct:number;operation:string;rows:any[];errors:string[]};
