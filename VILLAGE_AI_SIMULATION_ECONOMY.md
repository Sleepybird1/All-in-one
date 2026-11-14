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

### Context-sensitive consequences for refusing allied defense — confirmed
- Refusing to defend an attacked alliance member **still damages diplomatic relations**, even when the refusing nation has a legitimate practical reason.
- The diplomatic penalty is **reduced** when the refusing ally is exhausted from a recent war, is already fighting other wars, or otherwise lacks the realistic capacity to join another conflict.
- Refusal without a comparably compelling constraint incurs a **greater** relationship penalty. The system should weigh the nation's actual circumstances rather than apply one flat penalty to all refusals.
- Exact numerical modifiers, whether repeated refusals lead to expulsion, and how much each factor matters remain open.

### Voluntary alliance withdrawal and member expulsion — confirmed
- A nation may **voluntarily withdraw** from a military alliance.
- Existing alliance members may **vote to expel** another member, including for repeated failure to fulfill alliance obligations.
- Withdrawal and expulsion are distinct mechanisms; neither is an automatic outcome of one refusal to fight.
- Voting rules (majority/unanimity), notice periods, treaty penalties, and diplomatic effects remain undecided.

### Alliance expulsion voting threshold — confirmed
- Expelling a nation from a military alliance requires a **two-thirds majority vote** of the other eligible alliance members.
- The nation facing expulsion does not vote on its own expulsion. Exact handling of abstentions, rounding, and special cases with very small alliances remains to be decided.

### Alliance leadership — confirmed direction
- Formal military alliances have a **designated leader nation**, rather than operating entirely without centralized leadership.
- The leader's selection process, term, succession, coordination authority, and limits on compelling other members to act remain **undecided**. This decision does not override the confirmed principle that member nations independently decide whether to participate in wars.

### Alliance leadership by strength — confirmed
- The designated leader of a military alliance is selected **automatically based on relative national strength**, rather than through member elections.
- The exact combined measure of military/economic strength and how leadership changes when rankings change remain undecided.

### Wartime alliance coordination, sovereign production, and procurement — confirmed
- The alliance leader's authority is **primarily wartime military coordination**. The leader can propose strategic objectives and request that member nations attack or defend particular locations, and can communicate the coalition's overall wartime requirements (troops, equipment, weapons, supplies, etc.).
- These requests **do not grant command over other members' domestic economies**. The leader cannot force another nation to abandon food production, redirect factories to steel, or otherwise dictate its internal production priorities.
- Each participating nation independently determines what contribution it can make and how to meet the alliance's wartime needs, based on its own capacity and priorities. Not every nation can supply every requested item or troop contribution.
- If a nation needs additional swords, weapons, equipment, or other military supplies, it can issue **procurement contracts**. Player producers may fulfill these contracts when the nation cannot or chooses not to supply everything domestically.
- The leader's battlefield requests are coordination rather than unconditional orders; this preserves prior rules that allied nations retain independent decisions about war participation and national budgets.
- Precise leader authority, wartime resource allocation, contract pricing, troop command execution, and how alliance needs are aggregated remain open.

### Military supply shortages: delayed, escalating degradation — confirmed correction
- An army that cannot meet its weapons, food, ammunition, or other military supply requirements **gradually loses combat effectiveness as shortages persist**.
- **Do not apply a full or immediately meaningful penalty on the first missed daily quota.** Troops can continue operating initially using remaining stocks and resilience. A missed day is not equivalent to a sustained shortage.
- As unmet supply accumulates over multiple in-game days, the effect becomes increasingly serious: roughly a week of persistent shortfalls begins to hurt, while a prolonged shortage on the order of an in-game month can leave the force severely degraded and at risk of falling apart.
- The one-day, seven-day, and month-long examples are **illustrative progression, not finalized hard thresholds**. The precise simulation curve, reserve buffers, equipment categories, recovery after resupply, and meaning of an in-game month remain to be specified.
- This explicitly supersedes any earlier phrasing suggesting that supply penalties begin immediately at full effect or scale from the very first missed quota without an initial buffer.

### Affordable peacetime military stockpiles and wartime mobilization — confirmed
- Nations maintain military stockpiles of weapons, food, equipment, and other supplies so forces can continue operating during interruptions to production or delivery.
- **Stockpile targets must be economically sustainable**, determined by what the nation can reasonably afford and maintain alongside civilian production and public needs. AI nations must not blindly produce unlimited weapons or bankrupt/starve their economies by pursuing arbitrarily huge inventories.
- Peacetime stockpiles provide a **bridge to wartime mobilization**, when nations may deliberately increase or mass-produce military supplies and shift a greater share of productive capacity to the war effort.
- Mobilization still operates under real resource, workforce, infrastructure, and economic constraints. The exact reserve target formulas, affordability assessments, mobilization rates, and limits on civilian-production reductions remain undecided.

### Cannon industry, ammunition stockpiles, and recurring demand — confirmed
- The modpack's **Create Big Cannons and related cannon systems** are significant parts of national military industry. Nations require cannons and compatible ammunition as actual military supplies, not merely abstract combat statistics.
- Nations build and maintain **ammunition reserves during peacetime** and can issue player-fillable procurement contracts for ammunition and cannon-related equipment. Peacetime demand is lower than wartime demand, but never necessarily zero.
- Peacetime replenishment demand comes from **training**, **minor engagements** (including pirates, hostile mobs, undead, and dungeon security operations), and **replacement of aging/expiring stockpiles** where applicable. The exact expiration/degradation rules are not yet specified.
- **Wartime consumption and procurement increase sharply**, driving much greater production of cannon ammunition and related equipment. This supports a substantial player-built cannon and ammunition manufacturing industry.
- Supply remains limited by real national budgets, industrial capacity, and stockpile policy. Specific ammunition types, consumption rates, cannon production recipes, and detailed integration with combat simulation remain open.

### Shipbuilding and naval supply industry — confirmed direction
- **Ships and shipbuilding industries** are part of the national military-industrial economy, alongside cannon and ammunition industries.
- Nations can develop and procure ships and related naval equipment through their own industrial capacity or contracts, including opportunities for player-owned shipyards and suppliers.
- Naval procurement and upkeep should respect national affordability, real industrial capacity, and the broader distinction between peacetime readiness and wartime demand. Exact vessel classes, naval warfare mechanics, ship maintenance, production rates, and integration with specific ship mods remain undecided.

### Player-built warships: physical construction, abstract delivery — confirmed
- Player-owned shipyards can fulfill contracts for **complete warships as well as individual naval components**.
- For a complete ship contract, the player must **actually construct the vessel from blocks**. Once construction is validated and accepted, the built blocks are removed and converted into a **ship receipt/token item** representing that completed vessel. The nation receives the abstracted ship on successful delivery; the vessel is not expected to remain as a continuously simulated block-built ship.
- The player delivers the receipt/token to the purchasing nation's **naval port/dock delivery interface**. Ship sales require a **valid navigable naval trade route** between the origin and destination, rather than instant delivery or purely nominal trade access.
- **Landlocked nations/shipyards without viable maritime access cannot construct and export ships through this system.** A naval port/dock interface may only be placed within a restricted maximum block distance of an **ocean biome**. The exact distance and port validation rules remain undecided.
- Naval delivery incurs real economic costs reflecting **crew/personnel, fuel, maintenance, and voyage/transport expenses**, varying with the route and circumstances. Exact pricing formulas, route checks, and travel-time simulation remain open.
- The player is paid upon fulfilled contract in the **agreed compensation**, which can be **money or resources**. Ship construction costs and transport costs must be considered when evaluating profitability.
- Exact vessel validation criteria, allowed designs/mod integrations, token safeguards, ocean connectivity, receipt redemption, and failure/refund handling remain to be designed. The receipt should represent one validated ship and should not allow duplicate delivery.

### Ship contract validation and separate ammunition contracts — confirmed
- Before converting a physically built ship into its one-use receipt/token, the game **validates that the ship meets its specific contract requirements**. A generic hull or hollow box cannot be submitted as a fully equipped warship.
- Ship contracts are **generated according to the purchasing nation's needs** and specify required ship components and quantities. This includes **Create Big Cannons multiblock components**, such as breeches and autoloading breeches, with the requested configuration and count validated as part of the completed ship.
- **Ammunition is always procured under separate contracts**, not bundled into the shipbuilding contract. This is the user's explicit final correction, superseding the earlier suggestion that a ship contract might include ammunition or explosive shells.
- The exact blueprint/specification format, accepted cannon configurations, hull/propulsion validation rules, and treatment of optional equipment remain undecided.

### National ship classes, custom orders, and trade access — confirmed
- Nations can order **both standardized ship classes and custom ship specifications**.
- Custom ship designs **cost more** than comparable standard-class orders; the premium and cost formula remain undecided.
- **Each nation defines its own standard ship classes**, rather than all nations sharing one universal catalog.
- Player access to a nation's ship standards and design information **depends on diplomatic relations**. Exact visibility thresholds and treatment of existing knowledge remain open.
- **Poor diplomatic relations reduce the likelihood of receiving contracts**, because nations tend to shift their business to alternative trade partners. This is reduced demand/access, not random contract unpredictability.
- **Hostile relations block all direct trade**, including military and civilian contracts. No intermediary bypass was approved; any exception would require a separate decision.
- These rules apply alongside existing ship-validation, receipt, naval-route, and separate-ammunition-contract requirements.

### Gradual, resource-costed wartime industrial conversion — confirmed
- Nations transition from civilian to military production **gradually**, rather than instantly obtaining maximum wartime output.
- Wartime mobilization can **reallocate workers** from civilian production to military production and can involve **higher taxes**, but tax policy is a **dynamic national decision**, not an automatic fixed tax increase for every war or conversion.
- Repurposing an existing civilian factory requires **actual conversion work and material/resource expenditures** in addition to shifting labor. The nation cannot merely relabel civilian output as military output at no cost.
- Converting an existing factory is **less resource-intensive than constructing a brand-new factory**, but still has meaningful costs and a transition period.
- Conversion decisions must reflect national finances, available materials, industrial capabilities, workforce, and competing civilian needs. Exact conversion recipes, duration, tax behavior, and production ramp curves remain undecided.

### Postwar industrial reconversion and priority setting — confirmed
- After a war, nations **gradually reconvert military industry to civilian production**. Reconversion requires time, labor, resources, and real economic costs, rather than instantly restoring prewar civilian output.
- Each nation **chooses its own order of reconversion** rather than following a universal rule that civilian goods must always be restored first.
- Those priorities are determined by **multiple factors**, explicitly including the nation's strategic goals, public happiness, and the population's actual needs. The AI weighs these together, not strategy alone or happiness alone.
- Exact weights, conversion recipes, timing, and interactions with lingering defense requirements remain undecided.

### Population migration: ongoing movement and event-driven waves — confirmed
- Simulated populations may migrate **between villages and between nations** in response to employment opportunities, safety, and living conditions.
- Migration has **both a gradual ongoing component and occasional rapid waves** triggered by major events; it is not restricted to one mode.
- **Attacks on a village** are an explicit example of an event that can drive people to flee much more quickly than ordinary economic migration.
- Migration should change the actual simulated population distribution and thereby affect the labor pool and economic needs of origin and destination settlements. Exact migration rates, destination choice, border controls, transportation constraints, and refugee-handling rules remain undecided.

### Immigration policy, settlement capacity, and local versus capital authority — confirmed
- Nations control border policies affecting **both immigration and trade**. Open/restricted/closed policy choices have economic tradeoffs; exact policy categories and how immigration rules interact with trade restrictions remain to be designed.
- Immigrants and refugees can add to the **workforce and tax base**, but also require **food, housing, and other support**, increasing local demand and potentially burdening public services. Nations should not automatically maximize immigration when they have no workforce need or capacity.
- Immigration and refugee reception have **real costs**. Receiving communities must provide or construct additional housing or, where appropriate, **refugee camps**; new residents increase demand for local goods and services.
- **Individual cities/villages may refuse to accept immigrants** when they cannot afford or support them. Local capacity and willingness therefore matter, not merely national policy.
- **Only the nation's capital village / central national authority can compel another village to receive immigrants** despite that village's refusal. Ordinary villages cannot force immigration quotas on one another. The exact central-authority decision logic, costs, and effects of forced placement remain open.
- Border closure can reduce incoming pressure on housing/food but also forego labor and taxes; border openness can help labor supply but is not free. Avoid assuming that closed borders directly improve total food or housing supply—effects depend on actual population and capacity.
- Still undecided: allocation of arrivals among villages, camp operating costs, how long camps persist, refugee versus ordinary immigrant policy, infrastructure timelines, consequences of forced placements, and border enforcement.

### Local backlash from centrally imposed immigrant placement — confirmed
- When the capital forces a village to accept immigrants against its wishes, apply **local unhappiness and political-relations/stability penalties**. The village dislikes the imposed policy; do not automatically create riots, strikes, armed revolt, or civil war as a direct scripted consequence.
- **Existing discontent matters**: a village already strongly hostile toward its capital or nation may be pushed past an existing broader loyalty/secession threshold by the additional penalty. This is an interaction with the general accumulated-discontent system, **not** a special automatic immigration-triggered civil war.
- Exact penalty magnitude, duration, mitigation by national support, and thresholds remain undecided.

### Capital aid for forced immigrant placement and slow trust effects — confirmed
- When the capital orders a village to receive immigrants, it **may provide financial aid, food, housing/construction materials, or temporary shelter support** to help absorb the cost and reduce dissatisfaction.
- Such assistance is **optional, not mandatory**. The capital cannot provide resources it does not have and may impose placement without funding it.
- **Unfunded forced placements cause greater local unhappiness** than comparable placements supported with adequate assistance, particularly where local capacity is strained.
- Repeated unfunded placements do **not** impose an immediate permanent trust penalty. Instead, their political effects are **temporary and change/recover very, very slowly and gradually**; sustained repetition can accumulate discontent over time, while recovery should not be instantaneous.
- Exact penalty duration, recovery rate, stacking, and whether partial aid mitigates proportionally remain undecided.

### Immigrant economic integration and deferred culture/politics — confirmed
- New immigrants **integrate gradually** into the destination village economy. Initially they may require additional settlement support, but as they obtain housing and employment they can become increasingly productive and self-sufficient.
- **Integration speed varies with actual conditions**, especially the availability of jobs and housing; it is not a fixed universal timer.
- **Cultural similarity may eventually influence integration**, but this mechanic is explicitly **deferred**. The pack currently has no defined cultures or political ideology/party systems (e.g., communism, democracy, capitalism as political/economic frameworks). Do **not** implement or assume cultural compatibility scores, political parties, ideologies, or penalties now. Revisit only if the user later chooses to develop these systems.
- Exact integration rates, support requirements, employment matching, and housing thresholds remain undecided.

### Population growth constrained by real surpluses — confirmed
- Population growth is influenced by **housing availability, food, jobs, healthcare, living conditions, and available resource surpluses**; it must not simply increase unconditionally by a fixed percentage.
- **Adequate housing is a hard prerequisite for population increase**. A village without capacity to house additional residents cannot grow its population through the normal growth mechanic.
- **Surplus food is also a hard prerequisite**. Merely meeting current food consumption is insufficient: if there is no food surplus available to support additional people, population does not increase.
- The user mentioned a **fixed/base growth rate** alongside these conditions, but did not finalize a percentage or its exact interaction with the constraints. A baseline growth rate may be considered only when prerequisites are satisfied; its formula is still open.
- Exact surplus definitions, population decline triggers, healthcare/employment modifiers, and time scale remain undecided.

### Healthcare supplies, population decline, and emergency food reserves — confirmed
- Village healthcare capacity includes access to **health-related supplies such as healing potions**, alongside other healthcare resources. Exact potion consumption, production, and service effects remain undecided.
- **Prolonged food shortages and inadequate healthcare can reduce population**, both through increased mortality and through emigration. They do not merely halt population growth.
- **Mortality and population decline develop gradually** as shortages persist and resilience/reserves run down, rather than causing immediate mass deaths on the first day of a shortage. Exact delay and severity curves remain undecided.
- Villages should **always try to maintain emergency food reserves** as a planning priority, but actual reserves are limited by their resources and affordability. A village unable to afford or acquire enough food cannot magically create a reserve.
- Reserve targets, procurement priority relative to immediate consumption, storage limits, and emergency release triggers remain open.

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


## Continued design decisions — food crises, secession, and treaties (2026-11-14)

### Food shortages and rationing
- Food shortages escalate from rationing (unhappiness and reduced productivity, with survival possible) to prolonged starvation (higher mortality, emigration, greater dissatisfaction and instability). Population losses reduce workers and output, but also reduce food demand, so collapse is not inevitable.
- Rationing starts automatically at low food reserves; precise thresholds are not yet defined. Villages can ration locally; the national government can impose nationwide rationing during a national crisis.
- The national government can direct food surpluses from one village to another; physical transportation is required. It should normally purchase food at market price using treasury funds or debt, preferring borrowing over uncompensated seizure. Emergency uncompensated requisition is a last resort, causing greater local dissatisfaction and political damage.
- Compensation for seized food is a priority when affordable, but not guaranteed. Unpaid compensation is recorded as a financial liability and damages relations. It may eventually be written off if impossible to repay, with lingering political effects. Recipient aid can be a grant, sale, or repayable loan depending on circumstances.

### Internal dissent, secession, and asset control
- Villages may refuse voluntary sales to the capital. Refusal alone does not automatically mean rebellion. Negotiation, compensation, national demands, and military enforcement can escalate a dispute. Troop deployments cost resources and can increase instability. A village can submit or resist and attempt secession.
- Other villages can join a rebellion only when their own stability is poor AND relations with the rebel village are good; participation is still a strategic decision. Breakaway villages may unite or form separate nations depending on relations and stability.
- Seceding villages retain assets they physically control (factories, stockpiles, local funds, equipment), with contested federal installations/assets resolved through negotiations or conflict. The original nation weighs military/economic costs before choosing to fight or permit independence. Federal troops leave when peaceful secession is agreed, subject to negotiated asset withdrawal.
- Independence settlements may demand immediate or ongoing payments, resources, surplus deliveries, and military equipment. Terms can be mixed and negotiated based on need and bargaining power. Noncompliance can lead dynamically to renegotiation, sanctions/penalties, or war, considering both nations' financial and military situations.

### Debt, diplomacy, and treaty visibility
- During emergencies such as war, debtor nations may request negotiated payment deferrals; if forced to miss payments without approval, the default remains a breach. Debt persists. Deferrals may carry interest, with modest diplomatic penalties that scale with terms. Debt can be forgiven partly or fully for diplomacy, stability, or concessions such as rail access. Domestic stability can react to costs and benefits.
- Rail agreements can separately permit civilian freight or military transit. Public and secret agreements are separate treaties, not public/secret sections of one treaty; they can be negotiated together. Secret agreements cannot be discovered under the current design (espionage deferred), but their economic effects remain observable. AI should consider obligations across both types.
- Nations may take strategically risky deals despite foreseeable strain. Treaties can be permanent or time-limited, as specified; payments can be upfront or in installments. Missed payments always reduce trust somewhat even if other penalties are waived; reliable subsequent payments and diplomatic actions can restore trust gradually. Late-payment enforcement is contextual, depending on causes, duration, relations, and circumstances.
- Nations cannot deliberately lie about their treaty commitments, but can openly withdraw or refuse to comply. Early cancellation is possible, with diplomatic and potentially financial or military consequences; changes in relative power can influence enforcement. Nations may demand renegotiation without first breaking an existing treaty (latest confirmed decision).

### Details still to determine
- Rationing thresholds, exact penalty curves, compensation valuation and debt accounting, rules for contested federal assets, treaty breach costs, secrecy UI, and numerical AI decision weights remain open. Do not assume the above are implemented in gameplay; these are design decisions.


## Historical conversation audit — recovered baseline decisions (2026-11-14)

The following previously discussed user decisions were missing or insufficiently explicit in this specification. This is a retrospective backfill from available conversation history, not a claim that every historical message is accessible. Earlier illustrative numbers remain provisional unless identified as accepted targets.

### Economic model and world baseline — recovered
- Village and national prices are **dynamic**, driven by actual generated resources, local supply and demand, geography, infrastructure, transportation cost, and tariffs. Resource-rich locations can specialize; transport bottlenecks and trade policy change local market conditions.
- Village and national treasuries must earn revenue through **exports, services, and taxation**. They cannot spend or create unlimited currency. Shortfalls and debt have real consequences.
- The simulation begins at a **fixed mid-20th-century technology baseline**. Further technology is acquired through expensive research, purchase, or conquest; nations do not automatically unlock technology simply as time passes. Specific technology trees and prices are not yet designed.
- Trade routes through controlled territory or coastal waters can be restricted or embargoed; physical routes, capacity, and transit rights matter. Militaries require actual taxation/funding, food, and equipment.

### Player nation supply obligations — recovered
- Accepted design target: the player must **physically produce and deliver approximately 60% of every essential category** needed by villages in a player-controlled nation, with the remaining approximately 40% handled by locally simulated production. This covers food, tools, construction materials, fuel, military supplies, and medical supplies, rather than only one selected category. The 60/40 split is a tunable design target, not a hard-coded final balance.
- A player supply shortfall causes shortages, slower growth, unrest, and other proportional economic consequences; it does **not** instantly destroy a village or nation.
- Foreign imports to a player nation count toward its needs at **reduced fulfillment efficiency**, while domestic transfers between villages of that player nation receive full credit. A 0.2 multiplier / five imported units per one effective unit was discussed as an **illustrative** value only; exact balance remains open.
- Players physically build national power generation, rail networks, and major infrastructure. Local village industry may expand only where supported by resources or reliable imports.
- Player-built factories should affect local village output only through **verified production and actual deliveries**. Simply placing Create machines must not magically increase the abstract economy. Players are not prohibited from constructing factories; recognition of their output is the gated step.

### Conquest, reconstruction, and medical demand — recovered
- War-captured territory can have damaged infrastructure, disrupted services, and extra reconstruction demand. Peacefully ceded territory generally remains physically intact but may suffer political instability and population decline.
- Reconstruction requirements represent **actual outstanding material needs**; they decline when the required goods are delivered, **not merely with elapsed time**. Repair labor and capacity must still be accounted for.
- Healthcare consumes real supplies, including potions. Disease outbreaks can increase demand for **specific medicines** rather than only applying an abstract health penalty. Exact disease simulation and item requirements are not yet finalized.

### Consistency and implementation safeguards
- Preserve the distinction between **confirmed user decisions**, accepted but tunable baselines, illustrative examples, open questions, and implemented/tested behavior.
- Later explicit user corrections override earlier suggestions. In particular, the 60/40 player-supply target and the example 0.2 import efficiency are different mechanics, and neither should silently become a fixed implementation constant.
- Treaty renegotiation is confirmed as permitted, but **counteroffers during renegotiation have not yet been answered** and remain open.


## Transcript-only second-pass audit — clarifications (2026-11-14)

The following details were explicitly stated in the current conversation transcript and are recorded here to prevent broad summaries from losing their meaning:

- **Emergency food rationing:** rationing first reduces happiness **and productivity** while residents can survive; prolonged starvation adds deaths and emigration, further harming production, revenue, and stability. Reduced population also lowers food consumption, allowing possible stabilization. Village rationing is automatically triggered by low local reserves; national rationing may be imposed in a national shortage. Numerical trigger and escalation curves remain undecided.
- **Central food purchases and transfers:** the national government may purchase surplus food from a village using treasury funds or borrowing, then provide it to a needy village **free, as a sale, or as a repayable loan** depending on relations, stability, and finances. It should **prefer debt over confiscation**. Uncompensated emergency seizure is permitted when payment is not feasible, but incurs greater local discontent. Unpaid compensation is tracked as a liability **and** a political grievance; repayment is sought when possible, but sometimes a village absorbs an uncompensated loss.
- **Secession enforcement:** a village's refusal to sell voluntarily may escalate into an internal sovereignty dispute, but does not by itself automatically cause civil war. A national government can deploy troops to compel compliance; the village can submit or attempt secession. Other villages may join only with both poor own stability and good relations with the rebels, while considering feasibility. Upon agreed independence, **federal troops withdraw**. The former government can demand assets or future resource deliveries as terms of recognizing independence rather than fighting; the value of equipment physically in the region is a reason to fight or negotiate.
- **Independence settlement timing:** immediate and scheduled compensation are both permitted; a government urgently needing supplies can demand prompt payment, whereas another can accept gradual delivery. Military equipment is also negotiable as part of settlement. Missed obligations can provoke penalties, renegotiation, sanctions, or war dynamically; war or financial crisis can justify negotiated deferral. If the creditor refuses, unilateral nonpayment remains a breach.
- **Debt trust and interest:** every missed payment reduces trust somewhat **even when other penalties are waived**. On-time payment slowly rebuilds trust; diplomacy can accelerate recovery. Deferral interest is optional and causes a modest relations penalty. Debt forgiveness can be exchanged for tangible concessions such as **civilian or military railroad access**, with domestic stability responding to whether the bargain benefits the nation.
- **Secret agreements:** public and secret deals are **separate agreements**, even if arranged together, not visible and hidden clauses within one treaty. Secret deals are **not discoverable at all under the current design**, but their financial impacts can cause visible missed payments or shortages. Agreements can be permanent or expire according to their own terms, and can require up-front or installment payments. The AI can accept strategically risky obligations. Nations cannot lie about commitments, but can openly terminate or refuse to comply, accepting consequences.
- **Treaty renegotiation:** a nation can request changes to an existing treaty without immediately breaking it. Whether the other side can make **counteroffers** was the next open question and has not been answered.

**Audit scope:** This is a second pass over the conversation transcript provided in this chat and the current GitHub specification, not a claim of access to unrelated or unavailable chats. No numerical values or implementation behavior beyond explicitly approved decisions should be inferred.

### Treaty counteroffers — confirmed
- A counteroffer is a **rejection of the current proposal followed by a new proposal** with different terms. Nations can reject a treaty offer or renegotiation demand and submit a counteroffer rather than being limited to acceptance or outright rejection.
- The original proposing nation can then evaluate the new terms. No automatic acceptance, fixed number of negotiation rounds, or specific deadline has been approved.

### Treaty obligations during renegotiation — confirmed
- Nations may **pause performance of an existing treaty while renegotiating**. Pausing does not cancel or forgive the obligations: missed payments and deliveries accumulate and must be made good once negotiations end.
- Whether the pause requires mutual approval, how long repayment may take, and whether interest or penalties accrue during an authorized pause are still undecided.

### Negotiated forgiveness of paused obligations — confirmed clarification
- Obligations missed during a treaty renegotiation pause normally remain due, **unless the nations explicitly negotiate to waive, reduce, or forgive those accumulated obligations**. A pause by itself is not forgiveness.
- Repayment timing and schedules remain open for further decision.

### Installment repayment after treaty renegotiation — confirmed
- When accrued treaty obligations remain payable after renegotiation, the nations **may negotiate installment payments or staged resource deliveries** instead of requiring immediate settlement in full. The schedule must be agreed between the parties; exact terms are case-dependent.

### Repeated missed repayment installments — confirmed
- If a debtor repeatedly misses payments under a renegotiated repayment schedule, the creditor becomes **progressively less willing to grant further extensions or lenient terms**, even when overall diplomatic relations remain good.
- This is gradual and contextual, not an automatic declaration of war or immediate termination of negotiations. Exact escalation thresholds and penalties remain open.

### Creditworthiness and borrowing capacity — confirmed
- A nation's borrowing capacity depends on its **actual economic strength and ability to repay**, including tax revenue, assets, existing debt, and cash-flow capacity, **as well as both recent repayment performance and historical loan repayment record**. Do not use one universal fixed borrowing cap.
- Exact scoring, weighting of recent versus historical behavior, loan size limits, and interest-rate formulas remain to be designed. Better repayment records may inform lending terms, but no numerical rule is approved yet.

### National credit-score recovery — confirmed
- A nation's creditworthiness/credit score **gradually recovers after defaults** when it consistently makes on-time payments and improves its finances. Past defaults do not permanently prevent recovery.
- Recovery pace, lookback window, numerical score range, and exact effects on loan limits and interest rates remain undecided.

### Global credit score and lender-specific adjustments — confirmed
- Each nation has a **worldwide/base creditworthiness score** reflecting its economic fundamentals and repayment history.
- Individual lending nations can adjust their assessment and loan terms based on their **bilateral diplomatic relations and experience with the borrower**. A lender with good relations may be more lenient than the global baseline suggests.
- The global score and lender-specific assessment are distinct; exact scoring scales, weights, and effects on interest rates and limits remain undecided.

### Credit score and economic deterioration — confirmed correction
- A nation's **global credit score does not automatically decrease merely because its economy deteriorates**, so long as it continues meeting its repayment obligations. Economic weakness may still inform a lender's separate assessment of affordability and loan terms; do not silently translate it into a global score penalty.
- Missed payments/defaults and repayment history remain relevant to global credit-score changes. Exact score mechanics remain open.

### Gradual credit-score penalties for overdue payments — confirmed
- A missed payment causes a **gradually increasing credit-score penalty** over the period it remains overdue, up to a defined maximum for that missed payment, rather than the full penalty immediately on day one.
- Illustrative example only: a maximum **10-point** penalty accumulating **1 point per overdue day** reaches 10 points after 10 days. The actual point values, time scale, penalty cap, and behavior after late payment is cured are **not yet finalized**.

### Credit-score recovery after curing a late payment — confirmed
- When a nation pays an overdue obligation, the credit-score points already lost **do not immediately return**. The late-payment penalty stops growing once the overdue amount is settled, and the score **recovers slowly over time** through subsequent reliable payment behavior.
- Example: if a payment incurred a five-point penalty by day five, paying on day five does not instantly restore those five points. Exact recovery rates remain undecided.

### Credit penalties depend on lateness, not loan size — confirmed
- The credit-score penalty for a missed payment depends on **how long the payment remains overdue**, not on the principal size of the loan. A larger loan does not automatically incur a larger credit-score deduction for the same number of days late.
- This does not imply that loan size is irrelevant to financial exposure, debt burden, or lending decisions. Exact lateness-to-points formula remains undecided.

### Multiple overdue loans — confirmed
- **Each separate overdue loan incurs its own credit-score penalty**, accumulating according to that loan's lateness. Penalties from multiple simultaneously overdue loans stack; do not apply only the single longest-overdue loan's penalty.
- Individual penalties remain based on lateness, not loan principal. The total score floor, caps, and aggregation formula are still open for balancing.

### Numeric credit-score borrowing threshold — confirmed direction
- A nation's credit score is an **actual numerical value** used as a **threshold for borrowing eligibility**. A minimum score threshold can restrict borrowing rather than treating creditworthiness only as an informal qualitative judgment.
- The exact numerical score scale, minimum threshold, whether individual lenders may make exceptions, and how bilateral adjustments interact with eligibility have **not yet been determined**. Do not invent a cutoff.

### Lender-specific credit-score cutoffs — confirmed
- **Each lending nation sets its own minimum numerical credit-score threshold** for loan eligibility. There is no universal minimum cutoff shared by all lenders.
- This works alongside the global baseline score and lender-specific bilateral assessment. Exact thresholds, adjustment rules, and exceptions remain undecided.

### Dynamic lender credit-score thresholds — confirmed
- Each lending nation may **dynamically adjust its own minimum credit-score cutoff** in response to changing conditions, including wars and economic crises, rather than keeping that threshold fixed indefinitely.
- Changes affect the lender's willingness to issue new loans; exact adjustment factors, cadence, and whether existing loans are affected remain undecided.

### Changed lending cutoffs apply only to new loans — confirmed
- When a lender raises or lowers its minimum credit-score threshold, the new cutoff applies **only to new loan applications**. Previously approved loans remain governed by their agreed terms and are not retroactively affected by the new eligibility threshold.

### Secured intergovernmental loans — confirmed
- Nations may offer **secured loans** backed by pledged collateral, including factories, railroads, resources, or other eligible assets, in exchange for potentially more favorable borrowing terms.
- Collateral valuation, ownership restrictions, default seizure procedures, and exact interest-rate or borrowing-limit benefits are not yet finalized. Pledging collateral does not itself transfer ownership.

### Secured-loan default: repayment demand before collateral action — confirmed
- A lender must **demand repayment first** when a nation defaults on a secured loan; collateral ownership does **not** transfer automatically at the first default.
- If the borrower still fails to pay following the demand, it suffers a **substantial credit-score penalty and significant diplomatic-relations damage** with the creditor. Exact magnitudes and how this interacts with gradual lateness penalties remain open.
- Whether, when, and by what procedure the creditor may ultimately seize pledged collateral is **not yet decided**; do not assume automatic seizure.

### Company versus sovereign secured-loan enforcement — confirmed clarification
- **Company collateral** may be subject to seizure after an unresolved secured-loan default, consistent with company asset-liability rules. Exact enforcement procedure and timing remain open.
- **Sovereign/national default** does not automatically authorize seizure of a nation's pledged collateral. Instead, the default imposes **severe damage to diplomatic relations and the nation's credit score**, including a **persistent negative modifier that is difficult to remove**. The creditor may still seek negotiated resolution; do not assume unilateral confiscation of sovereign assets.
- A defaulting company can likewise suffer a severe, persistent creditworthiness/reputation modifier. Company and nation consequences should be tracked at their respective levels; the nation's score is not automatically identical to a company's.
- Exact penalty values, duration, removal conditions, and company seizure process remain undecided.

### Persistent default modifier removal — confirmed
- The severe, persistent default-related credit/reputation debuff for a company or nation **does not simply fade with elapsed time**. Removing it requires **specific corrective actions** to restore financial reputation.
- Which actions qualify, whether repayment is mandatory, and how much each action reduces the modifier remain undecided. Ordinary late-payment score recovery is a separate mechanic.

### Full repayment prerequisite for removing persistent default modifier — confirmed
- A defaulting nation or company **must repay the defaulted debt in full** before its persistent default-related credit/reputation penalty can be cleared. Alternative partial settlements do not satisfy this prerequisite under the current rule.
- Full repayment is a necessary condition, **not necessarily immediate automatic removal**: any additional corrective actions and reputation-rebuilding requirements remain to be decided.

### Credit-score threshold for clearing persistent default penalty — confirmed clarification
- Full repayment alone is insufficient to clear a serious-default debuff. The debtor must also **raise its worldwide/national credit score to a required recovery threshold**.
- The persistent debuff **reduces the national credit score while active**, so the debtor must improve its underlying creditworthiness enough to reach the required score **despite the debuff**; do not ignore or remove the debuff when testing eligibility.
- The actual threshold, numerical modifier, and additional corrective actions are not yet specified. For companies, analogous company credit/reputation recovery applies, with precise scoring mechanics open.

### Immediate removal of persistent default debuff after qualification — confirmed
- Once the debtor has **fully repaid the defaulted debt** and raised its **effective credit score (including the active debuff)** to the required recovery threshold, the persistent default debuff is **removed completely at once**, not gradually faded out.
- The underlying score and any other independent credit penalties remain governed by their own rules. Numerical thresholds remain undecided.

### Repeat defaults after rehabilitation — confirmed
- A nation or company that defaults again after recovering from a previous serious default receives a **harsher persistent default penalty than for its first default**.
- The increased penalty affects creditworthiness and associated reputation/relations under the existing default rules. Exact escalation amounts, how many past defaults count, and whether severity ever resets remain undecided.

### Default history rehabilitation after sustained good behavior — confirmed
- Prior serious defaults do **not count against a nation or company forever**. After a sufficiently long period of consistently reliable financial behavior, the historical repeat-default record can cease to increase the severity of future default penalties.
- This is separate from removing an *active* persistent default modifier, which still requires full repayment and reaching the effective credit-score threshold. The required good-behavior duration and reset rules remain undecided; 'years' was conversational, not a finalized game-time requirement.

### Rehabilitation reset trigger — confirmed
- The good-behavior period for clearing historical repeat-default escalation **restarts only after another serious default**, such as an unresolved secured-loan default involving pledged collateral and failure to honor repayment demands.
- An ordinary late or missed payment still causes its normal credit-score/trust consequences, but does **not** restart the historical serious-default rehabilitation period by itself.
- Exact classification thresholds for a serious default remain open.

### Territorial jurisdiction and collateral enforcement — confirmed clarification
- **Companies do not have sovereign authority over nations.** When a company pledges assets located inside a nation's borders and then defaults, the host nation can seize those assets under applicable debt-enforcement rules; the company cannot invoke sovereignty to prevent seizure.
- **National collateral inside the borrowing nation's own territory is different**: a foreign creditor does not automatically gain physical control or unilateral seizure power merely because it holds a security interest. The borrowing nation controls its territory; enforcement instead involves financial, diplomatic, and potentially negotiated consequences under the previously approved sovereign-default rules.
- This jurisdiction distinction does not finalize whether other countries may seize company assets outside their own territory or the detailed legal/process requirements for host-nation confiscation.

### Host-nation confiscation after company collapse — confirmed
- When a company collapses and can no longer maintain or pay for property located inside a nation's territory, **that host nation immediately confiscates the stranded company property/assets**. This applies even when the company had pledged the assets as collateral to a creditor in another country.
- The foreign creditor **does not independently seize assets inside a third nation's territory**; the host nation takes possession itself under its territorial authority. The disposition of those confiscated assets and whether a foreign creditor has any subsequent claim remain undecided.
- This is specifically a company-collapse rule, not a blanket rule that any missed company loan payment instantly causes confiscation.

### Third-country host ownership after collapse — explicit reaffirmation
- If a collapsed company's asset is physically located in a **third country**, that **third/host country confiscates the asset because it is within its territory**, regardless of where the company is based or where its creditor is located. The creditor country does not automatically acquire the asset.
- This reiterates the host-territorial-jurisdiction rule; asset disposition after seizure remains an open design question.

### Disposition of confiscated company assets — confirmed
- After confiscating assets of a collapsed company, the host nation **dynamically chooses what to do based on its own economic needs**. For a factory, available options include operating it, selling it to another company, or dismantling it for recoverable resources.
- The choice should account for actual national needs and circumstances; exact valuation, operating costs, salvage yields, and AI decision weights remain undecided.

### Confiscated factory operations, closure effects, and needs-driven valuation — confirmed
- A host nation operating a confiscated factory must cover real operating costs, including workers, maintenance, energy, and materials.
- The nation may sell a seized factory at a loss when that is preferable to keeping or dismantling it. Scrapping a factory immediately eliminates its jobs but yields recoverable materials in the short term.
- Factory closure has **economic**, not automatically diplomatic, spillovers to neighboring settlements. Trade-price effects occur **after a delay**, not instantaneously. The delay's numerical duration is deferred and varies with how crucial the factory is.
- Factory importance accounts for output, employment, and military supply together. These factors are evaluated using a **fixed, predefined weighting/formula whose effective priorities change dynamically with the nation's actual needs**. For example, labor shortages increase the importance of jobs; military shortages increase the importance of military output. The AI does not arbitrarily choose or rewrite the weights; it supplies/experiences the changing national conditions used by the rule.
- Exact weights, response functions, thresholds, and timing remain unfinalized.

## Foundational simulation state model — newly required design task (2026-11-14)

### User-confirmed architecture requirement
- Before continuing to design many isolated AI decision rules, define a **shared base set of state variables and data** that all village, national, company, economic, and diplomatic mechanics reference.
- Examples explicitly named by the user: **village needs, national needs, reputation, and stability**. Other base values must be identified and defined systematically, including their units, ownership/scope, update triggers, persistence, and which mechanics read or modify them.
- Use consistent **fixed decision formulas fed by dynamically changing state**, rather than allowing independent AI decisions to invent unrelated weights or duplicate incompatible representations of the same quantity.
- The actual field list, scales, equations, thresholds, and storage design are **not yet approved**; the following is a candidate taxonomy for review, not a finalized schema.

### Candidate shared state categories — proposed, awaiting review
1. Village: population, available workers, employment, housing capacity, food and medicine stockpiles, production and consumption, resource needs/surpluses, happiness, local stability, and loyalty to the capital.
2. Nation: member villages, territorial control, national aggregated needs, treasury, tax income, public expenditures, debt, global credit score, military forces and supplies, national stability, and infrastructure capacities.
3. Bilateral relations: nation-to-nation reputation/trust, treaty obligations, trade access, sanctions, alliances, and creditor-specific lending assessments.
4. Companies and assets: ownership, location/host jurisdiction, operating costs, employment, production capacity, inventory, liabilities, collateral, and insolvency status.
5. Logistics and markets: route connectivity, rail/port capacity, transport costs, local market prices, contracts, verified deliveries, and shortages.
6. Time and events: simulation tick/date, shortages and rationing durations, loan delinquency clocks, migration events, wartime status, and deferred obligations.

### Open next step
- Decide the canonical distinction between **raw measured state** (e.g. food stockpile), **derived indicators** (e.g. days of food coverage), and **AI decision outputs** (e.g. rationing order), then define the first core fields and their update cadence. Avoid treating provisional examples as finalized numeric scales.
