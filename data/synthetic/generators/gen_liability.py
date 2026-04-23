"""Liability clause generator — Contract Act §73-74; CP Act 2019 §2(47)."""
import json, random, hashlib, os, sys
sys.path.insert(0, os.path.dirname(__file__))
from pools import company_name, person_name

INDIAN_LAW = "Indian Contract Act 1872 Sections 73-74; Consumer Protection Act 2019 Section 2(47)"
CLAUSE_TYPE = "liability"
SOURCE = "synth_v2"

STD_OPEN = [
    "Each party agrees to indemnify, defend and hold harmless the other party, its affiliates, directors, officers and employees against any and all third-party claims, losses, damages, costs and expenses arising directly out of the breach of any representation, warranty or obligation under this {doc}.",
    "Subject to the limits set out hereinafter, the Service Provider shall be liable to the Client for direct losses suffered by the Client arising out of the Service Provider's breach of this {doc} or negligence in the provision of the services.",
    "The Supplier shall defend, indemnify and hold the Purchaser harmless against direct losses arising from the Supplier's breach of warranty, infringement of third-party intellectual property rights or breach of the applicable statutes and regulations.",
    "The Licensor's liability under this {doc}, whether in contract, tort or otherwise, shall be limited to direct damages suffered by the Licensee as a proximate consequence of the Licensor's default, in the manner contemplated under Section 73 of the Indian Contract Act, 1872.",
    "Where a party commits a breach of any of its obligations under this {doc}, the non-breaching party shall be entitled to claim such damages as naturally arose in the usual course of things from such breach, in accordance with Section 73 of the Indian Contract Act, 1872.",
    "Each party undertakes to reimburse the other for documented losses arising from its breach of the confidentiality, data protection or compliance obligations set out in this {doc}.",
    "The Service Provider shall indemnify the Client against any penalty, fine or loss imposed by any statutory authority on account of the Service Provider's failure to comply with the Information Technology Act, 2000, the Digital Personal Data Protection Act, 2023 or other applicable laws in the performance of the services.",
    "The parties have agreed that any claim for damages under this {doc} shall be governed by Sections 73 and 74 of the Indian Contract Act, 1872 and shall be assessed strictly on the basis of direct and foreseeable loss.",
    "The Consultant shall be liable to the Company for direct losses arising from any breach of professional obligations, including any error or omission in the advisory services rendered under this {doc}.",
]

STD_CORE = [
    " The aggregate liability of either party arising out of or in connection with this {doc} shall not exceed the total fees paid or payable by the Client under this {doc} during the twelve (12) months preceding the event giving rise to the claim.",
    " Neither party shall be liable to the other for any indirect, consequential, special, exemplary or punitive damages, including loss of profits, loss of business, loss of goodwill or loss of data, save to the extent that such exclusion is impermissible under the Consumer Protection Act, 2019.",
    " The limitation of liability set out herein shall not apply in the event of (a) death or personal injury caused by gross negligence, (b) fraud or wilful misconduct, or (c) breach of the confidentiality obligations, in which cases liability shall be uncapped and governed by Section 73 of the Indian Contract Act, 1872.",
    " The parties agree that liquidated damages of Rs. {ld},00,000/- shall be treated as a genuine pre-estimate of damages under Section 74 of the Indian Contract Act, 1872, and shall be payable on occurrence of the specified breach without necessity of proof of actual loss beyond the said sum.",
    " The cap on liability shall be reciprocal, and each party's total aggregate liability shall not exceed an amount equivalent to the consideration paid or payable under this {doc} for the twelve (12) month period preceding the event giving rise to the claim.",
    " The liability of the parties shall be joint and several only where expressly stated herein, and in all other cases each party shall be liable only for its own acts, omissions and breaches.",
    " In the event of breach, the aggrieved party shall give the defaulting party a written notice of the breach and an opportunity of thirty (30) days to cure the same before any claim for damages shall lie, save in cases of irremediable breach.",
]

STD_CLOSE = [
    " Nothing in this clause shall be construed so as to limit or exclude any liability that cannot be limited or excluded by operation of law, including liability under the Consumer Protection Act, 2019 or any other consumer welfare legislation applicable in India.",
    " Each party shall, at its own cost, maintain a valid policy of commercial general liability insurance with a reputed insurer in India of not less than Rs. {ins},00,000/- in respect of the activities contemplated under this {doc}.",
    " Any claim for indemnity under this clause shall be notified to the indemnifying party within ninety (90) days of the claimant becoming aware of the event giving rise to the claim, and the indemnifying party shall be entitled to assume control of the defence of such claim.",
    " The provisions of this clause shall survive the expiry or earlier termination of this {doc} and shall continue to bind the parties in respect of any claim that accrued prior to such expiry or termination.",
    " This limitation of liability reflects a fair and reasonable allocation of risk between the parties, having regard to the consideration payable and the nature of the services, and is a material inducement for the parties to enter into this {doc}.",
    " All indemnity amounts shall be paid by the indemnifying party within thirty (30) days of determination of liability by a court of competent jurisdiction or an arbitral tribunal, failing which simple interest at eighteen per cent (18%) per annum shall accrue on the unpaid amount.",
]

AGG_OPEN = [
    "The Service Provider shall indemnify and hold the Client fully and completely harmless against any and all claims, losses, damages, costs and expenses of whatsoever nature, howsoever arising, in connection with or even remotely related to the performance or non-performance of this {doc}.",
    "The liability of the Client under this {doc} is strictly limited to the fees paid by the Client for the immediately preceding one (1) month, while the liability of the Service Provider shall be uncapped.",
    "All claims by the Customer shall be brought within thirty (30) days of the event giving rise to the claim, failing which the claim shall stand irrevocably waived and shall be barred from any forum.",
    "In the event of any breach by the Vendor, the Purchaser shall be entitled to recover, as liquidated damages, a sum equivalent to three (3) times the aggregate fees paid, without any further proof of loss.",
    "The Licensee shall indemnify the Licensor against any loss, damage or expense arising out of the Licensee's use of the software, including loss arising from the Licensor's own acts or omissions save only those arising from gross negligence.",
    "The Service Provider waives any right to claim consequential or indirect damages, but the Client reserves all such rights, including the right to claim loss of profit, loss of business opportunity and reputational loss.",
    "The cap on the Service Provider's liability shall not apply in respect of any claim arising from, inter alia, breach of service level, breach of confidentiality, infringement of third-party IP, data loss, regulatory fine or any other claim of the Client's choosing.",
    "Any limitation on the Client's right to recover shall not apply where the Client chooses, in its discretion, to classify the breach as 'material', and the Client's classification shall be final and binding.",
    "The Vendor agrees that the Purchaser shall be entitled to set off against any sum payable to the Vendor any amount claimed as indemnity, without the necessity of establishing the claim before a court or tribunal.",
]

AGG_CORE = [
    " The Service Provider's aggregate liability shall be uncapped in respect of claims arising from data security, regulatory penalty, breach of confidentiality, service level default, intellectual property infringement, tax liability or any other category of breach identified by the Client from time to time.",
    " Notwithstanding any contrary provision, the Client reserves the right to recover indirect, consequential, special and punitive damages, including but not limited to loss of goodwill, loss of anticipated profits and reputational harm, without any cap whatsoever.",
    " The Vendor shall pay the Purchaser liquidated damages of Rs. {ld},00,000/- per day of delay beyond the agreed timelines, which sum the Vendor acknowledges is reasonable and not in the nature of a penalty.",
    " All indemnity obligations of the Service Provider shall be on a full and complete first-dollar basis without any deductible, threshold, basket or cap, and shall be payable within seven (7) days of demand from the Client.",
    " The Service Provider shall additionally bear all legal costs, expenses and fees of counsel engaged by the Client in any proceedings arising out of the Service Provider's breach, regardless of the outcome of such proceedings.",
    " The Service Provider shall be liable for losses incurred by the Client's affiliates, customers, vendors and third-party stakeholders, notwithstanding that they are not parties to this {doc}, and such losses shall be indemnified in full.",
]

AGG_CLOSE = [
    " The limitations applicable to the Client under this clause shall stand displaced in the event of any breach by the Service Provider, after which the Client shall be entitled to recover its losses in full regardless of the caps herein.",
    " The parties acknowledge that this allocation of risk is reflective of the bargaining positions and is specifically not open to reconsideration by any court or arbitral tribunal under Section 74 of the Indian Contract Act, 1872.",
    " The Service Provider shall procure and maintain at its own cost a standalone indemnity insurance policy of Rs. {ins},00,000/- in favour of the Client, and shall furnish evidence thereof on a monthly basis.",
    " All remedies available under this clause shall be cumulative and additional to those available at law, and election of one remedy shall not preclude recourse to another.",
    " The Service Provider shall have no right to set off or counterclaim against any sum payable as indemnity under this clause, and shall make payment of indemnity in full without deduction or retention.",
]

ILL_OPEN = [
    "The Service Provider hereby excludes and disclaims all liability of every kind and nature, including liability arising from its own gross negligence, wilful misconduct, fraud or breach of statutory obligations under the Consumer Protection Act, 2019 or other applicable consumer welfare laws.",
    "The Consumer agrees that, notwithstanding any provision of the Consumer Protection Act, 2019, the Company's aggregate liability in respect of any and all claims shall stand absolutely limited to Rs. 500/-, and the Consumer waives any further claim for compensation.",
    "Under no circumstances whatsoever, including in cases of death or personal injury arising out of the Service Provider's gross negligence, shall the Service Provider be liable for any damages, and the Customer hereby waives and releases the Service Provider from all such claims.",
    "The Company excludes all warranties, whether express or implied, including warranties of merchantability, fitness for purpose and conformity with specification, notwithstanding the provisions of Sections 14 to 16 of the Sale of Goods Act, 1930 and the Consumer Protection Act, 2019.",
    "The Consumer hereby irrevocably waives all rights and remedies under the Consumer Protection Act, 2019, including the right to approach the District, State or National Consumer Dispute Redressal Commissions, and agrees that no claim shall be brought in respect of any defect or deficiency.",
    "The aggrieved party shall have no right to claim compensation under Section 73 of the Indian Contract Act, 1872 in respect of any breach of this {doc}, and the party in breach shall not be liable for any loss, damage or expense of any kind arising from such breach.",
    "The Service Provider's total liability, whether arising under contract, tort, statute or equity, including for gross negligence and wilful misconduct, shall not exceed Rs. 100/-, and the parties acknowledge that this cap is a condition precedent to the formation of this {doc}.",
    "The Consumer agrees that the Company shall have no liability whatsoever for any death, personal injury, property damage or financial loss, howsoever caused, including through the Company's own fault or the fault of its employees, contractors or agents.",
]

ILL_CORE = [
    " The Consumer acknowledges and agrees that this blanket exclusion applies notwithstanding any decision of the Supreme Court or National Consumer Disputes Redressal Commission to the contrary, and that the clause shall be binding and not open to challenge as an 'unfair contract term' under Section 2(47) of the Consumer Protection Act, 2019.",
    " The parties specifically contract out of the remedies available under Sections 73 and 74 of the Indian Contract Act, 1872, and accept that no damages, compensation or specific relief shall be claimable in respect of any breach, howsoever grave.",
    " The Company disclaims all liability for any deficiency of service within the meaning of Section 2(11) of the Consumer Protection Act, 2019, and the Consumer waives any corresponding right of action.",
    " Without prejudice to the generality of the foregoing, the Company shall not be liable for losses arising from its own gross negligence, fraud, wilful misconduct or breach of mandatory statutory obligations, and the Customer's sole remedy shall be a refund not exceeding Rs. 100/-.",
    " The Consumer specifically waives the benefit of any class action that may be instituted in respect of the subject matter of this {doc}, and agrees not to participate in any such class action under the Consumer Protection Act, 2019.",
    " The exclusion of liability set out herein shall apply in respect of contractual, tortious, statutory, fiduciary and restitutionary claims alike, and no form of claim shall survive this exclusion.",
]

ILL_CLOSE = [
    " This clause shall be binding on the Consumer notwithstanding any rule of law that might otherwise render such exclusion void, invalid or unenforceable under the Consumer Protection Act, 2019.",
    " The parties have taken legal advice and agree that this exclusion is reasonable and enforceable, and shall not be construed as an 'unfair contract term' within the meaning of Section 2(47) of the Consumer Protection Act, 2019.",
    " Any attempt by the Consumer to invoke consumer welfare legislation in respect of this {doc} shall be treated as a material breach entitling the Company to terminate the engagement forthwith and to recover legal costs on a full indemnity basis.",
    " The Customer, for himself or herself and on behalf of successors, heirs and assigns, releases the Service Provider from all past, present and future claims arising out of or in connection with the services rendered under this {doc}.",
    " This provision shall constitute a complete defence to any suit, petition or complaint filed by the Customer before any court, Commission or tribunal in India.",
]

DOCS = ["services agreement","master services agreement","SaaS agreement",
        "consumer terms-of-service","supply agreement","commercial contract",
        "distribution agreement","consultancy agreement"]

def _subs(r):
    return {"ld": r.randint(5, 100), "ins": r.randint(25, 500)}

def _doc_picker(i):
    random.seed(i*59+3); return random.choice(DOCS)

if __name__ == "__main__":
    from common import run_generate
    target = sys.argv[1] if len(sys.argv) > 1 else "/tmp/l.jsonl"
    plan = [
        ("standard", 288, STD_OPEN, STD_CORE, STD_CLOSE, _subs, _doc_picker,
         CLAUSE_TYPE, INDIAN_LAW, SOURCE),
        ("aggressive", 224, AGG_OPEN, AGG_CORE, AGG_CLOSE, _subs, _doc_picker,
         CLAUSE_TYPE, INDIAN_LAW, SOURCE),
        ("illegal", 128, ILL_OPEN, ILL_CORE, ILL_CLOSE, _subs, _doc_picker,
         CLAUSE_TYPE, INDIAN_LAW, SOURCE),
    ]
    rows = run_generate(plan, target)
    print(f"Wrote {len(rows)} rows to {target}")
