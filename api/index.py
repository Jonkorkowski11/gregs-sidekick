import antigravity  # 🚀 UP, UP, AND AWAY!
import io
import base64
from flask import Flask, request, send_file, render_template_string
from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, Image, PageBreak
from reportlab.lib.styles import getSampleStyleSheet
from datetime import date

app = Flask(__name__)

# --- THE FRONTEND UI (TAILWIND CSS + FABRIC.JS) ---
HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Greg's Sidekick - Master Builder</title>
    <script src="https://cdn.tailwindcss.com"></script>
    <script src="https://cdnjs.cloudflare.com/ajax/libs/fabric.js/5.3.1/fabric.min.js"></script>
</head>
<body class="bg-slate-900 text-white min-h-screen p-4 md:p-10 font-sans">
    <div class="max-w-4xl mx-auto">
        <h1 class="text-4xl md:text-5xl font-extrabold text-blue-500 mb-2 flex items-center gap-3">
            🛠️ GREG'S SIDEKICK
        </h1>
        <p class="text-slate-400 mb-8 text-lg border-b border-slate-700 pb-4">PlumbingCAD Takeoff & Blueprint Engine</p>

        <form id="invoiceForm" action="/generate-invoice" method="POST" class="bg-slate-800 p-6 md:p-8 rounded-xl shadow-2xl border border-slate-700">
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
            <textarea name="materials" rows="4" class="w-full p-4 rounded bg-slate-900 text-green-400 font-mono border border-slate-600 focus:border-blue-500 focus:outline-none mb-6">
1/2-inch Red PEX-A Tubing (ft), 150, 0.75
1/2-inch Blue PEX-A Tubing (ft), 150, 0.75
Brass Multi-port Manifold, 1, 185.00
1/2-inch F1960 Expansion Rings, 24, 0.45</textarea>

            <h2 class="text-2xl font-bold text-blue-400 mb-2">Job Site Blueprint Designer</h2>
            <p class="text-sm text-slate-400 mb-4">Drag symbols or draw your piping layout below.</p>
            
            <div class="flex flex-wrap gap-2 mb-4 bg-slate-700 p-3 rounded-lg">
                <button type="button" onclick="addText()" class="bg-slate-600 px-3 py-1 rounded hover:bg-slate-500 text-sm font-bold">Label</button>
                <button type="button" onclick="addWaterHeater()" class="bg-blue-600 px-3 py-1 rounded hover:bg-blue-500 text-sm font-bold">W.H.</button>
                <button type="button" onclick="addValve()" class="bg-green-600 px-3 py-1 rounded hover:bg-green-500 text-sm font-bold">Valve</button>
                <button type="button" onclick="toggleDraw()" id="drawBtn" class="bg-yellow-600 px-3 py-1 rounded hover:bg-yellow-500 text-sm font-bold">Draw Pipe: OFF</button>
                <button type="button" onclick="clearCanvas()" class="bg-red-600 px-3 py-1 rounded hover:bg-red-500 text-sm font-bold">Clear</button>
            </div>

            <div class="bg-white rounded overflow-hidden mb-6">
                <canvas id="blueprintCanvas" width="800" height="400"></canvas>
            </div>
            
            <input type="hidden" name="blueprint_image" id="blueprintImage">

            <button type="submit" class="w-full bg-blue-600 hover:bg-blue-500 transition-colors text-white font-extrabold text-xl py-4 rounded-lg shadow-lg">
                FORGE INVOICE PDF 📄🚀
            </button>
        </form>
        
        <div class="mt-8 text-center text-slate-500 text-sm font-mono">
            Powered by Antigravity, Fabric.js, and Vercel Edge.
        </div>
    </div>

    <script>
        const canvas = new fabric.Canvas('blueprintCanvas');
        canvas.setBackgroundColor('#f8fafc', canvas.renderAll.bind(canvas));

        function addText() {
            const text = new fabric.IText('New Label', { left: 100, top: 100, fontSize: 20, fill: '#333' });
            canvas.add(text);
        }

        function addWaterHeater() {
            const rect = new fabric.Rect({ width: 60, height: 100, fill: '#3b82f6', stroke: '#1d4ed8', strokeWidth: 2 });
            const label = new fabric.Text('W.H.', { fontSize: 16, top: 40, left: 10, fill: 'white' });
            const group = new fabric.Group([rect, label], { left: 150, top: 150 });
            canvas.add(group);
        }

        function addValve() {
            const circle = new fabric.Circle({ radius: 15, fill: '#22c55e', stroke: '#15803d', strokeWidth: 2 });
            const line = new fabric.Rect({ width: 40, height: 4, fill: '#333', top: 13, left: -5 });
            const group = new fabric.Group([circle, line], { left: 200, top: 200 });
            canvas.add(group);
        }

        function toggleDraw() {
            canvas.isDrawingMode = !canvas.isDrawingMode;
            const btn = document.getElementById('drawBtn');
            if (canvas.isDrawingMode) {
                btn.textContent = 'Draw Pipe: ON';
                btn.classList.replace('bg-yellow-600', 'bg-orange-500');
                canvas.freeDrawingBrush.width = 5;
                canvas.freeDrawingBrush.color = '#333';
            } else {
                btn.textContent = 'Draw Pipe: OFF';
                btn.classList.replace('bg-orange-500', 'bg-yellow-600');
            }
        }

        function clearCanvas() {
            if (confirm('Clear the entire blueprint?')) {
                canvas.clear();
                canvas.setBackgroundColor('#f8fafc', canvas.renderAll.bind(canvas));
            }
        }

        document.getElementById('invoiceForm').onsubmit = function() {
            document.getElementById('blueprintImage').value = canvas.toDataURL({
                format: 'png',
                multiplier: 2 // High res for PDF
            });
        };
    </script>
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

    # 2. Parse Materials
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

    # 3. Build PDF in Memory
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=letter)
    elements = []
    styles = getSampleStyleSheet()

    # --- PAGE 1: INVOICE ---
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

    tax_rate = 0.06625 
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

    # --- PAGE 2: BLUEPRINT (IF EXISTS) ---
    blueprint_data = request.form.get('blueprint_image')
    if blueprint_data and "," in blueprint_data:
        elements.append(PageBreak())
        elements.append(Paragraph("<font size=20><b>JOB SITE BLUEPRINT</b></font>", styles['Title']))
        elements.append(Spacer(1, 20))
        
        # Decode base64 image
        header, encoded = blueprint_data.split(",", 1)
        image_bytes = base64.b64decode(encoded)
        image_buffer = io.BytesIO(image_bytes)
        
        img = Image(image_buffer)
        # Scale image to fit width of page
        img._restrictSize(480, 600) 
        elements.append(img)

    doc.build(elements)
    buffer.seek(0)
    
    filename = f"Invoice_{client_name.replace(' ', '_')}.pdf"
    return send_file(buffer, as_attachment=True, download_name=filename, mimetype='application/pdf')

if __name__ == '__main__':
    print("🛠️ MASTER BUILDER INITIATED: GREG'S SIDEKICK IS LIVE ON PORT 1100!")
    app.run(host='0.0.0.0', port=1100, debug=True)
