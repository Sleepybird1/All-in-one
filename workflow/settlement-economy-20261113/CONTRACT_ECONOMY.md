# Settlement contracts and economy

The balance values are provisional except where the owner set a range. The staged native pilot records district surveys, hub activity, membership, order reservations, and verified receipts supplied by a trusted adapter. See the [settlement source pilot](README.md#settlement-source-pilot) for current integration status.

## The economy loop

A village buys what its residents, active facilities and funded customers will use. It sells what its facilities can produce and what it can spare. A completed delivery changes stock and settles the order. A completed and commissioned project changes which facilities can operate. That is what creates new production jobs and standing demand.

**Need → funded order → verified receipt → stock → use or production → output sale → village revenue → new orders.**

A village has a population, staffed facilities, usable stock, storage space, a treasury, active customers, transport connections and a measured utility supply. The regional simulation can work from those saved records. A village chunk can stay unloaded while the simulation forecasts demand, quotes orders and determines whether a prepared upgrade is eligible.

## How villages grow

| Stage | What changes | What the village starts asking for |
| --- | --- | --- |
| Local trade partner | A market and small workshops serve a resident population. Establish a supply route. | Food, common metals, wire and small shipments. |
| Specialized town | Commission a mill, refinery, packing depot or another facility that fits the site and has buyers. | Feedstock, service spares, operators, regular freight and a measured local power supply. |
| Regional hub | Meet ongoing service targets and add depot capacity, staff, grid capacity and buyers. | Large tenders, parallel production lines, regular import/export routes and sustained power at several substations. |
| Offworld or endgame customer | Commission a facility or port with locally useful output and a buyer for repeat lots. | Bulk imports, specialized machinery, strategic export lots, replacements and regional grid service. |

Use four independent growth checks:

- **Customers.** Signed downstream orders or measured ongoing use must justify the extra output. Forecasts can show future demand before the customer commits funds.
- **Service record.** A regional tender can require recent deliveries in multiple periods at two or more existing trade partners. A starting calibration is at least 80% of essential demand served for three periods, with meaningful completed quantities rather than a receipt count. Newly connected villages add local jobs and access to new markets. Sustained business keeps access to larger regional work.
- **Capacity.** Verify staff and housing slots, input and output storage, transport, and the power and equipment required by the new facility. A village can be excellent at exporting one product and still buy everything else from nearby towns.
- **Money.** The village or a sponsor must cover the construction escrow and an opening operating reserve. A project may pay for the delivered build materials before commissioning. Ongoing demand begins after construction, utility checks, and verified startup.

Population growth depends on food surplus, housing, employment, healthcare, and living conditions. Each additional resident contributes a recurring household requirement. Industrial demand grows mainly when a facility adds shifts, lines or customers. If an anchor stays unloaded for a long time, the simulation can accumulate a limited shortage and reassess readiness. Downtime alone gives no extra population, inventory, revenue or machine output.

## Nations and population

An independent village can join a trade league. A mature league can become a nation with shared trade policy, infrastructure tenders, and a national treasury separate from every village treasury. Villages remain the local depots, work sites and places players visit. Each anchor represents its settlement and a surrounding district. A mature nation representing **40 million simulated residents** across its districts is a scale target for balancing.

### Residents the player sees

- Give each loaded village a provisional ceiling of **30–40 live villagers**. Show workers, traders, station crews, officials and residents at locations players use. Preserve the identities of named characters and leave player-managed villagers alone. Count existing villagers against the local display budget before adding any representatives.
- Use a shared server budget across active villages, with lower detail or fewer managed representatives farther from players. Allocate on the server so two players seeing the same town share its cast. When a managed village unloads, retain its role assignments, persistent character state and economic totals. Simulated residents need no individual AI, memory record or entity.
- Profile the actual pack before setting the cap. Measure the 30–40 range with several villages loaded at once, plus the normal railway, Create and ship workloads. Village population changes update aggregate counts and planned representation. Ordinary chunk loads keep the existing lookup-only behavior, and any NPC work happens separately on a budget.

### Houses, beds, and jobs

Use the actual generated village as the starting point. Record its existing residents, valid beds, and active workplaces when registering the anchor. Keep ordinary residents, their trades, and their saved positions. On village load, a queued job can restore the simulation's managed representatives in batches. Each representative has a stable identity and a job assignment before appearing on a safe, clear tile beside their assigned bed. When using vanilla professions, pair the assigned profession with an available matching job-site block. Civic roles such as a station attendant can use their registered workplace instead. Skip any slot with an occupied bed, unavailable job site, or unsafe spawn position, and retry after the relevant facility is ready.

For each town, **visible population target** = the least of the population-based target, usable bed capacity, staffed job capacity, and its allocated live-entity budget. Count existing residents and their bed and job reservations before adding any managed representatives. A town targeting 25 visible workers with 24 usable beds and 18 funded job slots can show 18 workers. To support all 25 it needs at least one additional bed and seven additional jobs. Plan houses by their actual bed count and workplaces by their active positions. A new depot or factory can therefore produce separate contracts for housing, equipment, and staffing. The simulation plans those additions before the village loads. The existing placement queue validates space before building, and the spawn queue runs only after beds and workplaces are ready.

Track simulated housing-unit counts separately from the capacity those homes currently provide. As occupancy rises, overcrowding increases emigration pressure and harms health, productivity, happiness, and stability. Severe overcrowding drives up healthcare, infrastructure, and maintenance costs, even when food is available. Occupancy thresholds, penalty curves, and whether a separate hard population ceiling applies remain open. Job allocation responds to village needs. Unemployment lowers stability, encourages emigration, and can reduce births depending on the village's conditions. [Approved housing and employment rules](../../VILLAGE_AI_SIMULATION_ECONOMY.md#employment-demographic-effects-and-housing-representation--confirmed-2026-11-14)

### Visible population thresholds

Give each anchor a visible baseline from its actual workplaces and amenities, then add one representative when its district population reaches each doubling threshold. Use **300,000, 600,000, 1.2 million, 2.4 million, 4.8 million, 9.6 million, 19.2 million, and 38.4 million** as initial total-population milestones. The population bonus grows slowly while the district can keep getting economically larger. Use district population once per anchor. A national merger adds no visible villagers on its own.

| District population | Added visible slots | Small town with a 12-slot baseline | Capital with a 30-slot baseline |
| ---: | ---: | ---: | ---: |
| Below 300,000 | 0 | 12 | 30 |
| 300,000 | 1 | 13 | 31 |
| 600,000 | 2 | 14 | 32 |
| 2.4 million | 4 | 16 | 34 |
| 10 million | 6 | 18 | 36 |
| 20 million | 7 | 19 | 37 |
| 40 million in one district | 8 | 20 | 38 |

The local target is the baseline plus the number of reached thresholds, capped by the settlement's local ceiling and the server's shared budget. Baselines are test values. A small town can start with a recognizable cast. Opening a market, station, or factory can add roles and raise its baseline when the budget allows. The national board can show a nation of 40 million across several villages, each with its own smaller district count.

Update the target at scheduled economy intervals and stage new villagers through the existing representation budget. For a provisional buffer, reduce a population slot only after the district stays below 90% of its threshold for two intervals. Apply reductions through ordinary managed cast turnover. The visible count is independent of food, freight, and industry calculations, which use the full simulated population and facility activity.

### What population changes

| Quantity | Calculation | What players build or haul |
| --- | --- | --- |
| Food and household goods | District population × consumption rate per resident per economy period, using rates tuned for pack throughput | Farms, food processing, granaries, and scheduled deliveries from producing districts to deficit districts |
| Industrial supplies | Active production batches × input use per batch, plus verified operating wear | Fuel, coolant, mechanisms, spare parts, and a grid sized for the work actually running |
| New machines | Newly funded lines × machines required by their bills of materials | Batches of pumps, engines, transformers, and controllers when districts expand |
| Replacement machines | Installed machines by type × the expected replacement rate at their operating load, followed by verified service accounting | Long-running manufacturing orders for the equipment the nation relies on |

Track food and household consumption by district, then aggregate results for the national board. Local output covers local needs first under the existing reserve and treaty rules. A surplus in one district only covers another district's shortage once a real shipment can move between them. Post the uncovered amount as funded production, supply, or freight lots. Keep national reserves and shared transport in the same accounting chain so one pallet can only satisfy one requirement.

The pilot uses **4 food items per resident per Minecraft day** of 24,000 elapsed game ticks. At that illustrative rate, a 40-million-resident nation needs **160 million food items per day**. If domestic production delivers 120 million and imports deliver 20 million, 20 million remain open to new contracts. Bulk packaging can change shipment handling while every delivery still charges the exact underlying items. Tune consumption and lot sizes after measuring processing and freight throughput.

| District | Simulated residents | Food use per day | Local production per day | Freight and uncovered demand per day |
| --- | ---: | ---: | ---: | --- |
| Farming district | 10,000,000 | 40,000,000 | 72,000,000 | Ships 32,000,000 to the port district |
| Port district | 16,000,000 | 64,000,000 | 0 | Receives 32,000,000 from farms and 20,000,000 in imports, with 12,000,000 still needed |
| Industrial district | 14,000,000 | 56,000,000 | 48,000,000 | Needs funded lots for the remaining 8,000,000 |

Calculate and store each village's needs separately from the government's national needs. The national calculation can consider aggregate village needs alongside independent obligations such as infrastructure, military procurement, and emergency reserves. The dashboard can show the current village, aggregate village needs, national-government needs, and a combined view. Deduplicate shared obligations so a tender and its underlying village orders cannot both pay for the same goods. Keep simulated household trade in the economy ledger. Depots release only verified stock, and funded contracts require verified receipts. [Approved dashboard and national demand rules](../../VILLAGE_AI_SIMULATION_ECONOMY.md#separate-village-and-national-needs-with-combined-dashboard-views--confirmed)

The in-world dashboard reports village statistics, stock, needs, relationships, and the factors affecting them. The reviewed headline statistics are population, happiness, stability, wealth, and relations. Other conditions and independent treasury balances can appear in the details. As national technology advances, the information display progresses from signs to a segmented display and then a computer-like interface. Separate interactive menus handle contracts and governance. The exact blocks, permissions, and remote access remain open. [Approved dashboard and action menu distinction](../../VILLAGE_AI_SIMULATION_ECONOMY.md#village-dashboard-versus-action-menus--confirmed-separation-2026-11-14)

Population change is births minus deaths plus immigration minus emigration. Growth from births requires food surplus. Healthcare can alter the birth rate and reduce preventable deaths. Moving between two villages credits one and debits the other. Count children and elderly together as dependents. Civilian workers can also serve in the militia. Nationally employed professional soldiers count toward the population where they are stationed and are accounted for separately from civilian jobs. The dashboard summary shows total population and net change, and its detailed view can show the four components. A merger or split preserves residents, funds, property, and outstanding commitments. Domestic routes can become cross-border contracts after a split. [Approved population accounting](../../VILLAGE_AI_SIMULATION_ECONOMY.md#population-accounting-and-dashboard)

## Contract types

| Type | Example | Credit and repeat behavior |
| --- | --- | --- |
| Replenishment | Supply food, steel, wire, fuel, coolant or parts | Receiving stock increases. New orders appear as users draw down inventory. |
| Production | Operate a village steelworks shift or fill an order for pressure equipment | Real inputs and eligible machine time create real output. Output waits for a customer or a reserved depot space. |
| Maintenance | Supply replacement parts for a refinery, reactor or Atmospheric Scoop | Spare deliveries stock the depot. Separate service evidence consumes parts and clears accrued wear. |
| Freight | Pick up packages made by one village and deliver to another | Destination receipt closes the shipment. An independent carrier can be paid from the freight budget. |
| Sustained power | Keep an industrial district above a minimum received rate | A meter must verify an uninterrupted qualifying window. Multiple contracted substations can be required to qualify at once. |
| Bulk energy | Deliver a quantity of energy to a reserve before a deadline | Metered net import accumulates over the window. Separate intervals can contribute. |
| Construction and commissioning | Supply, build and start a refinery or export terminal | Finite bill of materials and a separate startup milestone. The operating facility can create recurring jobs afterward. |
| Regional or external export | Ship standardized bulk steel or finished mechanisms under a supply agreement | Funded purchase lots renew on a schedule within the buyer's capacity, order quota and budget. |

## The calculations

All rates in a calculation must use the same interval. Examples use economy periods or operating minutes. Pick an actual clock and conversion before balancing the pack. A price or quota can be forecast without reserving items or funds.

### Purchase and supply requests

For each exact item or fluid:

- **Recurring use per period** = household use + inputs for scheduled production + facility upkeep. Count one-time project materials and committed sales as separate quantities due within the horizon. Record each obligation once. A sale already reserved from finished stock is excluded from usable stock and from open requirements.
- **Target stock** = safety stock + recurring use × replenishment horizon + one-time quantities due within that horizon. Choose the horizon from expected delivery time and a buffer for disruption.
- **Shortage** = max(0, target stock − usable on hand − in transit − accepted but unshipped − guaranteed unreserved local output arriving within the horizon).
- **Receivable space** = remaining depot space − space already reserved for earlier receipts. An accepted quantity reserves destination space and money. Sending it moves it from accepted-unshipped to inbound. Receiving it releases the matching reservation and adds stock.
- **Posted quantity** = the least of shortage, receivable space, the board's cap and whole units affordable from the buyer's available budget. Round down to a shipment lot. A shortfall below the minimum lot stays visible.

Use forecast production to inform the board, and subtract output from a shortage only when a firm amount is available by the due date and is still unassigned. Blocked trucks, queues, no power and late goods can change a future offer. Existing orders keep their accepted terms.

When funds or storage are tight, reserve capacity for basic needs first, then inputs required to fill already-funded customer orders, then discretionary expansion. A shutdown removes the idle line's ordinary operating demand. A recovery order can still request the fuel, spares, or feedstock needed to reopen it. Keep surplus items in storage or offer them to an eligible buyer. Stop requesting inputs when forecast stock and committed deliveries already cover the plan.

### Production and output jobs

A funded customer or a local stock target tells a facility what to make. Subtract unreserved finished stock and output already assigned to the same need. Then size the job in full production batches:

**Batches to schedule** = least of batches demanded, batches supported by actual usable inputs, staffed machine slots during the window, power budget, and free output space including committed pickups within the window.

To calculate the input bound, divide each usable input amount by its per-batch requirement, round down, and take the smallest. Output = completed batches × verified per-batch yield. Byproducts get separate storage and can become sell offers if they have a buyer. Running the numbers creates a production plan. Inventory is credited only after real inputs are consumed and the facility's work is verified.

For exports from a village, **available to sell** = max(0, unreserved on hand + eligible finished output − local safety stock − already scheduled local consumption). Confirmed sell lots are also capped by remaining buyer demand, funded payout, receiving space and booked transport. The village can pack the sale for player pickup or hand it off at a registered dock. Only the receiving side can mark the lot delivered.

Track orders that can start and orders that are blocked. A shortage of an input posts a supply request. A shortage of staff can post a recruitment, transport, or training job once jobs and housing exist. A shortage of energy can post a grid service contract. A shortage of funded customers leaves the proposed production job waiting. When the constraint is cleared, reevaluate the job at the next scheduled update.

### Demand-responsive factory automation

- Leave factory construction open to players and keep manual production controls available. Recurring village and national demand should make long-running factories useful at expanding scales, potentially producing and delivering millions of items over time.
- Later, players can use factory or decision blocks to accept eligible contracts under their rules. A basic rule can supply a chosen product to a village or nation whenever it needs it. Advanced rules can combine conditions without making complex programming necessary for basic supply.
- Under those rules, automation can adjust production, handle required funding or currency conversion, and use player-configured train destinations, routes, and operating instructions for dispatch. Respect actual inputs, workforce, energy, output and receiving capacity, route access, transport costs, and available funds. Verify each physical delivery and credit each item once. Registration is one way to establish reliable proof of fulfillment.
- Keep an initial manual path. The control blocks, automation tiers and triggers, financial exchanges, scheduling, permissions, and exception handling remain open. The roughly 60% physical player supply and 40% simulated local supply split is a balancing target.

[Approved contract acceptance](../../VILLAGE_AI_SIMULATION_ECONOMY.md#rule-based-automated-contract-acceptance-via-factorydecision-blocks--confirmed-2026-11-14) · [Approved factory automation](../../VILLAGE_AI_SIMULATION_ECONOMY.md#automated-production-management-and-nation-scale-factory-demand--confirmed-2026-11-14)

### Price, treasury and reputation

- **Base price** = reference production cost + agreed margin. Use measured yields, energy, and handling. Village markets keep local prices driven by supply, demand, resources, geography, infrastructure, trade access, tariffs, transport costs, and applicable relationships. National aggregates summarize those markets. Show freight once, either bundled in delivered price or as its own fee. The proposed 50–200% band is a tuning example. [Approved local pricing](../../VILLAGE_AI_SIMULATION_ECONOMY.md#historical-pricing-and-market-boundary-clarification--confirmed)
- **Spendable funds** = treasury − protected operating reserve − accepted escrow. **Escrow** = sum of accepted line quantity × locked unit price, plus any fixed fees. A partial receipt advances the order. Pay once when the required lines are complete, with explicit milestones for larger contracts.
- **Closing treasury** = opening treasury + real sales and services + logged external revenue − payouts and other explicit expenditures. Escrow changes available funds while the money stays in the treasury.
- Reward reliable service over distinct periods and by meaningful order volume. Village-to-supplier reputation changes the next quote and eligibility. Village-to-village relationships can affect which trade routes and tenders are available. A player or FTB Team owns the accepted terms, and its authorized carriers can contribute toward the same payout.
- Keep both sides of every purchase in the ledger. A village selling a lot and buying the identical lot back from the same seller must not generate an easy profit. A buyer needs a documented use, conversion, resale to a distinct paying customer, or a verified service. Receipt IDs and shipment reservations prevent duplicate settlement.

A **regional charter buyer** is a proposed source of solo endgame revenue. It receives a visible, capped budget by period and posts purchase agreements for goods it takes out of the local economy. This represents an outside customer rather than money created by a local buy-and-sell loop. Towns also earn from real product sales, repairs, power, refueling or transport services. When a treasury gets low, the board shows unfunded demand and the village prioritizes essentials. A starter grant can open the first trade route. Recurring customer revenue sustains it.

An export agreement should fund multiple lots over several periods and publish its renewal rules. Add a second buyer or route when a village's inventory or treasury relies too heavily on one customer. An oversupplied buyer issues smaller future lots or lets another village's request take priority. The player can choose to redirect capacity, stockpile within depot limits, or run fewer shifts until orders recover.

### Village wealth and national taxation

- Keep village treasury cash, national treasury cash, and village wealth as distinct records. The wealth indicator reflects economic gains after associated costs. Profits add to it and net losses reduce it. Gross trade turnover is excluded. Report wealth at a floor of zero while preserving actual losses and debts in their accounts.
- Collect national tax periodically as a percentage of village wealth. Zero taxable wealth yields zero tax. Set rates in response to village and national needs. The measurement window, treatment of taxable gain versus accumulated wealth, collection interval, rate limits, and transfer rules remain open. Count each eligible gain once.
- Happiness combines economic and living conditions. Happiness pulls stability gradually toward better or worse conditions, with faster change farther from neutral. Raising ordinary taxes can lower happiness. A tax-related decline in stability requires contextually excessive taxation. Count that effect once. Military stationing or occupation can affect happiness and stability independently depending on local conditions and relations with the national government. The thresholds and rates remain tunable.

[Approved village finance and taxation rules](../../VILLAGE_AI_SIMULATION_ECONOMY.md#village-budget-versus-village-wealth--clarified-foundational-distinction) · [Approved military presence rule](../../VILLAGE_AI_SIMULATION_ECONOMY.md#military-presence-affects-both-happiness-and-stability--confirmed)

## Trade leagues and rival blocs

Nearby villages can form a **trade league** when their routes are practical and they have a reason to cooperate. A steel town, a farm village, and a port can share freight schedules and buy power together. Each village keeps its own treasury, stock, facilities, and relationships with players. Joint contracts use contributions that members explicitly commit to that contract. A village can benefit from league membership and still trade with independent neighbors.

### Formation, stress, and splits

- A village can join a nation only across a shared land border. A completed default road gets the strongest preference among eligible neighbors, followed by whether their verified surplus covers each other's shortages and whether their trade is reliable. The pilot weights are 50% starter road, 35% shortage fit, and 15% reliability, with five qualifying trade days.
- Evaluate existing neighbor routes by travel time, available connections, and actual freight reliability. Build candidate groups from that route network. Three towns along a working railway may have more reason to cooperate than two villages separated by a mountain.
- Require several periods of reliable trade and a credible benefit for every joining village. Measure **membership benefit** as freight savings plus net revenue from additional sales and services, minus dues, relief contributions, and costs from missed commitments. Track essential supplies separately as **fulfilled essentials ÷ essentials due**. A period with no essentials due gives no coverage score.
- Let hard times change behavior first. Widespread shortages can make villages band together for cheaper freight or emergency supply. Repeated missed shipments, unfair allocations, disputed tolls, broken deals, and unpaid shared costs can instead strain the alliance. Track those causes so the player can see why a member is unhappy and which contract could help.
- A stressed village can request relief, emergency food contracts, or a redistribution of shared costs. Secession is a last resort. The pilot economic vote can use a sustained essential-supply crisis, exhausted reserves, and failed relief as preconditions. Its provisional trigger is less than 60% of essential food or life-support demand met for eight consecutive periods after relief begins, with less than one period of usable reserve and no credible funded resupply. The pilot calls for a vote and further confirmation, and cancels the attempt if essentials recover. An outright refusal to host a national garrison is an insurrection, with negotiation or military action dependent on stability and relations. [Approved garrison and insurrection rules](../../VILLAGE_AI_SIMULATION_ECONOMY.md#garrison-refusal-and-insurrection)
- Give confirmed secession a cooldown before any rejoin or second split. If a departing village was the only practical connection between groups, the league can split into two trade blocs. Recalculate ownership for affected districts and preserve their population, property, and active commitments.
- Membership changes update future offers, freight access, and preferences. Accepted orders keep their prices, cargo custody, and escrow. If a route closes, pause that shipment for an agreed reroute or return. Existing contributions stay attached to the orders they funded. Independent villages can still post local jobs and rebuild a trading relationship over time.

National aid weighs the severity and breadth of local hardship, village and national stability, and competing national needs. A village that can handle a local outbreak may manage it locally. When a nation intervenes, it can provide supplies, funding, personnel, or healthcare facilities and fund the most urgent effective measures first. Food aid can arrive all at once or in stages as supply allows. Every response requires available resources, financing, and delivery. A government can seek ordinary credit when repayment and lender terms are feasible. In an extreme emergency with no viable alternative, it may seek a loan despite poor feasibility and accept higher rates or collateral demands. A sovereign lender demands repayment first, with enforcement subject to territorial jurisdiction and the separate company rules. [Approved emergency borrowing rules](../../VILLAGE_AI_SIMULATION_ECONOMY.md#urgent-intervention-triage-and-general-sovereign-borrowing-rule--confirmed)

Recruitment policy sets the eligible share and the pace of mobilization. Track eligibility, active service, and the number of troops the economy can supply separately. Loss of civilian output begins when actual mobilization leaves jobs vacant. Available unemployed workers fill those vacancies gradually. Mass mobilization recruits essential workers last. Demobilization follows a policy change and returns essential workers first. Simulate most warfare at the army and national level. Player skirmishes can influence battles and negotiations while territorial outcomes still depend on military and logistical conditions. [Approved recruitment and productivity](../../VILLAGE_AI_SIMULATION_ECONOMY.md#military-recruitment-and-economic-productivity)

### Trade priority and favoritism

Protect local safety stock and honor accepted orders first. Divide the remaining supply into published allocations for members, preferred treaty partners, and the open market. League members get first call on their allocation and can negotiate longer delivery windows or lower shared handling costs. Partners get their own contracted share. Unclaimed allocations can become available to any eligible buyer after a cutoff.

Within each allocation, prioritize essential shortages, then funded production needs, then discretionary stockpiles. Use a simple urgency measure such as **essentials due before the next feasible delivery minus usable stock and firm inbound supply**, expressed as a fraction of essentials due. Rotate equally urgent buyers across periods so a large member cannot take every shared shipment. Set a per-member cap where appropriate. Favoritism can change who sees a new offer first and how much freight costs, while independent towns retain a market and can build their own alliances.

An example after subtracting protected stock and earlier commitments is **12,000 steel** available for new orders. A league could offer **6,000** to members, **3,600** to preferred partners, and **2,400** to the open market. If members only claim 4,000 by the cutoff, the remaining 2,000 can go to the next eligible buyers. These shares are tuning examples. Reduce the allocations proportionally when a promised production batch fails and adjust only future offers. Visible shortages, favored allocations, fees, and treaty status explain why two villages see different contracts.

### League-to-league contracts

Leagues can buy and sell as blocs through a designated depot. One side aggregates funded requests from several buyers. The other combines verified surplus from several producers. For each item, the pooled lot is the least of aggregate unmet demand, confirmed unreserved seller stock, reserved receiving space, booked transport, and quantity affordable from committed funds. Keep the original village and payer on each line so one receipt pays each supplier once and one member's shortfall never quietly draws from another treasury. Goods can be combined on one train or ship while the receiving depot credits the separate orders.

League relationships can also change over time. Reliable trade can earn a bloc a standing allocation or a shared rate for shipping and power. A rival bloc might face higher tolls, fewer offers, or a pause on new trade when a dispute escalates. Any restrictions should name the affected route or goods. Existing orders follow their signed terms, and neutral depots or independent suppliers can still offer alternate routes and emergency supply.

For example, a river league supplies steel and grain to a coastal league that produces pumps and fuel. Both sides pay against their own delivery receipts. The port can also post a paid freight job so you can run the train or airship even if you made none of the goods. A failed grain shipment can generate emergency orders in the coastal bloc. A dispute over tolls can create a new buyer for an alternate port, or a repair and freight tender to reopen the original route. That creates a reason to serve several villages and gives contracts that mix manufacturing, transport, and regional power.

Store only the route graph, recent reliability and dispute summaries, membership, and live commitments. Evaluate affected routes after a significant trade event or on a staggered economy deadline. Alliance decisions need no village chunks loaded. World changes still go through the existing approved placement system.

## Borders and territorial resources

The settlement simulation owns the borders. A village records its connected district cells before joining a nation. Draw a national boundary only after at least two districts unite. Expand gradually into adjacent land as funding and geography allow, stopping at neighboring borders or coastlines. A nation's territory is the union of its members' district cells. Freight may cross land and territorial waters where access, permissions, and treaties allow. Border calculations use cached information and do not generate chunks.

Villages automatically know the types and quantities of underground deposits within their territory. Use those quantities to estimate extraction potential without requiring players to prospect for the village. Machinery, labor, power, technology, inputs, and logistics limit realized output. Manufacturers can import raw materials where trade is practical. National simulation leaves physical veins intact. Biome and verified exports can support specialized farming, mining, industry, distribution, port, and shipyard roles. [Approved resource knowledge and yield](../../VILLAGE_AI_SIMULATION_ECONOMY.md#territorial-resource-knowledge-and-yield--confirmed-2026-11-14)

The MapFrontiers 2.6.0p2 adapter publishes named and colored boundaries in JourneyMap. An isolated native client verified automatic publication and the public nation popup. Full-pack sync from a naturally formed nation and multi-client restart validation remain open. Managed frontier IDs let updates replace previous shapes while preserving manually drawn frontiers. Territorial calculations use the authoritative cells, including holes and disconnected areas. The pilot uses 128-block cells. Chunk-resolution jurisdiction is a design target. Existing claim systems govern block ownership and protection. [Installed MapFrontiers release](https://modrinth.com/mod/mapfrontiers/version/1.21-2.6.0p2-neoforge) · [MapFrontiers public API](https://github.com/alejandrocoria/MapFrontiers-API)

Show three quantities on each nation's resource ledger:

| Quantity | Basis | What it can drive |
| --- | --- | --- |
| **Estimated deposits** | Eligible unsurveyed area × deposit frequency × average deposit size, using each dimension's biome, depth, and generation rules | Prospecting, survey, or import planning |
| **Confirmed remaining reserves** | Saved survey counts or finite deposit records within the border, less verified extraction, with ore grade and units preserved | Mine construction, extraction capacity, and depletion planning |
| **Available production and stock** | Verified operating throughput and inventory, limited by equipment, power, processing yield, and haulage | Actual funded supply and export contracts |

Use the pack's geology catalog and survey records. Exclude surveyed ground from the estimate so the same deposit appears once. Count finite oil in its native volume unit. For a vein crossing a border, allocate only portions with known locations. Keep any unresolved remainder in a single shared deposit record until surveyed. A border change transfers jurisdiction over that ground, while old inventory, depleted amounts, and shipment commitments keep their existing records. The map can show national totals and confidence without revealing exact locations of undiscovered deposits. Estimate broad regions from cached generation data, update confirmed counts as surveys finish, and keep all resource accounting off the chunk-load path.

For example, if a nation has 100 eligible unsurveyed cells with an average of 0.1 deposits per cell and 2,000 ore blocks per deposit, report **20,000 estimated ore blocks** there. If surveyed territory records 12,000 ore blocks with 3,000 already extracted, report **9,000 confirmed remaining** in that separate area. A full depot or a power outage can still bring exports to zero. These are example values for the calculation.

## Maintenance and power

- **Parts due** = max(0, floor(verified operating time / service interval) − completed service cycles) × parts per cycle. Start sourcing spares before the service is due. Parts in stock and service completed have separate receipts. Running a second shift creates more eligible runtime and more upkeep. Idle equipment does not accrue operating wear.
- **Sustained power** is verified at the customer boundary. Every contiguous sample must meet the required received rate for the full window. For regional service, multiple registered loads can be required to meet their minimums during that same window.
- **Bulk energy** = sum of credited net received energy intervals. An outage interrupts a sustained window. It leaves already confirmed bulk delivery in the ledger. Count energy at the customer boundary and reject replays and repeated charging/discharging of the same buffer.
- **Generation required** = target delivered rate / measured end-to-end efficiency, with headroom for peak loads and outages. Set real rate targets only after measuring the pack's generators, converter losses and transmission. Local TFMG loads and long-distance ElectroEnergetics transmission serve one grid.

### Atmospheric Scoop procurement pilot

- When a commissioned Atmospheric Scoop completes 32 extraction cycles, post only the missing parts from its existing service bill of four `tfmg:steel_mechanism` and one `createmechanisms:advanced_precision_mechanism` through a bound station depot.
- Use the scoop's native output and maintenance transitions, an installation identity, and a persistent service-cycle ID to open each demand once across movement, reload, and retries.
- Reserve existing station treasury and depot space for each signed lot, credit suppliers only after the matching physical hand-in, and mark service complete only when the exact paid parts are debited and applied to the original scoop.
- Price each part from its approved upstream yields, machine operations, energy, and haulage, credit condensate revenue only after a buyer actually receives it, and keep a bounded service window even when the fleet grows.
- At the current machine settings, 32 uninterrupted completed cycles yield 32,000 mB condensate and consume 104,857,600 FE and 51,200 mB coolant before the service parts, which provides a measurable basis for testing the economics.

This is a proposed order source. The native scoop tracks wear and accepts service parts, while automatic procurement, station treasury funding from exports, and restart-safe transfer of parts to the scoop still need an adapter.

## Seasons and supply planning

Use the installed Serene Seasons API as the Overworld calendar. Read its season state once per relevant dimension during scheduled economy work and reuse that snapshot for village and nation calculations. Choose temperate or tropical conditions from each district's recorded biome. Keep unconfigured dimensions on their existing local production rules. The live season configuration currently lists only the Overworld.

- Seasonal weather, growing conditions, crop calendars, and verified harvest throughput should affect projections for local food and raw inputs. Preserve the difference between an expected bad harvest and a verified inventory shortfall.
- Use projections to plan stockpiles before winter or a dry season and to post funded future orders for compatible crops, food, fuel, building materials, and repairs. Cold-weather heating demand requires a commissioned load and real metering. Use existing purchase and physical delivery receipts for every stock and treasury change.
- Give villages with different biomes a reason to trade in the same season. Use ports and warehouses to rotate supplies between reliable suppliers. A nation summarizes each district's local exposures and relief needs, keeping depot stock and committed cargo attached to their actual owners.
- Keep signed prices, cargo assignments and escrow through a season change. Revise new quotes and procurement forecasts. Drought, storms, and shortages can lead to repair or relief contracts only through verified events and the existing funding rules.
- Keep season work off chunk load. If progression qualifies a building upgrade, submit a prepared verified footprint to the existing placement queue. Tune industrial demand and price adjustments from observed pack yields, storage throughput, energy use and trade behavior before setting production coefficients.

## Worked example

A foundry needs **2,000 steel per period** for its existing business. With **1,000 safety stock** and a **three-period horizon**, it targets **7,000**. It has **2,500 on hand**, **1,500 in transit**, and **500 accepted but waiting to ship**. Its remaining shortage is **2,500**. If space permits and the budget covers **2,200**, a **500-unit lot size** yields a **2,000-steel offer**. Accepting that offer reserves another 2,000, leaving 500 uncovered at that moment.

The town then commissions a machine line that adds **1,200 steel use per period**. Its target rises from **7,000 to 10,600**. The line also creates demand for coolant, service parts and power, and sellable output for its customers. Suppose a customer wants 240 pumps. The line makes four per batch, the town has 96 steel for production at two per batch, machine slots for 36 batches, power for 32, and space for 40 batches of output. It schedules **32 batches for 128 pumps**. Power is the bottleneck this period. The unfilled 112 stay on the customer's order and can justify another shift or a grid upgrade.

At endgame, an illustrative program of **33,600 direct steel per service day** reaches **1,008,000 in 30 service days**. Splitting it into **19,200/day consumed on Earth** and **14,400/day exported** gives Earth a continuing industrial role. Separate, illustrative maintenance programs of **1,920 Steel Mechanisms** and **320 Nitro Energy Mechanisms per day** add **57,600** and **9,600** finished parts over the same span. These totals exclude embedded steel and do not establish pack rates. Backsolve the raw ores, power, factory count, pallet sizes and transport schedules from verified production yields before publishing live quotas.

One practical division of labor is Earth supplying food, bulk steel and machinery, the Moon shipping processed Desh, Mars supplying pressure equipment and processed Ostrum, and Venus supplying heat-resistant components and processed Calorite. Each destination should have both import orders and saleable output. A funded external buyer keeps demand open after the Warp Drive. A high-capacity factory then earns its keep through concurrent customer schedules and ongoing replacement demand.

## World and performance boundary

A village's ledger should change on verified deliveries, operating observations, or a staggered due date. Use elapsed time for bounded household accounting and forecasts. Keep physical stock, power, construction and machine output tied to world evidence. When the economy qualifies a real upgrade, it submits the prepared footprint before the visit. The existing chunk hook reads that decision and queues placement separately. An ordinary chunk load does no market work.

The scalability target is very low CPU use on worlds around ten million chunks. Unloaded settlements use aggregate simulation while the server runs, even with no players online. Economic time stops when the server stops. Player-controlled nations are to receive some protection while players are offline. Its scope, activation, duration, and safeguards remain open. [Approved offline protection direction](../../VILLAGE_AI_SIMULATION_ECONOMY.md#offline-player-nation-protection--principle-confirmed-details-deferred-2026-11-14)

The first live implementation can prove the whole loop with one workshop village, one real depot, and one recurring demand whose use can be demonstrated. Next add a second trading partner and a facility that turns a project into standing demand. Keep later figures provisional until actual inventory throughput, funding, generation and fleet capacity are measured.
