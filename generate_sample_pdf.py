from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas

def generate_sample(path="sample.pdf"):
    c = canvas.Canvas(path, pagesize=letter)
    width, height = letter

    c.setFont("Helvetica-Bold", 14)
    c.drawString(50, height - 50, "Account Statement")
    c.setFont("Helvetica", 11)
    c.drawString(50, height - 80, "Account No: 1234-5678-9012")
    c.drawString(50, height - 100, "Period: Jan–Dec 2024")
    c.drawString(50, height - 120, "Average Balance: $52,300.75")
    c.drawString(50, height - 140, "Status: Verified")
    c.drawString(50, height - 180, "Sample transactions:")
    y = height - 200
    for i in range(1, 6):
        c.drawString(60, y, f"2024-0{i}-15 | Description {i} | $ {100 * i:.2f}")
        y -= 15
    c.save()

if __name__ == "__main__":
    generate_sample("sample.pdf")
    print("sample.pdf generated.")