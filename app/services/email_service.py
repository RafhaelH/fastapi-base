"""Serviços para envio de emails."""
import logging
from datetime import datetime
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from pathlib import Path
from typing import Optional

import aiosmtplib
from jinja2 import Environment, FileSystemLoader

from app.core.config import settings

logger = logging.getLogger(__name__)

class EmailService:
    """Serviço para envio de emails via SMTP."""

    def __init__(self):
        """Inicializa o serviço de email com templates."""
        template_dir = Path(__file__).parent.parent / "templates" / "email"
        self.jinja_env = Environment(
            loader=FileSystemLoader(str(template_dir)),
            autoescape=True
        )

    async def send_email(
        self,
        to_email: str,
        subject: str,
        html_content: str,
        text_content: Optional[str] = None
    ) -> bool:
        """Envia um email via SMTP.

        Args:
            to_email: Email do destinatário
            subject: Assunto do email
            html_content: Conteúdo HTML
            text_content: Conteúdo em texto plano (opcional)

        Returns:
            True se enviado com sucesso, False caso contrário
        """
        if not all([settings.SMTP_USERNAME, settings.SMTP_PASSWORD, settings.EMAIL_FROM]):
            logger.error("Configurações de email não encontradas")
            return False

        try:
            # Criar mensagem
            message = MIMEMultipart("alternative")
            message["Subject"] = subject
            message["From"] = f"{settings.EMAIL_FROM_NAME} <{settings.EMAIL_FROM}>"
            message["To"] = to_email

            # Adicionar conteúdo em texto plano se fornecido
            if text_content:
                text_part = MIMEText(text_content, "plain", "utf-8")
                message.attach(text_part)

            # Adicionar conteúdo HTML
            html_part = MIMEText(html_content, "html", "utf-8")
            message.attach(html_part)

            # Enviar email
            await aiosmtplib.send(
                message,
                hostname=settings.SMTP_SERVER,
                port=settings.SMTP_PORT,
                start_tls=True,
                username=settings.SMTP_USERNAME,
                password=settings.SMTP_PASSWORD,
            )

            logger.info(f"Email enviado com sucesso para {to_email}")
            return True

        except Exception as e:
            logger.error(f"Erro ao enviar email para {to_email}: {str(e)}")
            # Não propagar exceção para evitar que a aplicação pare
            return False

    async def send_password_reset_email(
        self,
        to_email: str,
        reset_token: str,
        user_name: Optional[str] = None
    ) -> bool:
        """Envia email de reset de senha.

        Args:
            to_email: Email do usuário
            reset_token: Token de reset
            user_name: Nome do usuário (opcional)

        Returns:
            True se enviado com sucesso, False caso contrário
        """
        try:
            # URL de reset (ajustar conforme seu frontend)
            reset_url = f"{settings.FRONTEND_URL}/reset-password?token={reset_token}"

            # Renderizar template
            template = self.jinja_env.get_template("password_reset.html")
            html_content = template.render(
                app_name=settings.PROJECT_NAME,
                user_name=user_name,
                reset_url=reset_url,
                current_year=datetime.now().year
            )

            # Conteúdo em texto plano como fallback
            text_content = f"""
{settings.PROJECT_NAME} - Redefinição de Senha

Olá{f', {user_name}' if user_name else ''}!

Recebemos uma solicitação para redefinir a senha da sua conta.

Para redefinir sua senha, acesse o link abaixo:
{reset_url}

IMPORTANTE:
- Este link expira em 1 hora
- Só pode ser usado uma vez
- Se você não solicitou esta redefinição, ignore este email

Este email foi enviado automaticamente, não responda.

© {datetime.now().year} {settings.PROJECT_NAME}. Todos os direitos reservados.
            """.strip()

            # Enviar email
            return await self.send_email(
                to_email=to_email,
                subject=f"{settings.PROJECT_NAME} - Redefinir Senha",
                html_content=html_content,
                text_content=text_content
            )

        except Exception as e:
            logger.error(f"Erro ao enviar email de reset para {to_email}: {str(e)}")
            # Não propagar exceção para evitar que a aplicação pare
            return False

# Instância singleton
email_service = EmailService()
