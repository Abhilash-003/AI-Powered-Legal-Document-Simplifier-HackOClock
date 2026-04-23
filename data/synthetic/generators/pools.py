"""Shared variation pools for Indian legal clause generation.

Every pool is curated to keep register authentic: Pvt Ltd/LLP/sole prop
suffixes, Indian cities with locality granularity, Rs./₹/INR amounts,
and statute-appropriate phrasings.
"""
import random

# ---------------- Parties / Entities ----------------
COMPANY_PREFIXES = [
    "Indigo", "Rudra", "Vistara", "Saraswati", "Arya", "Bharat", "Shakti",
    "Tatva", "Prayag", "Niyama", "Aarogya", "Infotrend", "Infotera", "Cogito",
    "Vaayu", "Navya", "Surabhi", "Matrix", "Lotus", "Spectra", "Azuro",
    "Mahindra", "Godavari", "Kaveri", "Shree", "Trilok", "Anantara",
    "Meridian", "Polaris", "Kinara", "Rithika", "Chandra", "Harsha",
    "Aditi", "Dhruv", "Yuvika", "Brahmastra", "Himalaya", "Ganga",
    "Prakriti", "Yojana", "Udaan", "Kusuma", "Samskara", "Vidya", "Samarth",
    "Antariksh", "Kairos", "Veda", "Moksha", "Pratham", "Neelkanth",
    "Ashirvad", "Srinivasa", "Virat", "Apoorva", "Srijan", "Bhagwati",
    "Chola", "Maurya", "Vikramaditya", "Kumbha", "Aaradhya", "Hemant",
    "Siddhi", "Pragati", "Agastya", "Vishwakarma", "Shubham", "Navdeep",
]

COMPANY_SUFFIXES = [
    "Technologies Pvt. Ltd.", "Systems Pvt. Ltd.", "Industries Pvt. Ltd.",
    "Solutions Pvt. Ltd.", "Ventures LLP", "Enterprises Pvt. Ltd.",
    "Pharmaceuticals Pvt. Ltd.", "Retail Pvt. Ltd.", "Infotech Pvt. Ltd.",
    "Labs Pvt. Ltd.", "Media Pvt. Ltd.", "Finserv LLP",
    "Logistics Pvt. Ltd.", "Engineering Pvt. Ltd.", "Foods Pvt. Ltd.",
    "Biosciences Pvt. Ltd.", "Consulting LLP", "Realty Pvt. Ltd.",
    "Analytics Pvt. Ltd.", "Mobility Pvt. Ltd.", "Edutech Pvt. Ltd.",
    "Insurance Brokers Pvt. Ltd.", "Capital Advisors LLP",
    "Manufacturing Pvt. Ltd.", "Chemicals Pvt. Ltd.", "BPO Services Pvt. Ltd.",
    "Global Pvt. Ltd.", "India Limited", "India Pvt. Ltd.",
    "Digital Pvt. Ltd.", "Networks Pvt. Ltd.", "Studios Pvt. Ltd.",
]

# Used where sole proprietorship is authentic
M_AND_S_PREFIXES = ["M/s ", "Messrs. "]

# Individual names for Employee/Consultant/Landlord/Tenant roles
FIRST_NAMES_M = [
    "Rajesh", "Amit", "Vikram", "Arjun", "Karan", "Nikhil", "Sandeep",
    "Pradeep", "Manish", "Rohit", "Suresh", "Ajay", "Ravi", "Sanjay",
    "Ramesh", "Prashant", "Anil", "Harish", "Gautam", "Siddharth",
    "Aditya", "Akash", "Anirudh", "Kabir", "Ishaan", "Rahul", "Varun",
    "Deepak", "Vivek", "Shubham", "Yogesh", "Jignesh", "Paresh",
    "Mukesh", "Lalit", "Venkatesh", "Arnav", "Dhruv", "Kunal",
]
FIRST_NAMES_F = [
    "Priya", "Ananya", "Kavita", "Shruti", "Meena", "Pooja", "Nisha",
    "Riya", "Sonal", "Neha", "Divya", "Smita", "Preeti", "Anjali",
    "Swati", "Deepa", "Vidya", "Lakshmi", "Sunita", "Rekha", "Madhuri",
    "Aarti", "Gauri", "Kirti", "Shruthi", "Tanvi", "Isha", "Rhea",
    "Aishwarya", "Radhika", "Sonia", "Megha", "Sneha", "Shalini",
]
LAST_NAMES = [
    "Sharma", "Verma", "Gupta", "Agarwal", "Iyer", "Menon", "Patel",
    "Shah", "Desai", "Nair", "Reddy", "Naidu", "Pillai", "Bose", "Das",
    "Banerjee", "Mukherjee", "Chatterjee", "Kapoor", "Malhotra", "Joshi",
    "Bhatt", "Pandey", "Mishra", "Kulkarni", "Deshpande", "Rao",
    "Srinivasan", "Subramanian", "Ramachandran", "Khan", "Sheikh",
    "Singh", "Chauhan", "Yadav", "Thakur", "Jain", "Mehta", "Chopra",
    "Bhagat", "Sengupta", "Ghosh", "Pillay", "Krishnan", "Vaidya",
]

def person_name(gender=None):
    pool_m = FIRST_NAMES_M
    pool_f = FIRST_NAMES_F
    if gender is None:
        fn = random.choice(pool_m + pool_f)
    elif gender == "m":
        fn = random.choice(pool_m)
    else:
        fn = random.choice(pool_f)
    return f"{fn} {random.choice(LAST_NAMES)}"

def company_name(short=False):
    base = random.choice(COMPANY_PREFIXES)
    if short:
        return base
    return base + " " + random.choice(COMPANY_SUFFIXES)

def sole_prop():
    return random.choice(M_AND_S_PREFIXES) + random.choice(COMPANY_PREFIXES) + " " + random.choice([
        "Traders", "Enterprises", "Agencies", "Textiles", "Metals",
        "Printing Press", "Stores", "Hardware", "Associates",
    ])

# ---------------- Cities / Localities ----------------
CITY_LOCALITIES = {
    "Mumbai": ["Bandra (West)", "Andheri (East)", "Andheri (West)", "Lower Parel",
               "Powai", "Juhu", "Malad", "Goregaon (East)", "Vikhroli",
               "Worli", "Thane", "Navi Mumbai", "Kharghar", "Chembur"],
    "Bengaluru": ["Koramangala", "Whitefield", "Indiranagar", "HSR Layout",
                  "Electronic City", "Marathahalli", "Jayanagar", "JP Nagar",
                  "Bellandur", "Sarjapur Road", "Hebbal", "Malleshwaram"],
    "Delhi": ["Connaught Place", "Nehru Place", "Saket", "Defence Colony",
              "Greater Kailash", "Rajouri Garden", "Dwarka", "Rohini",
              "Pitampura", "Lajpat Nagar", "Karol Bagh", "Okhla"],
    "Gurugram": ["Sector 44", "Sector 29", "Golf Course Road", "Cyber City",
                 "Udyog Vihar", "Sohna Road", "MG Road", "Sector 54"],
    "Noida": ["Sector 62", "Sector 16", "Sector 125", "Sector 18",
              "Sector 135", "Sector 2", "Greater Noida"],
    "Pune": ["Hinjewadi", "Kharadi", "Viman Nagar", "Baner", "Aundh",
             "Hadapsar", "Magarpatta", "Koregaon Park", "Shivaji Nagar",
             "Kothrud", "Wakad", "Balewadi"],
    "Hyderabad": ["HITEC City", "Gachibowli", "Banjara Hills", "Jubilee Hills",
                  "Madhapur", "Kondapur", "Begumpet", "Secunderabad",
                  "Kukatpally", "Manikonda"],
    "Chennai": ["T. Nagar", "Nungambakkam", "Velachery", "OMR",
                "Guindy", "Thiruvanmiyur", "Adyar", "Anna Nagar",
                "Tambaram", "Porur"],
    "Kolkata": ["Salt Lake Sector V", "Park Street", "Ballygunge",
                "Alipore", "New Town", "Howrah", "Rajarhat"],
    "Ahmedabad": ["Navrangpura", "SG Highway", "Bodakdev", "Prahlad Nagar",
                  "Satellite", "Bopal", "Gota"],
    "Jaipur": ["Malviya Nagar", "C-Scheme", "Vaishali Nagar", "Mansarovar",
               "Sitapura", "Jhotwara"],
    "Kochi": ["Kakkanad", "Infopark", "Kaloor", "Edappally", "Vyttila"],
    "Chandigarh": ["Sector 17", "Sector 22", "Sector 34", "IT Park Panchkula"],
    "Indore": ["Vijay Nagar", "Palasia", "AB Road", "Scheme No. 78"],
    "Coimbatore": ["RS Puram", "Peelamedu", "Saravanampatti", "Avinashi Road"],
    "Lucknow": ["Hazratganj", "Gomti Nagar", "Aliganj", "Alambagh"],
    "Bhubaneswar": ["Patia", "Saheed Nagar", "Infocity"],
    "Visakhapatnam": ["Madhurawada", "MVP Colony", "Dwaraka Nagar"],
}

def city_and_locality():
    city = random.choice(list(CITY_LOCALITIES.keys()))
    loc = random.choice(CITY_LOCALITIES[city])
    return loc, city

CITY_TO_STATE = {
    "Mumbai": "Maharashtra", "Pune": "Maharashtra",
    "Bengaluru": "Karnataka", "Mangaluru": "Karnataka",
    "Delhi": "NCT of Delhi", "Gurugram": "Haryana",
    "Noida": "Uttar Pradesh", "Lucknow": "Uttar Pradesh",
    "Hyderabad": "Telangana", "Visakhapatnam": "Andhra Pradesh",
    "Chennai": "Tamil Nadu", "Coimbatore": "Tamil Nadu",
    "Kolkata": "West Bengal", "Ahmedabad": "Gujarat",
    "Jaipur": "Rajasthan", "Kochi": "Kerala",
    "Chandigarh": "Chandigarh", "Indore": "Madhya Pradesh",
    "Bhubaneswar": "Odisha",
}

# State rent control acts (for rent_escalation and eviction)
STATE_RCA = {
    "Mumbai": "Maharashtra Rent Control Act, 1999",
    "Pune": "Maharashtra Rent Control Act, 1999",
    "Delhi": "Delhi Rent Act, 1995",
    "Gurugram": "Haryana Urban (Control of Rent and Eviction) Act, 1973",
    "Noida": "Uttar Pradesh Regulation of Urban Premises Tenancy Act, 2021",
    "Lucknow": "Uttar Pradesh Regulation of Urban Premises Tenancy Act, 2021",
    "Bengaluru": "Karnataka Rent Act, 1999",
    "Hyderabad": "Telangana Buildings (Lease, Rent and Eviction) Control Act, 1960",
    "Chennai": "Tamil Nadu Regulation of Rights and Responsibilities of Landlords and Tenants Act, 2017",
    "Coimbatore": "Tamil Nadu Regulation of Rights and Responsibilities of Landlords and Tenants Act, 2017",
    "Kolkata": "West Bengal Premises Tenancy Act, 1997",
    "Ahmedabad": "Gujarat Rent Control Act, 2011",
    "Jaipur": "Rajasthan Rent Control Act, 2001",
    "Kochi": "Kerala Buildings (Lease and Rent Control) Act, 1965",
    "Chandigarh": "East Punjab Urban Rent Restriction Act, 1949",
    "Indore": "Madhya Pradesh Accommodation Control Act, 1961",
    "Bhubaneswar": "Orissa House Rent Control Act, 1967",
    "Visakhapatnam": "Andhra Pradesh Buildings (Lease, Rent and Eviction) Control Act, 1960",
}

# Shops & Establishments acts (for probation / notice_period)
STATE_SE = {
    "Maharashtra": "Maharashtra Shops and Establishments (Regulation of Employment and Conditions of Service) Act, 2017",
    "Karnataka": "Karnataka Shops and Commercial Establishments Act, 1961",
    "NCT of Delhi": "Delhi Shops and Establishments Act, 1954",
    "Haryana": "Punjab Shops and Commercial Establishments Act, 1958 (as applicable to Haryana)",
    "Uttar Pradesh": "Uttar Pradesh Dookan Aur Vanijya Adhishthan Adhiniyam, 1962",
    "Telangana": "Telangana Shops and Establishments Act, 1988",
    "Andhra Pradesh": "Andhra Pradesh Shops and Establishments Act, 1988",
    "Tamil Nadu": "Tamil Nadu Shops and Establishments Act, 1947",
    "West Bengal": "West Bengal Shops and Establishments Act, 1963",
    "Gujarat": "Gujarat Shops and Establishments (Regulation of Employment and Conditions of Service) Act, 2019",
    "Rajasthan": "Rajasthan Shops and Commercial Establishments Act, 1958",
    "Kerala": "Kerala Shops and Commercial Establishments Act, 1960",
    "Chandigarh": "Punjab Shops and Commercial Establishments Act, 1958 (as extended to Chandigarh)",
    "Madhya Pradesh": "Madhya Pradesh Shops and Establishments Act, 1958",
    "Odisha": "Odisha Shops and Commercial Establishments Act, 1956",
}

# ---------------- Industries / roles ----------------
INDUSTRIES = [
    ("information technology services", "software engineer"),
    ("information technology services", "senior software engineer"),
    ("information technology services", "technical architect"),
    ("information technology services", "DevOps engineer"),
    ("SaaS product development", "product manager"),
    ("SaaS product development", "engineering manager"),
    ("fintech", "risk analyst"),
    ("fintech", "full-stack developer"),
    ("fintech", "compliance officer"),
    ("banking and financial services", "relationship manager"),
    ("banking and financial services", "credit analyst"),
    ("pharmaceuticals", "research associate"),
    ("pharmaceuticals", "medical representative"),
    ("pharmaceuticals", "formulation scientist"),
    ("pharmaceuticals", "regulatory affairs manager"),
    ("pharmaceuticals", "quality assurance officer"),
    ("manufacturing", "production supervisor"),
    ("manufacturing", "quality control inspector"),
    ("manufacturing", "plant maintenance engineer"),
    ("automobile manufacturing", "design engineer"),
    ("FMCG", "area sales manager"),
    ("FMCG", "brand manager"),
    ("FMCG", "supply chain executive"),
    ("retail", "store manager"),
    ("retail", "visual merchandiser"),
    ("legal services", "associate advocate"),
    ("legal services", "senior associate"),
    ("consultancy", "management consultant"),
    ("consultancy", "partner"),
    ("EdTech", "content developer"),
    ("EdTech", "customer success manager"),
    ("real estate", "sales manager"),
    ("real estate", "project manager"),
    ("BPO/KPO", "process associate"),
    ("BPO/KPO", "team lead"),
    ("media and entertainment", "content producer"),
    ("media and entertainment", "senior journalist"),
    ("e-commerce", "category manager"),
    ("e-commerce", "operations manager"),
    ("healthcare", "hospital administrator"),
    ("healthcare", "nursing supervisor"),
    ("logistics", "warehouse manager"),
    ("logistics", "last-mile operations lead"),
    ("telecommunications", "network engineer"),
    ("insurance", "underwriting manager"),
    ("insurance", "claims adjudicator"),
    ("biotechnology", "bioinformatics analyst"),
    ("chemicals", "process engineer"),
    ("renewable energy", "project developer"),
    ("hospitality", "front-office manager"),
]

# ---------------- Numerical helpers ----------------
def inr_amount_lakhs(low=2, high=120):
    """Return formatted INR string for salary-like figures."""
    lakhs = random.randint(low, high)
    if random.random() < 0.3:
        return f"₹{lakhs * 100000:,}/- per annum"
    if random.random() < 0.5:
        return f"Rs. {lakhs * 100000:,}/- per annum"
    return f"INR {lakhs},00,000/- per annum"

def inr_monthly(low=15, high=250):
    """Monthly figures in thousands — rent, salary. Returns Rs. X,000/-."""
    k = random.randint(low, high)
    amt = k * 1000
    fmt = random.choice([
        f"Rs. {amt:,}/- per month",
        f"₹{amt:,}/- per month",
        f"INR {amt:,} per month",
    ])
    return fmt

def inr_monthly_rent():
    """Indian-formatted monthly rent figures."""
    options = [
        random.randint(12, 200) * 1000,    # flats
        random.randint(40, 600) * 1000,    # commercial
    ]
    amt = random.choice(options)
    def words(n):
        # rough word form for common values
        lakhs = n // 100000
        thousands = (n % 100000) // 1000
        parts = []
        if lakhs:
            parts.append(f"{lakhs} Lakh")
        if thousands:
            parts.append(f"{thousands} Thousand")
        return " ".join(parts) if parts else "Nil"
    return f"Rs. {amt:,}/- (Rupees {words(amt)} only)"

def pct(low, high):
    return random.randint(low, high)

def months_word(n):
    w = {1:"one",2:"two",3:"three",4:"four",5:"five",6:"six",7:"seven",
         8:"eight",9:"nine",10:"ten",11:"eleven",12:"twelve",
         15:"fifteen",18:"eighteen",24:"twenty-four",36:"thirty-six"}
    return w.get(n, str(n))

def days_word(n):
    w = {3:"three",5:"five",7:"seven",10:"ten",14:"fourteen",15:"fifteen",
         21:"twenty-one",30:"thirty",45:"forty-five",60:"sixty",
         90:"ninety",120:"one hundred and twenty",180:"one hundred and eighty"}
    return w.get(n, str(n))

# ---------------- Doc / agreement framing ----------------
EMPLOYMENT_DOCS = ["employment contract", "appointment letter",
                   "service agreement", "offer-cum-appointment letter"]
COMMERCIAL_DOCS = ["services agreement", "master services agreement",
                   "commercial contract", "consultancy agreement",
                   "supply agreement", "distribution agreement"]
REAL_ESTATE_DOCS = ["lease deed", "leave and license agreement",
                    "rental agreement", "commercial lease deed"]

# ---------------- Role labels ----------------
def employer_role():
    return random.choice(["the Employer", "the Company"])

def employee_role():
    return random.choice(["the Employee", "the said Employee"])

def consultant_role():
    return random.choice(["the Consultant", "the said Consultant"])

def lessor():
    return random.choice(["the Lessor", "the Landlord", "the Licensor"])

def lessee():
    return random.choice(["the Lessee", "the Tenant", "the Licensee"])
