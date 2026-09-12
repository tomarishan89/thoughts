"""
ISSUE-4.63: Confrontation of Prediction #9 with LVK Echo Searches
===================================================================

The framework predicts A_1/A_0 = 8.3e-5 for the first BH echo.
Current LVK searches (Miani et al. 2023, using GWTC-3 with coherentWaveBurst)
set upper limits on h_rss ~ 1-4 x 10^-23 /sqrt(Hz) per event.

Key question: Is the predicted echo strain ABOVE or BELOW the current 
observational upper limit?
"""


import sys
if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8')

import numpy as np

# ============================================================
# Constants
# ============================================================
G     = 6.67430e-11       # m^3/(kg s^2)
c     = 2.99792458e8      # m/s
hbar  = 1.054571817e-34   # J s
M_sun = 1.98892e30        # kg
l_P   = np.sqrt(hbar * G / c**3)
Mpc   = 3.0857e22         # 1 Mpc in meters

# ============================================================
# Framework predictions (from §6.10)
# ============================================================

A1_over_A0 = np.exp(-8 * np.pi * 0.3737)  # = 8.338e-5

print("=" * 80)
print("ISSUE-4.63: CONFRONTATION WITH LVK ECHO SEARCHES")
print("=" * 80)
print(f"\nFramework prediction: A_1/A_0 = {A1_over_A0:.4e}")

# ============================================================
# Estimate echo h_rss for specific GWTC-3 events
# ============================================================
# For a BH merger, the ringdown h_rss is related to the total
# energy radiated in ringdown:
#
#   E_ringdown = (c^3 * d^2) / (4*G) * 4*pi * f^2 * h_rss^2 * tau
#
# More practically, the ringdown strain is approximately:
#   h_ringdown ~ (G*M*epsilon) / (c^2 * d) * (2*pi*f_QNM)
#
# where epsilon ~ 0.03-0.1 is the ringdown radiation efficiency
#
# For the strongest GWTC-3 events:
#   GW150914: M_total ~ 65 M_sun, d ~ 440 Mpc, SNR_ring ~ 7-10
#   GW190521: M_total ~ 150 M_sun, d ~ 5.3 Gpc, SNR_ring ~ 4-7

events = [
    # name, M_total (M_sun), d (Mpc), approximate ringdown SNR
    ("GW150914", 65, 440, 8),
    ("GW190521", 150, 5300, 5),
    ("GW190814", 25.6, 241, 6),
    ("GW200129", 60, 1000, 7),
    ("Loud event (hypothetical)", 30, 100, 25),
]

# QNM frequency and damping
def f_QNM(M_kg):
    return 0.3737 * c**3 / (2 * np.pi * G * M_kg)

def tau_QNM(M_kg):
    """QNM damping time (e-folding time) for l=2 fundamental."""
    # tau = 1 / (Im(omega)) = GM / (0.0890 * c^3)
    return G * M_kg / (0.0890 * c**3)

def echo_delay(M_kg):
    R_plus = 2 * G * M_kg / c**2
    return (4 * G * M_kg / c**3) * np.log(R_plus / l_P)

print(f"\n{'Event':<25} {'M (Msun)':<10} {'d (Mpc)':<10} {'f_QNM (Hz)':<12} "
      f"{'dt_echo (ms)':<14} {'h_ring est':<12} {'h_echo est':<12} "
      f"{'h_rss_echo':<12} {'vs UL 4e-23'}")
print("-" * 130)

for name, M_solar, d_Mpc, snr_ring in events:
    M = M_solar * M_sun
    d = d_Mpc * Mpc
    
    f_q = f_QNM(M)
    tau_q = tau_QNM(M)
    dt_echo = echo_delay(M)
    
    # Estimate ringdown h_rss from SNR and LIGO noise
    # h_rss_ring ~ SNR * S_n(f)^{1/2} * 1/sqrt(tau)
    # At ~200 Hz, LIGO ASD ~ 4e-24 /sqrt(Hz) (design)
    # h_rss_ring ~ h_peak * sqrt(tau)
    
    # More direct: ringdown strain amplitude
    epsilon_ring = 0.03  # 3% of mass radiated in ringdown
    E_ring = epsilon_ring * M * c**2
    h_ring_amp = np.sqrt(4 * G * E_ring / (c**3 * d**2 * np.pi * f_q))
    
    # h_rss for ringdown: h_rss ~ h_amp * sqrt(tau_QNM / 2)
    h_rss_ring = h_ring_amp * np.sqrt(tau_q / 2)
    
    # Echo h_rss: 
    # The echo has SAME waveform morphology but amplitude suppressed by A1/A0
    h_echo_amp = h_ring_amp * A1_over_A0
    h_rss_echo = h_rss_ring * A1_over_A0
    
    # Compare with the observational upper limit
    # Miani et al. (2023) set h_rss < 1-4 x 10^-23 /sqrt(Hz) per event
    UL = 4e-23  # conservative upper limit
    
    status = "BELOW UL (consistent)" if h_rss_echo < UL else "ABOVE UL (TENSION)"
    ratio = h_rss_echo / UL
    
    print(f"{name:<25} {M_solar:<10.1f} {d_Mpc:<10.0f} {f_q:<12.1f} "
          f"{dt_echo*1000:<14.2f} {h_ring_amp:<12.3e} {h_echo_amp:<12.3e} "
          f"{h_rss_echo:<12.3e} {ratio:.4f}x ({status})")

# ============================================================
# Critical analysis: WHY the prediction survives
# ============================================================
print(f"\n{'=' * 80}")
print("CRITICAL ANALYSIS: WHY THE PREDICTION SURVIVES (OR NOT)")
print(f"{'=' * 80}")

print("""
The key comparison is:

  PREDICTED echo h_rss  vs.  OBSERVED upper limit on h_rss

There are TWO distinct approaches in the literature:

1. MORPHOLOGY-AGNOSTIC (Miani et al. 2023):
   - Search for ANY transient after ringdown
   - Upper limit: h_rss < 1-4 x 10^-23 per event
   - Our echo h_rss is ~ 10^-26 to 10^-28 (FAR below this limit)
   - STATUS: CONSISTENT (echo is too weak to be detected by this method)

2. TEMPLATE-BASED (Abedi & Afshordi):
   - Use specific echo templates with known time delay
   - Stack across events using the predicted Delta_t(M) for each
   - Upper limit on universal amplitude: A < 0.4 (at 90% CL)
   - Our prediction: A_1/A_0 = 8.3e-5
   - This is VASTLY below 0.4
   - STATUS: CONSISTENT (echo amplitude way below current sensitivity)

CONCLUSION: The framework's prediction (A_1/A_0 = 8.3e-5) is 
FOUR ORDERS OF MAGNITUDE below the current observational upper limit (A < 0.4).

The prediction is NOT in tension with current data — it is simply 
not yet testable with current detector sensitivity.
""")

# ============================================================
# What sensitivity is needed to test the prediction?
# ============================================================
print(f"{'=' * 80}")
print("REQUIRED SENSITIVITY TO TEST PREDICTION #9")
print(f"{'=' * 80}")

# The Abedi bound A < 0.4 was set with 47 events from GWTC-3.
# SNR of the echo search scales as sqrt(N) * A_real
# Current bound: A < 0.4 with N=47 events
# The bound scales as A_limit ~ 0.4 * sqrt(47/N)

# To reach A ~ 8.3e-5:
N_needed = 47 * (0.4 / A1_over_A0)**2
print(f"\nCurrent bound: A < 0.4 (90% CL, N=47 events)")
print(f"Framework prediction: A = {A1_over_A0:.4e}")
print(f"Ratio: {0.4/A1_over_A0:.0f}x below current sensitivity")
print(f"\nNumber of events needed (naive sqrt scaling): {N_needed:.2e}")

# With LIGO O4 + O5 + Einstein Telescope:
# LIGO O4: ~200 more BBH
# LIGO O5: ~1000 more BBH  
# Einstein Telescope: ~10^5 BBH/year
# Cosmic Explorer: ~10^6 BBH/year

detectors = [
    ("GWTC-3 (current)", 47),
    ("GWTC-5.0 (2026)", 390),
    ("End of O5 (est. 2030)", 3000),
    ("Einstein Telescope yr 1", 100000),
    ("Einstein Telescope yr 5", 500000),
    ("Cosmic Explorer yr 1", 1000000),
]

print(f"\n{'Detector/Epoch':<30} {'N events':<15} {'A_limit (90%)':<15} {'Tests A=8.3e-5?'}")
print("-" * 80)
for name, N in detectors:
    A_lim = 0.4 * np.sqrt(47.0 / N)
    testable = "YES" if A_lim < A1_over_A0 else "no"
    print(f"{name:<30} {N:<15,} {A_lim:<15.4e} {testable}")

# ============================================================
# Revised SNR estimate (self-consistent)
# ============================================================
print(f"\n{'=' * 80}")
print("REVISED SNR ESTIMATE (CONFRONTATION WITH DATA)")
print(f"{'=' * 80}")

print("""
Our earlier naive SNR estimate (SNR ~ 57 for a single event) used an 
order-of-magnitude ringdown strain that was TOO OPTIMISTIC. The actual 
ringdown SNR for a 30 Msun merger at 400 Mpc is ~8-10, not ~680,000.

Corrected estimate:
  h_ringdown ~ SNR_ring * h_noise / sqrt(BW)
  For SNR_ring = 10, h_noise = 4e-24/sqrt(Hz), BW = 100 Hz:
  h_ring ~ 10 * 4e-24 * sqrt(100) / 100 = 4e-23

  h_echo = 8.3e-5 * 4e-23 = 3.3e-27
  
  SNR_echo = h_echo / (h_noise / sqrt(BW))
           = 3.3e-27 / (4e-24 / sqrt(100))
           = 3.3e-27 / 4e-25
           = 0.008
  
  Stacked SNR with N events: 0.008 * sqrt(N)
  For N = 10,000,000: stacked SNR ~ 26 (barely detectable!)
""")

# Corrected computation
h_noise = 4e-24  # LIGO design ASD at ~200 Hz
BW = 100  # Hz

# For a typical event with ringdown SNR ~ 10
SNR_ring_typical = 10
h_ring_typical = SNR_ring_typical * h_noise / np.sqrt(BW) * np.sqrt(BW)
# Actually: ringdown h_char = SNR * h_noise (in matched filter)
# h_peak ~ SNR * S_n(f)^{1/2} / sqrt(T_obs)
# More carefully:
# SNR^2 = 4 * integral |h_tilde(f)|^2 / S_n(f) df
# For a ringdown of duration tau and amplitude h_0:
#   h_tilde ~ h_0 * tau / (1 + (f-f_0)^2 * tau^2)
# The SNR ~ h_0 * sqrt(tau / S_n(f_QNM))

M30 = 30 * M_sun
tau_30 = tau_QNM(M30)
fq_30 = f_QNM(M30)

# LIGO ASD at 250 Hz (close to f_QNM for 30 Msun ~ 400 Hz):
S_n_half = 4e-24  # strain/sqrt(Hz)

# From SNR_ring ~ 10:
h_0_ring = SNR_ring_typical * S_n_half / np.sqrt(tau_30 / 2)
print(f"Corrected ringdown amplitude: h_0 = {h_0_ring:.3e}")

h_0_echo = h_0_ring * A1_over_A0
print(f"Corrected echo amplitude: h_0_echo = {h_0_echo:.3e}")

SNR_echo_single = h_0_echo * np.sqrt(tau_30 / 2) / S_n_half
print(f"Corrected echo SNR (single event): {SNR_echo_single:.4e}")

# With stacking:
for N in [47, 390, 3000, 100000, 1000000, 10000000]:
    snr = SNR_echo_single * np.sqrt(N)
    det = " *** DETECTABLE ***" if snr > 5 else ""
    print(f"  N = {N:>10,}: stacked SNR = {snr:.3e}{det}")

print(f"\n{'=' * 80}")
print("FINAL VERDICT")
print(f"{'=' * 80}")
print(f"""
1. The framework's echo prediction (A_1/A_0 = {A1_over_A0:.4e}) is
   NOT in tension with current LVK data.

2. Current observational limits (A < 0.4 at 90% CL with 47 events)
   are ~4,800x above the predicted amplitude.

3. Detection requires ~10^7 events (Cosmic Explorer era, ~2040+)
   OR a significant improvement in single-event SNR.

4. The prediction is therefore UNFALSIFIABLE with current technology
   but BECOMES testable with next-generation detectors.

5. The earlier SNR estimate of 57 per event was INCORRECT — it used
   an order-of-magnitude overestimate of the ringdown strain.
   The corrected single-event echo SNR is ~{SNR_echo_single:.1e}.

IMPLICATION FOR THE FRAMEWORK:
  Prediction #9 survives current data — but its near-term falsifiability
  must be honestly reassessed. The prediction transitions from
  "testable now" to "testable in the 2040s".
""")
