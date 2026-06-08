Status: #library
Tags: #framework #AI-infra #power

---

# AI Energy Thesis

The bottleneck in AI infrastructure has shifted from chips to power. Grid-upgrade timelines (multi-year to decadal) are structurally incompatible with hyperscaler buildout timelines (12–24 months). This forces hyperscalers to become direct energy investors — owning or contracting generation rather than buying from utilities. Companies that can provide on-site, grid-independent power (fuel cells, nuclear, gas turbines) have durable pricing power because they solve a problem utilities physically cannot solve fast enough.

**What could break the thesis?** A large unhobbling/efficiency gain that sharply reduces the compute, memory, or energy needed to run frontier AI — after all, humans run "general intelligence" on ~20–30 watts. Even then, the likely response is to spend the freed-up resources on *more* AI rather than less, but it would still be a shock. Finding other thesis-breakers requires thinking outside the obvious capex variables.

## Behind-the-meter natural gas lane

The near-term shape of "on-site generation" is overwhelmingly **behind-the-meter (BTM) natural gas**: dozens of US data centers totaling tens of GW are now BTM-powered, with ~18-month deployment timelines vs. the multi-year utility interconnect queue. That time-to-power advantage is the core operational reason hyperscalers bypass the grid rather than wait on it. A representative pattern is a gas pipeline company building and operating a gas-to-power plant directly adjacent to a hyperscaler's data center. Notably, BTM is *less* politically fraught than staying on-grid — when generation is on-site and dedicated, there's no "the data center is taking residents' power" headline. This lane connects to [[permitting-as-binding-constraint]]: BTM solves the grid-queue delay that permitting creates upstream, but adds its own siting / political-consent risk at the data-center parcel itself.

## Nuclear SMR lane

The long-dated end of the on-site stack is **small modular reactor (SMR)** deployment (e.g. hyperscaler offtake deals for ~1 GW each). First power is expected toward the end of the decade, with construction in the back half of the buildout. Unlike BTM gas, SMRs aren't solving the current build cycle — they're solving the 2030+ baseline-power problem (carbon footprint, fuel-price exposure, regulatory durability). The read: hyperscaler willingness to write nine-figure pre-payments to *unbuilt* SMR companies is a strong signal that gas-powered BTM is understood internally as a bridge, not the destination.

---
# References
- [[permitting-as-binding-constraint]]
- [[ai-infra-thesis-kill-switches]]
- [[Wait-for-deal thesis]]
- [Behind-the-Meter AI Projects Surge in U.S. — NAM, 2026](https://nam.org/behind-the-meter-ai-projects-surge-in-u-s-35696/)
- [Gas-to-Power Boom — enkiai.com, 2026](https://enkiai.com/data-center/gas-to-power-boom-ai-drives-2026-on-site-energy-shift/)
