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

### Base subjective metric scales and happiness/stability distinction — confirmed
- Subjective simulation metrics such as happiness, stability, and diplomatic relations use a **0–100% scale**, and **fractional/decimal values are allowed**. Physical quantities (population, inventory, money, etc.) retain actual units.
- **Happiness is an input/modifier to stability**, not a synonym for stability. The user initially said 'combined score' but clarified that happiness affects stability; therefore preserve happiness as a distinct underlying metric and derive stability using happiness plus other factors. Do not collapse both into one undifferentiated stored value.
- Exact stability formula, other contributing modifiers, and update cadence remain to be designed.

### Separate village and national needs with combined dashboard views — confirmed
- **Village needs and national-government needs are separately calculated and stored**, not defined as a single national number equal to the sum of village requirements plus extras.
- National needs are **dynamic and may be influenced by the aggregate needs of villages**, alongside independent national priorities and obligations. The two values can inform one another without losing their distinct identities.
- The Village Dashboard may show **individual village needs, aggregate village needs, national-government needs, and a combined overall view**. The combined display is a presentation/aggregation, not the canonical stored national-needs variable; avoid double-counting shared obligations.
- Exact formulas, categories, aggregation semantics, and dashboard layout remain open.

### National strategic demand and fulfillment timing — confirmed
- National needs include strategic objectives such as military expansion, infrastructure projects, and emergency stockpiling even without immediate village shortages.
- Strategic resource requirements may be fulfilled **all at once or incrementally over time**, depending on the particular objective and circumstances. The timing, procurement schedule, and allocation priority versus village necessities remain to be designed; do not assume national strategic projects always take priority over village needs.

### National allocation priority versus individual village hardship — confirmed clarification
- The **national government sets priorities based on the nation-wide strategic picture**, not an automatic rule that any single struggling village outranks national objectives or the needs of all other villages.
- When one village faces a shortage but the rest of the nation has other priorities, that village **does not automatically become the top national priority**. Its hardship still contributes to the information used in national decisions.
- This does **not** mean the government must always ignore local emergencies or that military projects always win; the relative severity and breadth of needs, national goals, and available resources still matter. Exact allocation formula remains open.

### Severity-sensitive village needs in national prioritization — confirmed
- The national government must consider **severity** of a village's hardship, not merely whether a shortage exists or how many villages are affected. Actual starvation is substantially more urgent than a minor food shortfall.
- Severity modifies the village's influence on national priorities, but **does not automatically override the overall national assessment**; severity, population affected, wider national needs, and strategic priorities must be weighed together using the shared data model.
- Exact severity thresholds, weighting curves, and response timing are deferred until gameplay testing.

### Village emergency assistance and stability — confirmed
- The national government's response to an individual village's food shortage or starvation **depends on stability**, rather than automatically prioritizing starvation solely by its severity.
- Stability is a key input to national intervention and resource-priority decisions. The direction and magnitude of the relationship (e.g., whether lower stability increases intervention urgency, or political considerations can override it) remain to be specified; do not assume a fixed threshold or guaranteed aid.

### Stability-driven emergency assistance financing — confirmed
- A nation **may borrow to fund emergency assistance shipments to a village**, with the decision to borrow driven by the relevant stability situation rather than borrowing automatically for every shortage.
- If sufficient food is available, the nation can provide the required shipment in one lump sum; if insufficient, it delivers aid over time as food becomes available. Actual resources and financing are required; aid is not conjured into existence.
- The exact stability thresholds, borrowing amounts, lender selection, and repayment terms remain to be defined.

### Both village and national stability govern emergency borrowing — confirmed clarification
- When deciding whether to borrow to finance emergency aid to a village, the national government evaluates **both the affected village's stability and the nation's overall stability**.
- Village stability indicates local risk and urgency; national stability reflects the wider consequences and capacity to absorb borrowing or diversion of resources. Neither metric alone dictates borrowing.
- Exact formulas, thresholds, and how the two indicators trade off remain open for later gameplay balancing.

## Conversation audit and reconciliation — 2026-11-14

### Emergency aid, strategic priorities, and balancing — confirmed additions
- **Economic importance of the affected village is an explicit factor** in national emergency-aid decisions, alongside village stability, national stability, severity of need, nationwide strategic priorities, and available resources/borrowing capacity.
- A village that is **economically critical may receive substantial assistance even when its stability is high**. Stability is not the sole determinant of aid.
- Use a **weighted decision model with dynamically changing inputs/needs** rather than a universal yes/no rule. **Do not finalize numerical weights, thresholds, or multipliers until playtesting**; preliminary numbers may be generated for prototyping and then tuned through gameplay.
- Village and national needs remain separately tracked, with shared views and dynamic influence. Emergency intervention has real costs: if the nation has sufficient food, aid can be shipped in one delivery; otherwise it is delivered in installments as resources become available. Borrowing may be used based on both local and national stability.

### Audit notes: clarified versus deferred
- Earlier wording suggesting that starvation **must** be substantially more urgent than a minor shortage is **not a fixed priority override**. The later explicit clarification is that the national response depends on stability and other national conditions; shortage severity is one input, not an automatic ranking.
- National strategic priorities take account of the whole country; an isolated village's difficulty does not automatically displace them. However, critical economic importance and stability risks can increase its aid priority.
- Existing provisional candidate data fields and formulas remain proposals unless separately confirmed. No numerical balance values are locked.

### Cross-check of decisions captured from the available conversation
- Confirmed present in document: territorial seizure of collapsed company assets; need-based operation/sale/scrapping; real factory costs; closure impacts on jobs, salvage, and delayed economic prices; fixed rules driven by dynamic national needs; foundational shared state; decimal 0–100% subjective metrics; happiness modifies stability; separate village/national needs and combined dashboard; strategic needs and phased acquisition; nation-wide priorities; stability-sensitive emergency aid and borrowing.
- Added in this audit: village economic importance as a separate aid factor; high-stability but economically critical villages can still receive high aid; weighted model with numerical tuning explicitly deferred to playtesting; clarification preventing severity from becoming an unconditional override.
- This cross-check covers the conversation excerpts available here and the existing document, **not an independently verified exhaustive transcript of all prior sessions**.

## Population structure, military stationing, and insurrection — confirmed design decisions (2026-11-14)

### Population accounting and dashboard
- Every village tracks a **total population** and a **breakdown by population roles/groups**. Children and elderly are combined into a single **dependents** group rather than separately modeled age groups.
- Population change is calculated from **births minus deaths plus immigration minus emigration** (including movement between villages and across national borders). Movement between villages must reduce the origin village and increase the destination village without changing the nation's total population.
- The dashboard's **summary view** displays current total population and **net population change**. The **detailed view** can show births, deaths, immigration, and emigration as separate lines, alongside the net change. These are components of one population-change calculation, not independent extra population additions.
- Roles can overlap: the total population counts each individual **once**, while role totals are **not necessarily additive**. A person can simultaneously be a worker and a militiaman. No time-allocation fractions between these two roles are required; role flags suffice.

### Workers, militia, and professional soldiers
- **Militia** is its own identifiable role/group but militia members can also be regular village workers. Count their militia status separately without subtracting them from the worker population solely for being militia.
- **Professional soldiers** are a separate category, employed by the **national government as soldiers**; they are not counted as ordinary village workers even while not deployed.
- Villages record the **number of professional soldiers physically stationed there**, but the **nation decides deployment and garrison size** (for example, it can station 8,000 troops in a village). National soldier counts and village stationing counts must reconcile without counting the same troops as additional people.
- A village's willingness to host a garrison can vary with its **stability** and potentially its relations with the national government. Low stability may contribute to hostility toward troop presence; the precise relationship is not yet numerically defined.

### Garrison refusal and insurrection
- Villages **cannot ordinarily veto** national troop stationing. An outright refusal is an **act of insurrection**, not a routine administrative option.
- An insurrection over troop stationing **may begin with negotiation**, but the government may instead proceed **directly to military action**, depending on the simulation's circumstances and variables.
- **Stability and village–national relations** are confirmed inputs to deciding between negotiation and immediate military action. No automatic response, fixed threshold, or guaranteed peaceful stage has been approved.

### Implementation cautions and deferred values
- Keep physical population headcounts distinct from overlapping employment/militia role memberships and troop stationing assignments. Do not sum overlapping role counts to calculate population.
- Exact update intervals, role definitions beyond those named, troop-placement consequences, and formulas/weights for unrest and response are deferred for playtesting.
- These sections reconcile the confirmed decisions in the supplied continuation transcript; they do not imply that every prior session has been independently re-audited.

### Context restoration from the population and garrison discussion — clarified (2026-11-14)
- **Population accounting is hierarchical, not a choice between village or national tracking.** Each village has its own resident headcount and role breakdown, while the nation maintains/derives a nationwide picture. A national soldier is still physically present in a particular village when stationed there; national control of the military does not make that soldier invisible in village population data.
- **Different concepts must be separated:** civilian workforce and dependents describe village society; militia is an overlapping local role; professional military is a nationally employed role; troop stationing is a national deployment decision reflected in the local village's numbers. For totals, avoid adding overlapping roles or adding a garrison twice.
- **The user's garrison example was about political autonomy and consequences, not just counting troops.** The national government can choose to station a large force (the example was 8,000) in a village, while the village may dislike that decision. Low village stability was specifically suggested as one possible reason for opposition. The exact mechanism and other reasons are not yet specified.
- **Refusal is possible in gameplay, but not as a consequence-free veto.** The user explicitly said a village *could* refuse a national troop order, but doing so would constitute insurrection. This is a political conflict state, not an ordinary administrative refusal.
- **Response pathways are conditional:** negotiation is an option, **not a mandatory first stage**; direct military intervention is also possible. Stability and relations affect that choice. The user did not approve a universal trigger, predetermined escalation ladder, or specific numerical formula.
- **Population dashboard detail matters:** summary shows current population and net change; detailed views break out births, deaths, immigration, and emigration separately, even though those values feed one net population change. 'Single calculation' must not be misread as 'discard component data.'
- **No time-slicing for militia:** militia members can simultaneously hold civilian jobs, and the user rejected tracking fractional working versus militia hours as excessive calculation. The roles are flags/categories, not separate people.
- **Remaining ambiguities, not silently decided:** whether stationed troops count as permanent residents or a separate present-population line; whether national population totals include deployed troops abroad; what constitutes formal insurrection; what village conditions besides stability/relations influence troop resistance; and how national military orders interact with existing secession mechanics.

### Stationed soldiers in village population — confirmed
- National professional soldiers **stationed in a village count toward that village's total population**, rather than being excluded as a separate nonpopulation garrison.
- Their professional military role and national employment remain distinct from civilian worker roles. The national and village totals must reconcile without counting a stationed soldier twice.
- Specific housing, ration, and troop transfer accounting remain to be defined.

### Employment, demographic effects, and housing representation — confirmed (2026-11-14)
- **Job seeking/allocation responds automatically to village needs**, rather than requiring employers to manually recruit each worker. Detailed matching rules remain open.
- **Unemployment lowers village stability** and **increases emigration**.
- Unemployment can also **reduce birth rates after a threshold**. That trigger depends on **both unemployment and overall village stability**, and may vary between villages according to local conditions. The actual threshold values and formulas are deferred.
- **Housing is tracked by housing-unit counts**, with an associated **capacity for people** derived from the housing available. Housing capacity can change dynamically when the housing stock or its characteristics change; do not treat one unit as a permanently fixed universal number of residents.
- The user began by saying capacity, then clarified 'unit counts ... but it is capacity ... dynamically changed'; preserve both unit count and derived capacity rather than choosing only one.

### Housing overcrowding penalties and eventual hard cap — corrected decision
- Housing does **not** impose an immediate hard population cap at nominal capacity. As the **population-to-housing-capacity ratio** rises, overcrowding produces penalties (including adverse happiness/stability effects).
- At a **higher, as-yet-undetermined occupancy percentage**, a **hard population cap** applies. Thus both progressive overcrowding penalties and an eventual hard cap coexist.
- Exact occupancy ratios, penalty curves, and cap percentage are deferred to gameplay balancing. This supersedes the initial 'hard cap only' answer, which the user explicitly revised.

### Housing overcrowding escalation — latest clarification
- Overcrowding penalties **continue increasing with the population-to-housing-capacity ratio**. At severe levels they must affect wider economic systems, potentially including **food production, other production, and income**, not merely happiness or stability. The purpose is to prevent unchecked population expansion from remaining economically harmless.
- The user pushed back on the binary 'births/immigration stop versus forced migration' framing. **Do not finalize either mechanism** from that exchange. The earlier proposed hard cap remains in the discussion, but whether it is a literal population ceiling or a practical ceiling enforced through increasingly severe penalties needs explicit clarification.
- Exact escalation curves and thresholds are deferred to playtesting.

### Overcrowding must create escalating health and infrastructure costs — confirmed clarification
- Adequate food alone **must not neutralize a severe housing shortage**. A settlement cannot support arbitrarily large numbers of unhoused or overcrowded residents just because food is available.
- As the population-to-housing-capacity ratio worsens, penalties intensify across **health outcomes and healthcare costs**, **infrastructure demand**, **infrastructure maintenance costs**, and other economic/productivity effects already specified. At severe overcrowding, healthcare, infrastructure requirements, and maintenance expenses rise **dramatically**.
- Housing pressure therefore feeds back into village and national budgets, services, productivity, stability, and the sustainability of continued population growth. No exact numerical thresholds or curves are approved yet.
- The user's explanation favors an increasingly unsustainable practical limit; whether a separate literal hard-coded maximum population is also required remains unresolved pending direct confirmation.

### Gradual overcrowding emigration and birth-rate prerequisites — confirmed
- Overcrowding **gradually increases emigration pressure** as housing becomes more strained, rather than only triggering migration at a final hard-cap threshold. The first penalty threshold and numerical curve are deferred until playtesting.
- **Food availability is an absolute prerequisite for births/population growth from births** in the intended simulation model: without sufficient food, new population cannot be sustained through births. The exact food adequacy test and update rules remain undefined.
- **Healthcare/medical items modify birth rates**, but their absence **does not automatically reduce births to zero** when food is available. Medical supply should influence the rate by a percentage or other tunable modifier.
- Prior confirmed factors such as unemployment, stability, and housing constraints remain relevant; the relative weighting and interactions are not yet specified.

### Birth surplus threshold and medical mitigation of deaths — clarified
- Birth-driven population growth depends on having a **sufficient food surplus above existing consumption**, not merely any food in inventory. The required surplus threshold and rate curve remain deferred.
- Track a **baseline/expected death count or death rate** first. Then apply a **medical-supply availability ratio or threshold as a mortality-reduction modifier**: medical supplies prevent a portion of otherwise expected deaths rather than being represented solely as an extra death penalty when absent.
- Conceptual calculation: **actual deaths = baseline expected deaths − deaths prevented by medical availability**, subject to sensible bounds. The exact interpretation of the medical ratio, other mortality drivers (including food shortages), and formulas are not finalized.
- This clarification supersedes any simplistic claim that zero medical supplies must independently add deaths above an already-defined unmitigated baseline.

### Disease, mortality, and national intervention — confirmed (2026-11-14)
- **Baseline expected deaths increase** with starvation, disease, and severe overcrowding; available medical supplies then mitigate a portion of expected deaths. Actual numerical modifiers remain deferred.
- **Disease risk increases** with overcrowding and with insufficient medical supplies. Disease is a **named, village-specific underlying stat/modifier**, not merely folded into stability. It need not be a prominent top-level dashboard number, but its modifiers can be exposed in a detailed view.
- Disease conditions are tracked **village by village**, not solely as a national average. The nation can see differences across villages.
- **National disease response is conditional** on the breadth of affected villages, whether a village is managing the outbreak itself, and the resulting stability decline. A single village coping successfully may manage locally; when disease is not controlled and village stability begins falling, the national government may intervene. Widespread outbreaks also affect the national priority assessment.
- This does not create a mandatory automatic intervention threshold or imply the national government must always step in for one local outbreak. Exact decision weights, response timing, and resource requirements remain to be designed.

### National disease intervention: needs-based and affordability-constrained — confirmed
- When a nation intervenes in a village disease outbreak, it may provide **whatever combination of assistance the situation requires**, including medical supplies, funding, medical personnel, and healthcare facilities.
- Assistance is **not unlimited or automatically free**: the government must be able to afford and resource the response under the already established national budget, inventory, workforce, logistics, borrowing, stability, and competing-priority rules.
- The response should address the village's actual unmet needs rather than selecting one fixed intervention type. No guaranteed aid quantity, free construction, or automatic resource creation is implied.

### Urgent intervention triage and general sovereign borrowing rule — confirmed
- When the nation cannot fund every measure needed to control a disease outbreak, it **prioritizes the most urgent effective interventions first**, then funds additional measures as resources become available. Actual spending, supply, and delivery constraints still apply.
- **General rule beyond disease:** whenever a nation cannot afford a desired or necessary expenditure, it may **seek a loan** rather than treating a cash shortfall as an absolute prohibition. Ordinary borrowing is conditioned on **economic feasibility**, including repayment capacity and the willingness of an eligible lender under existing credit rules.
- **Desperation exception:** if borrowing is the nation's only viable way to address an extreme emergency, it may attempt to borrow **even when normal economic-feasibility checks would discourage it**. This does **not** guarantee that a lender agrees, that credit limits disappear, or that money materializes. Existing credit, collateral, diplomatic, and default consequences still apply.
- Exact definitions of 'economically feasible', 'desperate', and emergency prioritization remain deferred.

### Desperation loan terms — confirmed and cross-referenced
- In an extreme financial emergency, a borrowing nation **may accept substantially higher interest rates and otherwise unfavorable loan terms** when necessary to obtain funding.
- Lenders **may demand collateral** for such high-risk loans; the borrower can consider pledging eligible assets under the existing secured-sovereign-loan rules.
- **Do not reopen collateral default enforcement as a new decision:** a sovereign lender first demands repayment; a creditor cannot automatically seize assets inside the debtor nation's territory, and serious unresolved defaults incur major credit and diplomatic consequences. Company assets and host-country territorial confiscation follow their separately documented rules.
- These choices do not force lenders to offer a loan or override previously established sovereignty and credit constraints.

### Village budget versus village wealth — clarified foundational distinction
- Villages maintain **their own financial budgets/treasuries**, distinct from the national government's treasury.
- **Village wealth is not the village treasury balance.** It is a separate calculated economic indicator reflecting **how much money circulates/flows through the village economy**. The user explicitly distinguished village wealth from money held by the village government.
- The user selected **village wealth** as the basis for national taxation, rather than directly taxing individual residents or simply taking a fixed amount from the village budget. The precise tax base and how taxes are collected/transferred remain to be defined.
- Do not equate village wealth with cash reserves, government revenue, or total assets. Exact measurement window, included transactions, treatment of repeated circulation, and tax-rate mechanics are unresolved.

### Village wealth is based on positive net economic gains — confirmed clarification
- Village wealth is **not gross transaction volume**. Count the **positive net gain/profit** from economic activity after its associated costs, rather than counting the full face value of wages, revenue, or trade turnover as newly created wealth.
- For trade specifically, **only the profit from a trade contributes positively to village wealth**, not the entire sale price. Loss-making trades do not create positive wealth merely because money changed hands.
- Exact treatment of losses, wages as expenses versus household income, reinvestment, cross-village transfers, and whether 'wealth' is a flow per period or accumulated stock remains to be specified. Avoid double-counting the same value across a transaction chain.

### Village wealth losses, zero floor, and percentage-based taxation — confirmed
- Unprofitable trades **subtract their net losses from village wealth**; they do not merely contribute zero. Profits add to wealth and losses reduce it.
- The **reported village wealth indicator has a floor of zero**; it cannot become negative. This floor does not erase actual financial losses, debts, or negative cash flow, which should remain tracked in their appropriate accounts.
- **National tax revenue is percentage-based on village wealth**, so lower wealth produces lower tax revenue at a given tax rate. A zero wealth tax base yields zero tax under this rule, without implying that other separately defined taxes exist.
- The exact wealth measurement period, tax rate, timing, and whether taxable wealth uses a period's net gain versus an accumulated wealth indicator remain unresolved. Avoid claiming a specific percentage or automatically taxing the same profits repeatedly.

### National tax rate selection and collection cadence — confirmed
- National taxes on village wealth are **collected periodically**, not continuously on each transaction. The exact collection interval remains **deferred** for later balancing.
- The **national tax rate is dynamically determined by the nation's changing needs**, rather than being a permanently fixed universal percentage. National priorities, obligations, and fiscal needs inform the rate under consistent simulation rules.
- The precise rate-setting formula, limits, change frequency, and political/economic consequences are not yet finalized. Distinguish the periodically collected tax from the potentially more frequently updated wealth indicator.

### Tax-rate inputs and happiness impact — clarified
- National tax rates respond dynamically to **both country-wide needs and village needs**, not national needs alone.
- **Raising national taxes directly reduces village happiness**, **not stability as a separate direct tax penalty**. Because happiness is already a modifier of stability, tax increases may **indirectly** affect stability through the established happiness-to-stability calculation; do not double-apply an independent tax-to-stability penalty.
- Exact tax-response and happiness penalty curves remain deferred to playtesting.

### Taxation, happiness, and stability — corrected causal relationship
- **Village happiness is a composite indicator** determined by many different living-condition and economic factors; taxation is only one contributor.
- **Ordinary tax increases may reduce happiness but do not automatically reduce stability merely because happiness falls.** The earlier shorthand 'happiness always feeds into stability, therefore every tax-related happiness drop lowers stability' was too absolute for this tax rule.
- **Only excessive taxation can cause a tax-related stability decline**, with excessiveness determined under a future contextual threshold/decision rule. This can be represented as a separate excessive-taxation condition in the stability calculation, without double-counting the same penalty.
- Preserve the general earlier rule that happiness is relevant to stability, while making clear that the tax effect is conditional and not a one-to-one automatic transfer. The full happiness composition, stability interactions, and excessive-tax thresholds remain deferred.

### Military presence affects both happiness and stability — confirmed
- **National military occupation or troop stationing can affect both village happiness and village stability**, not just happiness.
- These are distinct effects and should not be collapsed into a single generic dissatisfaction score. The impact can depend on local conditions, including village–national relations and existing stability; the exact direction, magnitude, troop-to-population ratios, and conditions distinguishing ordinary stationing from occupation remain to be designed.
- This extends the earlier rule that a village may resent a national garrison and can escalate refusal into insurrection. Do not assume every additional soldier always produces the same penalty.


## Stability, relations, wealth, and military manpower — confirmed conversation decisions (2026-11-14)

### Stability and happiness
- Happiness affects stability **gradually over time**, not through instantaneous conversion or a one-to-one mapping. Low happiness pulls stability downward over time; high happiness lifts it over time.
- The farther happiness is from its neutral level, the faster the corresponding stability change. Exact neutral threshold, rates, and curve are implementation/balancing values.
- Other identified stability influences: excessive taxation, uncontrolled disease, severe economic hardship, national-government interference, and military occupation. Preserve the earlier distinction that ordinary taxation is not itself an automatic direct stability penalty; excessive taxation is a special condition.

### Village wealth
- Wealth increases with net economic profit from production and trade, decreases with net losses, and has a zero floor. Gross sales and transfers do not count as newly created wealth. Preserve earlier budget-versus-wealth and tax-base distinctions.

### Relations
- International relations can respond to war, military aggression, alliances, treaties, trade agreements, economic cooperation, diplomatic disputes, national intervention, territorial conflicts, debt defaults, repayment behavior, and policies affecting other nations.
- Internal village–national-government relations are a distinct relationship system, particularly where national policy or intervention causes tension.
- This is an accepted working list, **not asserted to be exhaustive**.

### Military manpower pool and recruitment
- Military manpower is **not** an additional top-level map statistic. Track an eligible/recruitable manpower pool separately from the number of people actually serving, and separately from the number of troops the nation can sustainably equip, pay, feed, and supply.
- A nation's recruitment **policy** determines its maximum recruitable share of population and its gradual mobilization/phase-in speed. Policy changes do not instantly turn all eligible citizens into soldiers.
- Seven accepted recruitment policies, in ascending order: **Volunteer Only**, **Limited Conscription**, **Extensive Conscription**, **Service by Requirement**, **Mass Mobilization**, **All Adults Serve**, **Scraping the Barrel**.
- Provisional Hearts of Iron IV-inspired recruitable-population limits agreed during discussion: Volunteer Only **1.5%**; Limited Conscription **2.5%**; Extensive Conscription **5%**; Service by Requirement **10%**; custom Mass Mobilization **15%**; All Adults Serve **20%**; Scraping the Barrel **25%**. These are *starting placeholders*, not locked balancing requirements.
- **Mass Mobilization** can draw from the entire eligible population in priority order: general population/nonessential workers first, essential workers only after those sources are insufficient. Removing essential workers can impair essential services and production. Mass Mobilization is itself a policy, not an independent emergency exception.
- Demobilization requires a **policy change**, rather than automatically occurring just because military needs decline. When demobilizing, return essential workers to civilian employment first. Rates and implementation details are left to coding/balancing.

### Military recruitment and economic productivity
- Merely becoming eligible for, or being added to, the manpower pool **does not remove a civilian from employment** and does not itself reduce productivity.
- Economic effects are based on **workers actually mobilized**, their prior employment, and their economic functions; do not apply arbitrary fixed productivity penalties just for choosing a higher recruitment tier.
- The conversation discussed a delay before productivity effects, but later explicitly decided that **unfilled positions reduce production right away** if they cannot be filled. Implement the latter as the operative rule for vacancies; do not silently impose a universal delay that contradicts it. Any remaining transition timing is an implementation detail.
- Worker replacement is **automatic and aggregate**, not simulated as decisions by individually modeled businesses. Available unemployed civilians can progressively fill jobs vacated by mobilized workers.
- **Higher unemployment permits faster replacement**; if there are no available unemployed workers, vacancies remain unfilled and their associated production is lost. Replacement occurs **over time**, not instantaneously.
- Military sustainability must separately consider the nation's economy, workforce needs, equipment, pay, food, and logistics; a large manpower pool does not imply an equally large maintainable army.

### Numerical implementation instruction
- The AI **writing the simulation code** should choose reasonable initial numerical values for any unspecified rates, delays, thresholds, penalties, and formulas, then make them adjustable for playtesting. This does **not** mean an AI agent within the running simulation dynamically chooses those values.
- Do **not** repeatedly request numerical balancing decisions from the designer during mechanics specification. Preserve explicitly discussed provisional percentages above until deliberately revised.
- Outstanding mechanics for later design include training/combat readiness, military upkeep, casualty/replacement flows, and detailed demobilization behavior; do not mark these as finalized.


### Explicit scope and rejected-stat decisions — audit correction (2026-11-14)
- The five main statistics discussed in this review were **population, happiness, stability, wealth, and relations**. The suggestion to add **Security** as a sixth top-level statistic was **rejected**. Crime and external threats were suggested as possible inputs, but no replacement rule was approved; do not silently add a Security statistic.
- **Military Strength, Political Influence, Infrastructure, and Public Health** were floated as possible major statistics, **not approved** as new top-level statistics. Military strength may be derived from actual units and equipment; infrastructure from buildings; disease/public health remains an underlying modifier as specified elsewhere. These were suggestions, not binding additions.
- The user chose **policy alone** as the initial determinant of recruitable-population percentage; do not silently make demographic, economic, or other conditions change the *policy percentage*. Economic and logistical constraints still limit the number of troops that can be sustained, and worker availability determines real impacts.
- The user confirmed that **mobilization phase-in speed is set by each recruitment policy**, rather than a universal fixed speed.
- Under mass mobilization, essential-worker recruitment is **last resort in the priority order**, not a separately adjustable trigger policy.
- In the transcript, the assistant asked whether emergency mobilization should have its own phase-in speed, but **no answer was given**. Do not treat a distinct emergency speed as approved.
- The user approved demobilizing essential workers first when manpower requirements decrease, **but only after a policy change**; declining demand alone does not automatically initiate demobilization.
- The earlier proposal of a fixed economic-impact delay was superseded in the specific case of **jobs left unfilled immediately**. Keep any separate delayed adjustment effects explicitly undecided rather than imposing them.
- The previous discussion of all seven manpower tiers and the 1.5/2.5/5/10/15/20/25% values is provisional. The user explicitly delegated **all remaining numeric balancing** to the coding AI, not just one delay.
- The relations list was accepted **for now**, without a claim that all previously discussed relation modifiers had been exhaustively recovered.


### Historical conversation cross-check: performance and tactical impact (2026-11-14)
- **Large-world performance requirement:** the economy and national simulation must remain viable on worlds with approximately **ten million chunks**, with **very low CPU usage**. Simulate unloaded villages/nations abstractly, without requiring chunks to be loaded or individual citizens to be spawned. This is a scalability design target, not a claim of benchmarked performance.
- **Player absence and natural change:** no online player/AFK presence is required for the simulation to advance while the **server is running**. Player absence must not itself trigger artificial world termination or immediate collapse. Nations may nevertheless naturally change, starve, collapse, or recover over realistic simulated timescales under the ordinary economic rules. The server-off pause rule remains intact.
- **Limits of player battlefield influence:** most warfare is simulated at the nation/army level. A player's tactical skirmishes can influence battle outcomes and diplomatic negotiations, but an individual player's victories must not automatically conquer continents or bypass the larger military/logistical simulation.


## Additional historical conversation reconciliation — 2026-11-14

These points were recovered from earlier conversation context and compared against the existing specification. They are design decisions, not evidence of implemented code.

### Territory, trade, and resource knowledge
- Village/nation borders **expand gradually** into available territory until they meet coastlines or neighboring borders; actual geographic constraints govern expansion. Do not treat border growth as an instantaneous land claim. Exact expansion rates and political rules are deferred.
- Trade routes may cross national territory and **territorial waters**, subject to border restrictions, embargoes, permissions, and applicable trade arrangements. Border/territorial control affects movement of goods and people.
- Villages **already know which mineral/resource deposits lie inside their controlled territory**. Do not introduce an additional village prospecting/scouting calculation as a mandatory discovery gate; the user rejected that as over-engineering. Knowing deposits does not mean they can extract them without development. The underlying resource-awareness rule was flagged for later review, not silently replaced.
- Manufacturing may use **imported raw materials** where economically/logistically available; not every village must possess every input deposit locally.
- Local village development/spending responds to **demand, available supply, and production bottlenecks**, rather than arbitrary industrial growth.

### Player industry and delivery accounting
- **Do not restrict the player's ability to construct factories** merely to enforce the simulation's industrial progression or economy. Production, inputs, operating costs, delivery, and actual fulfillment still matter.
- Delivered goods can count toward economic demand even when a registration mechanism is bypassed; registration is **not the sole valid proof of fulfillment**. Track deliveries robustly and ensure **each physical item/unit satisfies demand at most once**, preventing double-counting or repeated credit for the same goods. Exact delivery verification and anti-duplication implementation remain to be designed.
- Player-nation essential goods must be **actually produced or supplied**. Conquest grants access to territory, deposits, and infrastructure but does not create free output; annexed residents also add consumption needs. Foreign imports have the previously documented reduced fulfillment efficiency, while domestic transfers count fully. The 0.2 ratio remains illustrative, not fixed.

### Military, war, and policy clarifications
- Militia and standing-army commitments consume real **tax funding, food, equipment, and ongoing resources**, with personnel drawn from the simulated population. Military capacity is constrained by both manpower and support.
- Wartime industrial conversion and postwar reconversion are gradual and resource-constrained; **taxation changes are optional policy tools**, not a universally required step of conversion.
- The **offline protection** mechanic was discussed but explicitly **deferred**; do not silently mark it approved or implemented.

### Audit boundaries
- This reconciliation draws on retrievable historical conversation summaries and the supplied transcript. It is **not a claim that every historical message was individually available or checked**.
- Maintain the distinction between user-approved mechanics, proposals awaiting decisions, illustrative numerical examples, and verified implementation.


### Historical pricing and market-boundary clarification — confirmed
- **Local village markets remain distinct** rather than collapsing into one uniform national price. A nation may calculate aggregated indicators, but these must not overwrite location-specific prices, shortages, or transport constraints.
- **Do not set prices by arbitrary random rolls.** Prices emerge from actual supply, demand, local resource endowments, terrain, infrastructure, trade access, tariffs, and transportation costs. Numerical formulas and adjustment speeds are implementation/balancing decisions, but the causal inputs must remain grounded in simulated conditions.
- These statements refine the existing dynamic-pricing rule and do not authorize a fixed price table or a universal national market-clearing price.


### Summary cross-check: dashboard classification and unresolved supply target (2026-11-14)
- **Top-level decision statistics versus underlying inputs:** The latest reviewed core display set is population, happiness, stability, wealth, and relations. Food stocks, medical supplies, troop presence, and village-specific disease are tracked as resources, conditions, or modifiers rather than automatically promoted to additional headline statistics. Village and national **treasury/budget balances remain real, separately tracked financial state**; they must not be confused with the village wealth indicator. Their exact dashboard prominence is a separate UI decision.
- **Development** was suggested as a possible headline statistic, **not approved**. Do not add it as a confirmed sixth statistic.
- **Player essential-supply split requires reconciliation:** An earlier summary characterized the roughly **60% player-produced / 40% locally simulated** essential-goods split as an *unfinalized target*, while an existing section labels it an *accepted tunable design target*. Treat it as a **provisional target for balancing, not a mandatory hard-coded ratio**, pending explicit confirmation; do not silently implement it as a fixed universal requirement.
- This note distinguishes directly confirmed decisions from summary-only qualifications; it does not revise other established trade, logistics, or supply obligations.

### Offline player-nation protection — principle confirmed; details deferred (2026-11-14)
- **Decision:** Player-controlled nations receive some form of protection while their players are offline, rather than necessarily facing all risks without mitigation.
- **Deferred again at the user's request:** protection against invasion versus economic collapse, activation and duration, degree of protection, exceptions, fairness to AI nations, and anti-exploit safeguards. No immunity, invulnerability, or specific protection mechanism is approved yet.
- The simulation continues while the server runs; offline protection does not imply pausing national economic simulation.

### Territorial resource knowledge and yield — confirmed (2026-11-14)
- Villages automatically know **both the types and quantities of underground resource deposits** within their territory, without requiring a prospecting step.
- Deposit quantity is an input to **potential extraction yield**. Knowledge of deposits does not itself generate output: realized production still depends on extraction facilities, workers, power, technology, logistics, and other existing economic constraints.
- The exact yield formula and how quantities are represented are implementation/balancing details, not newly approved numerical values.

### Village information displays progress with national technology — confirmed direction (2026-11-14)
- The in-world village information interface should **evolve with the nation's technological progression**, rather than presenting a ComputerCraft-style computer display from the start.
- **Early stage:** simple physical **signs** conveying village information.
- **Intermediate stage:** a more capable **segmented display**.
- **Advanced stage:** a **ComputerCraft-like computer display/interface**, unlocked through the nation's computer/technology progression.
- This is a **visual and progression direction**, not yet a finalized UI specification. Exact blocks, screen layouts, statistics, interactions, installation requirements, and progression unlocks are still to be designed. Do not assume the user approved a specific hardware mod dependency merely by saying 'ComputerCraft-like'.

### Village dashboard versus action menus — confirmed separation (2026-11-14)
- The village **dashboard is an information display** that comprehensively reports that village's statistics and relevant conditions: resources, needs, relations, modifiers, and other information needed to understand the village. Do not arbitrarily restrict the dashboard to a small fixed subset of stats; exact layout and presentation remain to be designed.
- **Interactive menus serve a different purpose:** taking actions and making decisions, such as selecting contracts, managing diplomatic relations, and other available governance/economic actions.
- Both physical in-world displays and interactive menus are part of the intended experience; this is **not** an either/or choice. Preserve the technology-tiered display progression (signs, segmented displays, computer-like displays).
- The exact means of opening menus, permissions, which actions exist at each technology tier, and whether menus can be accessed remotely are **not yet decided**.

### Player-configured automated rail logistics and contracts — confirmed direction (2026-11-14)
- The goal is **automation of repetitive logistics**, not merely unlocking remote village menus with a technology tier.
- Players should be able to **preconfigure train routes, destinations, and operating instructions** so that trains can move goods between locations automatically, including to fulfill accepted/eligible contracts, without the player manually plotting each train path or dispatching each shipment.
- The player defines the presets/rules and retains control of the logistics network; actual routing and dispatch operate dynamically under those presets and existing physical track, access, capacity, and delivery-verification constraints.
- **Still to design:** whether contracts are automatically accepted versus only automatically fulfilled; matching goods/quantities to contracts; train scheduling, routing priorities, loading/unloading, exceptions, permissions, and the configuration interface. Do not treat these details as already approved.
- The user explicitly corrected the framing: this is **not necessarily a technology-gated central national computer or remote access requirement**. Do not impose that requirement without a separate decision.

### Rule-based automated contract acceptance via factory/decision blocks — confirmed (2026-11-14)
- Players can configure **automatic acceptance of contracts** when a contract satisfies a player-defined set of conditions; manual acceptance is not required for every qualifying contract.
- **Factory blocks or decision blocks** are intended as the physical/configuration mechanism for specifying and evaluating these rules. Their exact block types, recipes, interface, connectivity, and logic are still to be designed.
- Once an eligible contract is accepted, the existing player-configured train logistics system can handle its delivery automatically, subject to available goods, valid routes, capacity, and other established economic constraints.
- Do not assume every contract is accepted indiscriminately. Acceptance is conditional on player rules. Exact filters (e.g. item, quantity, profitability, destination, inventory, risk) are examples to discuss, not yet approved.

### Demand-driven factory automation and end-to-end fulfillment — confirmed (2026-11-14)
- Player-configured decision/factory blocks can express **simple instructions** as well as compound programmable conditions. Example intent: 'Send this product to that village or country whenever it needs it.' Do not require players to program complex logic for basic recurring supply.
- Once an eligible demand or contract matches the player's rules, the system should **coordinate the necessary steps automatically** to fulfill it, including relevant financial transactions, currency/money conversion where applicable, and logistics/dispatch. Actual funds, inventory, production capacity, route access, transport costs, contracts, and other established constraints still apply; automation does not create free goods or money.
- The core design objective is to give **large player-built factories sustained, meaningful demand**, potentially requiring production and delivery of **millions of items** over time. Recurring needs and automated supply chains should make high-throughput industry useful rather than decorative.
- The user confirmed both a simple 'supply whoever needs this' workflow and more advanced rule-based contract acceptance. Specific UI, decision-block logic, exchange/conversion mechanisms, throughput, and performance optimization remain to be designed.

### Automated production management and nation-scale factory demand — confirmed (2026-11-14)
- Players **retain the ability to adjust factory production manually**, but the intended later-stage experience supports **automatic production adjustments in response to actual demand** and other configured operating rules.
- The player should be able to focus primarily on **designing, constructing, and expanding factories**, rather than micromanaging every production setting, contract, dispatch, and delivery. Automation remains player-configurable and constrained by real inputs, capacity, energy, workforce, transport, and funds.
- The **nation/village simulation is a major pillar of the modpack**, not a minor background feature. National and village consumption, trade, infrastructure, military needs, and development should meaningfully shape **factory scale, production volumes, and expansion decisions**.
- This is a design direction for progressive automation, **not** a decision that every factory is fully autonomous from the beginning. Exact automation tiers, control interfaces, production algorithms, and triggers remain to be designed.


## November 14, 2026 — Physical economy automation, banking, taxation, budgets, and lending (conversation reconciliation)

Status: user-confirmed decisions below are design requirements, **not proof that mods already interoperate or that features are implemented**. Examples are illustrative, not fixed balance values. Preserve all earlier rules unless explicitly superseded.

### Physical factory automation and mod integration
- Automation is **not a menu unlock**. Players build and configure actual in-world factory gauges, sensors, logic/decision blocks, controllers, financial terminals, and connections. The exact combination of block wiring versus internal programmable logic remains **deferred**, not approved.
- Examine Create 6 Factory Gauges and logistics, Create: Extra Gauges, Create: Factory Controller, and **Create: Numismatics** as candidate foundations. Numismatics is the user-confirmed money mod. Potential roles: inventory/production requests, logic and arithmetic, consolidated production controls, banking, vendors, payment collection, and sales transactions. **Verify mod versions, actual block capabilities, and cross-mod compatibility before implementation**; proposed interactions are not confirmed native functionality.
- Economic demand/contract information must be accessible through **some physical connection or in-world infrastructure**, not globally exposed to every factory automatically. Exact connection method remains undecided.
- Player-configured automatic contract acceptance, factory production, payments/conversions, and train delivery remain intended, with physical supply and real money constraints. Players may use simple rules or more complex decision logic; retain manual override.

### Village and national accounts; flow of money
- **Each village has two distinct accounts**: (1) a working/operating **income-and-expense / tax pool** receiving money during the cycle and paying trade deals, wages, services, interest and other outgoings; (2) a **treasury/reserve savings** account holding retained funds. The **national government also has an operating/tax-pool account and a treasury/reserve account**, with analogous end-of-cycle settlement.
- Village and national balances remain separately owned. A combined national financial overview is an **aggregate report**, not a third spendable pot and not additional money. No double-counting between accounts.
- The national government normally accesses village funds only by **taxation or authorized transfers**, not arbitrary withdrawals. Possible confiscation for unpaid village taxes or obligations is **deferred**, including authorization, enforcement, and limits.
- At the end of a tax/pay cycle, first account for actual operating receipts and payments (trade, purchases, services, net interest, etc.). **Tax the eligible positive remaining operating-period balance**, not gross receipts or accumulated treasury savings. Transfer the national tax share to the national operating account; the village's after-tax remainder goes into its reserve treasury. National-level operating surpluses likewise settle into national reserves after its own obligations.
- **Reserve transfers and loan proceeds are financing movements, not earned revenue**. Do not re-tax reserve withdrawals or create taxable profit by moving money between accounts. Keep a ledger of external revenues, expenditures, financing transfers, interest and loss carryforwards to calculate the eligible taxable amount; do not blindly tax a cash balance inflated by internal transfers.
- When the operating pool cannot cover spending, funds may be drawn from treasury reserves; **borrowing may also be chosen even when reserves exist** to finance economically promising investment. No new wealth is created by opening an account, taking a loan, or transferring funds.
- Reserve depletion and financial strain may influence stability, production, taxation pressure and other economic modifiers. The exact trigger formula and severity are **not finalized**.

### Tax loss carryforward and timing
- A village's eligible net operating loss may offset its positive taxable balance **only in the immediately following tax cycle**, and only if the nation's tax policy permits it. Apply allowed deductions **automatically**; unused amounts expire after that next cycle. Never double-count losses or treat reserve withdrawals as losses.
- The national government may enable or disable loss carryforwards as a fiscal policy; fiscal pressure can motivate its choice. A policy change takes effect **in the next tax period**, leaving the current period's treatment unchanged. An old deduction is not guaranteed beyond that next-period policy.
- All receipts, spending, taxes, interest, transfers and deductions need separate accounting entries, so the taxable operating surplus is accurate and savings are not inadvertently taxed.

### Spending, fiscal pressure, simulation cadence
- **Debt-to-savings ratio** is a primary driver of how severely a village/nation cuts spending; rising debt relative to savings increases pressure for cuts. Cuts should begin **before** both accounts reach zero, not only after insolvency. Savings can fund investments and debt may coexist with positive savings.
- Existing economic **decision tick is approximately once every two minutes** while the server is running. On ticks, simulation entities decide purchases, sales, health spending, allocation, financing, and policy responses. Do not confuse this with every cash transfer occurring only once per tax cycle.
- **Current-cycle budget allocations already committed must not be retroactively rewritten**. Decision-tick fiscal analysis updates **next tax cycle's budget targets/allocations**; current-cycle obligations and actual payments still proceed under their applicable rules. Distinguish dynamically updated forecasts and future tax/budget policy from money already allocated. Precise tax-rate adjustment rules remain to be balanced.

### Lending sources, lender selection, pricing, and limits
- A village or nation can seek loans from its **own national government/bank, other villages, other nations, or other eligible lenders**. Evaluate lender relations, eligibility and **lowest feasible effective interest rate**; prefer viable domestic options before foreign lenders, but do not force an uncompetitive national loan. Poor relations can rule out or disfavor domestic lenders; a sufficiently better rate may justify a different source. If domestic offers are unsuitable, seek foreign lenders.
- **Each lender has a fixed/posted base rate for the offered loan**, influenced by the relevant creditworthiness/credit relationship. The **purpose of borrowing** (e.g. healthcare versus housing) modifies the effective interest rate. Do not invent independent, arbitrarily adjustable purpose tables for every lender; earlier user response rejected that extra layer.
- **Loan size relative to savings/reserves affects pricing and feasibility**. A loan approaching or exceeding the relevant village/nation's reserves should generally demand a higher rate or may be declined, depending on the lender's exposure and borrower economics. The user explicitly confirmed the loan-amount-to-savings influence. Example: a lender with 10 million in reserves may be reluctant to lend all 10 million without an extreme premium. **Both borrower credit/risk and lender capacity/exposure must be considered**; do not collapse these into a single borrower-only ratio.
- **No universal fixed maximum borrowing cap was approved.** Borrowing can be as large as lenders will economically support, with available reserves, credit, relations, loan purpose, existing debt and pricing governing offers. Do not introduce an arbitrary hard ceiling.
- Existing previously documented lending mechanics remain in force: payment history affects credit scores and recovery; lateness-based penalties per overdue loan; lender-specific minimum credit eligibility for new loans; demand for repayment before collateral enforcement; no automatic seizure of national assets; escalated consequences for repeated defaults with recovery rules. Check the earlier lending sections rather than reopening settled choices.
- Exact repayment schedules, interest formulas, budget thresholds, lender capacity models, and block/API integration should be cross-checked against prior sections and marked unresolved only if genuinely absent; **do not fabricate approvals or numerical thresholds**.


## November 14, 2026 — Contract generation, governance, budgets, public spending, and loan workflow (continued review)

Status: reconciled from the subsequent spoken conversation after the prior GitHub import. These are **design decisions**, not implemented features. Examples are illustrative. Preserve existing rules; where the user corrected an assistant interpretation, the correction below controls.

### Contract generation and market allocation
- Contracts arise from **real economic needs**: population and consumption, industrial development, inventory, domestic production, incoming trade, infrastructure upkeep, military requirements, financing, policies, and existing commitments. Check stock, scheduled deliveries, active contracts, and internal supply before posting unmet demand; avoid duplicate demand and arbitrary/random contracts.
- Contracts remain available for other eligible AI villages/nations/suppliers to fulfill if the player does not accept them. **Accepting a contract makes fulfillment obligatory**.
- **Do not automatically increase total national consumption merely because the player completes more contracts.** Successful fulfillment, pricing and reliability can gradually increase the player's *share* of existing national demand, displacing other suppliers as **old contracts finish**. Existing signed contracts are honored rather than canceled just to switch to a preferred supplier. Population/economic growth independently increases demand.
- Nations forecast resource depletion against required stock thresholds. They may issue a **binding contract now for future delivery** or arrange a future-dated requirement; acceptance binds the supplier. Financial stability, available funding, urgency and projected needs influence timing. The exact public visibility/status of nonbinding forecasts was not separately finalized; do not assert that all projected requirements are merely nonbinding previews.
- Procurement categories include goods/materials, construction, logistics, services, military/weapon/ammunition supply, financial/loan contracts, and **vehicle contracts as a distinct category**. Ships, trains and other vehicles may have their own procurement needs; categories may overlap by subject but must not double-count obligations.
- **One-time, recurring, and emergency** agreements are supported; emergencies may pay premiums and impose strict deadlines. Construction can be materials-only or require player-built physical structures.
- Goods demand includes consumables, concrete, machinery, replacement equipment and ongoing industrial upkeep. Contracts may be single purchases or recurring fixed-price supply.
- **Construction with maintenance** and vehicle/ship contracts may cover initial purchase/build plus recurring replacement parts and upkeep at an agreed **fixed unit price for the entire contract term**. Alternatively, the buyer procures individual maintenance items at then-current local market prices. Economic/financial feasibility and expected upkeep drive which structure a nation selects; financially unstable nations may still select fixed-price agreements if cheaper.
- Price negotiation applies to **all kinds of purchases from the player's company** (goods, construction, factories, ships, vehicles, upkeep). A supplier's **discounted fixed price to a struggling buyer improves relations**, while standard/higher agreed price is diplomatically neutral. Do not reverse the direction of the discount. Fixed price stays fixed after agreement.
- **Vehicle contracts** may request existing player-designed models or new custom designs. They can order multiple units once, multiple units over time, either with or without ongoing maintenance. Specific technical specifications, inspection, performance formulas and balancing remain deferred.
- War or shortages can prompt nations to buy quantities of ships, vehicles, weapons, ammunition, factory output and other equipment from player companies, using real production and payment. Full detailed fleet simulation was **not approved** merely by discussing it.

### Player company versus nation; supplier priority
- **Player company and player-controlled nation are distinct economic actors**, with distinct funds and accounting. Player company fulfills physical production/delivery contracts and is paid even when supplying its own nation. AI-to-AI fulfillment is modeled as simulated trade rather than requiring the player's factory.
- Player can govern national procurement by specifying **what quantity/item the nation needs**, including issuing a contract the player's own company may accept. **Market/simulation determines prices**; the player cannot freely invent contract prices to pay themselves. Domestic supply, physical production, actual transfers and financial accounting still apply.
- **Scope: ONLY contracts issued by the player's own player-controlled nation, when that nation is procuring goods or equipment.** Supplier evaluation order is **(1) villages belonging to that same player-controlled nation, (2) that player's separately owned manufacturing/trading company, (3) eligible foreign AI nations or suppliers**. This is **not a universal procurement hierarchy for every AI nation**; AI nations use their own existing diplomacy, trade, pricing and supplier-selection rules. **All-or-nothing award for this player-nation procurement path:** a candidate unable to fulfill the entire specified contract is skipped; the full contract is offered to the next eligible supplier, not split among them. The player's company is not synonymous with the player's nation and does not automatically receive other nations' contracts.
- Other AI suppliers compete and fulfill trade through the simulated economy; keep existing signed contracts in force. Supplier preference increases gradually with successful performance.

### National governance and contracts
- Player acts as **president/policy-maker**, not an individual village clerk. Village AI independently manages routine needs, local procurement and ordinary economic decisions within national rules.
- **Nationwide procurement policies are confirmed**: player sets standard contract rules (e.g. payment structure, deadlines, penalties, domestic procurement preferences) and villages apply them automatically by default; player may override particular contracts. Contract penalties are **configurable contract terms**, not a single universal fine. Precise limits and enforcement formulas remain to be implemented.
- Contracts support **upfront lump-sum payment, payment on delivery, and installment/progress payments**. Available terms reflect the contract and economic/relationship conditions. An issued agreement creates real obligations; do not treat funds as free or goods as delivered without fulfillment.

### Government budget and public services
- National government budget is **hierarchical**: a top-level **contracts/procurement budget** with adjustable allocations by contract category, alongside separate healthcare, military and other government spending budgets. These are **allocations, not separate bank accounts**. Do not confuse contract procurement with broader public-service expenditure.
- **Budget allocations are locked for the current tax/pay cycle for both player and AI**. No mid-cycle transfer/reallocation between budget categories; revised targets take effect next cycle. Two-minute simulation decisions still handle purchases and actual transactions within the applicable current allocations.
- **Budget overspending results in debt/financing obligations**, rather than automatically prohibiting spending. Funding must be economically accounted for; a loan still requires an eligible lender, and an unfunded obligation must not create money. End-of-cycle debt repayment can use operating income and reserves, subject to existing contractual minimum payments and policy.
- Player should choose **financial policy and desired borrowing/repayment posture**, while the simulation computes economically justified rates, fees and actual obligations. Player may specify a desired loan amount and purpose; **must not directly set arbitrary interest or fees** to exploit the economy. AI nations use the same economic validity checks.
- Public healthcare and similar services are **distinct from procurement contracts**. Government spending can finance operation of existing facilities, workforce and service delivery; actual healthcare output remains constrained by facilities, workers, potions/medical inputs and physical supply. **Spending cannot create goods or care out of nothing**.
- Use **aggregate village-level healthcare demand and production**, not per-citizen financial simulation. Population, disease, existing healthcare capacity, supply, and village economic conditions are relevant. Private activity should cover substantial needs; government intervention can fill gaps but should not automatically fund the entire private industry. Excessive government dependence and deficit pressure should matter. Exact coverage/funding formulas and automatic subsidy phaseout were **not finalized**.
- A budget may allocate healthcare, military, procurement and other public spending based on production needs, costs and economic capacity. Wealth is not itself an instantly spendable government balance; spending must be financed from actual accounts or debt.

### Loan contracts — requests, bids, partial funding and execution
- Loans are a **financial contract category**. Borrower specifies desired principal and purpose, broadcasts a request, and receives **multiple simultaneous offers** from eligible lenders for comparison. Simulation sets lender-specific offered principal, credit/relations eligibility, interest, fees and repayment terms. Lenders can offer **less than requested**; borrower may accept or reject and seek another lender.
- **Partial funding is allowed through multiple separate loans.** On accepting an offer for part of the total, finalize that loan, then **issue a NEW request for the remaining principal**, generating **fresh offers**. Do **not** automatically resize old offers. New request follows the selected request-duration settings. Example: $5m requested, $2m accepted, new $3m request.
- Borrower can select a finite or **indefinite request duration**. An indefinite request stays open until canceled or fulfilled. **Only the lender determines expiration of its individual loan offer**, which is separate from request duration.
- Before acceptance, a lender may **withdraw or revise a nonbinding offer**. After acceptance, the loan is binding on both parties.
- **Accepted loan principal transfers immediately in one lump sum** to the borrower's operating account from the lender's available funds; record matching debt. No deferred or installment disbursement. Transfers are financing, not taxable income.
- Scheduled loan repayments (monthly, yearly, or contracted cadence) are **automatic by default**, but player may **turn off auto-pay** at any time. This does not waive due payments, interest, penalties, credit damage or default rules. **No advance reminders** are required after auto-pay is disabled; user monitors the contracts dashboard and sees overdue status.
- **Unified contracts dashboard** should cover **issued contracts, currently paying/active contracts, and other contract statuses**, with category filters and detail views. Loan entries show outstanding balance, interest rate, next payment, schedule, status (active/overdue/paid), and auto-pay controls. Dashboard should distinguish national contracts from player-company obligations and other economic actors, rather than silently mixing ownership.
- Existing credit score, repayment, late fees, default/collateral, loan purpose, savings-exposure, lender relation and reserve rules from prior sections still apply. No arbitrary hard cap on borrowing was approved.

### Explicitly unresolved / implementation details
- Exact contract deadlines and penalties, financial formulas, public service subsidies, vehicle specifications, custom block integration, demand forecast parameters, market rates and other balance numbers remain implementation/design work. Do not infer approval for numeric examples.
- No GitHub code implementation is implied by these design notes.


### Contract mechanics matrix — explicit triggers, parties, and constraints (clarifying addendum)

**Scope and actor model:** An issuing **village** uses its own economic needs/budget within national policy; an issuing **AI nation** follows its own diplomacy and procurement decisions; the **player-controlled nation** can issue policy-directed procurement; the **player-owned company** is a separate potential supplier with its own funds, inventory and real production obligations. AI-to-AI fulfillment is simulated trade, not an automatic physical player-company contract. The special village -> player company -> foreign supplier order is **ONLY for procurement issued by the player's own nation**, as clarified above.

**Common generation pipeline (every two-minute decision evaluation, not necessarily one new contract per tick):**
1. Determine current and forecast need from population, consumption, industrial throughput, infrastructure/asset condition, healthcare, military threat/war, policy and development plans.
2. Subtract usable local inventory, already committed incoming deliveries, active contracted supply and feasible domestic production; do not issue overlapping orders for the same units.
3. Evaluate the remaining requirement against available funds, existing obligations, debt/reserves, stability, prices, diplomatic/trade access, supplier capability and delivery timing.
4. Select an appropriate contract **category** and **structure** (one-time, recurring, urgent, fixed-price upkeep, construction plus maintenance, etc.). A forecast can lead to a binding order now with future delivery; acceptance creates a real obligation.
5. Post/offer the contract under the **issuing actor's** applicable procurement rules. Other eligible AI parties may fulfill it if the player does not. Completed player deliveries can gradually win a larger *share* of demand but do not magically increase the buyer's underlying consumption.
6. Upon acceptance, track payer, supplier, quantity, pricing terms, funding, deadlines, delivery evidence, upkeep and penalties; reconcile physical goods and payment **once**, avoiding duplicate fulfillment or money creation.

**Category-specific contract causes and forms:**
- **Goods and materials:** Consumption and stock thresholds; shortage of concrete, metals, fuel, food, medical supplies, factory inputs, machines or replacement parts; existing production/incoming shipments reduce the order. Can be one-off or recurring at agreed fixed prices.
- **Construction / factories / infrastructure:** Population/housing needs, industrial capacity bottlenecks, planned expansion, roads/rail/power and facility replacement. May require delivery of materials **or actual player construction**. Can be lump-sum or staged and optionally include fixed-price future upkeep.
- **Vehicle / ship / rail equipment:** Demand for transport or industrial capacity, replacement/upkeep, new infrastructure, government/military requirements and war losses. Buyer may order existing player designs or request a custom design; one-time quantities or scheduled recurring batches, with optional maintenance. Exact performance checks and fleet modeling remain deferred.
- **Military weapons and ammunition:** War, mobilization, defense readiness, consumption, attrition, depleted reserves and forecast requirements. Orders must correspond to real military needs, funding and equipment production; they may be urgent or future-dated.
- **Logistics / transportation:** Need to move existing goods between producers and destinations where available logistics capacity/routes are insufficient. A logistics contract purchases **transport service**, not newly created goods.
- **Services / public needs:** Actual service demand and available capacity (e.g. healthcare); distinguish buying a defined service from the government's **separate operating budget** for staffing and facilities. No spending-created medical items or abstract free output.
- **Financial / loan:** A borrower requests an amount and purpose because of investment or financing need. Lenders bid calculated terms; offer expiration is lender-set, request duration can be finite/indefinite, accepted loans transfer lump sum, and partial acceptance produces a **fresh request** for the balance.

**Pricing and selection:** Local markets are distinct and price depends on actual supply/demand and trade conditions. Negotiated discounted fixed-price supply to a financially struggling buyer can improve relations; standard price is neutral. Long-term fixed unit prices do not float with subsequent market changes. Active contracts remain binding and are not canceled simply because a new supplier is preferred. For the player's **own nation's** all-or-nothing procurement, skip any candidate unable to fulfill the full order; this rule is not automatically imposed on every AI nation's trade.

**Still not decided:** exact contract-generation thresholds, forecast horizon, capacity verification, contract expiration for non-loan categories, penalty magnitudes, vehicle testing, maintenance wear formulas, and precise pricing/AI bidding formulas. These require explicit design or implementation balancing; no numeric values in examples are approved.
