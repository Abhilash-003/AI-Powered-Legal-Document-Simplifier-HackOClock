"""Rent escalation top-up — State RCA + TPA 1882. +560 rows."""
import json, random, hashlib, os, sys
sys.path.insert(0, os.path.dirname(__file__))

CLAUSE_TYPE = "rent_escalation"
SOURCE = "synth_v2"
INDIAN_LAW_BASE = "State Rent Control Act; Transfer of Property Act 1882"

CITY_LOCALITIES = {
    "Mumbai": ("Maharashtra Rent Control Act, 1999", ["Bandra (West)","Andheri (East)","Powai","Lower Parel","Juhu","Worli","Malad","Goregaon (East)","Thane","Vikhroli","Navi Mumbai","Kharghar"]),
    "Pune": ("Maharashtra Rent Control Act, 1999", ["Hinjewadi","Kharadi","Viman Nagar","Baner","Hadapsar","Koregaon Park","Shivaji Nagar","Kothrud"]),
    "Delhi": ("Delhi Rent Act, 1995", ["Connaught Place","Saket","Defence Colony","Greater Kailash","Dwarka","Lajpat Nagar","Rajouri Garden","Karol Bagh","Okhla"]),
    "Gurugram": ("Haryana Urban (Control of Rent and Eviction) Act, 1973", ["Sector 44","Sector 29","Golf Course Road","Cyber City","Udyog Vihar","Sohna Road"]),
    "Noida": ("Uttar Pradesh Regulation of Urban Premises Tenancy Act, 2021", ["Sector 62","Sector 16","Sector 125","Sector 18","Sector 135","Greater Noida"]),
    "Bengaluru": ("Karnataka Rent Act, 1999", ["Koramangala","Whitefield","Indiranagar","HSR Layout","Electronic City","Marathahalli","Jayanagar","JP Nagar","Bellandur","Sarjapur Road","Hebbal"]),
    "Hyderabad": ("Telangana Buildings (Lease, Rent and Eviction) Control Act, 1960", ["HITEC City","Gachibowli","Banjara Hills","Jubilee Hills","Madhapur","Kondapur","Begumpet","Kukatpally"]),
    "Chennai": ("Tamil Nadu Regulation of Rights and Responsibilities of Landlords and Tenants Act, 2017", ["T. Nagar","Nungambakkam","Velachery","OMR","Guindy","Adyar","Anna Nagar"]),
    "Kolkata": ("West Bengal Premises Tenancy Act, 1997", ["Salt Lake Sector V","Park Street","Ballygunge","Alipore","New Town","Rajarhat"]),
    "Ahmedabad": ("Gujarat Rent Control Act, 2011", ["Navrangpura","SG Highway","Bodakdev","Prahlad Nagar","Satellite","Bopal"]),
    "Jaipur": ("Rajasthan Rent Control Act, 2001", ["Malviya Nagar","C-Scheme","Vaishali Nagar","Mansarovar","Sitapura"]),
    "Kochi": ("Kerala Buildings (Lease and Rent Control) Act, 1965", ["Kakkanad","Infopark","Kaloor","Edappally","Vyttila"]),
    "Chandigarh": ("East Punjab Urban Rent Restriction Act, 1949", ["Sector 17","Sector 22","Sector 34","IT Park Panchkula"]),
    "Indore": ("Madhya Pradesh Accommodation Control Act, 1961", ["Vijay Nagar","Palasia","AB Road","Scheme No. 78"]),
    "Coimbatore": ("Tamil Nadu Regulation of Rights and Responsibilities of Landlords and Tenants Act, 2017", ["RS Puram","Peelamedu","Saravanampatti","Avinashi Road"]),
}

STD_OPEN = [
    "It is hereby agreed that the monthly rent of {rent} reserved in respect of the said premises situated at {locality}, {city}, shall stand enhanced by {pct}% on each anniversary of the commencement date of this {doc}.",
    "The Licensee covenants with the Licensor to pay the monthly licence fee of {rent} in respect of the said premises at {locality}, {city}, for the first twelve (12) months of the term hereby created, and thereafter the licence fee shall be increased by {pct}% compounded annually.",
    "The parties hereto have mutually agreed that the monthly rent of {rent} payable by the Lessee in respect of the said premises at {locality}, {city}, shall be revised upwards by {pct}% at the end of every completed year of tenancy.",
    "The rent reserved under this {doc} shall be subject to an annual escalation of {pct}% on the rent of the immediately preceding twelve-month period, subject to the ceiling prescribed under the {rca}.",
    "The monthly rent of {rent} in respect of the said premises at {locality}, {city}, shall be enhanced by five per cent (5%) in the second year of the tenancy and by an additional seven per cent (7%) in the third year of the tenancy, on a compounded basis.",
    "In consideration of the extended term of this {doc}, the parties have agreed to a rent escalation of {pct}% per annum, subject to applicable Rent Control Legislation, and the Lessee shall pay the enhanced rent without objection on the due date.",
    "Rent shall escalate annually by {pct}% on the first anniversary of the commencement of this lease and each subsequent anniversary thereafter, in line with market practice for commercial premises in {city}.",
]

STD_CORE = [
    " Such enhancement shall apply strictly to the base rent of the immediately preceding twelve-month period and shall in no event exceed the ceiling prescribed under the {rca}.",
    " The Lessee shall continue to pay the enhanced rent on or before the {dd}th day of every succeeding calendar month by way of NEFT/RTGS to the bank account of the Lessor notified in writing, and receipt of such payment shall be duly issued.",
    " No revision shall be effected without prior written intimation of thirty (30) days to the Lessee, and the Lessor shall furnish the Lessee with a revised rent schedule forming part of this {doc}.",
    " The Lessee shall be entitled to raise objection to any proposed escalation that exceeds the statutory cap under the {rca}, and the parties shall in good faith amend the escalation to bring the same within the statutory limit.",
    " The provisions of Section 108(j) of the Transfer of Property Act, 1882 shall apply to the payment of enhanced rent, and the Lessee's obligation to pay the said rent on the due date shall be a substantive condition of tenancy.",
    " Where the escalation for any year has not been effected by the Lessor within ninety (90) days of the anniversary date, the right to claim the escalation for that year shall be deemed waived.",
]

STD_CLOSE = [
    " Any further enhancement beyond the initial eleven-month term shall be effected only by mutual written consent of both parties, and shall be recorded in a supplemental agreement duly executed and registered, if required.",
    " The parties record that the escalation contemplated herein is in the nature of a pre-estimated rent adjustment and shall not be treated as a variation of the essential terms of the tenancy.",
    " This clause shall be read in conjunction with the provisions of the {rca} and the Transfer of Property Act, 1882, and any inconsistency shall be resolved in favour of the statutory provision.",
    " The Lessee shall be entitled to deduct any amount spent on authorised repairs from the escalated rent, subject to the limits prescribed under Section 108(f) of the Transfer of Property Act, 1882.",
    " The escalation schedule agreed herein shall operate for the duration of the initial term, and any renewal or extension shall be on such fresh terms as the parties may mutually agree.",
]

AGG_OPEN = [
    "The Lessor reserves the unilateral right to revise the monthly rent of {rent} in respect of the said premises at {locality}, {city}, by up to {pct}% per annum at the Lessor's sole discretion, by serving thirty (30) days' written notice to the Lessee.",
    "Notwithstanding the cap under the {rca}, the monthly rent of {rent} shall stand enhanced by {pct}% compounded annually throughout the term of this {doc}, and the Lessee waives the right to challenge such escalation.",
    "The parties agree to a mid-tenancy unilateral revision of the monthly rent of {rent} by the Lessor, up to twenty per cent (20%) of the base rent, by a written notice of sixty (60) days served on the Lessee in respect of the said premises at {locality}, {city}.",
    "The monthly rent of {rent} shall be revised annually by a percentage equal to the higher of (a) {pct}% per annum, or (b) the percentage increase in the rental value of comparable premises in {locality} as determined solely by a valuer nominated by the Lessor.",
    "The parties have agreed that the rent of {rent} shall stand revised to the 'prevailing market rate' at each anniversary of the commencement date, as solely assessed by the Lessor's internal valuation team at {city}.",
    "In addition to the annual escalation of {pct}%, the Lessee shall pay a 'market alignment charge' equivalent to three months' rent every three (3) years, which charge is non-refundable and non-adjustable against security deposit.",
    "The Lessor may, in the event of any adverse variation in the prevailing market rent, serve a thirty (30) day notice for upward revision of rent, and the Lessee shall have no right to terminate the tenancy in lieu of accepting the revision.",
]

AGG_CORE = [
    " Any delay by the Lessee in paying the escalated rent shall attract compound interest at twenty-four per cent (24%) per annum, which shall be compounded monthly and shall be recoverable as a debt due from the Lessee.",
    " The Lessee shall not be entitled to seek redressal before the Rent Controller, Rent Court or Small Causes Court in respect of any escalation effected under this {doc}, and waives such forum for dispute resolution.",
    " The Lessor shall be entitled to deduct the unpaid portion of the escalated rent from the security deposit, and the security deposit shall thereafter be replenished by the Lessee within seven (7) days on written demand.",
    " The Lessor's determination of the applicable escalation, including any market alignment charge, shall be final and binding on the Lessee, and shall not be re-opened in any proceeding before any forum.",
    " Any failure by the Lessee to pay the escalated rent within ten (10) days of the due date shall constitute an event of default entitling the Lessor to terminate the tenancy on seven (7) days' notice.",
]

AGG_CLOSE = [
    " The Lessee waives any claim that the escalation under this clause exceeds the ceiling under the {rca}, and accepts that the enhanced rent is a reasonable and fair reflection of the market conditions at {city}.",
    " The Lessee acknowledges that the aggressive escalation structure is consideration for the use and occupation of prime commercial space at {locality}, {city}, and shall not be re-opened or renegotiated.",
    " Nothing in this clause shall entitle the Lessee to abatement of rent on account of any circumstance, including force majeure, temporary loss of use or government-imposed lockdown, save to the extent expressly covered by statute.",
    " The Lessor shall have a first charge on the Lessee's moveable assets within the premises for the unpaid portion of the escalated rent, exercisable without the necessity of a court order.",
    " Any increase in applicable tax, statutory levy, maintenance charge or municipal impost shall be passed through to the Lessee in addition to the escalation contemplated herein.",
]

ILL_OPEN = [
    "The monthly rent of {rent} in respect of the said premises at {locality}, {city}, shall be enhanced by thirty-five per cent (35%) on each anniversary of the commencement date, notwithstanding the ceiling of {pct}% per annum prescribed under the {rca} applicable to the premises.",
    "The Lessor reserves the absolute right to revise the monthly rent at any time during the term of this {doc}, at the Lessor's sole discretion, by service of a notice of seven (7) days, and the Lessee hereby waives the protection of the {rca}.",
    "The parties hereby contract out of the ceiling on rent enhancement prescribed by the {rca}, and the Lessor shall be entitled to revise the monthly rent of {rent} by a sum equal to thirty per cent (30%) per annum compounded, effective from each anniversary of this {doc}.",
    "The Lessee undertakes to pay a non-refundable 'premium' of three (3) months' rent at the commencement of each calendar year of tenancy, in addition to the annual escalation of forty per cent (40%), and waives any protection under the {rca}.",
    "The rent reserved under this {doc} shall be revised bi-annually by twenty per cent (20%), and the Lessee acknowledges and accepts that such revision, though contrary to the {rca}, shall bind the Lessee as a permanent condition of tenancy.",
    "The parties have agreed that the Lessor shall not be bound by any statutory cap on rent enhancement, and shall enjoy complete discretion to revise the rent of {rent} as and when the Lessor considers appropriate.",
    "The Lessee hereby waives all protections and remedies under the {rca}, including the right to standard rent, fair rent and statutory ceiling on escalation, and accepts the rent structure prescribed herein as binding.",
]

ILL_CORE = [
    " The Lessee shall not be entitled to approach the Rent Controller, the Small Causes Court or the High Court at {city} for a declaration that the escalated rent is contrary to the {rca}, and such recourse is expressly waived.",
    " Any statutory cap on rent enhancement under the {rca} shall be deemed inapplicable to the said premises, and the parties have specifically contracted out of such statutory protection.",
    " The Lessor's determination of the revised rent shall be final and binding, and the Lessee shall not be entitled to invoke the standard rent provisions of the {rca} or any other Rent Control Legislation.",
    " The Lessee's acceptance of escalated rent above the statutory cap shall not be treated as a breach of the {rca}, and the parties shall not refer the matter to any Rent Court, Civil Court or Consumer Forum.",
    " Notwithstanding Section 108(j) of the Transfer of Property Act, 1882, the Lessee's obligation to pay the escalated rent shall be enforceable on demand, and failure to pay shall constitute a material breach giving rise to eviction without statutory notice.",
]

ILL_CLOSE = [
    " The Lessee shall indemnify the Lessor against any action initiated by any statutory authority alleging breach of the {rca}, and shall bear all costs incurred by the Lessor in defending such action.",
    " This clause shall bind the Lessee notwithstanding any amendment to the {rca} that may increase the Lessee's statutory protection in the future, and the Lessee shall not be entitled to claim the benefit of any such amendment.",
    " The Lessor shall be entitled to enforce the escalated rent by self-help, including re-entry on the said premises without judicial process, if the Lessee fails to pay the enhanced amount.",
    " The waiver of statutory protection contained herein is given as a condition precedent to the grant of tenancy, and the Lessee shall not be heard to argue otherwise in any proceeding before any forum.",
    " The Lessee's heirs, executors, administrators, legal representatives and assigns shall be equally bound by this waiver, and the waiver shall survive the determination of the tenancy.",
]

DOCS = ["lease deed","leave and license agreement","rental agreement","commercial lease deed","commercial rental agreement"]

def _subs(r):
    city = r.choice(list(CITY_LOCALITIES.keys()))
    rca, locs = CITY_LOCALITIES[city]
    loc = r.choice(locs)
    rent_k = r.choice([18, 22, 28, 35, 42, 48, 55, 62, 75, 88, 110, 135, 160, 210, 280, 350, 500, 750])
    rent_amt = rent_k * 1000
    def words(n):
        lakhs = n // 100000
        thousands = (n % 100000) // 1000
        parts = []
        if lakhs: parts.append(f"{lakhs} Lakh")
        if thousands: parts.append(f"{thousands} Thousand")
        return " ".join(parts) if parts else "Nil"
    rent_str = f"Rs. {rent_amt:,}/- (Rupees {words(rent_amt)} only)"
    return {
        "rent": rent_str,
        "locality": loc,
        "city": city,
        "rca": rca,
        "pct": r.choice([5, 6, 7, 8, 10]),
        "dd": r.choice([5, 7, 10, 15]),
    }

def _doc_picker(i):
    random.seed(i*83+5); return random.choice(DOCS)

def _indian_law(city_rca):
    """Individual indian_law per row using the RCA of the city."""
    return f"{city_rca}; Transfer of Property Act 1882"

# We need per-row indian_law override — extend compose
def run_generate_perrow(plan, out_path):
    from common import compose, dedupe_emit
    out, seen = [], set()
    for (risk, n, opens, cores, closes, subs_fn, doc_picker) in plan:
        i, tries = 0, 0
        while sum(1 for r in out if r["risk_level"]==risk) < n:
            i += 1; tries += 1
            doc = doc_picker(i)
            # force subs generation to extract RCA name
            rr = random.Random(i * 53 + 7)
            subs = subs_fn(rr)
            body = compose(opens, cores, closes, i, subs_fn=lambda r: subs, doc=doc)
            indian_law = _indian_law(subs["rca"])
            dedupe_emit(out, body, risk, CLAUSE_TYPE, indian_law, doc, SOURCE, seen)
            if tries > 80000: break
    with open(out_path, "a") as f:
        for r in out:
            f.write(json.dumps(r, ensure_ascii=False) + "\n")
    return out

if __name__ == "__main__":
    target = sys.argv[1] if len(sys.argv) > 1 else "/tmp/re.jsonl"
    plan = [
        ("standard",252,STD_OPEN,STD_CORE,STD_CLOSE,_subs,_doc_picker),
        ("aggressive",196,AGG_OPEN,AGG_CORE,AGG_CLOSE,_subs,_doc_picker),
        ("illegal",112,ILL_OPEN,ILL_CORE,ILL_CLOSE,_subs,_doc_picker),
    ]
    rows = run_generate_perrow(plan, target)
    print(f"Wrote {len(rows)} rows to {target}")
