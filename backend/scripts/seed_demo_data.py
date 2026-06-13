import os
import sys
from datetime import datetime, date, timedelta

# Inject backend directory into system path to resolve imports correctly
# Handles running from host root scripts/ or inside backend container scripts/
current_dir = os.path.abspath(os.path.dirname(__file__))
parent_dir = os.path.dirname(current_dir)
# If we are in backend/scripts/, the parent directory is the backend root
if parent_dir.endswith("backend") or os.path.exists(os.path.join(parent_dir, "app", "main.py")):
    sys.path.insert(0, parent_dir)
else:
    sys.path.insert(0, os.path.join(parent_dir, "backend"))

from app.core.database import SessionLocal
from app.core.security import get_password_hash
from app.models.farmer import Farmer
from app.models.farm import Farm
from app.models.soil import SoilReport
from app.models.farm_planner import FarmPlan, FarmTask
from app.models.yield_prediction import YieldPrediction
from app.models.notification import Notification
from app.models.farm_analytics import FarmAnalyticsSnapshot
from app.models.risk_alert import RiskAlert


def seed_demo_data():
    print("🌱 Starting AgriAssist AI Demo Data Seeder...")
    db = SessionLocal()

    try:
        # 1. Clean existing recruiter data (foreign keys with SET NULL / CASCADE will automatically clear or handle)
        print("🧹 Cleaning old recruiter data...")
        old_recruiter = db.query(Farmer).filter(Farmer.email == "recruiter@agriassist.ai").first()
        if old_recruiter:
            # Delete child farms manually to ensure clean database
            db.query(Farm).filter(Farm.farmer_id == old_recruiter.id).delete()
            db.query(Notification).filter(Notification.farmer_id == old_recruiter.id).delete()
            db.delete(old_recruiter)
            db.commit()
            print("✅ Cleaned old recruiter profile.")

        # 2. Create Recruiter Farmer Account
        print("👤 Creating recruiter profile...")
        recruiter = Farmer(
            email="recruiter@agriassist.ai",
            password_hash=get_password_hash("password123"),
            first_name="Anil",
            last_name="Kumar",
            location="Ludhiana, Punjab",
            theme_preference="dark",
            email_notifications=1,
            push_notifications=1,
            default_crop="wheat",
            default_soil_type="alluvial"
        )
        db.add(recruiter)
        db.commit()
        db.refresh(recruiter)
        print(f"✅ Recruiter registered successfully with ID: {recruiter.id}")

        # 3. Create Multi-Farm Holdings (3 Farms)
        print("🏡 Planting farm holdings...")
        farm_1 = Farm(
            farmer_id=recruiter.id,
            name="Green Valley Farm",
            location="Ludhiana, Punjab",
            total_area_acres=12.5,
            soil_type="alluvial",
            latitude=30.9010,
            longitude=75.8573
        )
        farm_2 = Farm(
            farmer_id=recruiter.id,
            name="Sunrise Farm",
            location="Karnal, Haryana",
            total_area_acres=8.0,
            soil_type="clayey",
            latitude=29.6857,
            longitude=76.9905
        )
        farm_3 = Farm(
            farmer_id=recruiter.id,
            name="River Edge Farm",
            location="Mysuru, Karnataka",
            total_area_acres=5.0,
            soil_type="loamy",
            latitude=12.2958,
            longitude=76.6394
        )
        db.add_all([farm_1, farm_2, farm_3])
        db.commit()
        db.refresh(farm_1)
        db.refresh(farm_2)
        db.refresh(farm_3)

        # Set default active farm for recruiter context
        recruiter.active_farm_id = farm_1.id
        db.commit()
        print(f"✅ Created 3 farms (Green Valley: ID {farm_1.id}, Sunrise: ID {farm_2.id}, River Edge: ID {farm_3.id}).")

        # 4. Create Soil Health Reports
        print("🧪 Logging soil parameters...")
        soil_1 = SoilReport(
            farmer_id=recruiter.id,
            farm_id=farm_1.id,
            ph=6.5,
            nitrogen=45.0,
            phosphorus=32.0,
            potassium=180.0,
            organic_matter=2.2,
            crop_planned="wheat",
            tested_at=date.today() - timedelta(days=15)
        )
        soil_2 = SoilReport(
            farmer_id=recruiter.id,
            farm_id=farm_2.id,
            ph=5.8,
            nitrogen=38.0,
            phosphorus=28.0,
            potassium=140.0,
            organic_matter=1.8,
            crop_planned="rice",
            tested_at=date.today() - timedelta(days=10)
        )
        db.add_all([soil_1, soil_2])
        db.commit()
        print("✅ Registered soil reports for Green Valley and Sunrise farms.")

        # 5. Create Yield Predictions
        print("📊 Projecting crop yields...")
        yield_1 = YieldPrediction(
            farmer_id=recruiter.id,
            farm_id=farm_1.id,
            crop_name="wheat",
            predicted_yield=18750.0,
            confidence_score=92,
            yield_category="High",
            prediction_factors='["Alluvial soil nitrogen balance", "Optimum weather temperature range"]',
            recommendations='["Apply potash at tillering stage", "Keep soil damp during flowering"]'
        )
        yield_2 = YieldPrediction(
            farmer_id=recruiter.id,
            farm_id=farm_2.id,
            crop_name="rice",
            predicted_yield=12800.0,
            confidence_score=85,
            yield_category="Medium",
            prediction_factors='["Clayey texture water retention", "Neutral pH index"]',
            recommendations='["Ensure flood irrigation during sowing", "Apply nitrogen urea dose"]'
        )
        db.add_all([yield_1, yield_2])
        db.commit()
        print("✅ Projections added.")

        # 6. Create AI Sowing Schedules and Tasks
        print("📅 Creating operational crop planners...")
        plan_1 = FarmPlan(
            farmer_id=recruiter.id,
            farm_id=farm_1.id,
            crop_name="wheat",
            area_acres=12.5,
            planned_start_date=date.today() - timedelta(days=2),
            expected_harvest_date=date.today() + timedelta(days=120)
        )
        db.add(plan_1)
        db.commit()
        db.refresh(plan_1)

        task_1 = FarmTask(
            farm_plan_id=plan_1.id,
            title="Prepare Soil Beds & Fertilizers",
            description="Mix NPK base compost inputs into field beds.",
            planned_date=date.today() - timedelta(days=2),
            completed_at=datetime.utcnow() - timedelta(days=2),
            status="completed",
            priority="high",
            category="sowing"
        )
        task_2 = FarmTask(
            farm_plan_id=plan_1.id,
            title="Sow Seedlings",
            description="Sow high-yield wheat cultivars at 1.5-inch depths.",
            planned_date=date.today(),
            status="pending",
            priority="high",
            category="sowing"
        )
        task_3 = FarmTask(
            farm_plan_id=plan_1.id,
            title="Sowing Irrigation Cycle",
            description="Ensure soil beds are evenly irrigated.",
            planned_date=date.today() + timedelta(days=5),
            status="pending",
            priority="medium",
            category="irrigation"
        )
        db.add_all([task_1, task_2, task_3])
        db.commit()
        print("✅ Generated wheat plan activity checklist.")

        # 7. Create Warnings and Alerts
        print("🚨 Seeding warning centers...")
        alert_1 = RiskAlert(
            farmer_id=recruiter.id,
            farm_id=farm_1.id,
            crop_name="wheat",
            alert_title="Late Blight Pest Outbreak Risk",
            category="disease",
            severity="high",
            probability=85,
            description="Heavy rainfall anomaly warning in Ludhiana district for June 19. Wet foliage increases late blight fungal growth rate.",
            prevention_steps='["Ensure dry foliage and clear farm water channels", "Apply preventive copper spray"]',
            monitoring_advice='["Inspect lower leaf foliage patterns for gray-green spots daily"]'
        )
        db.add(alert_1)
        db.commit()

        # Seed global alert inbox notifications
        notif_1 = Notification(
            farmer_id=recruiter.id,
            title="Soil report registered",
            message="Alluvial NPK soil analysis report successfully logged for Green Valley Farm.",
            notification_type="system",
            priority="low",
            source_module="soil",
            is_read=True
        )
        notif_2 = Notification(
            farmer_id=recruiter.id,
            title="High Risk Alert: Storm Warning",
            message="Storm warning issued for Ludhiana region. Verify crop protective shelter grids.",
            notification_type="risk",
            priority="high",
            source_module="risk_intelligence",
            is_read=False
        )
        db.add_all([notif_1, notif_2])
        db.commit()
        print("✅ Alert notifications added to farmer inbox.")

        # 8. Create Analytics Snapshot
        print("📈 Compiling analytics snaps...")
        snap = FarmAnalyticsSnapshot(
            farmer_id=recruiter.id,
            farm_id=farm_1.id,
            health_score=88.5,
            risk_score=25.0,
            projected_profit=90000.0,
            projected_yield=18750.0,
            active_crop_count=1,
            active_alert_count=1,
            snapshot_json='{"soil_reports_count": 1, "completed_tasks": 1, "active_warnings": 1}'
        )
        db.add(snap)
        db.commit()
        print("✅ Seeding completed successfully!")
        print("\n🎉 Recruiter demo profile details:")
        print("   Email:     recruiter@agriassist.ai")
        print("   Password:  password123")

    except Exception as e:
        db.rollback()
        print(f"❌ Seeding failed: {e}")
        raise
    finally:
        db.close()


if __name__ == "__main__":
    seed_demo_data()
