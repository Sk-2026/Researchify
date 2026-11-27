
import smtplib
from email.message import EmailMessage

from app.core.config import settings


class EmailNotificationService:

    @staticmethod
    def send_paper_alert(
        recipient_email: str,
        recipient_name: str,
        papers: list[dict],
    ) -> bool:
        """
        Send an email containing newly discovered relevant papers.
        """

        if not papers:
            return False

        sender_email = (
            settings.SMTP_FROM_EMAIL or settings.SMTP_USERNAME
        )

        if not sender_email or not settings.SMTP_USERNAME or not settings.SMTP_PASSWORD:
            raise ValueError(
                "SMTP credentials are not configured in the backend .env file."
            )

        message = EmailMessage()
        message["Subject"] = (
            f"ZealWithin: {len(papers)} new research paper(s) found"
        )
        message["From"] = sender_email
        message["To"] = recipient_email

        body = [
            f"Hello {recipient_name},",
            "",
            "ZealWithin has discovered new research papers matching your interests.",
            "",
        ]

        for index, paper in enumerate(papers, start=1):
            body.extend([
                f"{index}. {paper['title']}",
                f"Relevance score: {paper['relevance_score']:.1%}",
            ])

            if paper.get("doi"):
                body.append(
                    f"DOI: https://doi.org/{paper['doi']}"
                )

            if paper.get("abstract"):
                abstract = paper["abstract"]
                body.append(
                    f"Abstract: {abstract[:500]}"
                    + ("..." if len(abstract) > 500 else "")
                )

            body.append("")

        body.extend([
            "Keep the researcher in you alive.",
            "",
            "Team ZealWithin",
        ])

        message.set_content("\n".join(body))

        with smtplib.SMTP(
            settings.SMTP_HOST,
            settings.SMTP_PORT,
            timeout=settings.SMTP_TIMEOUT,
        ) as server:

            if settings.SMTP_USE_TLS:
                server.starttls()

            server.login(
                settings.SMTP_USERNAME,
                settings.SMTP_PASSWORD,
            )

            server.send_message(message)

        return True
