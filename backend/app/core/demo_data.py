"""Demo data initialization script"""

from sqlalchemy.orm import Session
from app.core.database import SessionLocal, engine
from app.models.user import User, Task, Memory
from app.schemas.task import GeneratedPlan, PlanStep
from datetime import datetime, timedelta
import json

def create_demo_user(db: Session):
    """Create a demo user"""
    user = User(
        email="demo@example.com",
        name="Demo User",
        profile_data={
            "name": "Demo User",
            "email": "demo@example.com",
            "phone": "+91 98765 43210",
            "address": {
                "house_number": "123",
                "street": "Main Street",
                "area": "Hyderabad",
                "district": "Hyderabad",
                "state": "Telangana",
                "pincode": "500001"
            },
            "aadhaar": "123456789012",
            "age": "30",
            "gender": "Male"
        }
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return user

def create_demo_tasks(db: Session, user_id: int):
    """Create demo tasks"""
    
    # Income Certificate Task
    income_plan = GeneratedPlan(
        steps=[
            PlanStep(
                id="step_1",
                description="Search for income certificate procedure in Telangana",
                tool="search_tool",
                parameters={"query": "income certificate Telangana procedure documents"},
                status="completed"
            ),
            PlanStep(
                id="step_2",
                description="Extract required documents from government website",
                tool="scraper_tool",
                parameters={"content_type": "documents"},
                status="completed"
            ),
            PlanStep(
                id="step_3",
                description="Generate pre-filled income certificate form",
                tool="form_generator",
                parameters={"form_type": "income_certificate", "user_data": {}},
                status="completed"
            ),
            PlanStep(
                id="step_4",
                description="Submit application at MeeSeva center",
                tool=None,
                parameters={},
                status="pending"
            ),
            PlanStep(
                id="step_5",
                description="Track application status",
                tool="status_tracker",
                parameters={"tracking_type": "income_certificate"},
                status="pending"
            )
        ],
        reasoning="Standard income certificate application process for Telangana state"
    )
    
    income_task = Task(
        user_id=user_id,
        title="Income Certificate Application",
        description="Apply for income certificate in Telangana state",
        status="in_progress",
        plan=income_plan.dict(),
        results={
            "completed_steps": 3,
            "total_steps": 5,
            "current_stage": "form_generation_completed",
            "next_action": "Submit application at MeeSeva center"
        }
    )
    db.add(income_task)
    
    # Driving License Task
    license_plan = GeneratedPlan(
        steps=[
            PlanStep(
                id="step_1",
                description="Search for driving license application process",
                tool="search_tool",
                parameters={"query": "driving license application Telangana process"},
                status="completed"
            ),
            PlanStep(
                id="step_2",
                description="Get learner's license application form",
                tool="scraper_tool",
                parameters={"content_type": "procedure"},
                status="completed"
            ),
            PlanStep(
                id="step_3",
                description="Prepare learner's license application",
                tool="form_generator",
                parameters={"form_type": "driving_license", "user_data": {}},
                status="completed"
            ),
            PlanStep(
                id="step_4",
                description="Pass written test and get learner's license",
                tool=None,
                parameters={},
                status="completed"
            ),
            PlanStep(
                id="step_5",
                description="Book driving test slot",
                tool="reminder_tool",
                parameters={"reminder_type": "appointment"},
                status="pending"
            )
        ],
        reasoning="Complete driving license application process from learner's to permanent license"
    )
    
    license_task = Task(
        user_id=user_id,
        title="Driving License Application",
        description="Apply for permanent driving license in Telangana",
        status="in_progress",
        plan=license_plan.dict(),
        results={
            "completed_steps": 4,
            "total_steps": 5,
            "current_stage": "learner_license_obtained",
            "next_action": "Book driving test slot"
        }
    )
    db.add(license_task)
    
    # Caste Certificate Task
    caste_plan = GeneratedPlan(
        steps=[
            PlanStep(
                id="step_1",
                description="Search for caste certificate application procedure",
                tool="search_tool",
                parameters={"query": "caste certificate Telangana application procedure"},
                status="completed"
            ),
            PlanStep(
                id="step_2",
                description="Identify required documents and authority",
                tool="scraper_tool",
                parameters={"content_type": "documents"},
                status="completed"
            ),
            PlanStep(
                id="step_3",
                description="Generate caste certificate application form",
                tool="form_generator",
                parameters={"form_type": "caste_certificate", "user_data": {}},
                status="pending"
            ),
            PlanStep(
                id="step_4",
                description="Submit application with supporting documents",
                tool=None,
                parameters={},
                status="pending"
            ),
            PlanStep(
                id="step_5",
                description="Field verification by revenue inspector",
                tool=None,
                parameters={},
                status="pending"
            )
        ],
        reasoning="Caste certificate application requiring field verification"
    )
    
    caste_task = Task(
        user_id=user_id,
        title="Caste Certificate Application",
        description="Apply for caste certificate in Telangana",
        status="pending",
        plan=caste_plan.dict(),
        results={
            "completed_steps": 2,
            "total_steps": 5,
            "current_stage": "documents_identified",
            "next_action": "Generate application form"
        }
    )
    db.add(caste_task)
    
    db.commit()
    return [income_task, license_task, caste_task]

def create_demo_memories(db: Session, user_id: int):
    """Create demo memory entries"""
    
    # Profile memory
    profile_memory = Memory(
        user_id=user_id,
        memory_type="profile",
        content=json.dumps({
            "name": "Demo User",
            "email": "demo@example.com",
            "preferences": {
                "language": "English",
                "notifications": "enabled",
                "state": "Telangana"
            }
        }),
        metadata={"updated_at": datetime.now().isoformat()}
    )
    db.add(profile_memory)
    
    # Previous requests
    requests = [
        "How to apply for PAN card?",
        "Documents required for passport application",
        "Voter ID registration process"
    ]
    
    for i, request in enumerate(requests):
        request_memory = Memory(
            user_id=user_id,
            memory_type="request",
            content=json.dumps({
                "request": request,
                "timestamp": (datetime.now() - timedelta(days=i+1)).isoformat(),
                "resolved": True
            }),
            metadata={
                "request_type": "information",
                "created_at": (datetime.now() - timedelta(days=i+1)).isoformat()
            }
        )
        db.add(request_memory)
    
    # Completed tasks memory
    completed_task = Memory(
        user_id=user_id,
        memory_type="task",
        content=json.dumps({
            "task_type": "aadhaar_update",
            "status": "completed",
            "completed_at": (datetime.now() - timedelta(days=5)).isoformat(),
            "result": "Aadhaar card address updated successfully"
        }),
        metadata={
            "task_status": "completed",
            "task_type": "aadhaar_update",
            "completed_at": (datetime.now() - timedelta(days=5)).isoformat()
        }
    )
    db.add(completed_task)
    
    db.commit()

def initialize_demo_data():
    """Initialize all demo data"""
    db = SessionLocal()
    
    try:
        # Check if demo user already exists
        existing_user = db.query(User).filter(User.email == "demo@example.com").first()
        if existing_user:
            print("Demo user already exists. Skipping initialization.")
            return
        
        print("Creating demo data...")
        
        # Create demo user
        user = create_demo_user(db)
        print(f"Created demo user: {user.email}")
        
        # Create demo tasks
        tasks = create_demo_tasks(db, user.id)
        print(f"Created {len(tasks)} demo tasks")
        
        # Create demo memories
        create_demo_memories(db, user.id)
        print("Created demo memories")
        
        print("Demo data initialization completed!")
        
    except Exception as e:
        print(f"Error initializing demo data: {e}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    initialize_demo_data()
