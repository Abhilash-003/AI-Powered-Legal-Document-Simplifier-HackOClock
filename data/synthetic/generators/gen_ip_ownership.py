"""IP ownership clause generator — Copyright Act 1957 §17 (+ §57 moral rights)."""
import json, random, hashlib, os, sys
sys.path.insert(0, os.path.dirname(__file__))

INDIAN_LAW = "Copyright Act 1957 Section 17"
CLAUSE_TYPE = "ip_ownership"
SOURCE = "synth_v2"

STD_OPEN = [
    "The Employee agrees that all copyrightable works, inventions, discoveries, improvements, designs, software code, databases and other intellectual property created or conceived by the Employee in the course of and incidental to his or her employment shall vest in and be the exclusive property of the Company.",
    "All works of authorship created by the Consultant in the performance of the scope of work set out in Schedule 1 shall be 'works made in the course of the author's employment' within the meaning of Section 17(c) of the Copyright Act, 1957 and shall belong exclusively to the Client.",
    "Any intellectual property created by the Employee during working hours, using the Company's resources or arising out of the duties assigned to the Employee under this {doc} shall be the sole and exclusive property of the Company.",
    "It is hereby agreed that the ownership of all inventions, trade secrets and confidential know-how developed in the course of the Consultant's services shall vest in the Client by operation of Section 17 of the Copyright Act, 1957 and Section 2(y) of the Patents Act, 1970 read with the Company's invention assignment policy.",
    "The Employee assigns to the Company all right, title and interest in and to the intellectual property generated during the period of employment, subject to the carve-outs for pre-existing IP and personal projects set out in Schedule 2 hereto.",
    "The parties acknowledge that copyright in the software and related documentation created by the Developer shall vest in the Licensee under Section 17(c) of the Copyright Act, 1957, subject to receipt of the consideration payable under this {doc}.",
    "The Employee covenants that all deliverables created in the performance of the duties assigned in {city}, including code, designs, datasets and written materials, shall be treated as 'works made for hire' and shall belong to the Company.",
    "Subject to Schedule A (Pre-Existing IP) annexed hereto, all IP rights in the outputs of this engagement shall vest in the Client upon creation, and the Consultant hereby assigns such rights under Section 18 of the Copyright Act, 1957.",
    "The Employee and the Company agree that intellectual property created in the scope of employment shall be deemed the property of the Company, while IP unrelated to the Company's business and created on personal time shall remain with the Employee.",
]

STD_CORE = [
    " The Employee shall execute such further deeds of assignment and other documents as may be reasonably required by the Company to perfect its title to the said intellectual property, at the Company's cost. The Employee expressly retains the right to be identified as the author of any literary or artistic work under Section 57 of the Copyright Act, 1957.",
    " The Consultant retains moral rights in any literary, dramatic, musical or artistic work created by him or her under this {doc} in accordance with Section 57 of the Copyright Act, 1957, including the right to claim authorship and to prevent distortion, mutilation or modification of such work that would be prejudicial to his or her honour or reputation.",
    " The scope of this assignment is strictly limited to intellectual property arising out of the Employee's duties and responsibilities, and shall not extend to (a) works created prior to the commencement of employment, (b) works created on personal time using personal resources and unrelated to the Company's business, or (c) inventions specifically excluded in Schedule 2.",
    " This assignment is a 'present assignment of future IP' under Section 18(1) of the Copyright Act, 1957 and shall take effect automatically upon creation of each work, without the necessity of any further instrument of assignment.",
    " In the case of journalists, editors and contributors covered by Section 17(a) or 17(b) of the Copyright Act, 1957, the copyright in their works shall be dealt with in accordance with the proviso thereto, and the ownership in respect of uses outside the publication shall revert to the author in the manner contemplated by law.",
    " Any patentable invention made by the Employee shall be disclosed promptly to the Company in writing, and the Employee shall cooperate in the filing and prosecution of patent applications in India and abroad. Inventor rights under the Patents Act, 1970 shall be preserved to the extent mandated by law.",
    " The Employee shall deliver all materials, drafts, working files and research notes relating to the IP so assigned upon request, and shall not retain copies except as necessary for legitimate personal reference and subject to the confidentiality obligations hereunder.",
]

STD_CLOSE = [
    " Pre-existing intellectual property of the Employee as listed in Schedule A shall remain the property of the Employee, and the Company shall have only a non-exclusive, royalty-free licence to use the same to the extent necessary to use the deliverables.",
    " The Employee shall be entitled to a fair and reasonable share of royalties in accordance with the Company's internal IP policy notified from time to time, where such IP is commercially exploited.",
    " This assignment shall survive the termination of this {doc}, save that the Company shall grant to the Employee, upon request, a non-exclusive licence to use certain outputs for personal portfolio purposes in accordance with the applicable policy at {city}.",
    " The Company shall be entitled to record its ownership of the intellectual property with the Copyright Office, the Controller of Patents, the Designs Registry and the Trade Marks Registry, as applicable.",
    " The Employee warrants that the IP so assigned shall be original, shall not infringe the intellectual property rights of any third party and shall not have been previously assigned or licensed to any other person.",
    " Any intellectual property developed jointly with a third party shall be dealt with in accordance with a separate written arrangement between the Company and such third party, and the Employee's obligations herein shall remain unaffected.",
]

AGG_OPEN = [
    "All intellectual property, including but not limited to inventions, discoveries, works of authorship, software, designs, processes, methods, data, formulas and know-how, created or conceived by the Employee at any time during employment, whether or not in the course of duties or during working hours and whether or not using Company resources, shall be the exclusive property of the Company.",
    "The Employee irrevocably assigns to the Company all intellectual property created during the term of employment and for a period of twelve (12) months after cessation of employment, whether related to the Company's business or not.",
    "The Company shall have unrestricted and perpetual rights to use, modify, sublicense and commercially exploit any intellectual property of the Employee, including pre-existing IP brought into the workplace or introduced in any deliverable.",
    "All IP contributed by the Consultant during the term of this {doc}, including IP generated on personal time and unrelated to the scope of services, shall vest in the Client and the Consultant shall have no residual rights of any kind.",
    "The Employee waives any right to be named as the author of works created during employment on any published, distributed or commercialised version of the work, to the extent such waiver is permissible in law.",
    "The Company's rights under this clause shall extend to all derivative works, improvements, modifications and adaptations of the Employee's intellectual property, whether made by the Company or by third parties licensed by the Company.",
    "The Employee agrees that any IP created during unpaid leave, sabbatical or medical leave of absence shall also vest in the Company as if created during active service.",
    "The Employee shall not disclose, use or commercialise, for personal gain or the benefit of any third party, any intellectual property covered by this clause, including after cessation of employment, for a period of ten (10) years.",
]

AGG_CORE = [
    " The Employee acknowledges that the consideration for this sweeping assignment is included within the Employee's salary, and no additional payment, royalty or bonus shall be payable in respect of any intellectual property so assigned, regardless of commercial value.",
    " The obligation to assign shall extend to improvements, derivative works and adaptations conceived up to twenty-four (24) months after the effective date of separation, on the rebuttable presumption that any such IP was conceived during employment.",
    " The Employee shall, upon request of the Company, execute powers of attorney, deeds of assignment and supporting declarations in such form as the Company may prescribe, and shall appear before any registry or court for the purpose of perfecting the Company's rights.",
    " The Company shall be at liberty to register the IP in its own name without attribution to the Employee, and the Employee waives the right to receive a copy of any filing made in respect of such IP.",
    " The Employee shall not, during employment or for a period of three (3) years thereafter, seek to invalidate, challenge or oppose any intellectual property right owned or claimed by the Company, whether in India or abroad.",
    " All royalties, settlements and damages recovered in respect of infringement of the Company's IP shall belong solely to the Company, and the Employee (as the original creator) shall have no share in the same.",
]

AGG_CLOSE = [
    " No schedule of pre-existing IP has been agreed, and the Employee is deemed to have disclosed no pre-existing IP. Any pre-existing IP subsequently claimed by the Employee shall be treated as fully assigned to the Company under this clause.",
    " The provisions of this clause shall apply notwithstanding the generality of any other clause, and in the event of any conflict with another clause of this {doc}, this clause shall prevail.",
    " The Employee acknowledges that the Company's significant investment in training, infrastructure and research justifies the expansive scope of this assignment, which scope shall be strictly construed against the Employee.",
    " The Employee shall indemnify the Company for any loss, cost or expense incurred by the Company in perfecting, defending or enforcing the IP rights so assigned, including attorneys' fees on a full indemnity basis.",
    " This clause shall be specifically enforceable by injunction, and the Employee waives the defence of inadequacy of consideration, lack of privity or hardship in any proceeding for specific performance.",
]

ILL_OPEN = [
    "The Employee hereby waives the moral rights conferred by Section 57 of the Copyright Act, 1957 in respect of all literary, dramatic, musical and artistic works created during employment, including the right to claim authorship and the right to prevent distortion or modification of the works.",
    "All works created by the Employee during employment, including the Employee's personal blog posts, photographs, music, paintings, novels and open-source contributions made on personal time and unrelated to the Company's business, shall be assigned absolutely to the Company without any consideration.",
    "This {doc} shall override the statutory exception in the proviso to Section 17 of the Copyright Act, 1957 applicable to journalists and contributors to newspapers, magazines and periodicals, and the Company shall own all such works including for uses outside the publication.",
    "The Employee agrees that all pre-existing intellectual property of the Employee, including works created before the commencement of employment and works unrelated to the Company's business, shall stand assigned to the Company upon the date of joining, without separate consideration.",
    "The Consultant irrevocably waives and releases all moral rights in works created under this {doc}, including the right to be identified as the author and the right to integrity of the work under Section 57 of the Copyright Act, 1957, and acknowledges that such waiver is absolute and irrevocable.",
    "The Employee, being a staff journalist engaged by a news organisation, assigns to the Employer all rights in contributions including for publication in unrelated media, notwithstanding the proviso to Section 17(a) of the Copyright Act, 1957 which reserves certain rights to the author.",
    "The Employee agrees that personal writings, artwork, compositions, research papers and inventions created outside working hours, using personal equipment and wholly unrelated to the Company's business, shall belong to the Company and shall be promptly disclosed and transferred.",
    "The Employee's family members and dependants, including spouse and children, shall also be treated as having assigned any intellectual property created by them during the Employee's employment that comes to the attention of the Company, to the extent permitted by law.",
]

ILL_CORE = [
    " This waiver of moral rights is stated to be absolute and shall bind the Employee's heirs, executors, administrators, legal representatives and assigns, notwithstanding that such rights are not assignable under the Copyright Act, 1957.",
    " The Company shall be entitled to publish the Employee's personal creations in any manner, and to modify, distort, mutilate or alter the same, and the Employee shall have no right to object to such treatment.",
    " The Employee specifically agrees that the expansive scope of assignment herein, including personal creations and pre-existing IP unrelated to the Company's business, is valid and enforceable notwithstanding the scope of 'course of employment' in Section 17(c) of the Copyright Act, 1957.",
    " The Employee shall be under a continuing obligation to disclose and assign to the Company all post-employment creations, regardless of their relationship to the Company's business, for a period of sixty (60) months after the date of separation.",
    " The parties agree that the statutory protections conferred on authors under Sections 18, 19, 19A and 57 of the Copyright Act, 1957 shall not apply to this assignment, and no dispute relating to such protections shall be referable to the Copyright Board.",
    " The scope of 'works made in the course of employment' under Section 17(c) is hereby expanded by agreement to include every work created by the Employee anywhere in the world during the term of employment, and the Employee accepts this expansion as binding.",
]

ILL_CLOSE = [
    " This clause shall operate notwithstanding any judicial pronouncement, including decisions of the Supreme Court of India, holding that moral rights under Section 57 cannot be waived by contract.",
    " The Employee undertakes not to initiate any proceeding before the Copyright Board, the Controller of Patents or any civil court challenging the scope or validity of this assignment, and any such challenge shall be treated as a material breach.",
    " The Employer shall have no obligation to credit the Employee in any publication, product or distribution of the works, even where the attribution is customary in the industry and even where required by Section 57 of the Copyright Act, 1957.",
    " The Employee specifically agrees that the overreach in this clause is reasonable in view of the aggregate compensation and shall not be read down or severed under any doctrine of public policy.",
    " This blanket assignment and waiver shall be perpetual and irrevocable and shall not be affected by the termination of this {doc} or by the death of the Employee.",
]

DOCS = ["employment contract","services agreement","founder agreement",
        "consultancy agreement","appointment letter","freelance agreement",
        "commission agreement","development agreement"]

def _subs(r):
    CITIES = ["Mumbai","Bengaluru","Pune","Hyderabad","Chennai","Gurugram","Noida",
              "Ahmedabad","Chandigarh","Kolkata","Indore","Coimbatore","Jaipur"]
    return {"city": r.choice(CITIES)}

def _doc_picker(i):
    random.seed(i*61+5); return random.choice(DOCS)

if __name__ == "__main__":
    from common import run_generate
    target = sys.argv[1] if len(sys.argv) > 1 else "/tmp/ip.jsonl"
    plan = [
        ("standard",288,STD_OPEN,STD_CORE,STD_CLOSE,_subs,_doc_picker,CLAUSE_TYPE,INDIAN_LAW,SOURCE),
        ("aggressive",224,AGG_OPEN,AGG_CORE,AGG_CLOSE,_subs,_doc_picker,CLAUSE_TYPE,INDIAN_LAW,SOURCE),
        ("illegal",128,ILL_OPEN,ILL_CORE,ILL_CLOSE,_subs,_doc_picker,CLAUSE_TYPE,INDIAN_LAW,SOURCE),
    ]
    rows = run_generate(plan, target)
    print(f"Wrote {len(rows)} rows to {target}")
