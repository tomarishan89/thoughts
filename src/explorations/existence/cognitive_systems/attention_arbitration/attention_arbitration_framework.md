# The Mechanics of Attention Arbitration: Channel Competition, Softmax Routing, and Sensory Preemption

**Author:** Ishan Tomar  
**Domain:** Tier 3 Cognitive Mechanics — Sub-Domain: Attention Arbitration  
**Companion Documents:** [`ATTENTION_MASTER_FRAMEWORK.md`](ATTENTION_MASTER_FRAMEWORK.md), [`issues_log.md`](issues_log.md), [`manuscript_audit.md`](manuscript_audit.md)  

---

## 1. Introduction & The Limited Attention Budget

In naive introspection, the conscious mind appears capable of unbounded contemplation. In physical reality, neural computation is constrained by thermodynamic exergy availability and finite synaptic channel capacity.

The brain's total informational metabolic allocation $\dot{\mathcal{E}}_{\text{info}}$ must support all concurrent operations:
1. **Sensory Processing:** Continuous monitoring of the external shared space $\Omega_{\mathbb{R}}^{\text{shared}}$.
2. **Somatic Proprioception:** Maintaining homeostatic boundary integrity.
3. **Internal Generative Modeling:** Running counterfactual simulations in $\Omega_{\mathfrak{Im}}$.
4. **Meta-Cognitive Evaluation:** Running the Third Eye operator $\mathcal{O}_{\text{TE}}$.

---

## 2. Dynamic Priority Arbitration

Because concurrent execution of all channels at full fidelity would violate the metabolic bound $\dot{\mathcal{E}}_{\text{info}} \le \dot{\mathcal{E}}_{\text{metabolic}} - \dot{\mathcal{E}}_{\text{somatic}}$, the brain employs a **thalamo-cortical arbitration manifold**.

### 2.1 Softmax Routing Kinetics

Each active informational stream $\mathbf{J}_k$ carries an intrinsic charge affinity $q_k$. Routing coefficients $a_k(\tau) \in [0, 1]$ evolve according to coupled competitive kinetics:

$$\dot{a}_k = \gamma \left( \frac{\exp\left(\beta q_k \|\mathbf{J}_k\|\right)}{\sum_m \exp\left(\beta q_m \|\mathbf{J}_m\|\right)} - a_k \right)$$

where $\gamma$ is the synaptic switching rate ( $\sim 10 - 50 \, \mathrm{s}^{-1}$ ), and $\beta$ is the arbitral gain.

---

## 3. The Non-Sovereignty of the Third Eye: The Bee-Sting Lemma

A recurring question in philosophy of mind is whether conscious self-evaluation is an autonomous sovereign process.

Consider an agent engaged in deep meta-cognitive self-evaluation or philosophical contemplation:

$$\mathbf{J}_{\text{TE}} \gg \mathbf{0}, \quad a_{\text{TE}} \approx 1$$

Now introduce an abrupt nociceptive shock to the physical boundary ( e.g., a bee sting on the arm ):

1. **Damage Flux Injection:** The nociceptive nerve fibers inject an abrupt, high-amplitude spike: $\|\mathbf{J}_{\text{pain}}\| \to \infty$.
2. **Charge Affinity Dominance:** Because biological survival is lexicographically prior to philosophical reflection, the somatic nociceptive charge affinity is maximal: $q_{\text{pain}} \gg q_{\text{TE}}$.
3. **Preemption Collapse:** Within milliseconds ( $\tau \sim 20 - 50 \, \mathrm{ms}$ ), the routing coefficient $a_{\text{pain}} \to 1$ while $a_{\text{TE}} \to 0$.

$$\boxed{\text{Result: Instantaneous dissolution of the meta-cognitive simulation loop.}}$$

This proves that the Third Eye is not a transcendent detached observer; it is an energetically vulnerable, subordinate sub-engine within the biological host.

---

## 4. Erasure Dissipation and Interruption Friction

When a complex imaginary simulation loop is preempted mid-stride, the incomplete state tensors cannot be cleanly integrated into the memory ledger $\mathcal{F}_{\text{ledger}}$. They must be actively cleared to allocate register space to the incoming threat.

By Landauer's principle, clearing these working memory buffers dissipates heat:

$$\Delta \mathcal{E}_{\text{flush}} \ge k_B T \ln 2 \cdot \mathcal{H}_{\text{active\_buffer}}$$

This dissipation manifests clinically as attentional switching costs, temporary cognitive disorientation, and executive fatigue following frequent sensory interruptions.
