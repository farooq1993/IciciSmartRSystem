from flask import Blueprint, request, jsonify, render_template, Response
from services.ingestion_service import load_source_data, load_target_data
from services.recon_service import reconcile_data
from models.recon_model import ReconResult
from utils.database import SessionLocal
import pandas as pd
import math
from datetime import datetime
from reportlab.pdfgen import canvas
import io
from reportlab.lib.pagesizes import letter


recon_api = Blueprint("recon_api", __name__)
db = SessionLocal()

@recon_api.route("/reconcile", methods=["POST"])
def reconcile():

    try:
        # Read uploaded files correctly
        source_file = request.files.get("source_file")
        target_file = request.files.get("target_file")

        fuzzy_threshold = int(request.form.get("fuzzy_threshold", 80))

        if not source_file or not target_file:
            return jsonify({"error": "source_file and target_file are required"}), 400

        # Load CSVs into DataFrames
        source_df = pd.read_csv(source_file)
        target_df = pd.read_csv(target_file)

        # Run reconciliation
        results_df, kpis, reasons = reconcile_data(
            source_df, target_df, fuzzy_threshold=fuzzy_threshold
        )

        result_records = results_df.to_dict(orient="records")

        # Save to DB
        db = SessionLocal()
        for r in result_records:
            db.add(ReconResult(
                tran_id=r["tran_id"],
                source_amount=r["source_amount"],
                target_amount=r["target_amount"],
                status=r["status"],
                reason=r["reason"]
            ))
        db.commit()
        db.close()

        return jsonify({
            "status": "success",
            "message": "Reconciliation completed and saved",
            "kpis": kpis,
            "reasons": reasons,
            "results": result_records
        })

    except Exception as e:
        return jsonify({"error": str(e)}), 500



@recon_api.route("/reports", methods=["GET"])
def get_reports():
    rows = db.query(ReconResult).order_by(ReconResult.id.desc()).all()
    db.close()

    result = []
    for r in rows:

        source_amount = None
        target_amount = None

        # --- FIX NaN VALUES ---
        if r.source_amount is not None and not (isinstance(r.source_amount, float) and math.isnan(r.source_amount)):
            source_amount = r.source_amount

        if r.target_amount is not None and not (isinstance(r.target_amount, float) and math.isnan(r.target_amount)):
            target_amount = r.target_amount

        result.append({
            "id": r.id,
            "tran_id": r.tran_id,
            "source_amount": source_amount,
            "target_amount": target_amount,
            "status": r.status,
            "reason": r.reason
        })

    return jsonify(result)


@recon_api.route("/reports/view", methods=["GET"])
def get_reports_page():
    return render_template("reports.html")

#Export report 
@recon_api.route('/export_pdf', methods=['GET'])
def export_pdf():
    data = db.query(ReconResult).all()

    buffer = io.BytesIO()
    p = canvas.Canvas(buffer, pagesize=letter)

    y = 750
    p.setFont("Helvetica", 10)
    p.drawString(30, 800, "Reconciliation Report")
    pdf_file_name = f"{datetime.now()}_report.pdf"
    for row in data:
        line = f"{row.tran_id}  |  {row.source_amount} | {row.target_amount} | {row.status} | {row.reason}"
        p.drawString(30, y, line)
        y -= 20

        if y < 50:
            p.showPage()
            y = 750

    p.save()
    buffer.seek(0)

    return Response(
        buffer,
        mimetype="application/pdf",
        headers={"Content-Disposition": f"attachment; filename={pdf_file_name}"}
    )

@recon_api.route('/export_csv', methods=['GET'])
def export_csv():
    data = db.query(ReconResult).all()

    rows = [
        {
            "tran_id": r.tran_id,
            "source_amount": r.source_amount,
            "target_amount": r.target_amount,
            "status": r.status,
            "reason": r.reason
        }
        for r in data
    ]

    df = pd.DataFrame(rows)
    csv_file_name = f"{datetime.now()}_report.cvs"
    output = io.StringIO()
    df.to_csv(output, index=False)
    output.seek(0)

    return Response(
        output,
        mimetype="text/csv",
        headers={"Content-Disposition": f"attachment; filename={csv_file_name}"}
    )




