# Eighteen chapter laboratories

An English companion map for A Brief History of the Liver, by Yucong Duan and Zhongdao Wu. Each entry links a selected argument to a working lab. These are conceptual and computational bridges, not a claim that every chapter is fully simulated. Source hashes refer to the supplied final chapter files, which are not redistributed.

## 1. The Quiet Center

Identify the observation boundary before interpreting the organ.

```sh
python -m hepatogenesis information --out chapter_01.json
```

Change a decoder while preserving the measured mutual information. Explain why equal information quantity does not imply equal task performance.

Coverage: conceptual bridge and a runnable teaching exercise; not a simulation of every process in the chapter.

Source chapter SHA-256: `c63873bcf01ee12fd9ac2e5d3e04a64af400f153a19d3b8f633236ec16609723`.

## 2. The Universe Before the Liver

Separate material ancestry from a sufficient explanation of organ formation.

```sh
python -m hepatogenesis physics --out chapter_02.json
```

Construct a first-law ledger. Identify which steps between cosmic matter and an organ are not simulated here.

Coverage: conceptual bridge and a runnable teaching exercise; not a simulation of every process in the chapter.

Source chapter SHA-256: `0b58c7f52be67953fc8447db7540e21e0aca8142dfed3c4d6041cafb2a93cd0d`.

## 3. Water and Carbon

Distinguish reaction feasibility, activity, coupling and sustained organization.

```sh
python -m hepatogenesis physics --out chapter_03.json
```

Reverse the sign of a reaction free-energy difference without reversing its flux. Explain the resulting negative production in the uncoupled audit.

Coverage: conceptual bridge and a runnable teaching exercise; not a simulation of every process in the chapter.

Source chapter SHA-256: `369102da461f5665d8f3c9b805556ac2afb8d088f58426933892bb2d246edfa6`.

## 4. The First Inside and Outside

Study why a boundary and an input-output balance matter.

```sh
python -m hepatogenesis physics --out chapter_04.json
```

Compare stored amount with cumulative inflow and outflow in an open transport chain. Do not label this a simulation of abiogenesis.

Coverage: conceptual bridge and a runnable teaching exercise; not a simulation of every process in the chapter.

Source chapter SHA-256: `42bb368724633f5202e2bceaa0dd8b5d334012e04dc687fdbab23a35d744edff`.

## 5. From Cells to Organs

Treat homology, functional analogy and abstraction as different claims.

```sh
python -m hepatogenesis finite --out chapter_05.json
```

Find states that share an observation but differ in task constraints. Discuss why functional similarity alone does not establish a shared evolutionary origin.

Coverage: conceptual bridge and a runnable teaching exercise; not a simulation of every process in the chapter.

Source chapter SHA-256: `4a3bcc54b6dc1b03e2a9026d3646c6f6c5504af4027827aff1a5caa3b562aabb`.

## 6. How a Body Grows a Liver

Make timing and historical state explicit.

```sh
python -m hepatogenesis compare --out chapter_06.json
```

Compare early and late repair intervals, holding the declared multiplier-time proxy equal. Identify why this is not equal biological dose.

Coverage: conceptual bridge and a runnable teaching exercise; not a simulation of every process in the chapter.

Source chapter SHA-256: `908f93ccca865a0b4b18565ea2339a8646835818e20801ca293ae2e284ad818d`.

## 7. Two Networks of Transport

Resolve geometry without losing the mass ledger.

```sh
python -m hepatogenesis physics --out chapter_07.json
```

Compare a 24-cell chain with a single well-mixed compartment under equal volume, flow and reaction parameters.

Coverage: conceptual bridge and a runnable teaching exercise; not a simulation of every process in the chapter.

Source chapter SHA-256: `47fd6790b0ede070400bc2738f88a993a15b9f4b76ad5f7e423e6ed0ec6ac7ce`.

## 8. The Timing of Hunger and Satiety

Separate current stores from flux and trajectory.

```sh
python -m hepatogenesis simulate --out chapter_08.json
```

Compare identical initial capacity/reserve and different burden. Report all input conditions and the observation horizon.

Coverage: conceptual bridge and a runnable teaching exercise; not a simulation of every process in the chapter.

Source chapter SHA-256: `0afbb0635025e05c9dc54a4176ef0b7e9876d9499984649513dee33651e50a1e`.

## 9. Selection and Transformation of Matter

Distinguish removal from a compartment from material disappearance.

```sh
python -m hepatogenesis physics --out chapter_09.json
```

Account separately for stored, exported and reacted material; verify the residual numerically.

Coverage: conceptual bridge and a runnable teaching exercise; not a simulation of every process in the chapter.

Source chapter SHA-256: `8c6ba382ff2b8ed3a974a6bbb296a3cf690db8c7c1b319a00d04a3c3f537650b`.

## 10. Between Tolerance and Defense

Do not collapse an action objective into response magnitude.

```sh
python -m hepatogenesis finite --out chapter_10.json
```

Use the goal, safe set and enabled actions as separate model fields. Explain why these are task labels, not immune-cell phenotypes.

Coverage: conceptual bridge and a runnable teaching exercise; not a simulation of every process in the chapter.

Source chapter SHA-256: `fefeaa280be4d7458ca9622f9f10887353e0434f0e52b021d5df039d2a316adf`.

## 11. How Disease Acquires a History

Ask whether stored structure changes future behavior.

```sh
python -m hepatogenesis benchmark --out chapter_11.json
```

Test dynamic, frozen and erased-history hypotheses with group-separated train/development/audit trajectories.

Coverage: conceptual bridge and a runnable teaching exercise; not a simulation of every process in the chapter.

Source chapter SHA-256: `2dbf0c02cfc2b631d1a35ca1948768bacf0b4fd9d4eb522066e65c650eb6d493`.

## 12. Regeneration and Aging

Track renewal without declaring the entire system reset.

```sh
python -m hepatogenesis compare --out chapter_12.json
```

Show which state components are reset by the erased-history hypothesis. Identify the difference between an assumption and a biological intervention.

Coverage: conceptual bridge and a runnable teaching exercise; not a simulation of every process in the chapter.

Source chapter SHA-256: `f0961722bb6d5b82773a5e36c91a34e87713e0a73fb4142a7fb0d32f0407dc58`.

## 13. Energy Fields

Keep power, free energy, flux and temperature dimensionally distinct.

```sh
python -m hepatogenesis physics --out chapter_13.json
```

Audit units and reaction direction. Explain why dimensionless reserve R cannot be silently relabeled as joules or ATP.

Coverage: conceptual bridge and a runnable teaching exercise; not a simulation of every process in the chapter.

Source chapter SHA-256: `9c0ce78eea9718357b2285761aafd1513b835c25eafd409cc84281bca3d7adff`.

## 14. Information Fields

Relate distinguishability to an observation/decoder/task contract.

```sh
python -m hepatogenesis information --out chapter_14.json
```

Reproduce the equal-one-bit/different-decoder example. Form a testable hypothesis with a null model and failure condition.

Coverage: conceptual bridge and a runnable teaching exercise; not a simulation of every process in the chapter.

Source chapter SHA-256: `99701d5c3df84ca2ec7365b11a1b95fb712b5e4de2168bafc27e4beaa396a1ed`.

## 15. Between Scales

Make the cost of coarse-graining visible.

```sh
python -m hepatogenesis finite --out chapter_15.json
```

Compute the observation-only and constraint-aware partitions. State the finite model in which preservation holds.

Coverage: conceptual bridge and a runnable teaching exercise; not a simulation of every process in the chapter.

Source chapter SHA-256: `d7e1811d3985846815290f8f76042586731aa1091039100a22fdf8478ced8aad`.

## 16. The Future Liver

Choose informative measurements without claiming a patient twin.

```sh
python -m hepatogenesis design --out chapter_16.json
```

Inspect the finite measurement-design ranking. Change the assumed noise and explain the limits of model separation.

Coverage: conceptual bridge and a runnable teaching exercise; not a simulation of every process in the chapter.

Source chapter SHA-256: `f4b5840f7ad7094f5ff787e78e616598c842384100fb274eb8272c144a3e9ba4`.

## 17. Returning to the Ultimate

Require proposed explanations to risk failure.

```sh
python -m hepatogenesis benchmark --out chapter_17.json
```

Run the negative control. Explain why a simpler model should survive when the history variable remains zero.

Coverage: conceptual bridge and a runnable teaching exercise; not a simulation of every process in the chapter.

Source chapter SHA-256: `48d8c6e11b0649e7799a64f319c9675642316947e7d1acf17384c58a80f37945`.

## 18. An Open Future

Connect history, information and one feasible policy.

```sh
python -m hepatogenesis finite --out chapter_18.json
```

Reproduce the hidden-state policy obstruction and its removal after an added observation. Distinguish exact finite reasoning from sampled continuous diagnostics.

Coverage: conceptual bridge and a runnable teaching exercise; not a simulation of every process in the chapter.

Source chapter SHA-256: `4487c56abdb6d9ea776fea30affcf449cc0a0f782a4fe373efae205ad6946715`.

