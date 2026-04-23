"""Common render helpers — modular composition + party-framing injection."""
import random, hashlib, json
from pools import company_name, person_name, CITY_TO_STATE

CITIES = ["Mumbai","Bengaluru","Pune","Hyderabad","Chennai","Gurugram","Noida",
          "Ahmedabad","Chandigarh","Kolkata","Indore","Coimbatore","Jaipur",
          "Kochi","Lucknow","Bhubaneswar","Visakhapatnam"]

INDUSTRIES = [
    "information technology services","SaaS product development","fintech",
    "banking and financial services","pharmaceuticals","manufacturing",
    "automobile manufacturing","FMCG","retail","legal services","consultancy",
    "EdTech","real estate","BPO/KPO","media and entertainment","e-commerce",
    "healthcare","logistics","telecommunications","insurance",
    "biotechnology","chemicals","renewable energy","hospitality",
]

# Preface templates — give each row a specific party/industry/geography anchor
PARTY_PREFACES = [
    "In the context of the services rendered by {person} to {company}, a company engaged in {industry} with its registered office at {city}, the parties have agreed that",
    "It is hereby recorded that with reference to this {doc} executed between {company} at {city} and {person}, engaged in the capacity of a professional in the {industry} sector,",
    "This provision shall govern the relationship between {company}, a company incorporated under the laws of India and carrying on business in {industry} at {city}, and {person}, and",
    "Pursuant to the engagement of {person} by {company} at its {industry} operations at {city},",
    "In respect of the {doc} between {company} (having its principal place of business at {city}) and {person} engaged in the {industry} division,",
    "The parties being {company}, a company registered under the Companies Act, 2013 having its corporate office at {city}, and {person}, have agreed that",
    "With effect from the date of execution of this {doc} at {city} between {company} and {person},",
    "It is mutually agreed between {company}, engaged in the business of {industry} with operations at {city}, and {person} that",
    "This clause shall apply to the engagement of {person} with {company} at its {industry} establishment at {city}, and",
]

# Empty preface option — some clauses start directly
EMPTY_PREFACE = [""] * 4

def render_preface(seed_idx, doc, emp_role="Mr."):
    r = random.Random(seed_idx * 41 + 3)
    pref_pool = PARTY_PREFACES + EMPTY_PREFACE
    p = r.choice(pref_pool)
    if not p:
        return ""
    return p.format(
        person=person_name_r(r),
        company=company_name_r(r),
        industry=r.choice(INDUSTRIES),
        city=r.choice(CITIES),
        doc=doc,
    ) + " "

def person_name_r(r):
    from pools import FIRST_NAMES_M, FIRST_NAMES_F, LAST_NAMES
    return f"{r.choice(FIRST_NAMES_M + FIRST_NAMES_F)} {r.choice(LAST_NAMES)}"

def company_name_r(r):
    from pools import COMPANY_PREFIXES, COMPANY_SUFFIXES
    return r.choice(COMPANY_PREFIXES) + " " + r.choice(COMPANY_SUFFIXES)

def compose(opens, cores, closes, seed_idx, subs_fn=None, doc="employment contract"):
    """Compose opener+core+closer with seed-based selection + optional prefix."""
    r = random.Random(seed_idx * 53 + 7)
    o = r.choice(opens)
    c = r.choice(cores)
    cl = r.choice(closes)
    subs = subs_fn(r) if subs_fn else {}
    body = (o + " " + c + " " + cl).format(doc=doc, **subs)
    # lowercase "the" capitalization after preface
    preface = render_preface(seed_idx, doc)
    if preface:
        # downcase the first word of body if body starts with a capitalized common word
        # but preserve if starts with pronoun/proper noun; simpler: just join with ", "
        # remove trailing space and link
        preface_trim = preface.rstrip()
        if preface_trim.endswith(","):
            # body begins naturally
            first = body[0].lower() + body[1:]
        else:
            first = body
        body = preface_trim + " " + first
    return body

def dedupe_emit(out, body, risk, clause_type, indian_law, doc_type, source="synth_v2",
                seen=None):
    if seen is None: seen = set()
    h = hashlib.sha1(body.encode()).hexdigest()
    if h in seen: return False
    seen.add(h)
    out.append({"clause_text": body, "clause_type": clause_type,
                "risk_level": risk, "indian_law": indian_law,
                "doc_type": doc_type, "source": source})
    return True

def run_generate(plan, out_path, max_tries=80000):
    """plan = list of (risk, n, opens, cores, closes, subs_fn, doc_picker, clause_type, indian_law, source).
    Writes JSONL; returns rows."""
    out, seen = [], set()
    for (risk, n, opens, cores, closes, subs_fn, doc_picker,
         clause_type, indian_law, source) in plan:
        i, tries = 0, 0
        while sum(1 for r in out if r["risk_level"]==risk) < n:
            i += 1; tries += 1
            doc = doc_picker(i) if doc_picker else "contract"
            body = compose(opens, cores, closes, i, subs_fn=subs_fn, doc=doc)
            dedupe_emit(out, body, risk, clause_type, indian_law, doc, source, seen)
            if tries > max_tries: break
    with open(out_path, "a") as f:
        for r in out:
            f.write(json.dumps(r, ensure_ascii=False) + "\n")
    return out
