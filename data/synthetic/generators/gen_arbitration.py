"""Arbitration clause generator.
Statute: Arbitration and Conciliation Act 1996 (§11, §20, §28, §34).
Risk split: 288 standard / 224 aggressive / 128 illegal = 640 rows.
"""
import json, random, hashlib, os, sys
sys.path.insert(0, os.path.dirname(__file__))
from pools import (company_name, person_name, city_and_locality,
                   inr_monthly, EMPLOYMENT_DOCS, COMMERCIAL_DOCS)

INDIAN_LAW = "Arbitration and Conciliation Act 1996 (Section 11; Section 34)"
CLAUSE_TYPE = "arbitration"
SOURCE = "synth_v2"

SEAT_CITIES = ["Mumbai", "New Delhi", "Bengaluru", "Hyderabad", "Chennai",
               "Gurugram", "Pune", "Kolkata", "Ahmedabad", "Noida"]

INSTITUTIONS = [
    ("the Delhi International Arbitration Centre", "DIAC Arbitration Rules, 2023"),
    ("the Mumbai Centre for International Arbitration", "MCIA Arbitration Rules, 2016"),
    ("the Indian Council of Arbitration", "ICA Rules of Domestic Commercial Arbitration"),
    ("the Nani Palkhivala Arbitration Centre", "NPAC Rules of Arbitration"),
    ("the International Centre for Alternative Dispute Resolution", "ICADR Arbitration Rules"),
]

FOREIGN_INSTITUTIONS = [
    ("the Singapore International Arbitration Centre", "SIAC Rules 2025", "Singapore"),
    ("the International Chamber of Commerce", "ICC Rules of Arbitration 2021", "Paris"),
    ("the London Court of International Arbitration", "LCIA Arbitration Rules 2020", "London"),
]

DOC_TYPES = [
    "commercial contract", "services agreement", "shareholder agreement",
    "joint venture agreement", "master services agreement",
    "distribution agreement", "supply agreement", "employment contract",
    "consultancy agreement", "franchise agreement",
]

# ===================== STANDARD (lawful, balanced) =====================
STD_OPENERS = [
    "Any dispute, difference or claim arising out of or in connection with this Agreement, including any question regarding its existence, validity, breach or termination, shall be referred to and finally resolved by arbitration.",
    "All disputes arising out of or in relation to this Agreement which cannot be amicably resolved by the parties within thirty (30) days of written notice shall be referred to arbitration.",
    "In the event of any dispute or difference arising between the parties hereto touching upon the construction, meaning or effect of this Agreement, the matter shall be referred to arbitration.",
    "Save and except matters for which interim relief is expressly sought before a competent court, all disputes arising hereunder shall be resolved by arbitration.",
    "It is hereby agreed that any controversy or claim arising out of or relating to this Agreement, or the breach thereof, shall be settled by arbitration.",
    "Any and all disputes arising from or in connection with this Agreement shall be referred for resolution by arbitration upon the written notice of either party.",
    "The parties shall endeavour to amicably settle any dispute arising out of or in connection with this Agreement, failing which such dispute shall be referred to arbitration.",
    "Every dispute, difference, claim or question relating to the interpretation, performance or breach of this Agreement shall be referred to arbitration.",
]

STD_CORES = [
    "The arbitral tribunal shall consist of a sole arbitrator to be appointed by mutual consent of the parties in accordance with Section 11 of the Arbitration and Conciliation Act, 1996, failing which either party may apply to the Hon'ble High Court of {state} for appointment.",
    "The tribunal shall consist of three arbitrators, with each party appointing one arbitrator and the two arbitrators so appointed jointly nominating the presiding arbitrator, in accordance with Section 11 of the Arbitration and Conciliation Act, 1996.",
    "The arbitration shall be conducted by a sole arbitrator mutually appointed by the parties; in the event of disagreement, the appointment shall be made by the Hon'ble High Court of {state} under Section 11(6) of the Arbitration and Conciliation Act, 1996.",
    "The arbitration shall be administered by {institution_name} in accordance with the {institution_rules} as in force at the time of commencement of arbitration.",
    "A sole arbitrator shall be appointed by mutual agreement, failing which an appointment shall be sought from {institution_name} in accordance with the {institution_rules}.",
    "The tribunal of three arbitrators shall be constituted under the {institution_rules} and the arbitration shall be administered by {institution_name}.",
    "The arbitrator shall be jointly nominated by the parties within thirty (30) days of the receipt of a notice invoking arbitration and, failing such nomination, the nomination shall be made under Section 11 of the Arbitration and Conciliation Act, 1996.",
]

STD_CLOSERS = [
    "The seat and venue of arbitration shall be {seat}, and the proceedings shall be conducted in the English language. The arbitral award shall be final and binding, subject only to challenge on the grounds specified in Section 34 of the Arbitration and Conciliation Act, 1996.",
    "The juridical seat of arbitration shall be {seat}, and the award shall be enforceable in accordance with Part I of the Arbitration and Conciliation Act, 1996. The courts at {seat} shall have exclusive supervisory jurisdiction in relation to the arbitration.",
    "The arbitration shall be seated at {seat} and shall be governed by the substantive laws of India. The award rendered shall be final and binding on the parties, save for challenges permissible under Section 34 of the said Act.",
    "The seat of arbitration shall be {seat} and the language of the proceedings shall be English. Each party shall bear its own costs unless the tribunal, in its discretion, determines otherwise.",
    "The place and seat of arbitration shall be {seat}. The arbitrator shall render the award expeditiously and in any event within the statutory timeline under Section 29A of the Arbitration and Conciliation Act, 1996, as extended from time to time.",
    "{seat} shall be the seat of arbitration and the courts at {seat} shall alone have exclusive jurisdiction in respect of any application under Section 9 or Section 34 of the Arbitration and Conciliation Act, 1996.",
    "The seat of arbitration shall be {seat}, and in accordance with Section 28 of the Arbitration and Conciliation Act, 1996, the substantive law governing the dispute shall be the laws of India.",
]

# ===================== AGGRESSIVE (valid but one-sided / borderline) =====================
AGG_TEMPLATES = [
    ("In the event of any dispute, difference or claim arising between the parties, "
     "the matter shall be referred to arbitration by a sole arbitrator to be nominated "
     "by {party_caps} from its panel of empanelled arbitrators, with the nomination communicated to the counterparty "
     "for its information. The seat and venue of arbitration shall be {seat} and the venue shall not be "
     "altered without the prior written consent of {party_caps}. The parties agree that the fees of the arbitrator "
     "and all administrative costs shall be borne equally by the parties regardless of the outcome of the proceedings, "
     "and no party shall be entitled to costs unless the tribunal awards the same in exceptional circumstances."),
    ("Any dispute arising out of or in connection with this Agreement shall be referred to arbitration to be "
     "conducted in accordance with the Arbitration and Conciliation Act, 1996. The party invoking arbitration "
     "shall deposit the entire estimated tribunal fee of Rs. {fee},00,000/- with {party_caps} within fifteen (15) days of issuing "
     "the notice of arbitration, failing which the claim shall stand withdrawn. The seat of arbitration shall be {seat}, "
     "and the award of the arbitrator shall, save in the case of manifest arithmetical error, be treated as final "
     "and non-appealable to the maximum extent permissible under the said Act."),
    ("All disputes shall be referred to arbitration by a panel of three arbitrators, with {party_caps} having "
     "the right to nominate the presiding arbitrator. Each party shall nominate one arbitrator within seven (7) days "
     "of the notice of arbitration, failing which the default nomination shall be made by {party_caps}. The seat and "
     "exclusive venue of arbitration shall be {seat} and no party shall raise any objection as to the forum, notwithstanding "
     "the location of performance under this Agreement."),
    ("Any dispute arising between the parties shall, in the first instance, be referred to the senior management of "
     "{party_caps} for resolution within thirty (30) days. If not amicably resolved, the dispute shall be referred to a "
     "sole arbitrator appointed by {party_caps} in accordance with its internal dispute resolution policy, whose decision "
     "shall be final and binding. The seat of arbitration shall be {seat}. The party initiating the claim shall "
     "bear the arbitrator's fees and the administrative expenses of the arbitration in full."),
    ("The arbitration shall be conducted in a fast-track mode under Section 29B of the Arbitration and Conciliation Act, 1996, "
     "and the parties agree that the entire proceedings shall be concluded and the award rendered within ninety (90) days of the "
     "first procedural hearing. No extension shall be granted save with the written consent of {party_caps}, which may be "
     "withheld at its sole discretion. The seat of arbitration shall be {seat}."),
    ("Notwithstanding anything to the contrary, the parties agree that {party_caps} shall have the exclusive and unilateral "
     "right to elect whether the dispute shall be resolved by arbitration or by civil litigation before the courts of {seat}. "
     "If arbitration is elected, the tribunal shall be constituted under Section 11 of the Arbitration and Conciliation Act, 1996, "
     "with the seat at {seat} and the proceedings in English. The counterparty shall be bound by the election of forum so made."),
    ("Any dispute arising hereunder shall be referred to a sole arbitrator, and the parties agree that the arbitrator shall be "
     "an individual empanelled with {party_caps} and drawn from its pre-approved panel of former judges. The seat of arbitration "
     "shall be {seat}. The arbitrator's fees shall be fixed at Rs. {fee},00,000/- and shall be paid equally by the parties within "
     "fifteen (15) days of the arbitrator's appointment, failing which the defaulting party's claim shall stand abandoned."),
    ("In the event of any dispute, {party_caps} reserves the right to consolidate such dispute with any other ongoing arbitration "
     "or court proceeding involving similar issues, and the counterparty hereby consents to such consolidation. The consolidated "
     "arbitration shall be seated at {seat}, with proceedings in English, and the tribunal so constituted shall have jurisdiction "
     "over all consolidated matters notwithstanding the absence of express consent of other claimants."),
    ("Any claim arising out of this Agreement must be notified in writing within sixty (60) days of the event giving rise to "
     "such claim, failing which the claim shall be deemed waived and shall not be arbitrable. Arbitration, where invoked, shall "
     "be by a sole arbitrator appointed by {party_caps} and shall be seated at {seat}. The counterparty agrees to waive its "
     "right to seek interim relief from any court pending constitution of the tribunal."),
    ("The parties agree that the arbitration shall be conducted in the language and at the venue elected by {party_caps}, "
     "provided the seat remains in India. The arbitrator shall be a person nominated from the panel maintained by {party_caps} "
     "and the counterparty shall have no right of challenge save on grounds of manifest bias demonstrable by clear and "
     "convincing evidence. The award shall be final and binding."),
]

# ===================== ILLEGAL (textually contradict statute) =====================
ILL_TEMPLATES = [
    # Perkins Eastman — unilateral appointment
    ("All disputes arising out of or in connection with this Agreement shall be referred to a sole arbitrator who shall be "
     "appointed solely and exclusively by {party_caps} at its absolute discretion, and the counterparty hereby irrevocably "
     "waives any objection to such unilateral appointment, including on the grounds specified in the Fifth and Seventh Schedules "
     "to the Arbitration and Conciliation Act, 1996. The seat of arbitration shall be {seat}."),
    ("The arbitrator shall be nominated exclusively by the Chairman and Managing Director of {party_caps}, and the said "
     "nomination shall be final, binding and not open to challenge before any court or authority. The counterparty expressly "
     "waives its right to seek substitution or termination of the mandate of the arbitrator under Sections 12, 13 or 14 of "
     "the Arbitration and Conciliation Act, 1996."),
    # Section 34 waiver
    ("The parties hereby expressly and unconditionally waive the right to challenge, set aside, revise or appeal against "
     "any arbitral award rendered under this Agreement, including any right of challenge under Section 34 of the "
     "Arbitration and Conciliation Act, 1996. The award shall be treated as final, binding and non-appealable on all grounds "
     "whatsoever. The seat of arbitration shall be {seat}."),
    ("The parties agree that the award rendered by the arbitral tribunal shall not be subject to any challenge, correction "
     "or setting aside proceedings whatsoever and the parties hereby waive the remedies available to them under Section 34 "
     "and Section 37 of the Arbitration and Conciliation Act, 1996. Any attempt by either party to initiate such proceedings "
     "shall constitute a material breach of this Agreement."),
    # Foreign seat in consumer / employment contract (void under CP Act framework)
    ("Notwithstanding that this is a consumer agreement executed in India between an Indian resident and {party_caps}, "
     "the parties agree that the seat and venue of arbitration shall be {foreign_seat} and the arbitration shall be administered by {foreign_rules}, "
     "and the Indian consumer hereby waives all rights to approach the Consumer Commissions, Consumer Courts or "
     "Indian courts in respect of any dispute arising hereunder."),
    ("This employment contract shall be governed by and interpreted in accordance with the laws of {foreign_seat}, "
     "and any dispute between the Employer and the Employee, including claims relating to wages, wrongful termination or "
     "statutory entitlements under Indian labour law, shall be exclusively arbitrated by {foreign_rules} with seat "
     "at {foreign_seat}. The Employee waives the right to approach any Indian Labour Court or Industrial Tribunal."),
    # Unilateral appointment variant #2
    ("In the event of any dispute, the arbitrator shall be one of the three persons whose names are pre-printed in Annexure A "
     "to this Agreement, all of whom are former employees or legal advisors of {party_caps}, and the selection among the three "
     "shall be made solely by {party_caps}. The counterparty expressly waives any objection to the independence or impartiality "
     "of the said arbitrator."),
    # Bar on court approach for interim relief / bypassing mandatory statutory protections
    ("The parties agree that no application shall be made by the counterparty under Section 9 or Section 17 of the Arbitration "
     "and Conciliation Act, 1996 for interim measures, and any such application shall be treated as a breach of this clause. "
     "The right to approach any court for interim protection is hereby waived in favour of {party_caps} alone, which shall be "
     "entitled to seek interim relief in any jurisdiction it may elect."),
    # Waiving right under sections 12/13/14 (ineligibility)
    ("The arbitrator shall be the in-house General Counsel or Company Secretary of {party_caps} from time to time, and "
     "the parties agree that such person shall be deemed independent and impartial notwithstanding the bar contained in the "
     "Seventh Schedule to the Arbitration and Conciliation Act, 1996. The counterparty specifically and unconditionally waives "
     "the ineligibility so prescribed."),
    # Contracting out entirely
    ("The parties agree that the provisions of Part I of the Arbitration and Conciliation Act, 1996, including the provisions "
     "relating to appointment, challenge, termination and setting aside, shall not apply to this arbitration, and the arbitration "
     "shall be conducted in such manner as {party_caps} may from time to time prescribe by written communication to the counterparty."),
]

# -------------------- Generation mechanics --------------------
def _state_from_seat(seat):
    from pools import CITY_TO_STATE
    key = "Delhi" if seat == "New Delhi" else seat
    return CITY_TO_STATE.get(key, "the State in which the seat is located")

def _render_standard(seed_idx):
    random.seed(seed_idx * 17 + 5)
    opener = random.choice(STD_OPENERS)
    core = random.choice(STD_CORES)
    closer = random.choice(STD_CLOSERS)
    seat = random.choice(SEAT_CITIES)
    inst_name, inst_rules = random.choice(INSTITUTIONS)
    state = _state_from_seat(seat)
    doc = random.choice(DOC_TYPES)
    body = " ".join([opener, core.format(institution_name=inst_name,
                                          institution_rules=inst_rules,
                                          state=state),
                     closer.format(seat=seat)])
    # small varied addenda to increase uniqueness
    if random.random() < 0.35:
        addenda = random.choice([
            " The arbitrator may, at his or her discretion, conduct the proceedings in a virtual mode subject to the consent of both parties.",
            " The parties shall maintain strict confidentiality over the proceedings, pleadings and the award, save as may be required by applicable law or for enforcement.",
            f" The costs of arbitration shall be apportioned by the tribunal in accordance with the outcome, subject to a reasoned order.",
            " Either party may, prior to or during the arbitration, apply to a competent court for interim measures under Section 9 of the said Act without waiver of its rights.",
        ])
        body = body + addenda
    return body, doc

def _render_aggressive(seed_idx):
    random.seed(seed_idx * 19 + 11)
    tmpl = random.choice(AGG_TEMPLATES)
    co = company_name()
    seat = random.choice(SEAT_CITIES)
    fee = random.randint(5, 45)
    body = tmpl.format(party_caps=co, seat=seat, fee=fee)
    doc = random.choice(DOC_TYPES)
    return body, doc

def _render_illegal(seed_idx):
    random.seed(seed_idx * 23 + 13)
    tmpl = random.choice(ILL_TEMPLATES)
    co = company_name()
    seat = random.choice(SEAT_CITIES)
    fi_name, fi_rules, fi_loc = random.choice(FOREIGN_INSTITUTIONS)
    body = tmpl.format(party_caps=co, seat=seat,
                       foreign_seat=fi_loc, foreign_rules=fi_name[4:] + " in accordance with the " + fi_rules if fi_name.startswith("the ") else fi_name + " in accordance with the " + fi_rules)
    # Illegal consumer / employment-specific doc types where applicable
    if "consumer" in body.lower():
        doc = "consumer terms-of-service"
    elif "employment" in body.lower() or "Employee" in body:
        doc = "employment contract"
    else:
        doc = random.choice(DOC_TYPES)
    return body, doc

def generate(total=640, split=(288, 224, 128)):
    out = []
    seen = set()
    def _emit(body, doc, risk):
        h = hashlib.sha1(body.encode("utf-8")).hexdigest()
        if h in seen:
            return False
        seen.add(h)
        out.append({
            "clause_text": body,
            "clause_type": CLAUSE_TYPE,
            "risk_level": risk,
            "indian_law": INDIAN_LAW,
            "doc_type": doc,
            "source": SOURCE,
        })
        return True
    n_std, n_agg, n_ill = split
    i = 0
    tries = 0
    while sum(1 for r in out if r["risk_level"]=="standard") < n_std:
        i += 1; tries += 1
        body, doc = _render_standard(i)
        _emit(body, doc, "standard")
        if tries > 30000: break
    i = 0; tries = 0
    while sum(1 for r in out if r["risk_level"]=="aggressive") < n_agg:
        i += 1; tries += 1
        body, doc = _render_aggressive(i)
        _emit(body, doc, "aggressive")
        if tries > 30000: break
    i = 0; tries = 0
    while sum(1 for r in out if r["risk_level"]=="illegal") < n_ill:
        i += 1; tries += 1
        body, doc = _render_illegal(i)
        _emit(body, doc, "illegal")
        if tries > 30000: break
    return out

if __name__ == "__main__":
    import sys
    target_path = sys.argv[1] if len(sys.argv) > 1 else "/tmp/arb.jsonl"
    rows = generate()
    with open(target_path, "a") as f:
        for r in rows:
            f.write(json.dumps(r, ensure_ascii=False) + "\n")
    print(f"Wrote {len(rows)} to {target_path}")
