"""PF/ESIC top-up — EPF Act 1952 §6; ESI Act 1948 §39. +560 rows."""
import json, random, hashlib, os, sys
sys.path.insert(0, os.path.dirname(__file__))

INDIAN_LAW = "EPF Act 1952 Section 6; ESI Act 1948 Section 39"
CLAUSE_TYPE = "pf_esic"
SOURCE = "synth_v2"

STD_OPEN = [
    "The Company shall deduct twelve per cent (12%) of the Employee's basic wages (inclusive of dearness allowance and retaining allowance, if any) as the Employee's share of the contribution to the Employees' Provident Fund and shall remit the same, along with a matching employer contribution of twelve per cent (12%), to the Regional Provident Fund Commissioner within fifteen (15) days of the close of every wage period.",
    "In accordance with Section 6 of the Employees' Provident Funds and Miscellaneous Provisions Act, 1952, the Company shall remit the statutory contributions in respect of the Employee to the Regional Provident Fund Commissioner, and the Universal Account Number (UAN) of the Employee shall be generated and intimated within thirty (30) days of the date of joining.",
    "The Employee shall be covered under the Employees' Provident Fund Scheme, 1952, the Employees' Pension Scheme, 1995 and the Employees' Deposit Linked Insurance Scheme, 1976, and contributions shall be remitted as mandated by Section 6 of the Employees' Provident Funds and Miscellaneous Provisions Act, 1952.",
    "Where the Employee's gross monthly wages do not exceed Rs. 21,000/-, the Employee shall additionally be covered under the Employees' State Insurance Act, 1948, and the Company shall deduct 0.75% of the wages as the Employee's contribution and contribute 3.25% of the wages as the employer's share under Section 39 of the said Act.",
    "The Company shall register the Employee's particulars on the ESIC portal and shall ensure that the biometric enrolment and generation of the Insurance Number is completed within ten (10) days of joining.",
    "Upon completion of five (5) years of continuous service with {company}, the Employee shall be entitled to gratuity under the Payment of Gratuity Act, 1972, calculated at fifteen (15) days' last drawn wages for every completed year of service, subject to the statutory ceiling.",
    "The statutory contributions to the EPF and ESIC shall be remitted by the Employer in addition to the Employee's salary and shall not be set off against or deducted from the gross salary recorded in the Appointment Letter.",
    "Statutory bonus under the Payment of Bonus Act, 1965 shall be payable to the Employee in accordance with the provisions of the said Act, subject to the wage ceiling and the minimum bonus of 8.33%, as revised from time to time.",
    "The Employer shall comply with all obligations under the Employees' Provident Funds and Miscellaneous Provisions Act, 1952, the Employees' State Insurance Act, 1948, the Payment of Gratuity Act, 1972 and the Payment of Bonus Act, 1965 in respect of the Employee.",
]

STD_CORE = [
    " The Electronic Challan-cum-Return (ECR) shall be filed with the EPFO portal within fifteen (15) days of the close of every month, and a copy of the acknowledgment shall be preserved as part of the statutory records maintained at {city}.",
    " The Employer shall deposit the ESIC contribution through the ESIC portal within fifteen (15) days of the last day of the calendar month, and the Employee shall be entitled to medical benefits through the dispensary allotted by the Regional Office of ESIC.",
    " In respect of international workers covered by the Employees' Provident Funds (International Workers) Scheme, 2008, contributions shall be made on full salary without the statutory wage ceiling applicable to domestic workers.",
    " The Company shall provide the Employee with a monthly salary slip showing the break-up of basic wages, dearness allowance, house rent allowance and other components, along with the statutory deductions towards EPF, ESIC and professional tax.",
    " Where the Employee opts to increase the voluntary contribution to the Employees' Provident Fund beyond the statutory minimum, the Company shall facilitate such increase through payroll without any matching increase in the employer's share.",
    " The Employer shall ensure that the Employee's Aadhaar and PAN are seeded with the UAN, and shall provide assistance in KYC updation and nomination under the Employees' Provident Fund Scheme, 1952.",
    " All statutory forms, including Form 11 and Form 2, shall be submitted by the Employee within the prescribed timelines, and the Employer shall forward the same to the appropriate authority.",
]

STD_CLOSE = [
    " Any statutory revision in the rates of contribution, wage ceilings, or eligibility thresholds shall apply automatically from the effective date of the notification, and the parties' obligations shall be adjusted accordingly.",
    " The Employee shall be entitled to withdraw or transfer the accumulated provident fund balance on cessation of employment in accordance with the provisions of the Employees' Provident Funds Scheme, 1952 and the procedure prescribed by the Regional Provident Fund Commissioner.",
    " The Employer shall issue Form 16, Form 3A and Form 19, as applicable, on or before the statutory due dates and shall provide all information and certificates necessary for the Employee's income tax filings.",
    " The Employer's compliance with the social security legislation aforesaid shall be without prejudice to the Employee's right to raise a grievance before the Regional Provident Fund Commissioner, the Regional Director of ESIC or the Controlling Authority under the Payment of Gratuity Act, 1972, as applicable.",
    " The Employer shall issue Form I (Insurance Card) to the Employee on registration under the ESIC Scheme, and the same shall be surrendered upon cessation of employment for cancellation.",
    " All contributions referred to herein shall be in addition to, and not in substitution of, the gross salary payable to the Employee as mentioned in the Appointment Letter.",
]

AGG_OPEN = [
    "The Cost-to-Company (CTC) of {ctc} per annum is all-inclusive and the Employee agrees that both the employer's share and the Employee's share of contributions to the Employees' Provident Fund (aggregating to 24% of PF wages) shall be deducted from the said CTC.",
    "The Employer reserves the right to designate the basic wages of the Employee at the minimum wage prescribed by the State Government of {state} in order to minimise the contribution base for the Employees' Provident Fund.",
    "All allowances payable to the Employee, including house rent allowance, conveyance allowance, special allowance and performance pay, shall be structured to fall outside the definition of 'basic wages' under the Employees' Provident Funds and Miscellaneous Provisions Act, 1952, so as to limit the Employer's contribution obligation.",
    "The Employee's CTC includes a notional 'employer PF' component of {pf} per annum, and any statutory revision in the PF rate or wage ceiling shall be absorbed entirely within the stated CTC without upward adjustment of gross salary.",
    "Where the Employee opts for voluntary provident fund (VPF) in excess of the statutory rate, the Employer's contribution shall in all events remain capped at the statutory rate on the statutory ceiling of Rs. 15,000/- per month.",
    "The Employer shall not reimburse the Employee's contribution to the Employees' Provident Fund or the Employees' State Insurance Corporation, and any shortfall in the net take-home salary attributable to statutory deductions shall be borne by the Employee.",
    "Employee stock option plans, retention bonuses and variable pay shall be structured as separate allowances outside the definition of 'wages' under the Employees' Provident Funds and Miscellaneous Provisions Act, 1952, and no contribution shall be made in respect of such amounts.",
    "The Employer may, at its discretion, reclassify the Employee's engagement as that of a 'retainer' or 'consultant' to avoid the liability to contribute to the Employees' Provident Fund, and the Employee consents to such reclassification on prior notice.",
]

AGG_CORE = [
    " In the event of any increase in the employer's contribution on account of a judicial pronouncement (including the Surya Roshni judgment of the Supreme Court), the Employer's CTC to the Employee shall stand reduced by an equivalent amount, and the Employee agrees to such adjustment.",
    " The Employee's gratuity contribution shall be limited to the amount payable under the statutory formula, and no amount beyond the statutory ceiling shall be payable on cessation of employment, notwithstanding the Employee's total tenure of service.",
    " The Employee consents to the Employer adopting payroll strategies, including the splitting of salary into various allowances, so as to minimise the base on which EPF contributions are computed, subject to applicable law.",
    " The Employer shall not be liable to pay any interest, damages or penalty under Section 7Q or 14B of the Employees' Provident Funds and Miscellaneous Provisions Act, 1952 arising from late remittance, and such liability shall be borne by the Employee to the extent attributable to any delay.",
    " The Employer may, on its own election, opt out of the ESIC scheme in respect of the Employee on the ground that the Employee is covered by an alternative group medical insurance policy, notwithstanding the mandatory nature of the ESIC Act, 1948.",
    " Bonus under the Payment of Bonus Act, 1965 shall be payable only where computation of allocable surplus so warrants, and the Employer shall be entitled to set off any ex-gratia or performance pay already paid against the statutory bonus liability.",
]

AGG_CLOSE = [
    " The Employee acknowledges that the structuring of CTC and allowances described herein is a fair commercial arrangement and shall not be re-opened before any forum at {city} or elsewhere.",
    " Any challenge raised by the Employee to the statutory classification of allowances, or the treatment of CTC as inclusive of statutory contributions, shall be treated as a material breach of this {doc}.",
    " The Employee agrees that the Employer's periodic revision of the break-up of gross salary, to align with changes in judicial interpretation of 'basic wages', shall not be treated as a reduction of salary or adverse variation of service conditions.",
    " The Employer shall have the right to recover from the Employee, through deduction from salary, any sum paid by the Employer on account of retrospective statutory demand attributable to the Employee's engagement.",
    " This clause reflects the Employer's commercial arrangement for cost management and shall be read in conjunction with the Employee's consent to such structuring as reflected in the Appointment Letter.",
]

ILL_OPEN = [
    "The Employee hereby waives and relinquishes any and all rights, benefits and claims under the Employees' Provident Funds and Miscellaneous Provisions Act, 1952, the Employees' State Insurance Act, 1948, the Payment of Gratuity Act, 1972 and the Payment of Bonus Act, 1965, and agrees that no contribution shall be deducted or remitted by the Employer on account of the Employee.",
    "Notwithstanding the mandatory nature of the Employees' Provident Funds and Miscellaneous Provisions Act, 1952, the Employee opts out of coverage under the said Act and the Schemes framed thereunder, and agrees that no Universal Account Number shall be generated in the name of the Employee.",
    "The Employee is engaged on a 'consultancy' basis at {city}, notwithstanding the actual nature of the engagement being that of an employee within the meaning of the Employees' Provident Funds and Miscellaneous Provisions Act, 1952, and no statutory contribution shall be payable by the Employer.",
    "The Employee agrees to forego the benefit of the Employees' State Insurance Act, 1948 and Section 39 thereunder, and accepts a flat monthly medical allowance of Rs. 500/- in lieu of the statutory medical, cash and maternity benefits.",
    "The Employer and the Employee hereby mutually agree that the provisions of Section 6 of the Employees' Provident Funds and Miscellaneous Provisions Act, 1952 shall not apply to this engagement, and the Employee's remuneration shall be paid in cash without statutory deductions.",
    "The Employee covenants that he or she shall not raise any demand or grievance before the Regional Provident Fund Commissioner, the Regional Director of ESIC or the Controlling Authority under the Payment of Gratuity Act, 1972 in respect of non-contribution by the Employer.",
    "The Employer shall not be under any obligation to remit contributions to the Employees' Provident Fund or the Employees' State Insurance Corporation in respect of the Employee, notwithstanding that the Employer is a covered establishment and the Employee meets the statutory thresholds.",
    "The Employee shall be treated for all purposes as a 'freelancer' notwithstanding having a fixed monthly remuneration, a reporting manager and allocated office space at {city}, and no statutory deduction shall apply.",
]

ILL_CORE = [
    " The Employee acknowledges that this waiver is absolute and irrevocable and shall bind his or her heirs, executors and legal representatives in respect of the said statutory benefits.",
    " The Employer shall not issue Form 11, Form 2, Form 16 or any other statutory form or return in respect of the Employee, and the Employee acknowledges the waiver of all associated entitlements.",
    " In consideration of the waiver contained herein, the Employee shall be paid a marginally higher gross salary, and such enhanced salary shall constitute full and final settlement of all statutory claims present and future.",
    " The parties record that this arrangement is mutually agreed, that the Employee has been fully informed of the statutory entitlements being foregone, and that the Employee's waiver shall not be re-opened before any forum.",
    " The Employer shall not deposit any amount towards gratuity, superannuation fund or national pension system in respect of the Employee, notwithstanding the eligibility of the Employee under the applicable statutory regime.",
]

ILL_CLOSE = [
    " This waiver is given as a condition precedent to engagement and shall be binding notwithstanding any decision of the Supreme Court or the High Courts of India holding that such statutory rights cannot be contractually waived.",
    " Any demand by the Employee for retrospective contribution or statutory benefit shall be treated as a material breach of this {doc} and shall entitle the Employer to terminate the engagement forthwith.",
    " The parties acknowledge that the 'consultant' characterisation of the engagement is intended to avoid the obligations of the social security legislation and is binding on both parties notwithstanding the factual indicia of employment.",
    " The Employee agrees to defend, indemnify and hold the Employer harmless against any demand, fine or penalty by the Regional Provident Fund Commissioner, ESIC or the labour authorities arising in relation to the Employee's engagement.",
    " This clause shall operate as a complete bar to any retrospective claim under the Employees' Provident Funds and Miscellaneous Provisions Act, 1952 or the Employees' State Insurance Act, 1948.",
]

DOCS = ["employment contract","contract labour agreement","consultant agreement","appointment letter"]
STATES = ["Maharashtra","Karnataka","NCT of Delhi","Haryana","Uttar Pradesh",
          "Telangana","Tamil Nadu","Gujarat","Rajasthan","West Bengal"]
CITIES = ["Mumbai","Bengaluru","Pune","Hyderabad","Chennai","Gurugram","Noida",
          "Ahmedabad","Chandigarh","Kolkata","Coimbatore","Jaipur","Kochi"]

def _subs(r):
    from pools import COMPANY_PREFIXES, COMPANY_SUFFIXES
    return {
        "company": r.choice(COMPANY_PREFIXES) + " " + r.choice(COMPANY_SUFFIXES),
        "city": r.choice(CITIES),
        "state": r.choice(STATES),
        "ctc": f"Rs. {r.randint(4, 40)},00,000/- per annum",
        "pf": f"Rs. {r.randint(21600, 65000):,}/- per annum",
    }

def _doc_picker(i):
    random.seed(i*73+9); return random.choice(DOCS)

if __name__ == "__main__":
    from common import run_generate
    target = sys.argv[1] if len(sys.argv) > 1 else "/tmp/pf.jsonl"
    plan = [
        ("standard",252,STD_OPEN,STD_CORE,STD_CLOSE,_subs,_doc_picker,CLAUSE_TYPE,INDIAN_LAW,SOURCE),
        ("aggressive",196,AGG_OPEN,AGG_CORE,AGG_CLOSE,_subs,_doc_picker,CLAUSE_TYPE,INDIAN_LAW,SOURCE),
        ("illegal",112,ILL_OPEN,ILL_CORE,ILL_CLOSE,_subs,_doc_picker,CLAUSE_TYPE,INDIAN_LAW,SOURCE),
    ]
    rows = run_generate(plan, target)
    print(f"Wrote {len(rows)} rows to {target}")
