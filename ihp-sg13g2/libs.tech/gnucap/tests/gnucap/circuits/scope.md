## Multi-device Verilog-AMS analog and logic circuit test benches



> **Task 3:** "Implement multi-device Verilog-AMS analog and logic circuit test benches"
>
> **Milestones**:
>
> ​	a. Define scope of test benches based on already existing open-source test benches
>
> ​	b. Implement and adapt existing test cases using Verilog-AMS best practices for modularity and reusability compatible with Gnucap 
>
> ​	c. Port all test cases to SPICE netlists compatible with Ngspice
>
> ​	d. Cross-validate simulations between Gnucap and Ngspice over the full multi-device testbench



## Milestone a

> Define scope of test benches based on already existing open-source test benches

**What should be the purpose of the testbench?**

1. **Test functionality:**
   - Cover simulator features analog and mixed-signal simulation, analysis type, including statistical analysis
   - Cover real word circuit-design tasks such as biasing, amplification, filtering, feedback stability, oscillation, switching, and sampling with measurable acceptance criteria
   - Test hierarchal designs composing increasingly complex circuits from different submodules
2. **Test robustness:**
   - Assess the ability to solve difficult test reliably 
   - Stress test the simulator with dedicated hard test circuits
3. **Test performance**:
   - Provide salable benchmark circuits
   - Measure runtime, memory use, and scaling with circuit size and complexity



**What should be the scope of the test bench**?

- Provide of the order of $10^2$ test circuits across functionality, robustness, and performance 
- A single circuit may support several distinct test cases



**Deliverable**: 

An annotated list of proposed test circuit cases. The list should document what it tests, purpose, source and proposed acceptance criteria.  



Do NOT reinvent the well. Literature review. Talk to experienced circuit designers. 



## Milestone c and d

For cross-simulator validation, automatically translate Verilog-A testbenches into netlists for ngspice and VACASK.

Cross-validate by visually comparing outputs.  

Regression testing we get for free by saving the simulation outputs and doing a bitwise comparison. 

**Deliverable**:

Test outputs for all circuits and simulators. 







Known difficulties in circuit simulations

| Difficulty                               | What happens                                                 | Useful test circuits                                         |
| ---------------------------------------- | ------------------------------------------------------------ | ------------------------------------------------------------ |
| **Nonlinear convergence**                | Newton iterations diverge, oscillate, or stall because device behavior is strongly nonlinear or the initial guess is poor | Schmitt trigger, diode rectifier                             |
| **Multiple operating points**            | The solver finds a valid equilibrium, but which one depends on initialization | Latch, bistable circuit                                      |
| **Stiff dynamics**                       | Very fast and very slow behavior coexist, making time integration expensive | Ring modulator, networks with widely separated time constants |
| **Switching and rapid transitions**      | The simulator must resolve sharp changes without missing events or repeatedly rejecting timesteps | Rectifier, switched-capacitor circuit                        |
| **Ill-conditioned or singular matrices** | Very different numerical scales amplify errors; floating nodes or conflicting constraints can prevent a solution | Extreme impedance networks; separate invalid-circuit diagnostic tests |
| **Accumulated numerical error**          | Integration introduces phase drift, artificial damping, or inaccurate settling over long runs | Oscillator, lightly damped RLC circuit                       |
| **Computational scale**                  | Device evaluations and sparse matrix solutions consume increasing runtime and memory | Large transistor circuits, scalable ladders                  |











 















