# Science, architecture and guarantees

## 1. The executable object is a scoped research claim

A theory does not become operational merely because its name appears on a screen.
HepatoGenesis associates a research question with explicit state variables,
allowed inputs, units, equations, observations, a time horizon and a falsifying
condition. A computed result is then attached to its model and protocol. If a
source changes, dependent claims return to review rather than retaining authority
from a former high score.

The implementation connects six components, but it does not claim a solved
multiscale simulator of the entire organ. The history model, finite game and
transport chain are separate mathematical systems. Their interface is an explicit
research contract, not an invented conversion between dimensionless memory,
concentration, energy and moral value.

## 2. Architecture

`common.py` supplies typed finite validation, canonical JSON, atomic files and
explicit CSV schemas. `dynamics.py` supplies the book's history equations and two
alternative models. `experiments.py` supplies split-aware evaluation, observation
design, finite sensitivity and an information/decoder experiment. `finite.py`
implements belief policies and task-aware partitions. `physics.py` implements
physical ledgers. `evidence.py` manages the dependency graph. `capsule.py` connects
all outputs and writes a verifiable bundle. `cli.py` and `server.py` expose these
same computations without maintaining a second, inconsistent simulation engine.

The offline report is generated from actual result objects. The live console
calls the Python API. Neither interface invents numbers in JavaScript. The
JavaScript draws the returned trajectories and exposes the result JSON.

## 3. History dynamics

The full state is x=(C,M,R), where C is normalized relative capacity, M is structural
burden and R is normalized reserve. Time and all model quantities are dimensionless.
These are not ALT, fibrosis stage, a clinical score, physical entropy or conscious
experience. The equations are:

```
dC/dt = a*R*(1-C)/(1+M) - b*(U+q*M)*C
dM/dt = c*U*C + d*(1-C) - k*e*R*M
dR/dt = f*S*(1-R) - g*(1-C)*R - h*U*R
```

U is a prescribed nonnegative pulse, S a nonnegative support input, and k a
nonnegative multiplier on one model clearance term. All parameters are nonnegative.
The permitted domain is 0<=C<=1, M>=0 and 0<=R<=1. At each domain boundary the
vector field points inward or tangentially. With piecewise bounded inputs and a
finite horizon, the M growth rate is bounded above by c*U+d. The denominator does
not reach zero. These observations establish model consistency under the stated
conditions; they do not establish the biological validity of the equations.

A segmented fixed-step fourth-order Runge-Kutta implementation places pulse and
repair transitions exactly on integration boundaries. Controls are held constant
within each segment, with half-open interval semantics. No post-hoc state clipping
is used. A domain violation causes failure. The true final time is emitted even
when the horizon is smaller than the requested step. Linear interpolation is
permitted inside the simulated interval and extrapolation is rejected.

The three model variants are deliberately explicit. Dynamic history evolves M.
Frozen history retains initial M but sets its derivative to zero. Erased history
sets M to zero and removes its effects. Frozen and erased variants are scientific
controls, not hidden approximations of the full implementation. All outputs name
the actual variant and preserve its assumptions.

The accumulated quantity integral((k-1)*e*R*M dt) is tracked as a fourth numerical
state. It differs from integral(k-1 dt). In the frozen countermodel it is only a diagnostic rate integral, not a change in M.
Identical multiplier-time does not imply
identical material clearance, dose, cost or outcome. Signed values are retained
when the multiplier is less than one. The sampled C floor and terminal target are
arbitrary teaching thresholds and never clinical reference values.

## 4. Model discrimination rather than self-affirmation

The public fixture contains eight complete trajectories: three training, two
development and three audit groups. Each has 12 C/R observations. Model parameter
q is fitted on training groups, with all other parameters fixed by the protocol.
The mean of each trajectory's squared C/R error is computed before averaging
across groups. No time point is treated as an independent person or experimental
replicate. Development error plus a declared retained-coordinate penalty chooses
one model; frozen M counts as a retained coordinate even though it does not evolve.
This is a representation cost, not a count of dynamic degrees of freedom. The selection object is hashed before audit values are computed.

The whole protocol is public and its generating model is named. This prevents
misrepresentation as a secret holdout or externally independent test. The positive
fixture favors dynamic history by construction. The negative control sets initial
M=0 and c=d=0 so M remains zero; all model observations then coincide and the
penalty selects the simpler description. Both outcomes are part of the release.
If audit observations are changed, fitted parameters and the frozen selection
hash must remain unchanged. A regression test checks that property.

No parameter posterior, p-value, clinical effect or generalization certificate is
reported. The finite sensitivity run samples parameters independently within
20 percent of defaults; it is a stress exercise, not a probability distribution
learned from patients. The code caps sample counts and records zero-sample runs
without retaining obsolete CSV rows.

## 5. Observation design

A finite list of times and C, R or C+R channels is evaluated. For each candidate,
the three models produce predictions. Each pair's squared difference is scaled by
a common assumed noise variance. The minimum pairwise separation is divided by
the number of channels, a declared proxy for cost. The selected candidate maximizes
this quantity. This is a transparent, finite design rule, not a complete expected
information-gain optimizer. It ignores unknown parameter distributions, correlated
noise, laboratory feasibility and patient burden unless a later extension models
them explicitly. Selection does not establish causality.

## 6. Constraint-aware abstraction

Observation equivalence alone may erase a dangerous hidden distinction. The
finite partition routine begins with observations and, in task-aware mode, safe
and goal flags. It repeatedly refines by enabled actions, action costs and the set
of successor blocks. Refinement stops at a stable partition after finitely many
splits. For the supplied finite transition system this preserves the declared
bisimulation signature. It is not a universal quotient of continuous histories.

The two-state abstraction fixture gives A and B the same output and self-loop.
An output-only partition merges them. Only A is safe and a goal, so the task-aware
partition separates them. This is an explicit counterexample to inferring safe
compression from matching outputs alone. Approximate epsilon-closeness is not
claimed to be a transitive equivalence relation.

## 7. Partial observation and the policy quantifier

At time zero, an initial set of possible states is split by the observation the
controller actually receives. For each resulting belief, one action must be
enabled in every possible state. Every nondeterministic successor is retained;
future beliefs are formed by the next observation. A recursive dynamic program
asks whether some action has successful continuations for every such belief.
At terminal time every possible state must be a goal; at every step all possible
states must be safe. The answer is exact for the finite horizon and declared model.

The quantifiers are `exists one observation-based policy, for all admitted hidden
states and disturbances`. They are not `for each state, exists a different action
known only to an oracle`. The default fixture makes this difference concrete.
Each of A and B can individually reach G, but the correct actions conflict while
the observations coincide. Adding an observation that distinguishes A and B
restores a feasible policy in this model.

Costs do not reveal hidden states. Each step charges the maximum state-dependent
action cost within the current belief. This is conservative relative to a budget
that tracked exact hidden path expenditure. The solver's guarantee is about this
explicit budget contract; it is not claimed to solve every partially observed
cost problem. Limits are 32 states, eight actions, horizon 12, integer budget 50
and 50,000 memoized belief nodes. No continuous-space viability kernel is computed.

## 8. Physical accounting

The transport example divides a total volume into cells with upwind advection,
neighbor exchange and first-order consumption. Flux between neighboring cells is
shared with opposite signs. Summing the update equations therefore cancels
internal fluxes. The recorded residual is final-initial-input+output+reacted.
Concentration is mmol/L, flow is L/h, reaction rate is 1/h and amount is mmol.
The step is reduced to maintain a positivity restriction. This is a discrete
conservation check, not proof of accurate anatomical transport.

The one-cell and 24-cell experiments share total volume, inlet, flow and reaction
rate. Their different outlet concentrations demonstrate that averaging changes
transport behavior. They do not simulate measured portal anatomy or a human liver.
A separate isothermal uncoupled reaction computes deltaG=deltaG0+R*T*ln(Q), using
dimensionless activities, and entropy production=-v*deltaG/T. An uphill forward
flux fails that uncoupled contract. Coupled reactions require joint accounting;
this simple flag cannot rule out properly coupled biological work.

The energy ledger checks input-output-work-heat-storage rate in watts. It does
not infer life, intelligence or value from balance. New physical-field proposals
must name degrees of freedom, units, evolution, coupling, observable, null model,
discriminating prediction and failure condition. Passing that form means only
that a proposal is sufficiently specified for discussion, never that it is true.

## 9. Research lineage and DIKWP

Data nodes preserve declared source information. Information nodes preserve
computed relationships and observations. Knowledge nodes identify explicit model
contracts. Wisdom nodes record consequence-sensitive scope and admissibility
checks. Purpose nodes identify an experimental question or intended use. These
are connected types in a dependency graph, not a mandatory five-stage ranking of
truth or a claim that the organ has human intentions.

Nodes are immutable versions. Every dependency must already exist, which prevents
forward cycles. Invalidation propagates to all descendants and marks them for
review. Scope mismatches in species, data kind or units also prevent simple
promotion. A reviewed name is a local assertion, not authenticated civil identity.
The conservative exact scope rule can over-block legitimate cross-scale work;
such transfer requires an explicit reviewed new contract instead of silent
conversion. The current system does not automate literature entailment or infer
that identical scope proves a claim.

SQLite transactions serialize append operations. Events form a SHA-256 hash
chain. Retaining an external head detects modification or truncation relative
to that head. An administrator who can rewrite the database, software and every
copy of the head remains outside the integrity guarantee. A checksum has no
power to make false data true.
