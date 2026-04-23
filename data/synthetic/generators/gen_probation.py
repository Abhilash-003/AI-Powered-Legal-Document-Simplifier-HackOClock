"""Probation top-up — Industrial Employment (Standing Orders) Act 1946 SO 14. +560 rows."""
import json, random, hashlib, os, sys
sys.path.insert(0, os.path.dirname(__file__))

INDIAN_LAW = "Industrial Employment (Standing Orders) Act 1946 Standing Order 14"
CLAUSE_TYPE = "probation"
SOURCE = "synth_v2"

STD_OPEN = [
    "The Employee shall be on probation for an initial period of {pm} months from the date of joining, in accordance with Standing Order 14 of the Industrial Employment (Standing Orders) Act, 1946 as applicable to the establishment at {city}.",
    "The first {pm} months of the Employee's service with {company} shall constitute the probationary period, during which the Employee's performance, attitude and suitability for regular employment shall be assessed.",
    "The Employee shall serve a probation period of {pm} months commencing from the date of joining, during which structured mid-probation and end-probation reviews shall be conducted by the Reporting Manager and the HR Business Partner.",
    "Upon satisfactory completion of the probation period of {pm} months, the Employee shall be confirmed in writing as a permanent employee of {company}, and the Letter of Confirmation shall specify the confirmed designation, grade and terms.",
    "The Employee shall be deemed to be on probation for a period of six (6) months from the date of joining unless confirmed earlier by a written communication, in line with the Model Standing Orders and the applicable State Shops and Establishments Act.",
    "Where the Employer requires additional time to assess the Employee's suitability for regular employment, the probation may be extended once by a period not exceeding {epm} months, by a written communication stating the reasons for such extension.",
    "During the probation period, either party may terminate the employment on {pnd} days' prior written notice or by tendering basic salary in lieu thereof, in accordance with Standing Order 14 of the Industrial Employment (Standing Orders) Act, 1946.",
    "Confirmation as a regular employee shall be effected only through a specific written order issued by the Head of Human Resources of {company}, and absence of such written order shall not by itself operate as deemed confirmation.",
]

STD_CORE = [
    " During probation, the Employee shall not be entitled to certain benefits reserved for confirmed employees, including paid annual leave beyond pro rata entitlement, long-term incentives and sabbatical leave, as specifically identified in the HR Manual.",
    " The Employee shall participate in the induction programme, mandatory compliance training and the onboarding orientation during the probation period, and satisfactory completion thereof shall be a factor in the confirmation decision.",
    " Extension of probation, where effected, shall be communicated to the Employee in writing with reasons, and shall not exceed a further period of {epm} months under any circumstances.",
    " The Employee's attendance, punctuality, adherence to standards of conduct and delivery against objectives shall be reviewed at the end of each month during probation, and feedback shall be shared in writing.",
    " Where a domestic enquiry is held in respect of alleged misconduct during probation, the procedural safeguards under the certified Standing Orders shall apply and the Employee shall have the opportunity to respond.",
    " Probation shall not be extended beyond nine (9) months in the aggregate, and in any event shall not be stretched so as to deny the Employee eligibility for gratuity under the Payment of Gratuity Act, 1972.",
    " During probation, the Employee shall be paid the full monthly salary recorded in the Appointment Letter, without any reduction or withholding on account of probationary status.",
]

STD_CLOSE = [
    " On confirmation, the Employee shall be entitled to all benefits applicable to confirmed employees of {company}, including gratuity eligibility, full annual leave and participation in long-term incentive plans.",
    " The Employee's seniority, for the purpose of future annual increments and long service awards, shall be reckoned from the original date of joining, notwithstanding the probationary status during the initial months.",
    " Nothing in this clause shall be construed so as to prejudice the statutory rights of the Employee under the Industrial Disputes Act, 1947, the Industrial Employment (Standing Orders) Act, 1946 and the applicable State Shops and Establishments Act.",
    " A copy of the certified Standing Orders applicable to the establishment at {city} shall be available at the Human Resources office for reference by the Employee at any time during the probation period.",
    " Where the Employee is transferred during the probation period to a different unit or location, the probation shall continue uninterrupted, and the reviews shall be conducted by the new Reporting Manager.",
    " The Employee shall acknowledge receipt of the Confirmation Letter in writing, and the date of effect of confirmation shall be the date stated in the said Letter.",
]

AGG_OPEN = [
    "The Employee shall be on probation for an initial period of nine (9) months from the date of joining, which period may be extended at the sole discretion of the Company by up to a further twelve (12) months without any requirement to record reasons in writing.",
    "The probation period shall continue until the Employee is confirmed in writing by the Managing Director of {company}, and no limit shall apply to the duration of probation save such limit as is mandatorily prescribed by law.",
    "Notwithstanding Standing Order 14 of the Industrial Employment (Standing Orders) Act, 1946, the probation period shall be twelve (12) months with an option to extend once by six (6) months, and the Employee's confirmation shall not be deemed on mere expiry of probation.",
    "During the probationary period, the Company may terminate the employment of the Employee at any time without assigning any reason and without the benefit of any notice or hearing, and such termination shall not be assailable before any forum.",
    "The Employee shall be paid basic salary alone during the probationary period, to the exclusion of all allowances, variable pay and benefits applicable to confirmed employees of {company}.",
    "The probationary period may be extended on as many occasions as the Company considers necessary, each extension being by a period not exceeding six (6) months, and the decision of the Company in this regard shall be final and binding.",
    "The Employee's probation shall stand automatically extended by a period equal to the aggregate of any leave availed during the initial probation period, whether paid, unpaid, medical or otherwise.",
    "During probation, the Employee shall not be eligible to apply for internal transfers, internal postings or participation in the Employee Stock Option Plan, and waiver of these rights is a condition of probationary engagement.",
]

AGG_CORE = [
    " The Company shall not be obliged to inform the Employee of any extension of probation prior to the expiry of the current probation period, and the Company's communication of extension may be issued retrospectively within thirty (30) days of such expiry.",
    " The Employee acknowledges that 'continuing probation' pending formal confirmation is a legitimate HR process, and the Employee shall not be entitled to claim deemed confirmation merely on account of expiry of the initial probation period.",
    " Termination of the Employee during probation shall not attract the notice or compensation requirements of Section 25F of the Industrial Disputes Act, 1947, and the Employee waives any claim of retrenchment in respect thereof.",
    " The Employee's attendance during probation shall not count towards continuous service for any statutory purpose, including gratuity eligibility under the Payment of Gratuity Act, 1972, unless expressly recorded as confirmed service.",
    " The probationary Employee shall be deemed to have consented to variations in reporting relationship, grade, designation and place of posting at the Company's sole discretion, without right of refusal or appeal.",
    " The Company may, at its discretion, during probation, vary the Employee's role, remove performance-linked allowances and adjust the structure of remuneration, and the Employee's continued presence at work shall constitute acceptance of such variations.",
]

AGG_CLOSE = [
    " Any dispute arising out of the probation, its extension or termination shall be referred to the sole discretion of the HR Head, whose decision shall be final and binding on the Employee.",
    " The Employee consents to the placement of adverse feedback on the personnel file during probation, and such feedback shall not require the Employee's countersignature and shall not be open to challenge.",
    " On termination during probation, the Employee shall not be entitled to any notice pay, severance pay or ex-gratia, and the full and final settlement shall be confined to earned salary up to the last working day.",
    " This clause shall be specifically enforceable and shall operate as a bar to any claim of deemed confirmation, notice pay or reinstatement sought by the Employee before any forum.",
    " The Employer's right to extend or terminate probation shall be exercisable notwithstanding receipt of positive performance reviews by the Employee, and the Employee shall not rely on such reviews as basis for confirmation.",
]

ILL_OPEN = [
    "The Employee shall be on probation for a period of twenty-four (24) months from the date of joining, extendable at the Company's discretion by a further twelve (12) months, notwithstanding the six-month limit recognised under Standing Order 14 of the Industrial Employment (Standing Orders) Act, 1946 as certified for the establishment.",
    "The Employee shall remain on probation for a minimum period of thirty-six (36) months, and the Company reserves the right to keep the Employee on perpetual probation without extending confirmation at any time, notwithstanding the Employee's completion of the probationary objectives.",
    "Upon completion of the initial six-month probation, the Employee shall be re-designated as 'extended probationer' for a further period of sixty (60) months, during which no gratuity, retrenchment compensation or statutory confirmation benefit shall accrue, notwithstanding the Payment of Gratuity Act, 1972 and the Industrial Employment (Standing Orders) Act, 1946.",
    "The Employee's probation shall continue indefinitely until a written Confirmation Letter is issued by the Managing Director, and the Employee waives any claim of deemed confirmation, acquired seniority or statutory benefit arising from mere lapse of time.",
    "The probationer Employee may be terminated at any time during probation by the Company without notice, pay in lieu, reasons or opportunity to be heard, notwithstanding the requirements of Standing Order 14 and principles of natural justice.",
    "The extension of probation shall operate retroactively, and any benefits paid to the Employee in the intervening period (including gratuity contribution, annual leave encashment or statutory bonus) may be recovered as overpayment by the Employer.",
    "During the extended probation period of eighteen (18) months, the Employee shall be paid a stipend of Rs. 8,000/- per month in lieu of the gross salary originally recorded in the Appointment Letter, notwithstanding the minimum wages notified by the State Government of {state}.",
    "The Employee acknowledges that the stretched probationary period is a mutually agreed arrangement and waives any right to raise a dispute under the Industrial Disputes Act, 1947 or the Industrial Employment (Standing Orders) Act, 1946 in relation to probation and confirmation.",
]

ILL_CORE = [
    " The Employee accepts that the primary purpose of the stretched probation is to postpone the Employee's eligibility for gratuity under Section 4 of the Payment of Gratuity Act, 1972 until such time as the Company elects to confirm the Employee.",
    " Termination of the Employee during the extended probation shall not constitute retrenchment within the meaning of Section 2(oo) of the Industrial Disputes Act, 1947, and no notice or compensation shall be payable.",
    " The Employee waives the statutory protection of the certified Standing Orders in respect of confirmation and continuance, and agrees to be bound by the Company's discretion to extend or terminate probation.",
    " The Employee specifically consents to the non-payment of annual increments, performance bonus and employee benefits during the extended probation, and acknowledges that such non-payment is consistent with the probationary status.",
    " The Employer shall not be required to maintain a service record, issue a Form B muster roll or file statutory returns in respect of the Employee during the extended probation, and such non-compliance shall not prejudice this engagement.",
]

ILL_CLOSE = [
    " This clause shall bind the Employee notwithstanding any certified Standing Orders, judicial pronouncement or legislative amendment to the contrary, and the Employee shall not raise any challenge to the validity or scope of this clause.",
    " The Employee shall have no right of appeal, redressal or industrial dispute in respect of termination during probation, and such termination shall not be reopened before any Labour Court, Industrial Tribunal or Conciliation Officer.",
    " The provisions of the Model Standing Orders shall stand displaced by this clause to the extent of inconsistency, and the Employer's certified Standing Orders shall be deemed amended to incorporate the provisions of this clause.",
    " Any concurrent legislative or judicial protection extended to probationers shall not apply to this engagement, and the parties have expressly contracted out of such protection.",
    " The Employee's continued presence at work after each extension of probation shall constitute an unambiguous acceptance of the extension and the consequences thereof.",
]

DOCS = ["employment contract","appointment letter"]
CITIES = ["Mumbai","Bengaluru","Pune","Hyderabad","Chennai","Gurugram","Noida",
          "Ahmedabad","Chandigarh","Kolkata","Coimbatore","Jaipur","Kochi","Indore","Lucknow"]
STATES = ["Maharashtra","Karnataka","NCT of Delhi","Haryana","Uttar Pradesh",
          "Telangana","Tamil Nadu","Gujarat","Rajasthan","West Bengal"]

def _subs(r):
    from pools import COMPANY_PREFIXES, COMPANY_SUFFIXES
    return {
        "company": r.choice(COMPANY_PREFIXES) + " " + r.choice(COMPANY_SUFFIXES),
        "city": r.choice(CITIES),
        "state": r.choice(STATES),
        "pm": r.choice([3, 6]),
        "epm": r.choice([2, 3]),
        "pnd": r.choice([7, 10, 14, 15]),
    }

def _doc_picker(i):
    random.seed(i*79+11); return random.choice(DOCS)

if __name__ == "__main__":
    from common import run_generate
    target = sys.argv[1] if len(sys.argv) > 1 else "/tmp/pb.jsonl"
    plan = [
        ("standard",252,STD_OPEN,STD_CORE,STD_CLOSE,_subs,_doc_picker,CLAUSE_TYPE,INDIAN_LAW,SOURCE),
        ("aggressive",196,AGG_OPEN,AGG_CORE,AGG_CLOSE,_subs,_doc_picker,CLAUSE_TYPE,INDIAN_LAW,SOURCE),
        ("illegal",112,ILL_OPEN,ILL_CORE,ILL_CLOSE,_subs,_doc_picker,CLAUSE_TYPE,INDIAN_LAW,SOURCE),
    ]
    rows = run_generate(plan, target)
    print(f"Wrote {len(rows)} rows to {target}")
