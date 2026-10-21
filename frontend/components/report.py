from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_CENTER
from reportlab.lib.units import mm
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, Image
from reportlab.lib.utils import ImageReader
import io

def build_report_pdf(data: dict) -> bytes:
    buf=io.BytesIO()
    doc=SimpleDocTemplate(buf,pagesize=A4,rightMargin=16*mm,leftMargin=16*mm,topMargin=14*mm,bottomMargin=14*mm)
    styles=getSampleStyleSheet()
    styles.add(ParagraphStyle(name="TitleRS",parent=styles["Title"],fontName="Helvetica-Bold",fontSize=21,leading=24,textColor=colors.HexColor("#17182A"),alignment=TA_CENTER,spaceAfter=5))
    styles.add(ParagraphStyle(name="SubRS",parent=styles["Normal"],fontSize=9,textColor=colors.HexColor("#687083"),alignment=TA_CENTER,spaceAfter=14))
    styles.add(ParagraphStyle(name="HRS",parent=styles["Heading2"],fontName="Helvetica-Bold",fontSize=11,textColor=colors.HexColor("#5865F2"),spaceBefore=8,spaceAfter=6))
    styles.add(ParagraphStyle(name="BodyRS",parent=styles["Normal"],fontSize=8.8,leading=13,textColor=colors.HexColor("#424756")))
    story=[Paragraph("RETINASCAN AI",styles["TitleRS"]),Paragraph("AI-Assisted Retinal Disease Screening Report",styles["SubRS"])]
    p=data.get("result",{}); pred=p.get("prediction","N/A"); conf=float(p.get("confidence",0)); name=data.get("patient_name","—")
    story += [Paragraph("PATIENT & SCREENING DETAILS",styles["HRS"])]
    details=[["Patient name",name,"Age",str(data.get("patient_age","—"))],["Phone",data.get("patient_phone") or "—","Gender",data.get("patient_gender","—")],["Doctor",data.get("doctor_name") or "—","Date",str(data.get("created_at",""))[:19].replace("T"," ")]]
    t=Table(details,colWidths=[27*mm,65*mm,25*mm,60*mm]); t.setStyle(TableStyle([("BACKGROUND",(0,0),(0,-1),colors.HexColor("#F1F2FF")),("BACKGROUND",(2,0),(2,-1),colors.HexColor("#F1F2FF")),("BOX",(0,0),(-1,-1),.5,colors.HexColor("#DDE0FF")),("INNERGRID",(0,0),(-1,-1),.3,colors.HexColor("#E6E7EF")),("FONTNAME",(0,0),(-1,-1),"Helvetica"),("FONTSIZE",(0,0),(-1,-1),8),("VALIGN",(0,0),(-1,-1),"MIDDLE"),("TOPPADDING",(0,0),(-1,-1),7),("BOTTOMPADDING",(0,0),(-1,-1),7)])); story += [t,Spacer(1,7)]
    story += [Paragraph("AI PREDICTION",styles["HRS"])]
    pred_table=Table([["Predicted class",pred],["Confidence",f"{conf:.1f}%"],["Model","Fine-tuned ResNet50"]],colWidths=[45*mm,132*mm]); pred_table.setStyle(TableStyle([("BACKGROUND",(0,0),(0,-1),colors.HexColor("#17182A")),("TEXTCOLOR",(0,0),(0,-1),colors.white),("FONTNAME",(0,0),(0,-1),"Helvetica-Bold"),("BOX",(0,0),(-1,-1),.6,colors.HexColor("#DDE0FF")),("INNERGRID",(0,0),(-1,-1),.3,colors.HexColor("#E6E7EF")),("FONTSIZE",(0,0),(-1,-1),9),("TOPPADDING",(0,0),(-1,-1),8),("BOTTOMPADDING",(0,0),(-1,-1),8)])); story += [pred_table,Spacer(1,8)]
    if data.get("image_bytes"):
        try:
            img=Image(io.BytesIO(data["image_bytes"]),width=48*mm,height=42*mm)
            story += [Paragraph("UPLOADED FUNDUS IMAGE",styles["HRS"]),img,Spacer(1,7)]
        except Exception: pass
    title={"AMD":"Age-related Macular Degeneration","DR":"Diabetic Retinopathy","DN":"Diabetic Neuropathy","MH":"Macular Hole","ODC":"Optic Disc Cupping","Normal":"Normal Retina"}.get(pred,pred)
    desc={"AMD":"Macular changes that can affect central vision.","DR":"Diabetes-related damage involving retinal blood vessels.","DN":"Subtle diabetes-related retinal changes requiring careful review.","MH":"A structural opening or thinning in the macular region.","ODC":"Enlargement of the optic cup, often associated with glaucoma.","Normal":"The model classified the submitted image as Normal."}.get(pred,"Model prediction returned by the screening service.")
    story += [Paragraph("SCREENING INTERPRETATION",styles["HRS"]),Paragraph(f"<b>{title} ({pred})</b><br/>{desc}",styles["BodyRS"]),Spacer(1,7)]
    if data.get("result",{}).get("probabilities"):
        rows=[["Class","Probability"]]+[[str(k),f"{float(v):.2f}%"] for k,v in data["result"]["probabilities"].items()]
        tt=Table(rows,colWidths=[80*mm,97*mm]); tt.setStyle(TableStyle([("BACKGROUND",(0,0),(-1,0),colors.HexColor("#5865F2")),("TEXTCOLOR",(0,0),(-1,0),colors.white),("FONTNAME",(0,0),(-1,0),"Helvetica-Bold"),("GRID",(0,0),(-1,-1),.3,colors.HexColor("#DDE0FF")),("FONTSIZE",(0,0),(-1,-1),8),("TOPPADDING",(0,0),(-1,-1),5),("BOTTOMPADDING",(0,0),(-1,-1),5)])); story += [Paragraph("CLASS PROBABILITIES",styles["HRS"]),tt,Spacer(1,8)]
    if data.get("result",{}).get("record",{}).get("notes") or data.get("notes"):
        story += [Paragraph("CLINICAL NOTES",styles["HRS"]),Paragraph(data.get("notes") or data.get("result",{}).get("record",{}).get("notes",""),styles["BodyRS"])]
    story += [Spacer(1,12),Paragraph("This AI-assisted report is intended for screening support and academic demonstration. It is not a standalone medical diagnosis. Findings should be reviewed and confirmed by a qualified ophthalmologist.",ParagraphStyle(name="Disc",parent=styles["BodyRS"],fontSize=7.8,leading=11,textColor=colors.HexColor("#735B16")))]
    doc.build(story)
    return buf.getvalue()
