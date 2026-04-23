"""Non-compete top-up — Indian Contract Act 1872 §27. +560 rows."""
import json, random, hashlib, os, sys
sys.path.insert(0, os.path.dirname(__file__))

INDIAN_LAW = "Indian Contract Act 1872 Section 27"
CLAUSE_TYPE = "non_compete"
SOURCE = "synth_v2"

STD_OPEN = [
    "The Employee shall, during the subsistence of his or her employment with {company}, devote whole time and attention exclusively to the business of the Company and shall not engage in any parallel trade or occupation, directly or indirectly, whether for consideration or otherwise.",
    "It is expressly agreed between the parties that during the currency of this {doc}, the Consultant shall not, without the prior written consent of {company}, render advisory, strategic or technical services of a similar nature to any competing entity.",
    "The restrictive covenant contained in this clause shall operate only during the period of active employment and shall automatically cease upon cessation thereof, in compliance with Section 27 of the Indian Contract Act, 1872.",
    "The Employee covenants with {company} that during the tenure of employment at its {city} office, he or she shall not, whether on own account or as a director, partner, employee or consultant of any other entity, engage in the business of {industry}.",
    "The parties acknowledge that, by reason of Section 27 of the Indian Contract Act, 1872, any post-employment restraint on lawful profession or trade shall be void, and accordingly the restrictive covenants set out herein shall operate only during the currency of employment.",
    "During the term of engagement under this {doc}, the Consultant shall not accept any assignment from a direct competitor of {company} carrying on business in {industry} in India, without the prior written consent of the Company.",
    "The Employee shall not, during the subsistence of employment, canvass, solicit or procure orders or customers of the Company for the benefit of any other person or entity, including for himself or herself.",
    "The Employee recognises that, in consideration of access to confidential information and trade secrets of {company}, it is reasonable for the Employer to expect exclusivity during employment, and accordingly the Employee undertakes not to engage in any parallel employment or consultancy during the term.",
]

STD_CORE = [
    " The Employee further agrees that during the subsistence of this {doc}, he or she shall not solicit, on own account or for any other person, the employment of any employee of {company}, and this exclusivity is understood to be an integral part of the employment bargain.",
    " The restraint contained in this clause is limited in scope to competitive activity that would use or build upon the Company's confidential information, and shall in no event extend beyond the duration of active employment with {company}.",
    " The parties record that nothing in this clause shall restrict the Employee, on cessation of employment, from practising his or her lawful profession, trade or business, consistent with the protection afforded by Section 27 of the Indian Contract Act, 1872.",
    " In consideration of a non-compete fee of Rs. {fee},00,000/- paid at the time of sale of goodwill, the Seller undertakes not to carry on a similar business within {city} for a period of three (3) years in accordance with the exception contained in Section 27 of the said Act.",
    " The Consultant agrees that during the term of this consultancy with {company}, he or she shall not accept any engagement that would create a conflict of interest with the Company's business in {industry}, and shall disclose any potential conflict in writing.",
    " The Employee's obligations under this clause are separate from and additional to the confidentiality, non-solicitation and intellectual property obligations set out elsewhere in this {doc}, which shall each operate independently and in accordance with their terms.",
]

STD_CLOSE = [
    " This clause shall not be construed so as to restrain the Employee from lawful post-employment activity, and nothing contained herein shall be enforceable beyond the date on which the Employee ceases to be employed by {company}.",
    " In the event that a court of competent jurisdiction at {city} holds any part of this clause to be overbroad, the parties agree that the clause shall be read down to the extent necessary to make it consistent with Section 27 of the Indian Contract Act, 1872.",
    " The Employer's sole remedy for any breach of this clause during employment shall be injunctive relief and damages, and not forfeiture of accrued salary or benefits.",
    " The Employee acknowledges that the obligations set out herein are reasonable and necessary for the protection of the Company's business interests during the period of active employment.",
    " This clause shall be read in harmony with the Employee's fundamental right under Article 19(1)(g) of the Constitution of India to practise any profession or to carry on any occupation, trade or business on cessation of employment.",
]

AGG_OPEN = [
    "The Employee undertakes that for a period of twenty-four (24) months following the effective date of cessation of employment with {company}, he or she shall not, whether directly or indirectly, engage in or associate with any business in {industry} in India.",
    "The Consultant agrees not to solicit or provide services, during the term of this {doc} and for a period of thirty-six (36) months thereafter, to any customer, prospective customer or business partner of {company} in any geography.",
    "For a period of twelve (12) months after the date of separation, the Employee shall not join, accept employment with, consult for or otherwise assist any of the entities listed in Annexure A, being direct and indirect competitors of {company}.",
    "The Employee acknowledges that, in consideration of access to trade secrets of {company}, a post-termination restraint of eighteen (18) months within a radius of 25 kilometres from any office of the Company at {city} is reasonable and shall be enforceable as a confidentiality obligation.",
    "Notwithstanding cessation of employment, the Employee shall not solicit or induce any employee or independent contractor of {company} to leave his or her employment or engagement with the Company for a period of twenty-four (24) months from the date of separation.",
    "The Employee shall be bound by a covenant of exclusivity during employment and by a covenant of non-solicitation for twenty-four (24) months thereafter, which restrictions are stated to be 'reasonable' and 'necessary' for protection of confidential information.",
    "The Employee agrees that any variable pay, retention bonus or deferred compensation shall be subject to clawback if the Employee breaches the post-termination non-solicitation covenant during the twelve (12) month restricted period.",
    "A non-compete fee equivalent to three (3) months' basic salary has been included within the total compensation, in consideration of which the Employee undertakes a post-employment restraint for eighteen (18) months.",
]

AGG_CORE = [
    " The Employee acknowledges that this restriction is framed as a continuing obligation of confidentiality, and shall be enforceable as a protective measure for the Company's trade secrets rather than as a restraint on profession, notwithstanding the apparent scope.",
    " The scope of the restricted activity includes roles that are merely 'similar' to the Employee's role at {company}, and the Employee waives the right to argue that such scope is overbroad or unreasonable.",
    " The Employer's right to seek specific performance by injunction is specifically acknowledged, and the Employee agrees that monetary damages will not adequately compensate for breach of this post-termination restraint.",
    " The restrictions shall apply to the Employee's engagement in any capacity, including as a director, shareholder, partner, consultant, adviser or independent contractor, with any competing entity during the restricted period.",
    " The Employee agrees that in the event of breach of this clause, the Employer shall be entitled to recover, in addition to damages, a sum equivalent to twenty-four (24) months' basic salary as liquidated damages under Section 74 of the Indian Contract Act, 1872.",
    " The post-termination restraint shall apply in all jurisdictions where the Company has carried on business during the Employee's employment, and the Employee acknowledges that this global scope is reasonable given the nature of the industry.",
]

AGG_CLOSE = [
    " The Employee waives any defence of unenforceability under Section 27 of the Indian Contract Act, 1872 and acknowledges that the restraint is justified by the Company's legitimate interest in protecting its investment in training and confidential information.",
    " This covenant has been negotiated with legal counsel and is fair consideration for the privileges of employment, and the Employee shall not be heard to argue otherwise in any proceeding for enforcement.",
    " The restrictions contained herein shall be in addition to any obligation arising in equity or by operation of law, and shall survive the termination of this {doc} for the duration specified.",
    " Any breach shall result in immediate termination of all severance payments, retention bonus vesting and deferred compensation, and the amounts so forfeited shall constitute liquidated damages.",
    " The Employee agrees that a sum of Rs. {fee},00,000/- per month of breach shall be payable as damages, without the necessity of proof of actual loss suffered by {company}.",
]

ILL_OPEN = [
    "The Employee hereby covenants that for a period of thirty-six (36) months following cessation of employment with {company}, he or she shall not engage in the business of {industry} in any capacity, anywhere in India, notwithstanding Section 27 of the Indian Contract Act, 1872.",
    "For a period of five (5) years from the date of separation, the Employee shall be absolutely barred from joining, consulting for, investing in or otherwise assisting any direct or indirect competitor of {company} in any geography whatsoever.",
    "The post-employment non-compete obligations of the Employee under this {doc} shall be enforceable by injunction and shall operate for a period of two (2) years from the date of cessation of employment, irrespective of the ground of separation.",
    "The Employee agrees that he or she shall not, after resignation or termination, engage in any occupation, trade or profession that is even remotely similar to the Employee's role at {company} for a period of seventy-two (72) months anywhere in the Indian Union.",
    "This restraint is framed as 'non-compete' rather than 'confidentiality' and is intended to bind the Employee absolutely for a period of four (4) years post-separation, notwithstanding the voidness of such restraints under Section 27 of the Indian Contract Act, 1872.",
    "The Employee acknowledges that the twenty-four (24) month post-termination restraint is supported by a non-compete fee of Rs. 15,000/-, and agrees that such consideration is sufficient to render the restraint enforceable despite Section 27 of the Indian Contract Act, 1872.",
    "The Employee shall not carry on, directly or indirectly, any lawful business or profession of any kind in the {industry} sector for a period of thirty (30) months after cessation of employment, and agrees that this restraint is 'partial' and therefore enforceable.",
    "Notwithstanding any decision of the Supreme Court of India, including Niranjan Shankar Golikari and Percept D'Mark, the parties agree that the post-termination non-compete contained in this clause is valid, reasonable and specifically enforceable.",
]

ILL_CORE = [
    " The Employee specifically waives the defence that this clause is void under Section 27 of the Indian Contract Act, 1872 and agrees that such defence shall not be pleaded before any court, arbitral tribunal or other authority.",
    " The restraint shall apply to all geographies where the Company or its affiliates operate, including future geographies entered after the date of cessation, and the Employee accepts the open-ended geographical scope.",
    " Breach of this post-termination restraint shall entitle {company} to recover, in addition to damages, a sum equivalent to thirty-six (36) months' basic salary as liquidated damages under Section 74 of the Indian Contract Act, 1872.",
    " The Employee acknowledges that this restraint is 'reasonable' in view of the confidential information made available, regardless of the absolute bar imposed on post-employment profession, occupation or trade.",
    " The parties record that the restraint shall apply even where the Employee is terminated without cause by the Company, and the Employee shall have no right to argue that such enforcement is inequitable.",
]

ILL_CLOSE = [
    " This covenant shall be specifically enforceable by injunction regardless of the voidness of post-employment restraint under Section 27 of the Indian Contract Act, 1872, and the Employee hereby contracts out of the said provision.",
    " The Employee's heirs, executors and successors shall also be bound by this covenant for the duration specified, and any breach by them shall be enforceable against them as if they were party to this {doc}.",
    " The Company shall be entitled to publicise the Employee's post-employment restraint to prospective employers, industry bodies and professional associations, and the Employee waives any claim for defamation or interference with prospective employment.",
    " Nothing in this clause shall be read down under Section 27 of the Indian Contract Act, 1872, and any judicial attempt to sever or narrow the restraint shall be treated as a breach by the Employee.",
    " The Employer's determination as to whether a breach has occurred shall be final and binding, and the Employee waives the right to judicial review of such determination.",
]

INDUSTRIES_LOC = ["information technology services","SaaS product development",
                   "pharmaceuticals","fintech","manufacturing","FMCG",
                   "e-commerce","media and entertainment","legal services",
                   "consultancy","EdTech","retail","BPO/KPO"]

DOCS = ["employment contract","consultancy agreement","founder agreement",
        "shareholder agreement","appointment letter","services agreement"]

def _subs(r):
    from pools import COMPANY_PREFIXES, COMPANY_SUFFIXES
    CITIES = ["Mumbai","Bengaluru","Pune","Hyderabad","Chennai","Gurugram","Noida",
              "Ahmedabad","Chandigarh","Kolkata","Indore","Coimbatore","Jaipur"]
    return {
        "company": r.choice(COMPANY_PREFIXES) + " " + r.choice(COMPANY_SUFFIXES),
        "city": r.choice(CITIES),
        "industry": r.choice(INDUSTRIES_LOC),
        "fee": r.randint(3, 50),
    }

def _doc_picker(i):
    random.seed(i*71+3); return random.choice(DOCS)

if __name__ == "__main__":
    from common import run_generate
    target = sys.argv[1] if len(sys.argv) > 1 else "/tmp/nc.jsonl"
    # top-up deltas
    plan = [
        ("standard",252,STD_OPEN,STD_CORE,STD_CLOSE,_subs,_doc_picker,CLAUSE_TYPE,INDIAN_LAW,SOURCE),
        ("aggressive",196,AGG_OPEN,AGG_CORE,AGG_CLOSE,_subs,_doc_picker,CLAUSE_TYPE,INDIAN_LAW,SOURCE),
        ("illegal",112,ILL_OPEN,ILL_CORE,ILL_CLOSE,_subs,_doc_picker,CLAUSE_TYPE,INDIAN_LAW,SOURCE),
    ]
    rows = run_generate(plan, target)
    print(f"Wrote {len(rows)} rows to {target}")
