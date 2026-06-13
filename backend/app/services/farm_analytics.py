import logging
import json
import io
from datetime import date, datetime
from typing import List, Dict, Any, Optional
from sqlalchemy.orm import Session
from sqlalchemy import func

from app.models.farmer import Farmer
from app.models.soil import SoilReport
from app.models.disease import DiseaseScan
from app.models.farm_planner import FarmPlan, FarmTask
from app.models.risk_alert import RiskAlert
from app.models.notification import Notification
from app.models.yield_prediction import YieldPrediction
from app.models.market_intelligence import ProfitabilityAnalysis
from app.models.consult_agent import ConsultationHistory
from app.models.farm_analytics import FarmAnalyticsSnapshot

from app.repositories.farm_analytics import farm_analytics_repo
from app.repositories.soil import soil_report_repo
from app.repositories.disease import disease_scan_repo
from app.repositories.farm_planner import farm_plan_repo, farm_task_repo
from app.repositories.risk_intelligence import risk_alert_repo
from app.repositories.notification import notification_repo
from app.repositories.yield_prediction import yield_prediction_repo
from app.repositories.consult_agent import consultation_history_repo

# ReportLab imports
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, PageBreak
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib import colors

logger = logging.getLogger("agriassist.analytics_service")


class FarmAnalyticsService:
    def calculate_realtime_kpis(self, db: Session, farmer_id: int, farm_id: Optional[int] = None) -> Dict[str, Any]:
        # 1. Health Score calculation (Base 75)
        health_score = 75.0
        latest_consult = db.query(ConsultationHistory).filter(
            ConsultationHistory.farmer_id == farmer_id
        ).order_by(ConsultationHistory.created_at.desc()).first()

        if latest_consult:
            try:
                snap = json.loads(latest_consult.context_snapshot_json)
                health_score = float(snap.get("consultation_details", {}).get("farm_health_score", 75))
            except Exception:
                pass
        else:
            # Fallback computation if no consultation history
            soil_query = db.query(SoilReport).filter(SoilReport.farmer_id == farmer_id)
            if farm_id is not None:
                soil_query = soil_query.filter(SoilReport.farm_id == farm_id)
            soil = soil_query.order_by(SoilReport.tested_at.desc()).first()
            if soil:
                if 6.0 <= soil.ph <= 7.5:
                    health_score += 10
                else:
                    health_score += 5
                if soil.nitrogen >= 40: health_score += 5
                if soil.phosphorus >= 30: health_score += 5
                if soil.potassium >= 150: health_score += 5

            # Deduct for high/critical disease scans
            bad_scans = db.query(DiseaseScan).filter(
                DiseaseScan.farmer_id == farmer_id,
                DiseaseScan.severity.in_(["High", "Critical"])
            ).count()
            health_score -= min(bad_scans * 10, 30)

            # Deduct for overdue tasks
            overdue_count = len(farm_task_repo.get_overdue_tasks(db, farmer_id, farm_id=farm_id))
            health_score -= min(overdue_count * 5, 20)
            
            health_score = max(0.0, min(health_score, 100.0))

        # 2. Risk Score calculation (Base 25)
        risk_score = 25.0
        alerts = risk_alert_repo.get_latest_run_alerts(db, farmer_id, farm_id=farm_id)
        if alerts:
            # Weight based on active warnings
            computed_risk = 15.0
            for alert in alerts:
                severity = (alert.severity or "medium").lower()
                if severity == "critical":
                    computed_risk += 25
                elif severity == "high":
                    computed_risk += 15
                elif severity == "medium":
                    computed_risk += 10
                else:
                    computed_risk += 5
            risk_score = max(0.0, min(computed_risk, 100.0))
        else:
            # Check for bad scans
            bad_scans = db.query(DiseaseScan).filter(
                DiseaseScan.farmer_id == farmer_id,
                DiseaseScan.severity.in_(["High", "Critical"])
            ).count()
            if bad_scans > 0:
                risk_score += min(bad_scans * 15, 50)
            risk_score = max(0.0, min(risk_score, 100.0))

        # 3. Active Sowing plans
        plans_query = db.query(FarmPlan).filter(FarmPlan.farmer_id == farmer_id, FarmPlan.status == "active")
        if farm_id is not None:
            plans_query = plans_query.filter(FarmPlan.farm_id == farm_id)
        plans = plans_query.all()
        active_crops = [p.crop_name for p in plans]
        active_crop_count = len(plans)

        # 4. Projected Yield (Sum of latest yield predictions for active plans, fallback to any latest)
        projected_yield = 0.0
        if active_crops:
            for crop in active_crops:
                pred_query = db.query(YieldPrediction).filter(
                    YieldPrediction.farmer_id == farmer_id,
                    YieldPrediction.crop_name == crop
                )
                if farm_id is not None:
                    pred_query = pred_query.filter(YieldPrediction.farm_id == farm_id)
                pred = pred_query.order_by(YieldPrediction.created_at.desc()).first()
                if pred:
                    projected_yield += pred.predicted_yield
        
        # If no yields matched active plans, sum latest predictions for distinct crops
        if projected_yield == 0.0:
            distinct_predictions_query = db.query(YieldPrediction.crop_name, func.max(YieldPrediction.id).label("max_id")).filter(
                YieldPrediction.farmer_id == farmer_id
            )
            if farm_id is not None:
                distinct_predictions_query = distinct_predictions_query.filter(YieldPrediction.farm_id == farm_id)
            distinct_predictions = distinct_predictions_query.group_by(YieldPrediction.crop_name).subquery()
            
            yield_records = db.query(YieldPrediction).join(
                distinct_predictions, YieldPrediction.id == distinct_predictions.c.max_id
            ).all()
            projected_yield = sum(y.predicted_yield for y in yield_records)

        # 5. Projected Profit / Revenue
        projected_profit = 0.0
        if active_crops:
            for crop in active_crops:
                analysis = db.query(ProfitabilityAnalysis).filter(
                    ProfitabilityAnalysis.farmer_id == farmer_id,
                    ProfitabilityAnalysis.crop_name == crop
                ).order_by(ProfitabilityAnalysis.created_at.desc()).first()
                if analysis:
                    projected_profit += analysis.estimated_profit
        
        # Fallback to any latest crop profitability sum
        if projected_profit == 0.0:
            distinct_analyses = db.query(ProfitabilityAnalysis.crop_name, func.max(ProfitabilityAnalysis.id).label("max_id")).filter(
                ProfitabilityAnalysis.farmer_id == farmer_id
            ).group_by(ProfitabilityAnalysis.crop_name).subquery()
            
            profit_records = db.query(ProfitabilityAnalysis).join(
                distinct_analyses, ProfitabilityAnalysis.id == distinct_analyses.c.max_id
            ).all()
            projected_profit = sum(p.estimated_profit for p in profit_records)

        # 6. Active Alerts Count (unread notifications + active risk warnings)
        unread_notifs = notification_repo.list_by_farmer(db, farmer_id, is_read=False)
        active_warnings = risk_alert_repo.get_latest_run_alerts(db, farmer_id, farm_id=farm_id)
        active_alert_count = len(unread_notifs) + len(active_warnings)

        return {
            "health_score": health_score,
            "risk_score": risk_score,
            "projected_yield": projected_yield,
            "projected_profit": projected_profit,
            "active_crop_count": active_crop_count,
            "active_alert_count": active_alert_count
        }

    def generate_snapshot(self, db: Session, farmer: Farmer) -> FarmAnalyticsSnapshot:
        from app.services.farm import farm_service
        active_farm = farm_service.get_or_create_active_farm(db, farmer)
        kpis = self.calculate_realtime_kpis(db, farmer.id, farm_id=active_farm.id)
        
        # Compile snapshot metadata JSON
        plans_query = db.query(FarmPlan).filter(FarmPlan.farmer_id == farmer.id, FarmPlan.status == "active")
        if active_farm:
            plans_query = plans_query.filter(FarmPlan.farm_id == active_farm.id)
        latest_plans = plans_query.all()
        crops_meta = [{"crop_name": p.crop_name, "area_acres": p.area_acres} for p in latest_plans]
        
        overdue_tasks = farm_task_repo.get_overdue_tasks(db, farmer.id, farm_id=active_farm.id)
        overdue_meta = [{"task_id": t.id, "title": t.title, "planned_date": t.planned_date.isoformat()} for t in overdue_tasks]

        snapshot_data = {
            "captured_at": datetime.now().isoformat(),
            "crops": crops_meta,
            "overdue_tasks": overdue_meta,
            "weather_temp": 28.0  # Placeholder weather metric
        }

        # Query weather context for snapshot
        try:
            _, _, temp, _, _ = weather_intelligence_service.get_weather_data(db, farmer.location or "Delhi, India")
            snapshot_data["weather_temp"] = temp
        except Exception:
            pass

        return farm_analytics_repo.create(
            db=db,
            farmer_id=farmer.id,
            farm_id=active_farm.id,
            health_score=kpis["health_score"],
            risk_score=kpis["risk_score"],
            projected_profit=kpis["projected_profit"],
            projected_yield=kpis["projected_yield"],
            active_crop_count=kpis["active_crop_count"],
            active_alert_count=kpis["active_alert_count"],
            snapshot_json=json.dumps(snapshot_data)
        )

    def list_trends(self, db: Session, farmer_id: int, farm_id: Optional[int] = None) -> List[FarmAnalyticsSnapshot]:
        return farm_analytics_repo.list_by_farmer(db, farmer_id, farm_id=farm_id)

    def get_dashboard_data(self, db: Session, farmer: Farmer) -> Dict[str, Any]:
        from app.services.farm import farm_service
        active_farm = farm_service.get_or_create_active_farm(db, farmer)
        kpis = self.calculate_realtime_kpis(db, farmer.id, farm_id=active_farm.id)
        trends = self.list_trends(db, farmer.id, farm_id=active_farm.id)

        # Generate automatic insights
        insights = []
        if kpis["health_score"] >= 80.0:
            insights.append(f"Farm health score is excellent ({kpis['health_score']:.0f}/100). Nutrients and tasks are well optimized.")
        elif kpis["health_score"] <= 60.0:
            insights.append(f"Farm health index has dipped to {kpis['health_score']:.0f}/100. Address overdue tasks and disease scans immediately.")
        else:
            insights.append("Farm parameters are stable. Continue scheduled nitrogen dressing cycles.")

        if kpis["risk_score"] >= 60.0:
            insights.append(f"Elevated risk level detected ({kpis['risk_score']:.0f}/100). High pest probability on field crops.")
        else:
            insights.append("Pest and weather risk factors remain within optimal margins.")

        # Soil metric check for insight
        soil_query = db.query(SoilReport).filter(SoilReport.farmer_id == farmer.id)
        if active_farm:
            soil_query = soil_query.filter(SoilReport.farm_id == active_farm.id)
        soil = soil_query.order_by(SoilReport.tested_at.desc()).first()
        if soil:
            if soil.nitrogen < 30 or soil.phosphorus < 30 or soil.potassium < 80:
                insights.append(f"Soil nutrient deficiencies detected in Nitrogen/Phosphorus. Follow custom fertilizer suggestions.")
            else:
                insights.append(f"Soil NPK composition ({soil.nitrogen}/{soil.phosphorus}/{soil.potassium}) is supportive of planned {soil.crop_planned}.")

        if kpis["projected_profit"] > 0:
            insights.append(f"Sowing plans are projected to yield Rs. {kpis['projected_profit']:.2f} in profitability.")
        
        # Distribution maps
        crop_distribution = {}
        plans_query = db.query(FarmPlan).filter(FarmPlan.farmer_id == farmer.id, FarmPlan.status == "active")
        if active_farm:
            plans_query = plans_query.filter(FarmPlan.farm_id == active_farm.id)
        plans = plans_query.all()
        for p in plans:
            crop_distribution[p.crop_name] = crop_distribution.get(p.crop_name, 0.0) + p.area_acres
        if not crop_distribution:
            crop_distribution = {"Unplanned": 1.0}

        alert_distribution = {"Weather": 0, "Risk": 0, "Disease": 0, "Planner": 0}
        unread_notifs = notification_repo.list_by_farmer(db, farmer.id, is_read=False)
        for notif in unread_notifs:
            cat = notif.notification_type.capitalize()
            if cat in alert_distribution:
                alert_distribution[cat] += 1
            else:
                alert_distribution["Risk"] += 1


        return {
            "kpis": kpis,
            "trends": trends,
            "insights": insights,
            "crop_distribution": crop_distribution,
            "alert_distribution": alert_distribution
        }

    def generate_pdf_report(self, db: Session, farmer: Farmer) -> io.BytesIO:
        from app.services.farm import farm_service
        active_farm = farm_service.get_or_create_active_farm(db, farmer)
        kpis = self.calculate_realtime_kpis(db, farmer.id, farm_id=active_farm.id)
        
        # Fetch detailed reports
        soil_query = db.query(SoilReport).filter(SoilReport.farmer_id == farmer.id)
        if active_farm:
            soil_query = soil_query.filter(SoilReport.farm_id == active_farm.id)
        soil = soil_query.order_by(SoilReport.tested_at.desc()).first()

        alerts = risk_alert_repo.get_latest_run_alerts(db, farmer.id, farm_id=active_farm.id)
        latest_consult = db.query(ConsultationHistory).filter(ConsultationHistory.farmer_id == farmer.id).order_by(ConsultationHistory.created_at.desc()).first()


        pdf_buffer = io.BytesIO()
        doc = SimpleDocTemplate(
            pdf_buffer,
            pagesize=letter,
            rightMargin=54, leftMargin=54, topMargin=54, bottomMargin=54
        )

        styles = getSampleStyleSheet()
        
        # Custom styles
        title_style = ParagraphStyle(
            "ReportTitle",
            parent=styles["Heading1"],
            fontName="Helvetica-Bold",
            fontSize=22,
            textColor=colors.HexColor("#2e7d32"),
            spaceAfter=10
        )
        subtitle_style = ParagraphStyle(
            "ReportSubtitle",
            parent=styles["Normal"],
            fontSize=10,
            textColor=colors.HexColor("#555555"),
            spaceAfter=20
        )
        h2_style = ParagraphStyle(
            "ReportH2",
            parent=styles["Heading2"],
            fontName="Helvetica-Bold",
            fontSize=14,
            textColor=colors.HexColor("#1b5e20"),
            spaceBefore=15,
            spaceAfter=10
        )
        body_style = ParagraphStyle(
            "ReportBody",
            parent=styles["BodyText"],
            fontSize=10,
            leading=14,
            spaceAfter=8
        )

        story = []

        # Header Title
        story.append(Paragraph("AgriAssist AI - Executive Farm Performance Report", title_style))
        story.append(Paragraph(f"Generated on {date.today().strftime('%B %d, %Y')} | Farmer Account ID: {farmer.id} | Location: {farmer.location or 'India'}", subtitle_style))
        story.append(Spacer(1, 10))

        # KPI Table
        story.append(Paragraph("1. Executive Core Metrics", h2_style))
        kpi_data = [
            ["Metric Parameter", "Current Status Value", "Analysis & Threshold Rating"],
            ["Farm Health Index", f"{kpis['health_score']:.1f} / 100", "Good" if kpis["health_score"] >= 75 else ("Fair" if kpis["health_score"] >= 50 else "Attention Required")],
            ["Risk Score Warning", f"{kpis['risk_score']:.1f} / 100", "High Alert" if kpis["risk_score"] >= 60 else "Safe / Normal"],
            ["Projected Yield (Sum)", f"{kpis['projected_yield']:.1f} kg", "Based on crop yield forecasts"],
            ["Estimated Net Profit", f"Rs. {kpis['projected_profit']:.2f}", "Calculated via market intelligence pricing"],
            ["Active Crop Plans", f"{kpis['active_crop_count']}", "Planned and monitored field acreage"],
            ["Pending System Alerts", f"{kpis['active_alert_count']} Open", "Unread warnings and critical hazards"]
        ]
        
        t = Table(kpi_data, colWidths=[200, 150, 150])
        t.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor("#2e7d32")),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 10),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 8),
            ('TOPPADDING', (0, 0), (-1, 0), 8),
            ('BACKGROUND', (0, 1), (-1, -1), colors.HexColor("#f1f8e9")),
            ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor("#c5e1a5")),
            ('FONTSIZE', (0, 1), (-1, -1), 9),
            ('BOTTOMPADDING', (0, 1), (-1, -1), 6),
            ('TOPPADDING', (0, 1), (-1, -1), 6),
        ]))
        story.append(t)
        story.append(Spacer(1, 15))

        # Soil context
        story.append(Paragraph("2. Soil Metrics Diagnostics", h2_style))
        if soil:
            soil_text = (
                f"The latest soil diagnostic report was registered on {soil.tested_at.strftime('%Y-%m-%d') if soil.tested_at else 'N/A'} for planned crop **{soil.crop_planned}**. "
                f"Recorded parameters include: pH level **{soil.ph}** (Rating: {'Optimal' if 6.0 <= soil.ph <= 7.5 else 'Suboptimal'}), "
                f"Nitrogen: **{soil.nitrogen} mg/kg**, Phosphorus: **{soil.phosphorus} mg/kg**, and Potassium: **{soil.potassium} mg/kg**."
            )
        else:
            soil_text = "No soil reports have been logged in the system database for this account yet."
        story.append(Paragraph(soil_text, body_style))
        story.append(Spacer(1, 10))

        # Active risks
        story.append(Paragraph("3. Active Field Risks & Hazards", h2_style))
        if alerts:
            risk_data = [["Hazard Warning", "Category", "Risk Level", "Probability"]]
            for alert in alerts[:5]:
                risk_data.append([alert.alert_title, alert.category.capitalize(), alert.severity.upper(), f"{alert.probability}%"])
            rt = Table(risk_data, colWidths=[200, 100, 100, 100])
            rt.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor("#c62828")),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('BACKGROUND', (0, 1), (-1, -1), colors.HexColor("#ffebee")),
                ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor("#ef9a9a")),
                ('FONTSIZE', (0, 0), (-1, -1), 9),
                ('BOTTOMPADDING', (0, 0), (-1, -1), 5),
                ('TOPPADDING', (0, 0), (-1, -1), 5),
            ]))
            story.append(rt)
        else:
            story.append(Paragraph("All clear. No active risk warnings or pathogen hazards detected on field plans.", body_style))
        story.append(Spacer(1, 10))

        # Recommendations
        story.append(Paragraph("4. Executive Agronomist Guidance Actions", h2_style))
        rec_list = []
        if latest_consult:
            try:
                snap = json.loads(latest_consult.context_snapshot_json)
                rec_list = snap.get("consultation_details", {}).get("recommended_actions", [])
            except Exception:
                pass

        if rec_list:
            for rec in rec_list:
                story.append(Paragraph(f"• {rec}", body_style))
        else:
            story.append(Paragraph("• Maintain scheduled watering intervals adapting to forecasts.", body_style))
            story.append(Paragraph("• Apply customized NPK top-dressings matching plan cycles.", body_style))

        # Build PDF document
        doc.build(story)
        pdf_buffer.seek(0)
        return pdf_buffer


farm_analytics_service = FarmAnalyticsService()
