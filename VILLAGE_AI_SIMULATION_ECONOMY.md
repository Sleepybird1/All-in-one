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

### Approved principles with details explicitly deferred

- **Population consumption and growth numerical balancing:** the four-food-items-per-resident-per-Minecraft-day baseline and other numeric consumption/growth parameters are deferred for later balancing; do not treat them as finalized.
- **Offline player-nation protection:** desirable to prevent catastrophic losses during vacations, but rules and anti-exploit balancing are deferred.
- **Territorial resource awareness:** villages know which underground deposits exist within their territory without player prospecting, but extraction still requires actual economic capacity. The user explicitly requested revisiting this design for further thought.
- **Village Dashboard detailed UI:** tabs, statistics, customization mechanisms, and presentation are not yet decided.
- **Exact multipliers, formulas, labor allocation, asset valuation, and thresholds:** remain provisional unless separately approved.

### Review discipline

Only label a decision **user-approved** after explicit confirmation. Keep suggestions, examples, implementation claims, and deferred questions separate. Add subsequent confirmed decisions here as the review continues; do not silently convert proposals into rules.
