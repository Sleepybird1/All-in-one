# Village AI Simulation and Economy — Approved Design Decisions

Status: ongoing user-reviewed design specification. These are intended mechanics, not proof of implementation.


## Confirmed review — November 14, 2026

This section records decisions explicitly approved during the design review. It describes intended behavior, **not necessarily implemented or tested features**. Preserve the implementation and testing notes elsewhere in this README. Numerical examples are not final balancing values.

### Confirmed decisions

1. **Player versus AI economic rules.** Both use production, consumption, trade, taxation, debt, happiness, and stability. Foreign imports fulfill player-nation needs less efficiently than AI-nation needs (0.2 was only an illustrative multiplier). Transfers among villages of the same player nation receive full credit. Exact multiplier is open.
2. **Simulation time and unloaded settlements.** The economy runs while the server is online even without logged-in players. Unloaded villages are simulated abstractly; the world does not advance while the server is off.
3. **Weighted needs.** Essential shortages, especially food, weigh more heavily in happiness and stability than surplus discretionary goods. Needs cannot be simply averaged to cancel out starvation.
4. **Autonomous trade.** Player-nation villages buy and sell routinely within player-set policies, treaties, and embargoes. AI nations set and manage their own policies through AI.
5. **Collective secession.** Multiple villages can jointly consider secession, weighing plausible survival and complementary economies. Success need not be guaranteed; willingness is calculated behind the scenes.
6. **Secession consequences.** Breakaway nations inherit real resources, shortages, infrastructure dependencies, and applicable debts; no artificial economic reset.
7. **Rare voluntary national mergers.** Trade alone does not cause mergers. They require exceptional political/social integration and willingness from governments and populations; no automatic merger timer.
8. **Village spawning and geography.** Villages generate naturally on ReTerraForged continents; roughly 1,000–2,000 blocks apart was a design target, not a guarantee. Actual spawn location, terrain, and territorial deposits shape economic potential.
9. **Abstract populations.** Large populations are represented in simulation rather than spawning millions of physical villagers.
10. **Infrastructure construction and ownership.** Players physically build major infrastructure. AI villages/nations may commission player-built facilities; commissioned infrastructure belongs to the commissioning nation unless a contract states otherwise. Independently financed company infrastructure remains company-owned even inside foreign borders, potentially subject to local taxes or land fees. Construction, ownership, and usage rights are distinct.
11. **Foreign asset seizure.** A host nation may confiscate foreign company assets without compensation after severe diplomatic deterioration. It may also seize assets to enforce unpaid taxes, fees, or debts, even with otherwise friendly relations. Rail networks are valued as discrete whole assets, with length a major valuation input; valuation formula remains open. Relations and debt size influence warnings/grace periods versus immediate seizure. Further assets may be seized until obligations are satisfied.
12. **Company versus national liability.** Company debts primarily expose that company's assets and operating/trading access in the creditor nation; the player's home nation may suffer a smaller diplomatic impact, but does not automatically assume the debt. Government default has stronger diplomatic consequences, potentially including sanctions, severed ties, or war. War is possible, not automatic.
13. **Restoring relations and market access.** Company bans for unpaid debt are not intrinsically permanent: full repayment is required before rebuilding credit/reputation and seeking renewed access. Rebuilding is difficult, particularly with the affected nation. Nations likewise can eventually restore relations after severe default or conflict; neither type of diplomatic rupture is automatically permanent. Exact restoration mechanics remain open.
14. **Recurring contracts.** Village contracts respond to actual consumption and infrastructure needs. Fulfilled contracts pay the supplier and improve stockpiles/services; demand can recur as goods are consumed, supporting long-term factory use.
15. **Physical rail logistics.** Railway trade requires connected, verified Create tracks, applicable transit rights, and realistic capacity and operating costs. Foreign access may incur fees.
16. **Labor and maintenance for infrastructure.** Construction materials alone are insufficient. Construction and operation require paid labor from actual simulated populations, ongoing maintenance, and wages. Workers employed on a project are unavailable for competing work. For foreign company infrastructure, the simulation automatically allocates jobs between the company's home nation and host nation rather than allowing the player to choose all workers. This applies to railways, factories, mines, power plants, and other company infrastructure. Allocation calculations are not finalized.
17. **Village Dashboard.** The dashboard is the central interface for economic information, orders, and deliveries. It should be customizable, information-rich, and visually polished. Specific layout, features, and graphs are a separate design task, not approved details.
18. **Electricity consequences.** Shortages reduce actual industrial production and services and can cascade into unemployment, lost tax revenue, further shortages, instability, and potentially collapse. There is no arbitrary automatic bankruptcy/collapse trigger. Severity, duration, reserves, imports, and resilience matter.

19. **Warfare and territorial consequences.** AI nations conduct simulated wars; players can take part in bounded tactical combat. Conquest and territorial transfers can damage infrastructure and disrupt services, with reconstruction requiring resources. Exact combat mechanics remain open.


## National formation, expansion, sovereignty, and re-admission — approved design direction

### 1. Village-to-nation formation and growth
- Independent villages can voluntarily join a developing nation when both sides find the arrangement worthwhile. Economic complementarity, trade, resources, wealth, security, infrastructure, and expected improvement in living conditions may affect the decision; specific weights remain open.
- The joining village evaluates its own prospects; the receiving nation evaluates whether admitting it improves or harms the existing nation. Admission is not automatic simply because a village offers land or population.
- Nations can range from a handful of villages (illustratively five villages and five million residents) to 40–50 or even 100 villages. These are examples, not fixed size targets or caps. Very large nations should be possible but uncommon.
- Expansion becomes progressively less likely as nations grow and mature. No hard village-count cap is approved. Size, economic benefit, integration costs, and political differences should create diminishing incentives so a continent does not inevitably consolidate into one superstate.

### 2. Political and economic compatibility
- Political differences can discourage or block accession. An applicant may reject membership because the prospective nation's taxes are too high, even if it is otherwise prosperous.
- Administrative capacity (the cost and difficulty of governing dispersed territory) was discussed as a potential factor, but its implementation or precise weight is not separately settled.
- Decisions must be weighted evaluations of expected costs, risks, and benefits, not automatic acquisition of any available territory.

### 3. Maturation and sovereign-state mergers
- Over time a growing nation consolidates its borders and develops a stronger sovereign identity. As this happens, voluntary mergers of two already established sovereign nations become exceptionally rare.
- Village accession to an expanding nation and merger of two mature nations are distinct mechanics. Trade relationships do not create a mandatory eventual merger.

### 4. Seceded or failing nations seeking admission
- A nation that seceded and subsequently struggles can seek to join another nation. It may value stability, prosperity, and survival more highly than independence.
- A prospective host may reject a failing, disloyal, or unstable applicant because absorbing it could weaken national stability or finances.
- The host can make a conditional offer, such as requiring a measurable improvement in stability or a payment before accession. The numerical improvement, payment amount, and evaluation formula are not yet approved.
- The applicant must decide whether the conditions are acceptable; both sides have agency. There is no guarantee that a seceded nation is readmitted or absorbed.

### Territorial change and state creation — user clarification
- Nations may form, grow, lose territory, or cease to exist through voluntary accession, annexation, capitulation following conflict, and secession. These are distinct pathways, not merely voluntary village mergers.
- Secession can establish a new sovereign nation or produce territory that later seeks admission to another nation, consistent with the earlier secession and accession decisions.
- Territorial changes must be reflected in actual sovereignty and borders, with economic and infrastructure consequences rather than a cosmetic map recoloring.
- **Not yet individually approved:** whether annexation can occur peacefully or only by force, whether capitulation automatically annexes any land, and the detailed peace-settlement options. Capitulation should not be assumed to erase the defeated nation without an explicit rule.

### Capitulation, subordinate states, reparations, and overseas garrisons — confirmed direction
- Capitulation **does not automatically mean full annexation** or the disappearance of the defeated country. The defeated nation can remain on the map in a subordinate or puppet-like relationship to the victor.
- Defeat may impose substantial reparations, restrictions on independent decision-making, and military limitations, including prohibition of a standing army. The exact mix of conditions and whether each is universal or negotiated remains to be designed.
- The controlling/victorious nation assumes meaningful security obligations in the subordinate state's territory. If a dungeon or other threat requires military response inside that territory, it must allocate troops to secure it.
- Troops stationed abroad are **deducted from the controlling nation's available armed forces**; they cannot simultaneously be counted as available at home. Foreign deployments are real military commitments with opportunity costs.
- Overseas garrisons can also confer strategic benefits: forward-positioned troops may respond to nearby threats or political/military disputes more quickly. Thus foreign basing is both a liability and an advantage.
- Military deployment, local threats, and garrison commitments should be represented in the simulation rather than being purely decorative.
- **Still open:** puppet autonomy, duration and enforcement of restrictions, reparations formulas, peace negotiations, troop travel/readiness, basing permissions, and when deployed forces can intervene in a dispute.

### Paths from puppet status to independence — confirmed
- A subordinate/puppet nation can regain independence **peacefully** when the controlling nation approves release, including cases where reparations and other agreed obligations have been satisfied.
- Payment and compliance do **not** guarantee release: some controlling nations may refuse to relinquish control even after the subordinate nation fulfills its demands.
- If peaceful release is denied, the subordinate nation may seek independence through a **new war of independence** against its controlling nation.
- These are alternative, situation-dependent routes, not a fixed timer or automatic release trigger. The specific political evaluations, military success requirements, and treaty terms remain to be designed.

### Third-party support for puppet independence — confirmed
- Puppet/subordinate nations can petition other independent countries to pressure their controlling nation to restore sovereignty, including explicit threats or diplomatic intervention.
- Third-party states may support independence movements through financial aid, military equipment, diplomatic pressure, or direct military intervention. Whether they help depends on their own interests and calculations; support is not automatic.
- Specific diplomatic demands, escalation rules, alliance behavior, and intervention thresholds remain open.

### National public finances and services — confirmed direction
- Nations maintain a **central public budget/treasury**, funded at least in part by taxes collected from their villages/economies.
- The national budget funds military commitments, public infrastructure, diplomatic obligations, **healthcare**, and other government services and responsibilities. Healthcare is an explicit core expenditure, not an optional omission.
- The precise division of funding and authority between village and national budgets, tax rates, healthcare model, and additional spending categories remains to be designed.

### Autonomous AI national budgeting — confirmed
- AI-controlled nations independently set and revise their own spending priorities across military, healthcare, infrastructure, diplomacy, and other public services according to their perceived needs and circumstances.
- AI decisions can involve genuine tradeoffs and imperfect long-term outcomes. For example, an immediate military threat may prompt defense spending that reduces available healthcare or infrastructure funding, potentially causing later consequences.
- AI nations are independent decision-makers, not passive economies whose budget priorities are assigned by the player. Exact decision algorithms, budget shares, and adjustment cadence remain open.

### Intergovernmental borrowing — confirmed
- Nations may request loans or financial assistance from **player-controlled nations** and **other AI-controlled nations**. AI nations can initiate these requests independently.
- Borrowing is a separate financial relationship from routine commodity trade and from national tax revenues.
- **Not yet finalized:** whether all assistance must be repaid, interest rates, loan durations, collateral, lender acceptance criteria, default handling, and how players approve or reject requests. These remain design questions rather than confirmed terms.

### Loan terms and renegotiation — confirmed
- Intergovernmental loans begin with **fixed, agreed terms** at origination, rather than rates and repayment requirements changing automatically during the loan.
- Terms can subsequently be **renegotiated by agreement**, particularly when a borrowing nation is struggling financially and maintains good diplomatic relations with its lender.
- Renegotiation is possible, not guaranteed; the lender has agency and need not approve changes.
- **Not yet determined:** the precise initial pricing/term-setting method, interest calculations, collateral, grace periods, and which concessions may be negotiated. Do not interpret “fixed at the beginning” as a universal fixed interest rate across all loans.

### Sovereign debt default: creditor responses — confirmed direction
- When a nation defaults on intergovernmental debt, the creditor may pursue **asset seizure**, **cutting diplomatic or economic ties**, and **attempts to influence the debtor nation's government**.
- These are potential responses, not an automatic mandatory sequence or guaranteed outcomes. Their availability and success should depend on circumstances and political/economic constraints, with exact mechanics still to be designed.
- The user has **not yet approved** automatic territorial seizure, war as debt collection, or any specific method of government influence. The legal/diplomatic prerequisites and limits for asset seizure remain open.

### Creditor demands for assets in debtor territory — confirmed
- Following sovereign default, a creditor nation may **demand ownership or transfer of assets located inside the debtor nation's territory**, not merely assets already within the creditor's borders.
- Such demands cause **additional diplomatic relationship damage**. Nations with good relations are less inclined to make aggressive demands, whereas hostile nations are more likely to pursue them.
- A demand is not automatic transfer or unilateral seizure: the debtor's response, enforcement mechanism, and possible escalation remain to be designed. No automatic annexation or military enforcement is implied.
- The precise diplomatic penalty and which assets may be demanded remain undecided.

### Dynamic escalation from sovereign debt disputes — confirmed
- Unpaid sovereign debt and refusal of creditor demands can be **incentives toward war**, but never automatically trigger war or serve as the sole deterministic condition. War decisions weigh multiple political, economic, military, and diplomatic factors.
- **Relative national strength and size matter:** a small creditor facing a much larger debtor may judge war impractical despite a serious default. The example of a 2-million-person creditor and 40-million-person debtor is illustrative, not a fixed numerical threshold.
- Creditor responses vary by nation and circumstances: some accept the loss and terminate trade or relations; others apply pressure or ask allies to prepare for potential conflict.
- **Allies retain independent agency.** An allied nation can decline requests to prepare for or join a war if doing so is economically or strategically infeasible, even while remaining an ally.
- Escalation should unfold through dynamic, interdependent decisions rather than scripted guaranteed chains. Exact decision weights, mobilization rules, and diplomatic consequences remain unfinalized.

### Formal defensive alliances — confirmed
- Nations may establish **formal military alliances oriented toward collective defense when a member nation is attacked**.
- Such alliances are **not guarantees of military action to protect an ally's economic prosperity, debt collection, or other purely commercial interests**.
- An attack on a member triggers allied consideration of assistance, but each nation retains independent decision-making and may decline participation based on its military, economic, and political circumstances.
- The exact treaty obligations, diplomatic penalties for refusal, definition of an attack, and available nonmilitary assistance remain open.

### Alliance assistance in defensive and offensive conflicts — clarification confirmed
- Formal military alliances prioritize **defending members who are attacked**, but this does **not prohibit voluntary allied support for offensive action** against a country severely harming an ally's interests.
- An ally may choose to support such an offensive war, but is **less likely to participate than in a defensive war**. Each nation independently weighs the circumstances, costs, risks, and interests.
- When a member is attacked, another member's refusal to provide assistance **has consequences** for alliance relations. The precise severity, possible expulsion, and treatment of justified refusals remain undecided.
- The previously documented rule that alliances are not automatic economic guarantees remains intact: economic harm does not itself compel allied military participation.

### Still open for design
- Exact accession scoring, political-difference representation, growth resistance curves, thresholds, administrative effects, negotiating terms, and when a nation counts as mature or sovereign.
- How conditional offers are displayed to players and whether counteroffers or deadlines exist.

### Approved principles with details explicitly deferred

- **Population consumption and growth numerical balancing:** the four-food-items-per-resident-per-Minecraft-day baseline and other numeric consumption/growth parameters are deferred for later balancing; do not treat them as finalized.
- **Offline player-nation protection:** desirable to prevent catastrophic losses during vacations, but rules and anti-exploit balancing are deferred.
- **Territorial resource awareness:** villages know which underground deposits exist within their territory without player prospecting, but extraction still requires actual economic capacity. The user explicitly requested revisiting this design for further thought.
- **Village Dashboard detailed UI:** tabs, statistics, customization mechanisms, and presentation are not yet decided.
- **Exact multipliers, formulas, labor allocation, asset valuation, and thresholds:** remain provisional unless separately approved.

### Review discipline

Only label a decision **user-approved** after explicit confirmation. Keep suggestions, examples, implementation claims, and deferred questions separate. Add subsequent confirmed decisions here as the review continues; do not silently convert proposals into rules.
