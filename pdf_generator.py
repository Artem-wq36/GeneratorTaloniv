
import json
import os
from pathlib import Path

import qrcode

from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import mm
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.platypus import (
    SimpleDocTemplate,
    Paragraph,
    Spacer,
    Table,
    TableStyle,
    Image
)


def register_fonts():
    if "AppFont" in pdfmetrics.getRegisteredFontNames():
        return

    windows_fonts = Path(os.environ.get("WINDIR", "C:/Windows")) / "Fonts"

    candidates = [
        (
            windows_fonts / "arial.ttf",
            windows_fonts / "arialbd.ttf"
        ),
        (
            windows_fonts / "calibri.ttf",
            windows_fonts / "calibrib.ttf"
        ),
        (
            Path("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"),
            Path("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf")
        )
    ]

    for regular, bold in candidates:
        if regular.exists():
            pdfmetrics.registerFont(
                TTFont("AppFont", str(regular))
            )

            if bold.exists():
                pdfmetrics.registerFont(
                    TTFont("AppFont-Bold", str(bold))
                )
            else:
                pdfmetrics.registerFont(
                    TTFont("AppFont-Bold", str(regular))
                )

            return

    raise RuntimeError(
        "Не вдалося знайти шрифт Arial або DejaVuSans. "
        "Встановіть відповідний шрифт для підтримки української мови."
    )


def generate_pdf(data, settings, number, output_path, qr_path):
    register_fonts()

    output_path = Path(output_path)
    qr_path = Path(qr_path)

    output_path.parent.mkdir(parents=True, exist_ok=True)
    qr_path.parent.mkdir(parents=True, exist_ok=True)

    qr_data = {
        "ticket_number": number,
        "vehicle": data["vehicle"],
        "driver": data["driver"],
        "manager": data["manager"],
        "loading_date": data["loading_date"],
        "loading_time": data["loading_time"],
        "location": settings["location"]
    }

    qr_image = qrcode.make(
        json.dumps(qr_data, ensure_ascii=False)
    )

    qr_image.save(qr_path)

    document = SimpleDocTemplate(
        str(output_path),
        pagesize=A4,
        rightMargin=20 * mm,
        leftMargin=20 * mm,
        topMargin=18 * mm,
        bottomMargin=18 * mm
    )

    styles = getSampleStyleSheet()

    title_style = ParagraphStyle(
        "TicketTitle",
        parent=styles["Title"],
        fontName="AppFont-Bold",
        fontSize=19,
        leading=24,
        alignment=TA_CENTER,
        textColor=colors.HexColor("#1B4965"),
        spaceAfter=8 * mm
    )

    normal_style = ParagraphStyle(
        "TicketNormal",
        parent=styles["Normal"],
        fontName="AppFont",
        fontSize=10,
        leading=15
    )

    header_style = ParagraphStyle(
        "TableHeader",
        parent=normal_style,
        fontName="AppFont-Bold",
        textColor=colors.white,
        alignment=TA_CENTER
    )

    story = []

    company_name = settings["company_name"]
    company_address = settings["company_address"]

    story.append(
        Paragraph(
            f"<b>{company_name}</b>",
            title_style
        )
    )

    story.append(
        Paragraph(
            company_address,
            normal_style
        )
    )

    story.append(Spacer(1, 8 * mm))

    story.append(
        Paragraph(
            f"Електронний талон на завантаження №{number:08d}",
            title_style
        )
    )

    story.append(Spacer(1, 3 * mm))

    creation_time = data["creation_time"]

    rows = [
        [
            Paragraph("Параметр", header_style),
            Paragraph("Інформація", header_style)
        ],
        ["Дата завантаження", data["loading_date"]],
        ["Час завантаження", data["loading_time"]],
        ["Номер транспортного засобу", data["vehicle"]],
        ["Ім'я водія", data["driver"]],
        ["Контакт менеджера", data["manager"]],
        ["Місце завантаження", settings["location"]],
        ["Дата створення талона", creation_time]
    ]

    table = Table(
        rows,
        colWidths=[65 * mm, 105 * mm],
        repeatRows=1
    )

    table.setStyle(
        TableStyle([
            (
                "BACKGROUND",
                (0, 0),
                (-1, 0),
                colors.HexColor("#1B4965")
            ),
            (
                "TEXTCOLOR",
                (0, 0),
                (-1, 0),
                colors.white
            ),
            (
                "FONTNAME",
                (0, 0),
                (-1, -1),
                "AppFont"
            ),
            (
                "FONTNAME",
                (0, 0),
                (-1, 0),
                "AppFont-Bold"
            ),
            # Перші два параметри виділені жирним шрифтом.
            (
                "FONTNAME",
                (0, 1),
                (-1, 2),
                "AppFont-Bold"
            ),
            (
                "FONTSIZE",
                (0, 0),
                (-1, -1),
                9
            ),
            (
                "GRID",
                (0, 0),
                (-1, -1),
                0.5,
                colors.HexColor("#AAB7C4")
            ),
            (
                "BACKGROUND",
                (0, 1),
                (-1, -1),
                colors.HexColor("#F4F7FA")
            ),
            (
                "VALIGN",
                (0, 0),
                (-1, -1),
                "MIDDLE"
            ),
            (
                "LEFTPADDING",
                (0, 0),
                (-1, -1),
                8
            ),
            (
                "RIGHTPADDING",
                (0, 0),
                (-1, -1),
                8
            ),
            (
                "TOPPADDING",
                (0, 0),
                (-1, -1),
                8
            ),
            (
                "BOTTOMPADDING",
                (0, 0),
                (-1, -1),
                8
            )
        ])
    )

    story.append(table)
    story.append(Spacer(1, 10 * mm))

    story.append(
        Paragraph(
            settings["footer_text"],
            normal_style
        )
    )

    story.append(Spacer(1, 5 * mm))

    story.append(
        Paragraph(
            "QR-код містить інформацію про цей талон.",
            normal_style
        )
    )

    story.append(Spacer(1, 3 * mm))

    qr = Image(
        str(qr_path),
        width=35 * mm,
        height=35 * mm
    )

    story.append(qr)

    document.build(story)