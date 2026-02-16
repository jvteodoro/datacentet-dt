Great — this is a **foundational abstraction step**, very similar to defining a *canonical measurement model* for a Digital Twin or EMS.
I’ll define **two base data objects**:

* **ACPowerLineState**
* **DCPowerLineState**

These are **engineering-grade**, **vendor-neutral**, and aligned with **professional electrical grid observation** (IEC / IEEE practice).
I’ll separate **what is measured**, **what is derived**, and **what is contextual**, because in real systems these are different acquisition paths.

---

# 1. AC Power Line – Base Data Object

## **ACPowerLineState**

This object models a **single AC line or bus** (single-phase or three-phase).

---

## 1.1 Electrical Fundamental Metrics (Measured)

### Voltage

* `Vrms_phase_A`
* `Vrms_phase_B`
* `Vrms_phase_C`
* `Vrms_line_to_line_AB`
* `Vrms_line_to_line_BC`
* `Vrms_line_to_line_CA`

### Current

* `Irms_phase_A`
* `Irms_phase_B`
* `Irms_phase_C`
* `Ineutral` (if applicable)

### Frequency

* `frequency_Hz`

---

## 1.2 Power Metrics (Measured or Derived)

### Active Power

* `P_phase_A` (W)
* `P_phase_B`
* `P_phase_C`
* `P_total`

### Reactive Power

* `Q_phase_A` (VAR)
* `Q_phase_B`
* `Q_phase_C`
* `Q_total`

### Apparent Power

* `S_phase_A` (VA)
* `S_phase_B`
* `S_phase_C`
* `S_total`

---

## 1.3 Power Quality Metrics (Professional Grid Metrics)

### Power Factor

* `power_factor_phase_A`
* `power_factor_phase_B`
* `power_factor_phase_C`
* `power_factor_total`

### Harmonics

* `THD_voltage_phase_A` (%)
* `THD_voltage_phase_B`
* `THD_voltage_phase_C`
* `THD_current_phase_A`
* `THD_current_phase_B`
* `THD_current_phase_C`

### Individual Harmonics (optional but professional-grade)

* `harmonic_voltage_spectrum_phase_A[n]`
* `harmonic_current_spectrum_phase_A[n]`
  *(typically n = 2…50)*

---

## 1.4 Grid Stability & Disturbances

* `voltage_sag_events`
* `voltage_swell_events`
* `interruptions_count`
* `flicker_Pst`
* `flicker_Plt`
* `unbalance_voltage_percent`
* `unbalance_current_percent`

---

## 1.5 Energy Metrics (Accumulated)

* `energy_active_import_Wh`
* `energy_active_export_Wh`
* `energy_reactive_import_VARh`
* `energy_reactive_export_VARh`
* `energy_apparent_VAh`

---

## 1.6 Thermal & Mechanical Context (Associated)

* `conductor_temperature_C`
* `busbar_temperature_C`
* `transformer_temperature_C`

---

## 1.7 Protection & State Indicators

* `breaker_state` (open/closed/tripped)
* `relay_trip_flags`
* `overcurrent_flag`
* `overvoltage_flag`
* `undervoltage_flag`
* `frequency_out_of_range_flag`

---

## 1.8 Metadata / Context

* `phase_configuration` (single / three-phase)
* `nominal_voltage`
* `nominal_frequency`
* `timestamp`
* `measurement_accuracy_class` (IEC 62053 class)

---

# 2. DC Power Line – Base Data Object

## **DCPowerLineState**

This object models a **DC bus, feeder, or rail** (48 V, 380 V, HVDC).

---

## 2.1 Electrical Fundamental Metrics (Measured)

### Voltage

* `Vdc`
* `Vdc_min`
* `Vdc_max`
* `voltage_ripple_rms`
* `voltage_ripple_peak_to_peak`

### Current

* `Idc`
* `Idc_min`
* `Idc_max`

---

## 2.2 Power Metrics

* `Pdc` (W)
* `power_direction` (source → load / load → source)

---

## 2.3 Energy Metrics

* `energy_import_Wh`
* `energy_export_Wh`
* `net_energy_Wh`

---

## 2.4 DC Power Quality Metrics

*(DC has quality too — just different)*

### Ripple & Noise

* `ripple_frequency_spectrum[n]`
* `ripple_percentage`

### Transients

* `voltage_spike_events`
* `current_spike_events`

### Stability

* `voltage_deviation_percent`
* `load_step_response_time_ms`

---

## 2.5 Grounding & Leakage

* `insulation_resistance_MOhm`
* `leakage_current_mA`
* `ground_fault_flag`

*(Critical in 380 V DC systems)*

---

## 2.6 Thermal Metrics

* `conductor_temperature_C`
* `connector_temperature_C`
* `power_device_temperature_C`

---

## 2.7 Protection & Switching State

* `breaker_state`
* `solid_state_switch_state`
* `overcurrent_flag`
* `overvoltage_flag`
* `undervoltage_flag`
* `arc_fault_detected_flag`

---

## 2.8 Metadata / Context

* `dc_bus_nominal_voltage`
* `dc_bus_type` (48V / 380V / HVDC)
* `timestamp`
* `measurement_accuracy_class`

---

# 3. Key Conceptual Difference Between the Objects

| Aspect              | AC Object            | DC Object       |
| ------------------- | -------------------- | --------------- |
| Frequency           | Core metric          | Not applicable  |
| Reactive power      | Explicit             | None            |
| Harmonics           | Sinusoidal harmonics | Ripple & noise  |
| Power factor        | Core KPI             | Not applicable  |
| Fault behavior      | Zero-crossing helps  | Arc persistence |
| Control granularity | Phase-based          | Rail-based      |

---

# 4. Why these objects are *base objects*

These are **minimal complete representations**:

* Anything missing → blind spot for grid-grade monitoring
* Anything extra → optimization or analytics layer

They can serve as:

* Digital Twin state vectors
* EMS / SCADA telemetry schema
* Edge controller contracts
* Research datasets
* Input to optimization / AI layers

---

# 5. Important Design Insight

> **AC systems are phase-centric.
> DC systems are rail-centric.**

Your objects reflect this difference cleanly.

---

If you want, next we can:

* Normalize both into a **common abstract PowerLineState**
* Define **sampling rates & time semantics**
* Map **which layers populate which fields**
* Translate this into **IEC / IEEE aligned schemas**
* Turn this into a **DSL or API contract**

Just tell me the direction.
