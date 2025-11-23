"""
Create sample job postings for testing
Run this before testing the farmer side
"""
from data_store import DataStore
from datetime import datetime

def create_sample_data():
    store = DataStore()

    # Create a sample farm owner
    owner_phone = "whatsapp:+15555550001"
    store.create_user(owner_phone, 'farm_owner')
    store.update_user(owner_phone, {'registered': True})
    store.update_user_profile(owner_phone, {
        'name': 'Sarah Johnson',
        'farm_name': 'Sunny Acres Farm',
        'location': 'Sacramento, CA'
    })

    # Create sample jobs with new detailed format
    jobs = [
        {
            'work_type': 'Tomato Harvest',
            'workers_needed': 5,
            'work_hours': '6:00 AM - 2:00 PM',
            'payment_type': 'per day',
            'payment_amount': 150.00,
            'location': 'Green Valley Farm, Sacramento, CA',
            'transportation': 'provided',
            'meeting_point': 'Town Square, 5:45 AM pickup',
            'description': 'Pick ripe tomatoes, sort by size. Bring water bottle and sun hat. Lunch break at 10:30 AM.',
            'owner_phone': owner_phone,
            'owner_name': 'Sarah Johnson',
            'farm_name': 'Sunny Acres Farm',
            'hours': 'full-time'  # For matching compatibility
        },
        {
            'work_type': 'Strawberry Picking',
            'workers_needed': 8,
            'work_hours': '5:00 AM - 12:00 PM',
            'payment_type': 'per day',
            'payment_amount': 120.00,
            'location': 'Berry Fields Farm, Davis, CA',
            'transportation': 'provided',
            'meeting_point': 'Main Street Bus Stop, 4:45 AM pickup',
            'description': 'Early morning harvest. Must be gentle with berries. Experience helpful but not required.',
            'owner_phone': owner_phone,
            'owner_name': 'Sarah Johnson',
            'farm_name': 'Sunny Acres Farm',
            'hours': 'part-time'
        },
        {
            'work_type': 'Corn Planting',
            'workers_needed': 4,
            'work_hours': '7:00 AM - 3:00 PM',
            'payment_type': 'per hour',
            'payment_amount': 18.00,
            'location': 'Valley View Farm, Woodland, CA',
            'transportation': 'not provided',
            'meeting_point': 'N/A - Workers arrange own transport',
            'description': 'Plant corn seeds using machinery. Training provided. Must be able to work in heat.',
            'owner_phone': owner_phone,
            'owner_name': 'Sarah Johnson',
            'farm_name': 'Sunny Acres Farm',
            'hours': 'full-time'
        },
        {
            'work_type': 'Lettuce Harvest',
            'workers_needed': 6,
            'work_hours': '6:00 AM - 1:00 PM',
            'payment_type': 'per day',
            'payment_amount': 140.00,
            'location': 'Fresh Fields, West Sacramento, CA',
            'transportation': 'provided',
            'meeting_point': 'Central Park, 5:30 AM sharp',
            'description': 'Cut and pack lettuce. Fast-paced work. Gloves and tools provided.',
            'owner_phone': owner_phone,
            'owner_name': 'Sarah Johnson',
            'farm_name': 'Sunny Acres Farm',
            'hours': 'full-time'
        },
        {
            'work_type': 'Orange Picking',
            'workers_needed': 3,
            'work_hours': '7:00 AM - 2:00 PM',
            'payment_type': 'per task',
            'payment_amount': 25.00,
            'location': 'Citrus Grove, Elk Grove, CA',
            'transportation': 'provided',
            'meeting_point': 'Library parking lot, 6:45 AM',
            'description': '$25 per bin filled. Average workers fill 5-7 bins per day. Picking bags provided.',
            'owner_phone': owner_phone,
            'owner_name': 'Sarah Johnson',
            'farm_name': 'Sunny Acres Farm',
            'hours': 'flexible'
        },
        {
            "work_type": "Tobacco Harvesting",
            "pay_rate": 16.5,
            "location": "Chapel Hill, NC",
            "hours": "full-time",
            "workers_needed": 8,
            "description": "Harvest tobacco leaves. Must be comfortable working in humid conditions. Experience preferred but training provided. Transportation from central Chapel Hill.",
            "owner_phone": "whatsapp:+19195550001",
            "owner_name": "James Wilson",
            "farm_name": "Blue Ridge Farms"
        },
        {
            "work_type": "Sweet Potato Harvesting",
            "pay_rate": 17.0,
            "location": "Durham, NC",
            "hours": "full-time",
            "workers_needed": 6,
            "description": "Harvest sweet potatoes. Heavy lifting required. Paid weekly. Perfect for those with harvesting experience.",
            "owner_phone": "whatsapp:+19195550002",
            "owner_name": "Maria Rodriguez",
            "farm_name": "Carolina Sweet Farms"
        },
        {
            "work_type": "Strawberry Picking",
            "pay_rate": 15.5,
            "location": "Raleigh, NC",
            "hours": "part-time",
            "workers_needed": 10,
            "description": "Pick strawberries during morning hours. Family-friendly environment. Great for students or part-time workers. Piece rate also available.",
            "owner_phone": "whatsapp:+19195550002",
            "owner_name": "Maria Rodriguez",
            "farm_name": "Carolina Sweet Farms"
        },
        {
            "work_type": "Greenhouse Work",
            "pay_rate": 18.0,
            "location": "Carrboro, NC",
            "hours": "full-time",
            "workers_needed": 3,
            "description": "Maintain greenhouse plants, water, transplant seedlings. Climate-controlled environment. Good for year-round work.",
            "owner_phone": "whatsapp:+19195550003",
            "owner_name": "David Chen",
            "farm_name": "Green Leaf Gardens"
        },
        {
            "work_type": "Livestock Care",
            "pay_rate": 19.0,
            "location": "Hillsborough, NC",
            "hours": "flexible",
            "workers_needed": 2,
            "description": "Care for cattle and pigs. Feed animals, clean barns, assist with veterinary care. Early morning start required.",
            "owner_phone": "whatsapp:+19195550003",
            "owner_name": "David Chen",
            "farm_name": "Green Leaf Gardens"
        },
        {
            "work_type": "Organic Vegetable Farming",
            "pay_rate": 20.0,
            "location": "Chapel Hill, NC",
            "hours": "full-time",
            "workers_needed": 4,
            "description": "Work on certified organic farm. Plant, weed, harvest various vegetables. Knowledge of organic methods a plus. Health benefits available.",
            "owner_phone": "whatsapp:+19195550001",
            "owner_name": "James Wilson",
            "farm_name": "Blue Ridge Farms"
        },
        {
            "work_type": "Equipment Maintenance",
            "pay_rate": 22.0,
            "location": "Pittsboro, NC",
            "hours": "full-time",
            "workers_needed": 1,
            "description": "Maintain and repair farm equipment including tractors and harvesters. Mechanical experience required. Higher pay for certified mechanics.",
            "owner_phone": "whatsapp:+19195550004",
            "owner_name": "Robert Taylor",
            "farm_name": "Taylor Agricultural Services"
        },
        {
            "work_type": "Irrigation Specialist",
            "pay_rate": 21.0,
            "location": "Cary, NC",
            "hours": "full-time",
            "workers_needed": 2,
            "description": "Install and maintain drip irrigation systems. Experience with modern irrigation technology preferred. Company truck provided.",
            "owner_phone": "whatsapp:+19195550004",
            "owner_name": "Robert Taylor",
            "farm_name": "Taylor Agricultural Services"
        },
        {
            "work_type": "Blueberry Harvesting",
            "pay_rate": 16.0,
            "location": "Southern Pines, NC",
            "hours": "seasonal",
            "workers_needed": 15,
            "description": "Peak season blueberry harvest. June-August work. Piece rate available for experienced pickers. Housing assistance available for seasonal workers.",
            "owner_phone": "whatsapp:+19195550005",
            "owner_name": "Linda Brown",
            "farm_name": "Piedmont Berry Farm"
        },
        {
            "work_type": "General Farm Labor",
            "pay_rate": 17.5,
            "location": "Chapel Hill, NC",
            "hours": "full-time",
            "workers_needed": 5,
            "description": "Various farm tasks including planting, weeding, harvesting, and maintenance. Good entry-level position. Training provided.",
            "owner_phone": "whatsapp:+19195550001",
            "owner_name": "James Wilson",
            "farm_name": "Blue Ridge Farms"
        }
    ]

    print("Creating sample jobs...\n")

    for job in jobs:
        job_id = store.create_job(job)
        print(f"✅ Created: {job['work_type']} - ${job['pay_rate']}/hr - {job['location']}")
        print(f"   Job ID: {job_id}\n")

    print(f"\n🎉 Sample data created successfully!")
    print(f"📊 Total jobs: {len(jobs)}")
    print(f"👨‍🌾 Farm owner: {owner_phone}")
    print(f"\nYou can now test the farmer side of the chatbot!")

if __name__ == "__main__":
    create_sample_data()
