"""Termination clause generator — ID Act 1947 §25F. Modular composition."""
import json, random, hashlib, os, sys
sys.path.insert(0, os.path.dirname(__file__))

INDIAN_LAW = "Industrial Disputes Act 1947 Section 25F"
CLAUSE_TYPE = "termination"
SOURCE = "synth_v2"

CITIES = ["Mumbai","Bengaluru","Pune","Hyderabad","Chennai","Gurugram","Noida",
          "Ahmedabad","Chandigarh","Kolkata","Indore","Coimbatore","Jaipur",
          "Kochi","Lucknow","Bhubaneswar","Visakhapatnam"]

# ========== STANDARD ==========
STD_OPEN = [
    "Either party may terminate this employment by giving not less than {nd} days' prior written notice to the other or by tendering basic salary in lieu of such notice.",
    "The Company may terminate the services of the Employee on grounds of redundancy, unsatisfactory performance or breach of material terms of this {doc} by serving a written notice of {nd} days.",
    "Subject to the provisions of the Industrial Disputes Act, 1947 and the applicable certified Standing Orders, the employment hereunder may be brought to an end by mutual consent or by notice in writing.",
    "The Employer reserves the right to terminate the employment of the Employee on any of the grounds enumerated in Schedule I of the Model Standing Orders, including misconduct, habitual absence, theft or dishonesty.",
    "The services of the Employee may be terminated in the event of redundancy arising from restructuring, divestment or closure of the business unit at {city}.",
    "It is hereby agreed that the Employee may resign from service at any time by tendering {nd} days' prior written notice to the Human Resources department.",
    "This {doc} may be determined by either party without assigning any reason by serving {nd} days' prior written notice in writing.",
    "The Company may terminate the Employee forthwith in the case of gross misconduct, wilful insubordination, fraud or conviction for an offence involving moral turpitude, following a domestic enquiry.",
    "Upon the Employee being declared medically unfit for continued service by a Medical Board constituted by the Company, the employment may be terminated on compassionate grounds.",
    "Either party may bring this employment to an end through a mutual separation arrangement recorded in writing and signed by both parties.",
]

STD_CORE = [
    " In all cases where the Employee is a workman within the meaning of Section 2(s) of the Industrial Disputes Act, 1947 and the termination constitutes retrenchment, the Company shall pay one (1) month's notice pay and retrenchment compensation calculated at fifteen (15) days' average pay for every completed year of continuous service in compliance with Section 25F of the said Act.",
    " Where the termination amounts to retrenchment, the Employee shall be entitled to the statutory compensation prescribed under Section 25F of the Industrial Disputes Act, 1947, in addition to all earned wages, leave encashment and gratuity, if any.",
    " The Employer shall ensure strict compliance with the notice and compensation requirements of Section 25F of the Industrial Disputes Act, 1947 in respect of workmen who have rendered not less than 240 days of continuous service in the preceding twelve months.",
    " Prior to any termination on grounds of misconduct, a charge-sheet shall be issued, a domestic enquiry shall be conducted in accordance with principles of natural justice and the Employee shall be given a reasonable opportunity of being heard.",
    " In the case of retrenchment, the Employer shall follow the 'last come first go' principle set out in Section 25G of the Industrial Disputes Act, 1947 and shall intimate the appropriate Government as required under Section 25F(c).",
    " The statutory gratuity payable under Section 4 of the Payment of Gratuity Act, 1972 shall be remitted to the Employee within thirty (30) days of the effective date of separation, along with earned leave encashment.",
    " Where the termination is on ground of medical incapacity, the Employer shall explore avenues for redeployment before effecting termination, and shall in any event comply with the statutory entitlements of the Employee.",
    " The Employer shall additionally comply with the notice and compensation provisions of the applicable State Shops and Establishments Act or the certified Standing Orders, whichever is more beneficial to the Employee.",
]

STD_CLOSE = [
    " All company property, including identity cards, access cards, laptops and confidential materials, shall be returned on the last working day, and the full and final settlement shall be effected within thirty (30) days thereof.",
    " The Employer shall issue an experience certificate and a relieving letter upon the Employee completing all exit formalities and returning company property in good order.",
    " The Employee shall continue to be bound by the obligations of confidentiality, non-solicitation and intellectual property assignment contained in this {doc} notwithstanding the cessation of employment.",
    " This clause shall be without prejudice to the right of either party to claim damages for any breach of the {doc} committed prior to its termination.",
    " Any unresolved grievance arising out of the termination may be referred by the Employee to the Conciliation Officer appointed under the Industrial Disputes Act, 1947 having territorial jurisdiction over {city}.",
    " The provisions of this clause shall be read together with the applicable certified Standing Orders as approved by the Certifying Officer under the Industrial Employment (Standing Orders) Act, 1946.",
    " The Employer shall report the separation to the Regional Provident Fund Commissioner, the Employees' State Insurance Corporation and the applicable statutory authorities within the prescribed timelines.",
]

# ========== AGGRESSIVE ==========
AGG_OPEN = [
    "Notwithstanding anything contained hereinabove, the Employee shall give the Company ninety (90) days' prior written notice of resignation, while the Company shall be entitled to terminate this {doc} on fifteen (15) days' notice.",
    "The Company may terminate this employment at any time for 'material breach' as determined solely by the Management Committee, whose decision shall be final and not subject to review.",
    "This {doc} may be terminated by the Company by serving seven (7) days' notice to the Employee at {city} on grounds including, without limitation, non-achievement of targets or restructuring.",
    "The Employer reserves the unilateral right to accelerate the notice period and direct the Employee to demit office on a date earlier than that provided by the Employee's notice of resignation, without payment of salary for the foreshortened period.",
    "The Company may terminate the Employee summarily and without notice in any case where, in the Company's sole assessment, the Employee's continued presence in office would affect employee morale or the Company's goodwill.",
    "Resignation by the Employee during the currency of this Agreement shall require six (6) months' prior written notice, whereas termination by the Company may be effected on thirty (30) days' notice or less at the Company's discretion.",
    "Where the Company elects to terminate the services of the Employee, it shall be entitled to place the Employee on garden leave for the duration of the notice period on payment of basic salary alone.",
    "The Company may terminate the Employee for 'cause' at any time without notice, and the term 'cause' as used herein shall be determined by the Chief People Officer in his or her absolute discretion.",
    "The Company, if in receipt of any adverse feedback regarding the Employee from a client, vendor or member of senior management, may terminate the employment forthwith without the necessity of a domestic enquiry.",
]

AGG_CORE = [
    " In the event of termination by the Company, all variable pay, retention bonus, joining bonus (including pro rata recovery), sign-on cash and stock-linked incentives not yet vested shall stand forfeited without the necessity of any further action.",
    " The Employee shall not be entitled to any severance, ex gratia or notice pay beyond the statutory minimum expressly mandated by law, and shall specifically not be entitled to any payment in lieu of unexpired notice of the Company's election.",
    " During the notice period or any garden leave, the Employee shall render knowledge transfer as directed by the Company, shall be available on reasonable demand beyond regular working hours and shall not be entitled to claim overtime or any additional remuneration.",
    " The Employee shall continue to be bound by the non-compete and non-solicitation covenants set out in this {doc} for a period of twelve (12) months following the effective date of separation, irrespective of the cause of termination.",
    " In the event of a short-notice termination by the Company, payment of only the basic component of salary shall be made for the unexpired notice period, to the exclusion of all allowances, reimbursements and variable components.",
    " The Company shall be at liberty to adjust any alleged dues owed by the Employee, including training costs, asset recovery and liquidated damages, against the full and final settlement payable on termination, without the necessity of judicial adjudication.",
    " The Employee waives any claim to re-employment, re-deployment or reinstatement in the event of termination, and shall not solicit employment with the Company, its affiliates or its clients for a period of twenty-four (24) months thereafter.",
]

AGG_CLOSE = [
    " The Employee acknowledges that the asymmetric notice provided in this clause is a material inducement for the Company to enter into this {doc} and has been accepted with full understanding of its implications.",
    " Any dispute arising out of or in connection with the termination shall be referred to the sole arbitration of an arbitrator appointed by the Company, with seat at {city}.",
    " The Employee shall have no right to raise an industrial dispute or seek reinstatement through the Conciliation Officer, Labour Court or Industrial Tribunal in respect of any termination effected under this clause.",
    " The Company's determination in respect of any ground of termination shall be final and the Employee expressly waives the right to seek judicial review of such determination.",
    " This clause shall survive the termination of this {doc} and the post-termination restrictive covenants shall be specifically enforceable by injunction in addition to any claim for damages.",
    " The Employee acknowledges that it is impracticable to compute the Company's loss on termination and accordingly accepts the liquidated damages and forfeiture provisions set out herein as reasonable.",
]

# ========== ILLEGAL ==========
ILL_OPEN = [
    "Notwithstanding any provision of the Industrial Disputes Act, 1947 to the contrary, the Employee acknowledges that this employment is on an 'at-will' basis and may be terminated by the Employer at any time without notice and without any compensation whatsoever.",
    "The services of the Employee, though a workman within the meaning of Section 2(s) of the Industrial Disputes Act, 1947, may be terminated forthwith and without notice on the ground of 'loss of confidence' as determined by the Plant Head at {city}.",
    "The Employer may terminate this contract of employment instantaneously by oral communication followed by a confirmatory e-mail, and the Employee hereby waives the rights conferred by Section 25F of the Industrial Disputes Act, 1947.",
    "This agreement may be terminated unilaterally by the Company at any time and for any reason, and the Employee shall have no right to raise an industrial dispute before any Labour Court or Industrial Tribunal in respect of such termination.",
    "It is expressly agreed that termination of the Employee's services shall never be characterised as 'retrenchment' within the meaning of Section 2(oo) of the Industrial Disputes Act, 1947, regardless of the actual circumstances.",
    "The Company reserves the right to treat any unauthorised absence of three (3) consecutive days as an automatic cessation of employment, without the necessity of any notice, domestic enquiry or service of show-cause notice.",
    "The probationary employment of the Employee at the Company's facility at {city} may be terminated at any time without notice and without payment of any kind, and such right shall continue even after confirmation as a permanent workman.",
    "The Employee expressly and irrevocably waives the protection of Chapter V-A of the Industrial Disputes Act, 1947 in consideration of the terms of employment offered herein.",
    "For the avoidance of doubt, the Employee's engagement, though styled as an employment contract, shall be deemed a pure commercial arrangement not governed by the Industrial Disputes Act, 1947.",
]

ILL_CORE = [
    " The Employee expressly waives all rights and remedies available under the Industrial Disputes Act, 1947 and the rules framed thereunder, including any right to retrenchment compensation, notice pay or reinstatement.",
    " No retrenchment compensation shall be payable under Section 25F of the Industrial Disputes Act, 1947, notwithstanding that the Employee may have completed more than five years of continuous service.",
    " The Employee hereby waives the right to one month's prior written notice or pay in lieu thereof, as well as the retrenchment compensation of fifteen (15) days' average pay per completed year of service, both as mandated under Section 25F.",
    " This waiver of statutory rights is given in consideration of the initial employment offer and the Employee acknowledges that this is a condition precedent to engagement.",
    " Any termination effected under this clause shall not attract the procedural or substantive safeguards of the Industrial Disputes Act, 1947 or the Industrial Employment (Standing Orders) Act, 1946, and no enquiry or hearing shall be necessary.",
    " The Company shall not be required to obtain prior permission from the appropriate Government even in cases where Chapter V-B of the Industrial Disputes Act, 1947 would otherwise apply.",
    " The Employee agrees that all accrued salary, bonus, leave encashment, statutory gratuity and retrenchment compensation (if any) shall be forfeited in favour of the Company towards liquidated damages.",
]

ILL_CLOSE = [
    " This clause shall operate as an absolute bar to any claim before the Conciliation Officer, Labour Court or Industrial Tribunal at {city} or elsewhere.",
    " The Employee acknowledges that the above waiver is given freely and with full understanding, and shall not be revisited under any circumstance.",
    " Any purported claim under the Industrial Disputes Act, 1947 shall be treated as a breach of this {doc} and shall entitle the Company to recover damages, including legal costs on a full indemnity basis.",
    " The Employer shall be entitled to enforce the terms of this clause notwithstanding any contrary provision of law, rule, notification, award, settlement or certified Standing Orders.",
    " The parties have agreed that the statutory safeguards of the labour legislation of India shall have no application to this engagement, and this agreement shall be construed strictly in accordance with its express terms.",
]

DOC_CHOICES = ["employment contract","appointment letter","services agreement",
               "franchise agreement","distribution agreement"]

def _render(open_pool, core_pool, close_pool, seed_idx):
    random.seed(seed_idx * 37 + 11)
    nd = random.choice([15, 30, 45, 60, 90])
    city = random.choice(CITIES)
    doc = random.choice(DOC_CHOICES)
    parts = [
        random.choice(open_pool).format(nd=nd, doc=doc, city=city),
        random.choice(core_pool).format(nd=nd, doc=doc, city=city),
        random.choice(close_pool).format(nd=nd, doc=doc, city=city),
    ]
    return "".join(parts), doc

def _doc_for(text):
    low = text.lower()
    if "franchise" in low: return "franchise agreement"
    if "distribut" in low: return "distribution agreement"
    if "consultan" in low: return "consultancy agreement"
    if "appointment letter" in low: return "appointment letter"
    return random.choice(["employment contract","services agreement","appointment letter"])

def generate():
    out, seen = [], set()
    def _emit(body, risk, doc):
        h = hashlib.sha1(body.encode()).hexdigest()
        if h in seen: return False
        seen.add(h)
        out.append({"clause_text": body, "clause_type": CLAUSE_TYPE,
                    "risk_level": risk, "indian_law": INDIAN_LAW,
                    "doc_type": _doc_for(body), "source": SOURCE})
        return True
    for risk, n, (o, c, cl) in [("standard",288,(STD_OPEN,STD_CORE,STD_CLOSE)),
                                 ("aggressive",224,(AGG_OPEN,AGG_CORE,AGG_CLOSE)),
                                 ("illegal",128,(ILL_OPEN,ILL_CORE,ILL_CLOSE))]:
        i, tries = 0, 0
        while sum(1 for r in out if r["risk_level"]==risk) < n:
            i += 1; tries += 1
            body, doc = _render(o, c, cl, i)
            _emit(body, risk, doc)
            if tries > 80000: break
    return out

if __name__ == "__main__":
    target = sys.argv[1] if len(sys.argv) > 1 else "/tmp/t.jsonl"
    rows = generate()
    with open(target, "a") as f:
        for r in rows: f.write(json.dumps(r, ensure_ascii=False) + "\n")
    print(f"Wrote {len(rows)} rows to {target}")
