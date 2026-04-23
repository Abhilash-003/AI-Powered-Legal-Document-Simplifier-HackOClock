# Demo contract — 8-clause Indian rental agreement

Copy the text between the `===` markers and paste into the "Upload PDF / paste text" box (toggle "paste text instead"). Processes in ~40 seconds. Exercises all UI features — 2 high-risk, 2 aggressive, 4 standard clauses spanning rental + employment-adjacent Indian statutes.

---

## What each clause is (spoilers — don't read during the live demo)

| # | Expected type | Expected risk | Statute |
|---|---|---|---|
| 1 | rent_escalation | standard | Karnataka Rent Control Act |
| 2 | rent_escalation | **illegal** | ↑ violates cap |
| 3 | eviction | standard | TP Act §106 |
| 4 | eviction | **illegal** | waives §106 notice |
| 5 | non_compete | **aggressive** | Contract Act §27 (scope) |
| 6 | pf_esic | standard | EPF/ESI Act |
| 7 | notice_period | aggressive | Standing Orders Act |
| 8 | arbitration | standard | Arbitration and Conciliation Act 1996 |

---

## Contract text — paste this

```
===
LEAVE AND LICENCE + EMPLOYMENT AGREEMENT (composite sample for demo)

1. RENT ESCALATION (STANDARD). The monthly licence fee of Rs. 42,000/- (Rupees Forty-Two Thousand only) for the said premises at Indiranagar, Bengaluru, shall be enhanced by seven per cent (7%) on each anniversary of the commencement date, in accordance with and subject to the ceiling prescribed under the Karnataka Rent Control Act, 2001. The Licensee shall continue to pay the enhanced fee on or before the fifth day of every succeeding calendar month.

2. RENT ESCALATION (SUSPECT). Notwithstanding the foregoing, the Licensor reserves the absolute and unilateral right to further increase the licence fee at any time, by any amount whatsoever, on thirty (30) days' oral or written notice to the Licensee, and the Licensee waives any claim that such enhancement exceeds the ceiling under the Karnataka Rent Control Act, 2001.

3. EVICTION GROUNDS (STANDARD). In the event of any default by the Licensee in payment of the licence fee, the Licensor shall issue a written notice of demand requiring cure within fifteen (15) days. Should the Licensee fail to remedy within the said period, the Licensor may terminate this licence by serving a notice under Section 106 of the Transfer of Property Act, 1882, and proceed before the Small Causes Court at Bengaluru for an order of eviction.

4. EVICTION WAIVER (SUSPECT). The Licensee hereby expressly waives the benefit of any statutory notice of termination prescribed under Section 106 of the Transfer of Property Act, 1882, and agrees that the Licensor may terminate this licence with immediate effect on the Licensor's oral or written demand, whereupon the Licensee shall forthwith vacate the premises and hand over possession without recourse to any court or authority.

5. NON-COMPETE (SUSPECT). The Licensee, who is also engaged by the Licensor's affiliate Bengaluru Ventures Pvt. Ltd. as an employee, covenants that during and for a period of twenty-four (24) months after cessation of such employment, he shall not directly or indirectly render services to any enterprise engaged in the business of enterprise software development within the Indian states of Karnataka, Tamil Nadu, and Maharashtra.

6. PROVIDENT FUND AND ESIC (STANDARD). The Company shall deduct twelve per cent (12%) of the Employee's basic wages as the employee's contribution towards the Employees' Provident Fund and shall make a matching employer contribution of twelve per cent (12%), in accordance with Section 6 of the Employees' Provident Funds and Miscellaneous Provisions Act, 1952, and shall deduct and remit Employees' State Insurance contributions under Section 39 of the Employees' State Insurance Act, 1948, as applicable based on the Employee's wage ceiling.

7. NOTICE PERIOD (SUSPECT). Upon confirmation, the Employee shall serve a written notice of ninety (90) days prior to resignation, while the Company shall be entitled to terminate the Employee's services at any time by serving fifteen (15) days' written notice or payment of fifteen days' salary in lieu thereof, as per the terms of the Industrial Employment (Standing Orders) Act, 1946 certified for the establishment.

8. ARBITRATION (STANDARD). All disputes or differences arising out of or in relation to this Agreement shall be settled by arbitration seated in Bengaluru under the Arbitration and Conciliation Act, 1996, before a sole arbitrator to be mutually appointed by the parties, failing which the arbitrator shall be appointed by the Karnataka High Court under Section 11 of the said Act.
===
```

---

## Expected UI behaviour when you paste and click Analyze

- **Header banner** within ~30-40 s: *"Composite rental and employment agreement, Bengaluru"* · posture: **HIGH**
- **Top 3 concerns** will include clauses 2, 4, and 5 (the suspect ones)
- **Metric cards:** roughly 2 High · 2-3 Medium · 3-4 Low
- **Left column (text input mode)** will show a clause list, NOT a PDF view (text paste has no bboxes). That's expected.
- **Clicking clauses 2, 4, or 5** should show red badges + the specific Indian statute citation + negotiation script
- **Chat panel** — try: *"Can I legally refuse clause 4?"* — Claude should cite Section 106 and say the waiver is void.

---

## Contingency if the demo misbehaves

- If Claude API latency spikes, `asyncio.gather` may take 60-90 s instead of 30 s. Pre-upload the contract during your intro slide so results are ready when you switch to the UI.
- If a specific clause mis-classifies, stay calm — open chat and ask *"why did clause 5 get flagged?"* Claude will explain using the retrieved Indian statute references via the Advisor tool.
