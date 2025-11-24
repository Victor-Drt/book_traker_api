# tasks.py
from celery import shared_task
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
from django.core.files.base import ContentFile
from django.core.mail import EmailMessage
from io import BytesIO

@shared_task
def generate_user_report(user_email):
    buffer = BytesIO()
    c = canvas.Canvas(buffer, pagesize=letter)
    c.drawString(100, 750, "Relatório de Leitura do Usuário")
    c.drawString(100, 730, f"Email: {user_email}")
    c.save()

    pdf = buffer.getvalue()
    buffer.close()

    email = EmailMessage(
        "Seu Relatório de Leitura",
        "Segue o PDF do seu histórico de leitura.",
        to=[user_email],
    )
    email.attach("relatorio.pdf", pdf, "application/pdf")
    email.send()
