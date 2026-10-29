# SPORTZA — Methodology & Mathematical Formulations

This document details the mathematical formulations and sports science methodologies implemented in SPORTZA.

---

## 1. Internal Workload Formulations

### Session Rating of Perceived Exertion (sRPE)
Adopted from Foster et al. (2001) and Impellizzeri et al. (2004):
$$\text{sRPE} = \text{Duration (minutes)} \times \text{RPE (Borg CR-10)}$$
Measured in Arbitrary Units (AU).

### Daily Training Load ($DL$)
$$DL_d = \sum_{i=1}^{k} \text{sRPE}_{d, i}$$
Where $k$ is the number of training, recovery, or competition sessions completed on day $d$.

### Acute Training Load (ATL) & Chronic Training Load (CTL)
- **Acute Training Load (Fatigue Proxy):** Rolling 7-day average of daily loads:
$$\text{ATL}_t = \frac{1}{7} \sum_{i=0}^{6} DL_{t - i}$$
- **Chronic Training Load (Fitness Proxy):** Rolling 28-day average of daily loads:
$$\text{CTL}_t = \frac{1}{28} \sum_{i=0}^{27} DL_{t - i}$$

### Acute:Chronic Workload Ratio (ACWR)
$$\text{ACWR}_t = \frac{\text{ATL}_t}{\text{CTL}_t} \quad (\text{masked when } \text{CTL}_t < 1.0)$$

### Training Monotony & Strain
Adopted from Foster (1998):
$$\text{Monotony}_t = \frac{\text{Mean}(DL_{t-6 \dots t})}{\text{StdDev}(DL_{t-6 \dots t})}$$
$$\text{Strain}_t = \text{Weekly Load}_t \times \text{Monotony}_t$$
High monotony coupled with high strain highlights inadequate periodization and limited recovery variation.

---

## 2. Personal Baseline Standardizations

For athlete $p$, metric $m$ at date $t$:
$$\mu_{p, m, 28} = \frac{1}{N_{obs}} \sum_{i=1}^{28} x_{p, m, t-i} \quad (N_{obs} \ge 7)$$
$$\sigma_{p, m, 28} = \sqrt{\frac{1}{N_{obs} - 1} \sum_{i=1}^{28} (x_{p, m, t-i} - \mu_{p, m, 28})^2}$$
$$z_{p, m, t} = \frac{x_{p, m, t} - \mu_{p, m, 28}}{\sigma_{p, m, 28} + \epsilon}$$
Where $\epsilon = 10^{-4}$ prevents division by zero when an athlete reports constant values.

---

## 3. Positional Locomotor Thresholds (STATSports GNSS)

Adopted from Winther et al. (2021) and Bradley & Vescovi (2015) for elite female soccer:
- **Total Distance (TD):** Cumulative trajectory displacement.
- **High-Speed Running Distance (HSRD):** Distance traveled at speeds $> 4.44\text{ m/s}$ ($> 16.0\text{ km/h}$).
- **Sprint Distance (SpD):** Distance traveled at speeds $> 5.55\text{ m/s}$ ($> 20.0\text{ km/h}$).
- **Acceleration / Deceleration Distance:** Displacement where $|\Delta v / \Delta t| > 2.26\text{ m/s}^2$ with a minimum effort duration of $0.3\text{ s}$.
- **Worst-Case Scenario (Peak 1-Min):** Maximum rolling 1-minute distance within a match session compared against the following 5-minute transient fatigue period and 5-minute match average.

