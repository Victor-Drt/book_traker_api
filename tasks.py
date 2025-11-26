# tasks.py
import logging
from celery import shared_task
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
from django.core.mail import EmailMessage
from django.contrib.auth.models import User
from django.db.models import Sum
from django.db.models.functions import TruncMonth
from django.conf import settings
from io import BytesIO

from books.models import Books, Progress

logger = logging.getLogger(__name__)


@shared_task
def generate_user_report(user_id):
    """
    Gera um relatório PDF com o histórico de leitura do usuário
    e envia por email.
    """
    try:
        user = User.objects.get(id=user_id)
    except User.DoesNotExist:
        logger.error(f"Usuário com ID {user_id} não encontrado")
        return
    
    if not user.email:
        logger.error(f"Usuário {user.username} não possui email cadastrado")
        return

    # Buscar livros concluídos
    finished_books = Books.objects.filter(owner=user, is_finished=True).order_by('-updated_at')
    
    # Buscar progressos para calcular páginas por mês e tempo total
    progresses = Progress.objects.filter(book__owner=user).order_by('date')
    
    # Calcular páginas lidas por mês
    monthly_data = (
        progresses.annotate(month=TruncMonth("date"))
        .values("month")
        .annotate(total_pages=Sum("pages_read"))
        .order_by("month")
    )
    
    pages_by_month = {
        entry["month"].strftime("%Y-%m"): entry["total_pages"]
        for entry in monthly_data
    }
    
    # Calcular tempo total de leitura
    # Estimativa: assumindo 1 página por minuto (ajustável)
    total_pages_read = progresses.aggregate(total=Sum("pages_read"))["total"] or 0
    estimated_minutes = total_pages_read  # 1 página = 1 minuto
    total_hours = estimated_minutes / 60
    total_days = total_hours / 24
    
    # Calcular período de leitura (primeira a última data)
    if progresses.exists():
        first_date = progresses.first().date
        last_date = progresses.last().date
        reading_period = (last_date - first_date).days
    else:
        reading_period = 0
    
    # Gerar PDF
    buffer = BytesIO()
    c = canvas.Canvas(buffer, pagesize=letter)
    width, height = letter
    
    # Configurações de fonte e posição
    y_position = height - 50
    line_height = 20
    
    # Título
    c.setFont("Helvetica-Bold", 16)
    c.drawString(50, y_position, "Relatório de Leitura")
    y_position -= 30
    
    # Informações do usuário
    c.setFont("Helvetica", 12)
    c.drawString(50, y_position, f"Usuário: {user.get_full_name() or user.username}")
    y_position -= line_height
    c.drawString(50, y_position, f"Email: {user.email}")
    y_position -= 30
    
    # Livros concluídos
    c.setFont("Helvetica-Bold", 14)
    c.drawString(50, y_position, "Livros Concluídos")
    y_position -= line_height
    
    c.setFont("Helvetica", 10)
    if finished_books.exists():
        for book in finished_books:
            if y_position < 100:  # Nova página se necessário
                c.showPage()
                y_position = height - 50
            
            c.drawString(70, y_position, f"• {book.title} - {book.author}")
            y_position -= line_height
            c.drawString(90, y_position, f"  Categoria: {book.category} | Páginas: {book.total_pages}")
            y_position -= line_height
    else:
        c.drawString(70, y_position, "Nenhum livro concluído ainda.")
        y_position -= line_height
    
    y_position -= 20
    
    # Páginas lidas por mês
    if y_position < 150:
        c.showPage()
        y_position = height - 50
    
    c.setFont("Helvetica-Bold", 14)
    c.drawString(50, y_position, "Páginas Lidas por Mês")
    y_position -= line_height
    
    c.setFont("Helvetica", 10)
    if pages_by_month:
        for month, pages in sorted(pages_by_month.items()):
            if y_position < 100:
                c.showPage()
                y_position = height - 50
            
            # Formatar mês: YYYY-MM -> Mês/YYYY
            year, month_num = month.split('-')
            month_names = {
                '01': 'Janeiro', '02': 'Fevereiro', '03': 'Março', '04': 'Abril',
                '05': 'Maio', '06': 'Junho', '07': 'Julho', '08': 'Agosto',
                '09': 'Setembro', '10': 'Outubro', '11': 'Novembro', '12': 'Dezembro'
            }
            month_formatted = f"{month_names.get(month_num, month_num)}/{year}"
            c.drawString(70, y_position, f"{month_formatted}: {pages} páginas")
            y_position -= line_height
    else:
        c.drawString(70, y_position, "Nenhum registro de leitura encontrado.")
        y_position -= line_height
    
    y_position -= 20
    
    # Tempo total de leitura
    if y_position < 150:
        c.showPage()
        y_position = height - 50
    
    c.setFont("Helvetica-Bold", 14)
    c.drawString(50, y_position, "Estatísticas de Leitura")
    y_position -= line_height
    
    c.setFont("Helvetica", 10)
    c.drawString(70, y_position, f"Total de páginas lidas: {total_pages_read}")
    y_position -= line_height
    c.drawString(70, y_position, f"Tempo estimado de leitura: {int(total_hours)} horas ({total_days:.1f} dias)")
    y_position -= line_height
    
    if reading_period > 0:
        c.drawString(70, y_position, f"Período de leitura: {reading_period} dias")
        y_position -= line_height
        avg_pages_per_day = total_pages_read / reading_period if reading_period > 0 else 0
        c.drawString(70, y_position, f"Média de páginas por dia: {avg_pages_per_day:.1f}")
    
    c.save()
    
    pdf = buffer.getvalue()
    buffer.close()
    
    # Enviar email
    try:
        email = EmailMessage(
            "Seu Relatório de Leitura",
            f"Olá {user.get_full_name() or user.username},\n\n"
            "Segue em anexo o seu relatório completo de leitura com:\n"
            "- Livros concluídos\n"
            "- Páginas lidas por mês\n"
            "- Tempo total de leitura\n\n"
            "Continue lendo!",
            from_email=settings.DEFAULT_FROM_EMAIL,
            to=[user.email],
        )
        email.attach("relatorio_leitura.pdf", pdf, "application/pdf")
        email.send()
        logger.info(f"Relatório enviado com sucesso para {user.email}")
    except Exception as e:
        logger.error(f"Erro ao enviar email para {user.email}: {str(e)}")
        raise
