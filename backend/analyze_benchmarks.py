import asyncio
import json
from collections import defaultdict
from sqlalchemy.future import select
from app.database.database import AsyncSessionLocal
from app.models import BenchmarkRun

async def analyze():
    async with AsyncSessionLocal() as db:
        res = await db.execute(select(BenchmarkRun))
        runs = res.scalars().all()

        if not runs:
            print("No benchmark runs found.")
            return

        total_runs = len(runs)
        
        # 1. Error Categorization (Average accuracy per field)
        scalar_accs = defaultdict(list)
        list_precs = defaultdict(list)
        list_recs = defaultdict(list)
        list_accs = defaultdict(list)
        
        # 2. Hospital Comparison
        hosp_accs = defaultdict(list)

        for r in runs:
            m = r.metrics_json
            hosp = r.document_source.split('.')[0] if r.document_source else "Unknown"
            
            overall = m.get("overall", {}).get("accuracy", 0)
            hosp_accs[hosp].append(overall)

            for k, v in m.get("scalar_fields", {}).items():
                scalar_accs[k].append(v.get("accuracy", 0))

            for k, v in m.get("list_fields", {}).items():
                list_precs[k].append(v.get("precision", 0))
                list_recs[k].append(v.get("recall", 0))
                list_accs[k].append(v.get("accuracy", 0))

        print("=== 1. Error Categorization ===")
        for k, v in scalar_accs.items():
            print(f"  {k}: {sum(v)/len(v):.2%}")
        for k in list_accs.keys():
            p = sum(list_precs[k])/len(list_precs[k])
            r = sum(list_recs[k])/len(list_recs[k])
            a = sum(list_accs[k])/len(list_accs[k])
            print(f"  {k}: Precision={p:.2%}, Recall={r:.2%}, Accuracy={a:.2%}")

        print("\n=== 2. Hospital Comparison ===")
        for hosp, accs in hosp_accs.items():
            print(f"  {hosp}: {sum(accs)/len(accs):.2%}")

        print("\n=== 4. Failure Pattern Detection ===")
        print("  Highest Error Rates found in:")
        sorted_fields = []
        for k, v in scalar_accs.items():
            sorted_fields.append((k, sum(v)/len(v)))
        for k in list_accs.keys():
            sorted_fields.append((k, sum(list_accs[k])/len(list_accs[k])))
        
        sorted_fields.sort(key=lambda x: x[1])
        for f, acc in sorted_fields[:3]:
            print(f"  - {f} (Accuracy: {acc:.2%})")

if __name__ == "__main__":
    asyncio.run(analyze())
