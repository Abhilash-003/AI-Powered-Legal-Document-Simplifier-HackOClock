"""Notice period clause generator — Standing Orders Act 1946 Schedule Item 9."""
import json, random, hashlib, os, sys
sys.path.insert(0, os.path.dirname(__file__))

INDIAN_LAW = "Industrial Employment (Standing Orders) Act 1946 Schedule Item 9"
CLAUSE_TYPE = "notice_period"
SOURCE = "synth_v2"

STD_OPEN = [
    "Either party may terminate this {doc} by giving the other not less than {nd} days' prior written notice or by tendering basic salary in lieu of such notice.",
    "The notice period applicable to confirmation of employment under this {doc} shall be {nd} days, and the same shall be reciprocal to both the Employee and the Company.",
    "Save during the period of probation, the employment of the Employee shall be terminable by either party on {nd} days' prior written notice to be served at the registered address recorded with the Human Resources department.",
    "Upon confirmation of the Employee as a regular employee, the notice period for termination by either party shall stand at {nd} days in accordance with the certified Standing Orders applicable to the establishment.",
    "The Employee and the Company agree to reciprocal notice of {nd} days for termination of this {doc} post-confirmation, without prejudice to the right of either party to terminate for cause.",
    "During the probation period, the notice of termination shall be {pnd} days by either side, whereas post-confirmation it shall be {nd} days, in line with Schedule Item 9 of the Industrial Employment (Standing Orders) Act, 1946 and the applicable State Shops and Establishments Act.",
    "Notice of termination shall be served in writing in English to the other party at the address recorded in the {doc}, and service by registered post with acknowledgment due or by email to the designated HR mailbox shall be effective service.",
    "Either party may, in lieu of serving the full notice period, tender payment of basic salary (excluding allowances and variable components) in lieu of the unexpired notice period.",
]

STD_CORE = [
    " The Employer shall comply with the notice requirements of Section 25F of the Industrial Disputes Act, 1947 and the retrenchment compensation obligations thereunder in respect of workmen, even where the contractual notice has been served.",
    " The parties agree that the notice period shall not be extended or foreshortened unilaterally by either party, save by mutual written agreement or in the case of acceptance of payment in lieu.",
    " During the notice period, the Employee shall cooperate in knowledge transfer, shall handover ongoing assignments to the designated successor and shall not commence engagement with any other employer.",
    " Where the Employee is a workman within the meaning of the Industrial Disputes Act, 1947, the Company undertakes to comply additionally with the one month's statutory notice required under Section 25F of the said Act in the event of retrenchment.",
    " The Employee shall return all company property, including access cards, laptops, mobile devices and confidential materials, on or before the last working day of the notice period.",
    " The Company shall be entitled to place the Employee on garden leave for all or any part of the notice period on payment of full salary, and the Employee shall remain bound by the confidentiality and restrictive covenants during such period.",
    " If notice is served by the Employer on grounds of misconduct, the Employer shall hold a domestic enquiry in accordance with principles of natural justice prior to giving effect to the termination.",
]

STD_CLOSE = [
    " The full and final settlement, including earned wages, leave encashment, gratuity under the Payment of Gratuity Act, 1972 and variable components accrued, shall be remitted within thirty (30) days of the last working day.",
    " This clause shall be read in conjunction with the applicable certified Standing Orders and the State Shops and Establishments Act having territorial application to the establishment at {city}.",
    " The Employer shall issue an experience certificate and a relieving letter upon the Employee completing the exit formalities, and these shall bear the date of the last working day.",
    " Any dispute as to the calculation of notice period or payment in lieu thereof shall be referred for adjudication under the Industrial Disputes Act, 1947 or the applicable labour legislation.",
    " Where notice is served during the probation period, the probation-notice of {pnd} days shall apply, and no retrenchment compensation shall be payable in respect of a bona fide separation during probation.",
    " The Company shall not unreasonably withhold consent to the Employee accepting a counter-offer or a fresh employment opportunity during the notice period, subject to the Employee's continued performance of duties.",
]

AGG_OPEN = [
    "The notice period for termination by the Employee shall be ninety (90) days, whereas the notice period for termination by the Company shall be fifteen (15) days, and this asymmetry has been specifically negotiated and accepted by the Employee.",
    "The Employee shall give the Company not less than one hundred and eighty (180) days' prior written notice of resignation, failing which the Company shall be entitled to recover damages equivalent to six (6) months' salary.",
    "The Company may, at its sole discretion, accept or reject the Employee's resignation and may extend the effective date of relief by up to ninety (90) days beyond the contractual notice period, during which the Employee shall continue to perform all duties assigned.",
    "The notice period for confirmed Employees engaged in 'strategic roles' (as identified by the Company from time to time) shall be one hundred and twenty (120) days on the Employee's side and thirty (30) days on the Company's side.",
    "The Company shall have the right to buy out the Employee's notice on payment of basic salary for the unexpired period, while the Employee shall have no corresponding right to buy out the notice, and shall serve the full period as directed.",
    "In the event of any short-notice separation by the Employee, the Company shall be entitled to recover, as liquidated damages, a sum equivalent to basic salary for the unexpired portion of notice, and to set off the same against full and final dues.",
    "During the notice period, the Employee shall not be entitled to any variable pay, retention bonus or performance bonus, notwithstanding the accrual of such amounts for work performed prior to tendering of notice.",
    "The Company reserves the right, in its sole discretion, to waive notice in whole or in part without payment in lieu, where, in the Company's opinion, the Employee's continued presence in office poses reputational or operational risk.",
]

AGG_CORE = [
    " No relieving letter, experience certificate or full and final settlement shall be issued until the full notice period has been served or the equivalent salary deposited with the Company, at the Company's sole discretion.",
    " The Employee's accrued leave shall not be adjusted against the notice period, and no leave encashment shall be payable for unutilised leave in the event of a short-notice separation.",
    " Any period of unauthorised absence during the notice period shall entitle the Company to extend the effective date of relief by an equivalent period and to withhold all dues for such period.",
    " The Employee consents to the Company intimating prospective employers of any short-service during the notice period, and the Company shall not be liable for any adverse consequence on the Employee's future employment.",
    " The notice period shall not run during any period of paid or unpaid leave, medical leave, sabbatical or maternity leave availed by the Employee, and the effective date of relief shall be extended accordingly.",
    " The Employee shall bear all costs incurred by the Company in hiring a replacement during the notice period, including recruitment fees, training costs and transition support, which shall be deducted from the full and final settlement.",
]

AGG_CLOSE = [
    " The Employee acknowledges that the asymmetric notice arrangement reflects the Company's investment in training and confidentiality and is a material inducement for the continuation of employment.",
    " This clause shall be specifically enforceable by injunction, and the Employee waives any defence of hardship, inadequacy of consideration or unconscionability in any such proceeding.",
    " Any counter-offer accepted by the Employee shall not entitle the Employee to truncate the notice period, and the Employee shall be liable to the Company for any loss arising from non-compliance.",
    " The Employee waives the right to demand payment of salary in lieu of notice, which right shall be solely exercisable by the Company at its discretion.",
    " The Employer's obligation to pay salary during the notice period is conditional upon the Employee rendering active service in good faith, failing which salary shall be withheld and recovered against outstanding dues.",
]

ILL_OPEN = [
    "The services of the Employee, though a confirmed workman within the meaning of Section 2(s) of the Industrial Disputes Act, 1947, may be terminated by the Employer with immediate effect and without any notice or payment in lieu, notwithstanding Schedule Item 9 of the Industrial Employment (Standing Orders) Act, 1946.",
    "The Employer shall not be required to give any notice of termination or retrenchment, and the Employee hereby waives the statutory notice of one month under Section 25F of the Industrial Disputes Act, 1947 and the notice under Schedule Item 9 of the Standing Orders Act, 1946.",
    "If the Employee fails to serve the full notice period, the Employer shall be entitled to forfeit all accrued salary, leave encashment, statutory gratuity and any statutory retrenchment compensation payable to the Employee, as liquidated damages.",
    "The Employee, though confirmed as a permanent employee, agrees that the Company may terminate the employment without notice or pay in lieu, and waives the benefit of Schedule Item 9 of the Industrial Employment (Standing Orders) Act, 1946 as certified for the establishment.",
    "This clause shall override Standing Order 13 and Schedule Item 9 of the Industrial Employment (Standing Orders) Act, 1946, which provide for notice of termination, and shall bind the Employee as a permanent and unalterable condition of employment.",
    "No notice shall be due to a workman whose employment is terminated by reason of 'loss of confidence', 'change of reporting relationship' or 'organisational restructuring', notwithstanding the requirements of the certified Standing Orders and the Industrial Disputes Act, 1947.",
    "The Employee's accrued salary and statutory benefits shall be forfeited in the event of failure to serve the contractual notice, and such forfeiture shall include gratuity payable under the Payment of Gratuity Act, 1972 and retrenchment compensation under Section 25F of the Industrial Disputes Act, 1947.",
]

ILL_CORE = [
    " The Employee acknowledges that the waiver of statutory notice rights contained in this clause is a condition precedent to engagement and shall be binding notwithstanding any contrary provision of law or certified Standing Orders.",
    " The Employer shall be entitled to treat any absence of three consecutive days as an automatic cessation of employment without notice, domestic enquiry or opportunity to be heard, and the Employee's statutory remedies are hereby disclaimed.",
    " The one-month statutory notice and retrenchment compensation prescribed by Section 25F of the Industrial Disputes Act, 1947 shall not apply to the Employee, and the parties contract out of Chapter V-A of the said Act.",
    " The Employee shall not be entitled to refer any dispute arising out of notice, termination or retrenchment to a Conciliation Officer, Labour Court or Industrial Tribunal under the Industrial Disputes Act, 1947, such recourse being expressly waived by the Employee.",
    " Where the Employee's salary is forfeited towards notice shortfall, such forfeiture shall include statutory gratuity under the Payment of Gratuity Act, 1972, which the Employee is deemed to have assigned in favour of the Employer.",
]

ILL_CLOSE = [
    " This waiver is absolute and irrevocable, and shall not be reopened before any court, tribunal or authority notwithstanding any rule of public policy, statute or judicial pronouncement to the contrary.",
    " The Employee's heirs, executors and legal representatives shall be equally bound by the waivers and forfeitures herein, and no claim shall lie against the Employer for the amounts so forfeited.",
    " Any attempt by the Employee to initiate a statutory proceeding to recover forfeited dues shall be treated as a material breach entitling the Employer to recover legal costs on a full indemnity basis.",
    " The parties agree that the statutory safeguards of the Industrial Employment (Standing Orders) Act, 1946, including Schedule Item 9, shall have no application to this {doc}.",
    " This clause shall constitute a complete answer and defence to any claim by the Employee or his or her heirs for the reliefs contemplated under Indian labour legislation.",
]

DOCS = ["employment contract","appointment letter","service agreement","offer-cum-appointment letter"]

def _subs(r):
    CITIES = ["Mumbai","Bengaluru","Pune","Hyderabad","Chennai","Gurugram","Noida",
              "Ahmedabad","Chandigarh","Kolkata","Coimbatore","Jaipur","Kochi"]
    return {"nd": r.choice([30, 45, 60, 90]),
            "pnd": r.choice([7, 10, 14, 15, 21]),
            "city": r.choice(CITIES)}

def _doc_picker(i):
    random.seed(i*67+1); return random.choice(DOCS)

if __name__ == "__main__":
    from common import run_generate
    target = sys.argv[1] if len(sys.argv) > 1 else "/tmp/np.jsonl"
    plan = [
        ("standard",288,STD_OPEN,STD_CORE,STD_CLOSE,_subs,_doc_picker,CLAUSE_TYPE,INDIAN_LAW,SOURCE),
        ("aggressive",224,AGG_OPEN,AGG_CORE,AGG_CLOSE,_subs,_doc_picker,CLAUSE_TYPE,INDIAN_LAW,SOURCE),
        ("illegal",128,ILL_OPEN,ILL_CORE,ILL_CLOSE,_subs,_doc_picker,CLAUSE_TYPE,INDIAN_LAW,SOURCE),
    ]
    rows = run_generate(plan, target)
    print(f"Wrote {len(rows)} rows to {target}")
