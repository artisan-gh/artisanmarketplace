# incident_category/migrations/0002_auto_20260719_1557.py
from django.db import migrations, models
from django.utils.text import slugify

def seed_categories(apps, schema_editor):
    IncidentCategory = apps.get_model('incident_category', 'IncidentCategory')
    SubCategory = apps.get_model('incident_category', 'SubCategory')

    data = {
        "Construction & Building": [
            "Mason", "Bricklayer", "Carpenter", "Joiner", "Plumber",
            "Electrician", "Welder", "Steel Bender", "Painter",
            "POP Ceiling Installer", "Tiler", "Roofer",
            "Aluminum Fabricator", "Glass Installer", "Building Contractor",
            "Scaffolder", "Survey Assistant", "Concrete Specialist",
            "Borehole Driller"
        ],
        "Wood & Furniture": [
            "Furniture Maker", "Cabinet Maker", "Upholsterer",
            "Wood Carver", "Interior Wood Finisher", "Door Installer",
            "Window Installer"
        ],
        "Metal Fabrication": [
            "Blacksmith", "Metal Fabricator", "Stainless Steel Fabricator",
            "Gate Maker", "Burglar Proof Installer", "Welding Technician",
            "Metal Door Manufacturer"
        ],
        "Automotive": [
            "Auto Mechanic", "Auto Electrician", "Auto Painter",
            "Auto Sprayer", "Auto Body Repairer", "Tire Technician",
            "Car Air Conditioner Technician", "Engine Specialist",
            "Brake Specialist", "Transmission Specialist",
            "Car Diagnostic Technician", "Vehicle Inspector",
            "Car Detailer", "Car Wash Operator"
        ],
        "Motorcycle & Bicycle": [
            "Motorbike Mechanic", "Bicycle Mechanic", "Bicycle Builder"
        ],
        "Electrical & Electronics": [
            "Solar Panel Installer", "CCTV Installer", "Generator Technician",
            "Electrical Maintenance Technician", "Home Automation Installer",
            "Appliance Repair Technician", "TV Repair Technician",
            "Refrigerator Technician", "Air Conditioner Technician",
            "Microwave Repair Technician", "Washing Machine Technician"
        ],
        "ICT & Digital": [
            "Computer Technician", "Laptop Repair Technician",
            "Phone Repair Technician", "Network Technician",
            "CCTV Engineer", "Software Developer", "Web Developer",
            "Mobile App Developer", "Graphic Designer", "UI/UX Designer",
            "Cybersecurity Technician", "Data Recovery Specialist"
        ],
        "Fashion & Beauty": [
            "Tailor", "Fashion Designer", "Dressmaker",
            "Embroiderer", "Cobbler (Shoemaker)", "Leather Worker",
            "Barber", "Hairdresser", "Makeup Artist", "Nail Technician",
            "Wig Maker", "Tattoo Artist", "Henna Artist"
        ],
        "Home Services": [
            "Cleaner", "Housekeeper", "Pest Control Technician",
            "Laundry Specialist", "Dry Cleaner", "Gardener",
            "Landscaper", "Pool Cleaner", "Home Organizer"
        ],
        "Agriculture": [
            "Tractor Operator", "Irrigation Technician",
            "Poultry Specialist", "Livestock Technician", "Farm Mechanic",
            "Greenhouse Technician", "Beekeeper", "Fisheries Technician"
        ],
        "Water & Sanitation": [
            "Borehole Technician", "Water Pump Installer",
            "Septic Tank Constructor", "Drainage Specialist",
            "Water Treatment Technician"
        ],
        "Energy": [
            "Solar Installer", "Inverter Technician", "Battery Technician",
            "Generator Mechanic", "Wind Turbine Technician"
        ],
        "Interior Decoration": [
            "Interior Designer", "Wallpaper Installer", "POP Designer",
            "Curtain Installer", "Blind Installer", "Floor Installer",
            "Vinyl Flooring Installer", "Carpet Installer"
        ],
        "Security": [
            "Locksmith", "Safe Installer", "CCTV Installer",
            "Security Fence Installer", "Electric Fence Installer",
            "Access Control Installer"
        ],
        "Printing & Branding": [
            "Sign Writer", "Screen Printer", "Digital Printer",
            "Engraving Specialist", "Sticker Installer", "Billboard Installer"
        ],
        "Arts & Crafts": [
            "Sculptor", "Painter (Artist)", "Potter", "Basket Weaver",
            "Bead Maker", "Goldsmith", "Silversmith", "Jewelry Maker",
            "Leather Craftsman"
        ],
        "Food & Catering": [
            "Caterer", "Baker", "Pastry Chef", "Event Cook",
            "Cake Designer", "Barbecue Specialist"
        ],
        "Events": [
            "Decorator", "Event Planner", "Florist", "Photographer",
            "Videographer", "DJ", "Sound Engineer", "Lighting Technician",
            "Master of Ceremonies (MC)"
        ],
        "Logistics": [
            "Mover", "Furniture Installer", "Delivery Rider",
            "Courier", "Packing Specialist"
        ],
        "Marine": [
            "Boat Builder", "Outboard Motor Mechanic",
            "Fisherman Equipment Repairer"
        ],
        "Mining & Industrial": [
            "Heavy Equipment Mechanic", "Industrial Electrician",
            "Industrial Welder", "Industrial Plumber", "Machine Operator"
        ],
        "Cleaning & Restoration": [
            "Carpet Cleaner", "Sofa Cleaner", "Mattress Cleaner",
            "Pressure Washing Technician", "Fire Damage Restoration Technician",
            "Flood Restoration Technician"
        ],
        "Healthcare Support": [
            "Wheelchair Repair Technician", "Medical Equipment Technician",
            "Orthopedic Appliance Technician"
        ],
        "Miscellaneous Skilled Trades": [
            "Clock Repairer", "Watch Repair Technician",
            "Musical Instrument Repairer", "Piano Technician",
            "Toy Repair Specialist", "Umbrella Repairer"
        ],
    }

    for cat_name, sub_names in data.items():
        # ─── Create category with unique code ──────────────────
        base_code = slugify(cat_name)[:50]
        code = base_code
        counter = 1
        while IncidentCategory.objects.filter(code=code).exists():
            code = f"{base_code}-{counter}"
            counter += 1
        cat, created = IncidentCategory.objects.get_or_create(
            name=cat_name,
            defaults={
                "code": code,
                "is_active": True
            }
        )

        # ─── Create subcategories with unique codes ────────────
        for sub_name in sub_names:
            base_sub_code = slugify(sub_name)[:50]
            sub_code = base_sub_code
            counter_sub = 1
            while SubCategory.objects.filter(code=sub_code).exists():
                sub_code = f"{base_sub_code}-{counter_sub}"
                counter_sub += 1
            SubCategory.objects.get_or_create(
                category=cat,
                name=sub_name,
                defaults={
                    "code": sub_code,
                    "is_active": True
                }
            )

def reverse_seed(apps, schema_editor):
    IncidentCategory = apps.get_model('incident_category', 'IncidentCategory')
    IncidentCategory.objects.all().delete()

class Migration(migrations.Migration):

    dependencies = [
        ('incident_category', '0001_initial'),
    ]

    operations = [
        migrations.RunPython(seed_categories, reverse_seed),
    ]
