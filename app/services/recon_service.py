from services.utils import fuzzy_match
import pandas as pd

def reconcile_data(source_df, target_df, fuzzy_threshold=80):
    results = []
    reasons_count = {"Exact match": 0, "Amount mismatch": 0,
                     "Description fuzzy match": 0, "Record missing in target system": 0}

    matched = 0
    unmatched = 0
    pending = 0

    for _, s in source_df.iterrows():
        match = target_df[target_df["tran_id"] == s["tran_id"]]

        if match.empty:
            unmatched += 1
            reasons_count["Record missing in target system"] += 1

            results.append({
                "tran_id": s["tran_id"],
                "source_amount": s["amount"],
                "target_amount": None,
                "status": "UNMATCHED",
                "reason": "Record missing in target system"
            })
            continue

        t = match.iloc[0]

        if s["amount"] == t["amount"]:
            matched += 1
            status = "MATCHED"
            reason = "Exact match"
            reasons_count["Exact match"] += 1
        else:
            score = fuzzy_match(str(s["description"]), str(t["description"]))

            if score >= fuzzy_threshold:
                pending += 1
                status = "PENDING"
                reason = f"Amount mismatch but description fuzzy match: score={score}"
                reasons_count["Description fuzzy match"] += 1
            else:
                unmatched += 1
                status = "UNMATCHED"
                reason = "Amount mismatch"
                reasons_count["Amount mismatch"] += 1

        results.append({
            "tran_id": s["tran_id"],
            "source_amount": s["amount"],
            "target_amount": t["amount"],
            "status": status,
            "reason": reason
        })

    results_df = pd.DataFrame(results)

    kpis = {
        "total": len(results),
        "matched": matched,
        "unmatched": unmatched,
        "pending": pending,
        "match_percentage": round((matched / len(results)) * 100, 2) if len(results) else 0
    }

    return results_df, kpis, reasons_count
