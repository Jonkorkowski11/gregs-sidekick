import antigravity  # 🚀 UP, UP, AND AWAY!
import io
from flask import Flask, request, send_file, render_template_string
from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet
from datetime import date

app = Flask(__name__)

# --- THE FRONTEND UI (TAILWIND CSS) ---
HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Greg's Sidekick - Master Builder</title>
    <script src="https://cdn.tailwindcss.com"></script>
</head>
<body class="bg-slate-900 text-white min-h-screen p-4 md:p-10 font-sans">
    <div class="max-w-3xl mx-auto">
        <h1 class="text-4xl md:text-5xl font-extrabold text-blue-500 mb-2 flex items-center gap-3">
            🛠️ GREG'S SIDEKICK
        </h1>
        <p class="text-slate-400 mb-8 text-lg border-b border-slate-700 pb-4">PlumbingCAD Takeoff & Auto-Invoice Engine</p>

        <form action="/generate-invoice" method="POST" class="bg-slate-800 p-6 md:p-8 rounded-xl shadow-2xl border border-slate-700">
            <h2 class="text-2xl font-bold text-white mb-6">Job Details</h2>
            
            <div class="grid grid-cols-1 md:grid-cols-2 gap-6 mb-8">
                <div>
                    <label class="block text-sm font-semibold text-slate-300 mb-2">Client Name</label>
                    <input type="text" name="client_name" value="Sarah & John Connor" class="w-full p-3 rounded bg-slate-900 text-white border border-slate-600 focus:border-blue-500 focus:outline-none">
                </div>
                <div>
                    <label class="block text-sm font-semibold text-slate-300 mb-2">Job Address</label>
                    <input type="text" name="job_address" value="456 Oak Lane, East Brunswick, NJ" class="w-full p-3 rounded bg-slate-900 text-white border border-slate-600 focus:border-blue-500 focus:outline-none">
                </div>
                <div>
                    <label class="block text-sm font-semibold text-slate-300 mb-2">Labor Hours</label>
                    <input type="number" step="0.5" name="labor_hours" value="8" class="w-full p-3 rounded bg-slate-900 text-white border border-slate-600 focus:border-blue-500 focus:outline-none">
                </div>
                <div>
                    <label class="block text-sm font-semibold text-slate-300 mb-2">Labor Rate ($/hr)</label>
                    <input type="number" step="1" name="labor_rate" value="125" class="w-full p-3 rounded bg-slate-900 text-white border border-slate-600 focus:border-blue-500 focus:outline-none">
                </div>
            </div>

            <h2 class="text-2xl font-bold text-blue-400 mb-2">PlumbingCAD Materials Takeoff</h2>
            <p class="text-sm text-slate-400 mb-4">Paste exported CAD lists here (Format: Item Description, Quantity, Unit Price)</p>
            <textarea name="materials" rows="6" class="w-full p-4 rounded bg-slate-900 text-green-400 font-mono border border-slate-600 focus:border-blue-500 focus:outline-none mb-6">
1/2-inch Red PEX-A Tubing (ft), 150, 0.75
1/2-inch Blue PEX-A Tubing (ft), 150, 0.75
Brass Multi-port Manifold, 1, 185.00
1/2-inch F1960 Expansion Rings, 24, 0.45</textarea>

            <button type="submit" class="w-full bg-blue-600 hover:bg-blue-500 transition-colors text-white font-extrabold text-xl py-4 rounded-lg shadow-lg">
                FORGE INVOICE PDF 📄🚀
            </button>
        </form>
        
        <div class="mt-8 text-center text-slate-500 text-sm font-mono">
            Powered by Antigravity, Vercel Edge, and Master Builder Tech.
        </div>
    </div>
</body>
</html>
"""

@app.route('/')
def index():
    return render_template_string(HTML_TEMPLATE)

@app.route('/generate-invoice', methods=['POST'])
def generate():
    # 1. Grab form data
    client_name = request.form.get('client_name', 'Client')
    job_address = request.form.get('job_address', 'Address')
    try:
        labor_hours = float(request.form.get('labor_hours', 0))
        labor_rate = float(request.form.get('labor_rate', 0))
    except ValueError:
        labor_hours, labor_rate = 0, 0

    # 2. Parse Materials from the Text Area
    raw_materials = request.form.get('materials', '')
    materials_takeoff = []
    for line in raw_materials.split('\n'):
        if line.strip():
            parts = line.split(',')
            if len(parts) >= 3:
                desc = parts[0].strip()
                try:
                    qty = float(parts[1].strip())
                    price = float(parts[2].strip())
                    materials_takeoff.append((desc, qty, price))
                except ValueError:
                    continue

    # 3. Build PDF in Memory (RAM)
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=letter)
    elements = []
    styles = getSampleStyleSheet()

    elements.append(Paragraph("<font size=24><b>GREG'S SIDEKICK PLUMBING</b></font>", styles['Title']))
    elements.append(Paragraph("<font size=12><i>Expert PEX, CAD Design & Plumbing Solutions</i></font>", styles['Normal']))
    elements.append(Spacer(1, 20))

    elements.append(Paragraph(f"<b>Date:</b> {date.today().strftime('%B %d, %Y')} | <b>Invoice #:</b> GS-{date.today().strftime('%Y%m%d')}", styles['Normal']))
    elements.append(Paragraph(f"<b>Client:</b> {client_name}", styles['Normal']))
    elements.append(Paragraph(f"<b>Job Site:</b> {job_address}", styles['Normal']))
    elements.append(Spacer(1, 20))

    data = [["Description (CAD Takeoff)", "Qty", "Unit Price", "Total"]]
    subtotal = 0

    for item in materials_takeoff:
        desc, qty, price = item
        total = qty * price
        subtotal += total
        data.append([desc, str(qty), f"${price:.2f}", f"${total:.2f}"])

    labor_total = labor_hours * labor_rate
    subtotal += labor_total
    data.append(["Master Plumber Labor & Install", str(labor_hours), f"${labor_rate:.2f}", f"${labor_total:.2f}"])

    tax_rate = 0.06625 # New Jersey State Tax
    tax = subtotal * tax_rate
    grand_total = subtotal + tax

    data.append(["", "", "Subtotal:", f"${subtotal:.2f}"])
    data.append(["", "", "Tax (6.625%):", f"${tax:.2f}"])
    data.append(["", "", "GRAND TOTAL:", f"${grand_total:.2f}"])

    t = Table(data, colWidths=[250, 50, 80, 80])
    t.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), colors.HexColor("#003366")),
        ('TEXTCOLOR', (0,0), (-1,0), colors.whitesmoke),
        ('ALIGN', (0,0), (-1,-1), 'CENTER'),
        ('FONTNAME', (0,0), (-1,0), 'Helvetica-Bold'),
        ('BOTTOMPADDING', (0,0), (-1,0), 12),
        ('BACKGROUND', (0,1), (-1,-4), colors.HexColor("#f4f4f4")),
        ('GRID', (0,0), (-1,-1), 1, colors.black),
        ('FONTNAME', (2,-3), (3,-1), 'Helvetica-Bold'),
        ('TEXTCOLOR', (3,-1), (3,-1), colors.darkgreen),
    ]))

    elements.append(t)
    elements.append(Spacer(1, 40))
    elements.append(Paragraph("<b>Thank you for choosing Greg's Sidekick Plumbing!</b>", styles['Normal']))

    # Finalize PDF & ready the buffer
    doc.build(elements)
    buffer.seek(0)
    
    # 4. Blast the PDF back to the user's browser!
    filename = f"Invoice_{client_name.replace(' ', '_')}.pdf"
    return send_file(buffer, as_attachment=True, download_name=filename, mimetype='application/pdf')

# ========================================================
# RUNNING LOCALLY ON PORT 1100
# ========================================================
if __name__ == '__main__':
    # When you run this file on your computer, it hits port 1100.
    # When Vercel runs it in the cloud, it ignores this and uses serverless routing!
    print("🛠️ MASTER BUILDER INITIATED: GREG'S SIDEKICK IS LIVE ON PORT 1100!")
    app.run(host='0.0.0.0', port=1100, debug=True)
