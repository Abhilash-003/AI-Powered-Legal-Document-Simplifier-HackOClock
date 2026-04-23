"""Eviction top-up — TPA 1882 §106 + State RCAs. +560 rows."""
import json, random, hashlib, os, sys
sys.path.insert(0, os.path.dirname(__file__))

CLAUSE_TYPE = "eviction"
SOURCE = "synth_v2"

CITY_LOCALITIES = {
    "Mumbai": ("Maharashtra Rent Control Act, 1999", ["Bandra (West)","Andheri (East)","Powai","Lower Parel","Juhu","Worli","Malad","Goregaon (East)","Thane"]),
    "Pune": ("Maharashtra Rent Control Act, 1999", ["Hinjewadi","Kharadi","Viman Nagar","Baner","Hadapsar","Koregaon Park","Shivaji Nagar"]),
    "Delhi": ("Delhi Rent Act, 1995", ["Connaught Place","Saket","Defence Colony","Greater Kailash","Dwarka","Lajpat Nagar","Rajouri Garden","Karol Bagh"]),
    "Gurugram": ("Haryana Urban (Control of Rent and Eviction) Act, 1973", ["Sector 44","Sector 29","Golf Course Road","Cyber City","Udyog Vihar","Sohna Road"]),
    "Noida": ("Uttar Pradesh Regulation of Urban Premises Tenancy Act, 2021", ["Sector 62","Sector 16","Sector 125","Sector 18","Sector 135"]),
    "Bengaluru": ("Karnataka Rent Act, 1999", ["Koramangala","Whitefield","Indiranagar","HSR Layout","Electronic City","Marathahalli","Jayanagar","JP Nagar","Bellandur"]),
    "Hyderabad": ("Telangana Buildings (Lease, Rent and Eviction) Control Act, 1960", ["HITEC City","Gachibowli","Banjara Hills","Jubilee Hills","Madhapur","Kondapur","Begumpet"]),
    "Chennai": ("Tamil Nadu Regulation of Rights and Responsibilities of Landlords and Tenants Act, 2017", ["T. Nagar","Nungambakkam","Velachery","OMR","Guindy","Adyar","Anna Nagar"]),
    "Kolkata": ("West Bengal Premises Tenancy Act, 1997", ["Salt Lake Sector V","Park Street","Ballygunge","Alipore","New Town"]),
    "Ahmedabad": ("Gujarat Rent Control Act, 2011", ["Navrangpura","SG Highway","Bodakdev","Prahlad Nagar","Satellite"]),
    "Jaipur": ("Rajasthan Rent Control Act, 2001", ["Malviya Nagar","C-Scheme","Vaishali Nagar","Mansarovar","Sitapura"]),
    "Kochi": ("Kerala Buildings (Lease and Rent Control) Act, 1965", ["Kakkanad","Infopark","Kaloor","Edappally","Vyttila"]),
    "Chandigarh": ("East Punjab Urban Rent Restriction Act, 1949", ["Sector 17","Sector 22","Sector 34"]),
    "Indore": ("Madhya Pradesh Accommodation Control Act, 1961", ["Vijay Nagar","Palasia","AB Road"]),
    "Coimbatore": ("Tamil Nadu Regulation of Rights and Responsibilities of Landlords and Tenants Act, 2017", ["RS Puram","Peelamedu","Saravanampatti"]),
}

STD_OPEN = [
    "In the event the Lessee fails to pay the monthly rent reserved hereunder on the due date, the Lessor shall issue a written notice of demand calling upon the Lessee to cure the default within fifteen (15) days of receipt of such notice in respect of the said premises situated at {locality}, {city}.",
    "Should the Lessee commit a breach of any material term of this {doc} in respect of the said premises at {locality}, {city}, the Lessor shall serve upon the Lessee a written notice specifying the breach and requiring rectification within thirty (30) days from the date of receipt of the said notice.",
    "This tenancy being a month-to-month tenancy in respect of the said premises at {locality}, {city}, may be determined by either party by giving not less than fifteen (15) days' notice in writing expiring with the end of a month of the tenancy, in compliance with Section 106 of the Transfer of Property Act, 1882.",
    "In the event the Licensee fails to vacate the said premises at {locality}, {city}, on the expiry of the term or on the earlier determination of this {doc}, the Licensor shall be entitled to initiate proceedings for eviction before the jurisdictional court at {city}.",
    "The Lessor may terminate this {doc} on any of the grounds enumerated in Section 12 of the {rca}, being the grounds of non-payment of rent, unlawful subletting, change of user, breach of a condition of tenancy or bona fide requirement for personal occupation.",
    "Any breach of the terms of this {doc} shall entitle the Lessor to issue a cure notice of thirty (30) days to the Lessee, and upon failure to cure within the said period, the Lessor shall be at liberty to terminate the tenancy by further notice in writing.",
    "Default in payment of monthly rent or licence fee beyond the statutory grace period shall entitle the Lessor to determine the tenancy in accordance with the {rca} read with Section 106 of the Transfer of Property Act, 1882.",
    "The Lessor reserves the right to determine this tenancy for bona fide requirement, non-payment of rent, unauthorised subletting or any other ground permitted under the {rca}, by serving a statutory notice as provided in Section 106 of the Transfer of Property Act, 1882.",
]

STD_CORE = [
    " Upon failure of the Lessee to remedy the breach or arrears within the notice period, the Lessor shall be at liberty to terminate the tenancy by serving a further notice under Section 106 of the Transfer of Property Act, 1882, and thereafter proceed before the jurisdictional Small Causes Court or Rent Controller at {city} for an order of eviction.",
    " In the case of the Lessor, the notice of termination shall also specify the ground of eviction recognised under the {rca}, namely non-payment of rent, unlawful subletting, breach of a condition of tenancy, or bona fide requirement for personal occupation.",
    " No eviction shall be effected save in execution of a decree or order of the Competent Authority or the Court of Small Causes at {city}, and until such decree or order the Lessee shall continue to enjoy quiet possession of the said premises.",
    " The Lessee shall be entitled to a reasonable opportunity of being heard before any order of eviction is passed, and the Lessor shall not attempt to obtain possession by self-help or by forcible re-entry in violation of Section 6 of the Specific Relief Act, 1963.",
    " On determination of the tenancy by notice, the Lessor shall approach the jurisdictional Rent Controller or the Small Causes Court at {city} for an order of eviction, and until such order is obtained, the Lessor shall not interfere with the Lessee's peaceful possession.",
    " Nothing in this clause shall entitle the Lessor to re-enter the said premises otherwise than through due process of law in accordance with the Specific Relief Act, 1963 and the {rca}.",
    " The Lessor shall give the Lessee at least {days} days' written notice to remedy any alleged breach before invoking the eviction machinery under the {rca}, and the Lessor shall act in good faith in assessing the cure.",
]

STD_CLOSE = [
    " The security deposit shall be refunded to the Lessee within thirty (30) days of handover of vacant possession, subject to deduction only of admitted arrears and documented damages beyond ordinary wear and tear.",
    " This clause shall be read in conjunction with the {rca} and the provisions of Section 106 of the Transfer of Property Act, 1882, and shall be construed so as to give full effect to both statutes.",
    " The Lessor shall, following eviction, issue to the Lessee a detailed statement of the security deposit adjustment, and any balance remaining shall be refunded by NEFT/RTGS within the time stipulated.",
    " Any dispute as to the ground of eviction or the quantum of deduction from the security deposit shall be referred to the jurisdictional Rent Controller at {city} in accordance with the {rca}.",
    " The Lessee shall hand over the said premises in the same condition as at the commencement of tenancy, save reasonable wear and tear, and shall settle all statutory dues including municipal taxes and utility charges up to the date of vacation.",
    " Any amount payable by the Lessee towards arrears of rent, maintenance charge or damages shall be recoverable as a debt due under Section 73 of the Indian Contract Act, 1872, without prejudice to the eviction remedy.",
]

AGG_OPEN = [
    "In the event of any breach of this {doc} in respect of the said premises at {locality}, {city}, the Lessor shall serve a seven (7) day notice on the Lessee, failing cure of which the Lessor shall be entitled to forfeit the entire security deposit and terminate the tenancy forthwith.",
    "The Lessor reserves the right to serve a notice of forty-eight (48) hours on the Lessee to vacate the said premises at {locality}, {city}, on the ground of 'material breach' as determined in the sole discretion of the Lessor, without the necessity of an opportunity to be heard.",
    "Any alleged breach of the terms of this {doc}, including non-payment of rent, unauthorised use of the premises or any other breach in the Lessor's sole assessment, shall entitle the Lessor to automatic forfeiture of the security deposit of {deposit}.",
    "The Lessor may, on the happening of any act or omission treated by the Lessor as a breach, take immediate possession of the said premises by changing the locks, disconnecting the utilities or restricting access, notwithstanding the Lessee's continued occupation.",
    "Where the Lessee fails to pay rent within five (5) days of the due date, the Lessor shall be entitled to issue a notice for vacation of the said premises within seven (7) days, and the Lessee's right of cure shall be limited to a single occasion in the tenancy.",
    "The Lessor reserves the unilateral right to determine, at its sole discretion, whether any conduct of the Lessee constitutes breach of this {doc}, and the Lessor's determination shall be final and binding notwithstanding any contrary evidence.",
    "On the Lessor serving a termination notice, the Lessee shall vacate the said premises within ten (10) days and shall have no right to continue in possession thereafter, notwithstanding any pending litigation or judicial proceeding.",
]

AGG_CORE = [
    " The Lessee hereby waives the benefit of Section 114 of the Transfer of Property Act, 1882 which provides for relief against forfeiture of tenancy on payment of rent and costs.",
    " The Lessee shall not be entitled to raise before any forum the defence that the notice of eviction was not served for a reasonable period or that the ground of eviction does not fall within the {rca}.",
    " The Lessor shall be entitled to recover an amount equivalent to three (3) months' rent as damages for illegal overholding, payable from the date of expiry of the notice period until the date of vacation.",
    " The Lessor's right to re-enter shall include the right to the assistance of the local police for peaceful removal of the Lessee, and the Lessee shall not resist such re-entry.",
    " The security deposit of {deposit} shall stand automatically forfeited on the occurrence of any breach, and the Lessee shall not be entitled to any adjustment of the deposit against arrears of rent or damages.",
]

AGG_CLOSE = [
    " Any challenge by the Lessee to the eviction notice before the Rent Controller, Small Causes Court or High Court shall entitle the Lessor to recover legal costs on a full indemnity basis in addition to other remedies.",
    " The Lessee acknowledges that the truncated notice period and aggressive remedies in this clause are reasonable in view of the commercial nature of the said premises at {locality}, {city}.",
    " The Lessor's forfeiture and re-entry rights herein are cumulative and additional to the statutory remedies, and exercise of one shall not preclude recourse to another.",
    " This clause shall be specifically enforceable and shall bind the Lessee notwithstanding any rule of equity in favour of the Lessee relating to forfeiture or overholding.",
    " The Lessee shall remove all possessions from the said premises within seventy-two (72) hours of receipt of the termination notice, failing which the Lessor may remove and store them at the Lessee's cost, without liability for any loss or damage.",
]

ILL_OPEN = [
    "The Lessee hereby waives the notice required under Section 106 of the Transfer of Property Act, 1882 in respect of the said premises at {locality}, {city}, and agrees that the Lessor may determine this tenancy with immediate effect and re-enter the premises forthwith.",
    "The Lessor shall be entitled, at its sole discretion, to enter the said premises at {locality}, {city}, change the locks and dispossess the Lessee without the necessity of judicial process, notwithstanding the provisions of the Specific Relief Act, 1963.",
    "On demand by the Lessor at any time during the term of this {doc}, the Lessee shall immediately vacate the said premises at {locality}, {city}, without the necessity of any notice under Section 106 of the Transfer of Property Act, 1882 or the {rca}.",
    "The Lessor shall be entitled to forcibly remove the Lessee and the Lessee's goods and possessions from the said premises at any time upon the Lessee's alleged default, and the Lessee waives any claim for trespass, damage or interference with possession.",
    "The Lessee agrees that in the event of non-payment of rent for a single month, the Lessor may cut off the water and electricity supply to the said premises and lock the main entrance, regardless of the Lessee's continued occupation.",
    "Notwithstanding Section 6 of the Specific Relief Act, 1963, which bars dispossession save by due process of law, the Lessor shall have the right of physical re-entry on the said premises without any court order, on the occurrence of any alleged default.",
    "The parties agree that the provisions of the {rca} relating to grounds of eviction, procedure for eviction and protection of tenants shall not apply to the tenancy created by this {doc}, and the Lessor shall be at liberty to evict the Lessee at will.",
]

ILL_CORE = [
    " The Lessee expressly waives all protections under the {rca}, including the right to a cure period, the right to contest the ground of eviction and the right to seek relief against forfeiture under Section 114 of the Transfer of Property Act, 1882.",
    " The Lessee acknowledges that self-help by the Lessor, including changing locks, disconnecting utilities or physically removing the Lessee, shall not be actionable as trespass, nuisance or conversion.",
    " Any suit for restoration of possession under Section 6 of the Specific Relief Act, 1963 shall be deemed waived, and the Lessee shall not file or pursue any such suit.",
    " The Lessor's determination of the ground of eviction shall be final and binding, and the {rca} shall be deemed inapplicable to the tenancy, notwithstanding the express language of that statute.",
    " The Lessee shall indemnify the Lessor against any legal costs incurred by the Lessor in resisting any claim brought by the Lessee under the {rca} or the Transfer of Property Act, 1882, on a full indemnity basis.",
]

ILL_CLOSE = [
    " This waiver and authorisation of self-help is given as consideration for the grant of tenancy, and shall bind the Lessee notwithstanding any judicial pronouncement holding that such waiver is void as against public policy.",
    " The Lessee's heirs, executors, administrators and legal representatives shall be equally bound by this clause, and shall not assail the Lessor's right of re-entry or forfeiture on any ground whatsoever.",
    " The Lessor may, at its discretion, initiate criminal proceedings under the Bharatiya Nyaya Sanhita, 2023 for criminal trespass against the Lessee who fails to vacate on demand, and the Lessee's failure to vacate shall constitute the mens rea for such offence.",
    " The parties specifically record that the bar on recovery of possession without due process under the Specific Relief Act, 1963 shall not be invoked by the Lessee in any proceeding, and any such invocation shall be a breach of this {doc}.",
    " The Lessee shall not be entitled to receive the security deposit of {deposit} or any part thereof on eviction under this clause, and such deposit shall stand forfeited to the Lessor as absolute liquidated damages.",
]

DOCS = ["lease deed","leave and license agreement","rental agreement","commercial lease deed"]

def _subs(r):
    city = r.choice(list(CITY_LOCALITIES.keys()))
    rca, locs = CITY_LOCALITIES[city]
    loc = r.choice(locs)
    dep_k = r.choice([80, 120, 180, 220, 300, 400, 500, 650])
    return {
        "locality": loc,
        "city": city,
        "rca": rca,
        "days": r.choice([15, 21, 30, 45]),
        "deposit": f"Rs. {dep_k*1000:,}/-",
    }

def _doc_picker(i):
    random.seed(i*89+7); return random.choice(DOCS)

def run_generate_perrow(plan, out_path):
    from common import compose, dedupe_emit
    out, seen = [], set()
    for (risk, n, opens, cores, closes, subs_fn, doc_picker) in plan:
        i, tries = 0, 0
        while sum(1 for r in out if r["risk_level"]==risk) < n:
            i += 1; tries += 1
            doc = doc_picker(i)
            rr = random.Random(i * 53 + 7)
            subs = subs_fn(rr)
            body = compose(opens, cores, closes, i, subs_fn=lambda r: subs, doc=doc)
            indian_law = f"Transfer of Property Act 1882 Section 106; {subs['rca']}"
            dedupe_emit(out, body, risk, CLAUSE_TYPE, indian_law, doc, SOURCE, seen)
            if tries > 80000: break
    with open(out_path, "a") as f:
        for r in out:
            f.write(json.dumps(r, ensure_ascii=False) + "\n")
    return out

if __name__ == "__main__":
    target = sys.argv[1] if len(sys.argv) > 1 else "/tmp/ev.jsonl"
    plan = [
        ("standard",252,STD_OPEN,STD_CORE,STD_CLOSE,_subs,_doc_picker),
        ("aggressive",196,AGG_OPEN,AGG_CORE,AGG_CLOSE,_subs,_doc_picker),
        ("illegal",112,ILL_OPEN,ILL_CORE,ILL_CLOSE,_subs,_doc_picker),
    ]
    rows = run_generate_perrow(plan, target)
    print(f"Wrote {len(rows)} rows to {target}")
