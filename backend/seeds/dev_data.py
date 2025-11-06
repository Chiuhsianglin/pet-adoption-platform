"""
Development seed data for Pet Adoption Platform
"""
import asyncio
from datetime import datetime
from decimal import Decimal
import bcrypt
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_async_db
from app.models import User, Pet, AdoptionApplication, ChatRoom, Message, Notification
from app.models.user import UserRole
from app.models.pet import PetSpecies, PetGender, PetSize, PetStatus, EnergyLevel
from app.models.adoption import ApplicationStatus
from app.models.chat import MessageType
from app.models.notification import NotificationType


def hash_password(password: str) -> str:
    """Hash password using bcrypt"""
    salt = bcrypt.gensalt()
    hashed = bcrypt.hashpw(password.encode('utf-8'), salt)
    return hashed.decode('utf-8')


async def create_seed_users(db: AsyncSession) -> dict:
    """Create seed users for testing"""
    users = {}
    
    # Admin user
    admin = User(
        email="admin@petadoption.com",
        password_hash=hash_password("admin123"),
        first_name="Admin",
        last_name="User",
        phone="+1-555-0101",
        role=UserRole.admin,
        is_active=True,
        is_verified=True,
        bio="Platform administrator",
        city="San Francisco",
        state="CA",
        country="USA",
        created_at=datetime.utcnow(),
        updated_at=datetime.utcnow()
    )
    db.add(admin)
    users['admin'] = admin
    
    # Shelter users
    shelter1 = User(
        email="shelter1@petadoption.com",
        password_hash=hash_password("shelter123"),
        first_name="Happy Paws",
        last_name="Shelter",
        phone="+1-555-0201",
        role=UserRole.shelter,
        is_active=True,
        is_verified=True,
        bio="Dedicated to finding loving homes for pets",
        address_line1="123 Pet Street",
        city="San Francisco",
        state="CA",
        postal_code="94101",
        country="USA",
        created_at=datetime.utcnow(),
        updated_at=datetime.utcnow()
    )
    db.add(shelter1)
    users['shelter1'] = shelter1
    
    shelter2 = User(
        email="shelter2@petadoption.com",
        password_hash=hash_password("shelter123"),
        first_name="Loving Care",
        last_name="Animal Rescue",
        phone="+1-555-0202",
        role=UserRole.shelter,
        is_active=True,
        is_verified=True,
        bio="Rescuing and rehoming animals since 2010",
        address_line1="456 Animal Ave",
        city="Oakland",
        state="CA",
        postal_code="94601",
        country="USA",
        created_at=datetime.utcnow(),
        updated_at=datetime.utcnow()
    )
    db.add(shelter2)
    users['shelter2'] = shelter2
    
    # Adopter users
    adopter1 = User(
        email="adopter1@example.com",
        password_hash=hash_password("adopter123"),
        first_name="John",
        last_name="Smith",
        phone="+1-555-0301",
        role=UserRole.adopter,
        is_active=True,
        is_verified=True,
        bio="Love animals and looking for a furry companion",
        address_line1="789 Home Street",
        city="San Jose",
        state="CA",
        postal_code="95101",
        country="USA",
        created_at=datetime.utcnow(),
        updated_at=datetime.utcnow()
    )
    db.add(adopter1)
    users['adopter1'] = adopter1
    
    adopter2 = User(
        email="adopter2@example.com",
        password_hash=hash_password("adopter123"),
        first_name="Emily",
        last_name="Johnson",
        phone="+1-555-0302",
        role=UserRole.adopter,
        is_active=True,
        is_verified=True,
        bio="First-time pet owner excited to adopt",
        address_line1="321 Family Lane",
        city="Berkeley",
        state="CA",
        postal_code="94701",
        country="USA",
        created_at=datetime.utcnow(),
        updated_at=datetime.utcnow()
    )
    db.add(adopter2)
    users['adopter2'] = adopter2
    
    await db.flush()  # Ensure IDs are generated
    return users


async def create_seed_pets(db: AsyncSession, users: dict) -> dict:
    """Create seed pets for testing"""
    pets = {}
    
    # Dogs
    dog1 = Pet(
        name="Buddy",
        species=PetSpecies.dog,
        breed="Golden Retriever",
        age_years=3,
        age_months=6,
        gender=PetGender.male,
        size=PetSize.large,
        weight_kg=30.5,
        color="Golden",
        description="Friendly and energetic dog, loves playing fetch and swimming. Great with kids!",
        medical_info="Up to date on vaccinations, heartworm negative",
        behavioral_info="Well-trained, knows basic commands, leash trained",
        adoption_fee=Decimal("250.00"),
        status=PetStatus.available,
        shelter_id=users['shelter1'].id,
        microchip_id="982000123456789",
        vaccination_status="Current",
        spayed_neutered=True,
        house_trained=True,
        good_with_kids=True,
        good_with_pets=True,
        energy_level=EnergyLevel.high,
        photos=["buddy_1.jpg", "buddy_2.jpg", "buddy_3.jpg"],
        created_at=datetime.utcnow(),
        updated_at=datetime.utcnow()
    )
    db.add(dog1)
    pets['dog1'] = dog1
    
    dog2 = Pet(
        name="Luna",
        species=PetSpecies.dog,
        breed="Border Collie Mix",
        age_years=2,
        age_months=0,
        gender=PetGender.female,
        size=PetSize.medium,
        weight_kg=22.0,
        color="Black and White",
        description="Intelligent and loyal companion. Loves mental stimulation and outdoor activities.",
        medical_info="Healthy, all vaccinations current",
        behavioral_info="Very smart, eager to please, knows many tricks",
        adoption_fee=Decimal("200.00"),
        status=PetStatus.available,
        shelter_id=users['shelter1'].id,
        microchip_id="982000123456790",
        vaccination_status="Current",
        spayed_neutered=True,
        house_trained=True,
        good_with_kids=True,
        good_with_pets=True,
        energy_level=EnergyLevel.high,
        photos=["luna_1.jpg", "luna_2.jpg"],
        created_at=datetime.utcnow(),
        updated_at=datetime.utcnow()
    )
    db.add(dog2)
    pets['dog2'] = dog2
    
    # Cats
    cat1 = Pet(
        name="Whiskers",
        species=PetSpecies.cat,
        breed="Domestic Shorthair",
        age_years=1,
        age_months=8,
        gender=PetGender.male,
        size=PetSize.medium,
        weight_kg=4.5,
        color="Orange Tabby",
        description="Playful kitten with a sweet personality. Loves toys and cuddles.",
        medical_info="Neutered, vaccinated, FIV/FeLV negative",
        behavioral_info="Litter trained, playful, social",
        adoption_fee=Decimal("150.00"),
        status=PetStatus.available,
        shelter_id=users['shelter2'].id,
        microchip_id="982000123456791",
        vaccination_status="Current",
        spayed_neutered=True,
        house_trained=True,
        good_with_kids=True,
        good_with_pets=True,
        energy_level=EnergyLevel.medium,
        photos=["whiskers_1.jpg", "whiskers_2.jpg"],
        created_at=datetime.utcnow(),
        updated_at=datetime.utcnow()
    )
    db.add(cat1)
    pets['cat1'] = cat1
    
    cat2 = Pet(
        name="Shadow",
        species=PetSpecies.cat,
        breed="Maine Coon",
        age_years=4,
        age_months=0,
        gender=PetGender.female,
        size=PetSize.large,
        weight_kg=6.8,
        color="Black",
        description="Gentle giant with a calm demeanor. Perfect lap cat for quiet evenings.",
        medical_info="Spayed, current on vaccines, healthy",
        behavioral_info="Calm, affectionate, good with other cats",
        adoption_fee=Decimal("175.00"),
        status=PetStatus.pending,
        shelter_id=users['shelter2'].id,
        microchip_id="982000123456792",
        vaccination_status="Current",
        spayed_neutered=True,
        house_trained=True,
        good_with_kids=True,
        good_with_pets=True,
        energy_level=EnergyLevel.low,
        photos=["shadow_1.jpg"],
        created_at=datetime.utcnow(),
        updated_at=datetime.utcnow()
    )
    db.add(cat2)
    pets['cat2'] = cat2
    
    # Rabbit
    rabbit1 = Pet(
        name="Coco",
        species=PetSpecies.rabbit,
        breed="Holland Lop",
        age_years=0,
        age_months=6,
        gender=PetGender.female,
        size=PetSize.small,
        weight_kg=1.2,
        color="Brown and White",
        description="Adorable young rabbit with floppy ears. Enjoys hay and fresh vegetables.",
        medical_info="Spayed, healthy",
        behavioral_info="Gentle, litter trained, enjoys being petted",
        adoption_fee=Decimal("75.00"),
        status=PetStatus.available,
        shelter_id=users['shelter1'].id,
        vaccination_status="N/A",
        spayed_neutered=True,
        house_trained=True,
        good_with_kids=True,
        good_with_pets=False,
        energy_level=EnergyLevel.medium,
        photos=["coco_1.jpg"],
        created_at=datetime.utcnow(),
        updated_at=datetime.utcnow()
    )
    db.add(rabbit1)
    pets['rabbit1'] = rabbit1
    
    await db.flush()
    return pets


async def create_seed_applications(db: AsyncSession, users: dict, pets: dict) -> dict:
    """Create seed adoption applications"""
    applications = {}
    
    # Application for Shadow (cat2) - pending
    app1 = AdoptionApplication(
        pet_id=pets['cat2'].id,
        applicant_id=users['adopter1'].id,
        status=ApplicationStatus.pending,
        application_data={
            "housing_type": "apartment",
            "has_yard": False,
            "other_pets": [],
            "experience_with_pets": "I had cats growing up",
            "daily_schedule": "Work from home, very flexible",
            "emergency_vet": "SF Animal Hospital",
            "references": [
                {"name": "Jane Doe", "phone": "555-1234", "relationship": "friend"}
            ]
        },
        notes="Initial application submitted",
        created_at=datetime.utcnow(),
        updated_at=datetime.utcnow()
    )
    db.add(app1)
    applications['app1'] = app1
    
    # Application for Buddy (dog1) - under review
    app2 = AdoptionApplication(
        pet_id=pets['dog1'].id,
        applicant_id=users['adopter2'].id,
        status=ApplicationStatus.under_review,
        application_data={
            "housing_type": "house",
            "has_yard": True,
            "other_pets": [],
            "experience_with_pets": "First-time pet owner",
            "daily_schedule": "Work 9-5, but partner works from home",
            "emergency_vet": "Berkeley Vet Clinic",
            "references": [
                {"name": "Bob Smith", "phone": "555-5678", "relationship": "neighbor"},
                {"name": "Alice Brown", "phone": "555-9012", "relationship": "coworker"}
            ]
        },
        notes="Good application, need to verify references",
        reviewed_by=users['shelter1'].id,
        reviewed_at=datetime.utcnow(),
        created_at=datetime.utcnow(),
        updated_at=datetime.utcnow()
    )
    db.add(app2)
    applications['app2'] = app2
    
    await db.flush()
    return applications


async def create_seed_chat_and_messages(db: AsyncSession, applications: dict, users: dict):
    """Create seed chat rooms and messages"""
    # Chat room for first application
    chat1 = ChatRoom(
        application_id=applications['app1'].id,
        is_active=True,
        created_at=datetime.utcnow(),
        updated_at=datetime.utcnow()
    )
    db.add(chat1)
    await db.flush()
    
    # Messages in chat room
    msg1 = Message(
        chat_room_id=chat1.id,
        sender_id=users['adopter1'].id,
        content="Hi! I'm very interested in Shadow. She seems like the perfect cat for me.",
        message_type=MessageType.text,
        is_read=True,
        created_at=datetime.utcnow(),
        updated_at=datetime.utcnow()
    )
    db.add(msg1)
    
    msg2 = Message(
        chat_room_id=chat1.id,
        sender_id=users['shelter2'].id,
        content="Thank you for your interest! Shadow is indeed a wonderful cat. I see you've submitted an application. Do you have any questions about her?",
        message_type=MessageType.text,
        is_read=True,
        created_at=datetime.utcnow(),
        updated_at=datetime.utcnow()
    )
    db.add(msg2)
    
    msg3 = Message(
        chat_room_id=chat1.id,
        sender_id=users['adopter1'].id,
        content="Yes, I'd like to know more about her daily routine and favorite activities.",
        message_type=MessageType.text,
        is_read=False,
        created_at=datetime.utcnow(),
        updated_at=datetime.utcnow()
    )
    db.add(msg3)


async def create_seed_notifications(db: AsyncSession, users: dict):
    """Create seed notifications"""
    # Notification for adopter1
    notif1 = Notification(
        user_id=users['adopter1'].id,
        title="Application Received",
        message="Your adoption application for Shadow has been received and is being reviewed.",
        type=NotificationType.application,
        is_read=True,
        action_url="/applications/1",
        metadata={"pet_name": "Shadow", "application_id": 1},
        created_at=datetime.utcnow(),
        updated_at=datetime.utcnow()
    )
    db.add(notif1)
    
    # Notification for adopter2
    notif2 = Notification(
        user_id=users['adopter2'].id,
        title="New Message",
        message="You have a new message about your application for Buddy.",
        type=NotificationType.message,
        is_read=False,
        action_url="/chat/2",
        metadata={"pet_name": "Buddy", "chat_room_id": 2},
        created_at=datetime.utcnow(),
        updated_at=datetime.utcnow()
    )
    db.add(notif2)
    
    # System notification for all users
    for user_key, user in users.items():
        if user.role != UserRole.admin:  # Don't send to admin
            system_notif = Notification(
                user_id=user.id,
                title="Welcome to Pet Adoption Platform!",
                message="Thank you for joining our community. Start browsing pets available for adoption.",
                type=NotificationType.system,
                is_read=False,
                action_url="/pets",
                created_at=datetime.utcnow(),
                updated_at=datetime.utcnow()
            )
            db.add(system_notif)


async def seed_database():
    """Main function to seed the database with development data"""
    print("🌱 Starting database seeding...")
    
    async for db in get_async_db():
        try:
            print("👥 Creating seed users...")
            users = await create_seed_users(db)
            
            print("🐕 Creating seed pets...")
            pets = await create_seed_pets(db, users)
            
            print("📝 Creating seed applications...")
            applications = await create_seed_applications(db, users, pets)
            
            print("💬 Creating seed chat rooms and messages...")
            await create_seed_chat_and_messages(db, applications, users)
            
            print("🔔 Creating seed notifications...")
            await create_seed_notifications(db, users)
            
            await db.commit()
            print("✅ Database seeding completed successfully!")
            
        except Exception as e:
            await db.rollback()
            print(f"❌ Error seeding database: {str(e)}")
            raise
        finally:
            await db.close()
        break  # Only run once


if __name__ == "__main__":
    asyncio.run(seed_database())