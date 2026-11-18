MOBILE COMPUTING ASSIGNMENT 1 (CO1) – CODE AND OUTPUTS

Run on Windows:
1. Install Python 3.10+
2. Open Command Prompt in this folder.
3. Run: py -m pip install -r requirements.txt
4. Run: py run_all.py

run_all.py generates CSV datasets in data/ and PNG charts in outputs/.
Inputs follow the uploaded assignment: 12 km² township, 336 duplex channels,
0.5 km reference radius, 0.025 Erlang/user, 2% blocking target, 12 dB SIR
target, propagation exponents 2.5/3.5/4, and 25,000-person stadium event
at 0.05 Erlang/person. Random seed: 20261102.

LIMITATIONS:
This is an educational analytical/Monte Carlo prototype, not a commercial
radio-planning simulator. The Monte Carlo model uses a circular approximation
to a hexagonal serving cell and six first-tier interferers on a reuse-distance
ring. Sectorisation uses a simplified directional attenuation assumption.
The hierarchical result is an illustrative sectorised/microcell comparison;
a full interference-aware dynamic channel allocator is not implemented.
Measured antenna patterns, exact hexagon geometry, handover queues, backhaul,
drive-test propagation and real deployment quotations are outside this model.

Keep theoretical analytical SIR values separate from Monte Carlo measurements.
CSV and PNG outputs are simulated/modelled results, not field measurements.
Review the code and be prepared to explain the assumptions before submission.
