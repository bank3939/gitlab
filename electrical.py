import math


def analyze_dc(voltage_v, resistance_ohm):
    if not math.isfinite(voltage_v) or voltage_v < 0:
        raise ValueError("Voltage must be a finite, non-negative number.")
    if not math.isfinite(resistance_ohm) or resistance_ohm <= 0:
        raise ValueError("Resistance must be a finite number greater than zero.")

    current_a = voltage_v / resistance_ohm
    power_w = voltage_v * current_a
    return {"current_a": current_a, "power_w": power_w}


def analyze_circuit(voltage_v, branches):
    if not math.isfinite(voltage_v) or voltage_v < 0:
        raise ValueError("Voltage must be a finite, non-negative number.")
    if not branches:
        raise ValueError("A circuit must contain at least one branch.")

    branch_resistances = []
    for branch in branches:
        if not branch:
            raise ValueError("Each branch must contain at least one resistor.")
        if any(not math.isfinite(value) or value <= 0 for value in branch):
            raise ValueError("Resistance values must be finite numbers greater than zero.")
        branch_resistances.append(sum(branch))

    equivalent_resistance = 1 / sum(1 / value for value in branch_resistances)
    results = []
    for resistors, branch_resistance in zip(branches, branch_resistances):
        branch_current = voltage_v / branch_resistance
        results.append({
            "resistance_ohm": branch_resistance,
            "current_a": branch_current,
            "resistors": [
                {
                    "resistance_ohm": resistance,
                    "current_a": branch_current,
                    "voltage_v": branch_current * resistance,
                    "power_w": branch_current**2 * resistance,
                }
                for resistance in resistors
            ],
        })

    total_current = voltage_v / equivalent_resistance
    return {
        "equivalent_resistance_ohm": equivalent_resistance,
        "total_current_a": total_current,
        "total_power_w": voltage_v * total_current,
        "branches": results,
    }


def _parse_resistors(value):
    try:
        resistors = [float(item.strip()) for item in value.split(",")]
    except ValueError as error:
        raise ValueError("Enter resistance values as numbers separated by commas.") from error
    if not resistors or any(not math.isfinite(item) or item <= 0 for item in resistors):
        raise ValueError("Each resistance must be a finite number greater than zero.")
    return resistors


def main():
    print("DC Circuit Calculator")
    print("1. Series  2. Parallel  3. Mixed (parallel branches with series resistors)")
    circuit_type = input("Choose circuit type [1-3]: ").strip()
    if circuit_type not in {"1", "2", "3"}:
        raise ValueError("Choose 1, 2, or 3 for the circuit type.")

    voltage_v = float(input("Source voltage (V): ").strip())
    if circuit_type == "1":
        branches = [_parse_resistors(input("Resistances in series (ohms, comma-separated): "))]
    elif circuit_type == "2":
        branches = [[value] for value in _parse_resistors(
            input("Parallel resistances (ohms, comma-separated): ")
        )]
    else:
        branch_count = int(input("Number of parallel branches: ").strip())
        if branch_count < 2:
            raise ValueError("A mixed circuit must have at least two branches.")
        branches = [
            _parse_resistors(input(f"Resistances in branch {index + 1} (ohms, comma-separated): "))
            for index in range(branch_count)
        ]
        if not any(len(branch) > 1 for branch in branches):
            raise ValueError("For a mixed circuit, at least one branch needs multiple resistors.")

    result = analyze_circuit(voltage_v, branches)
    print(f"\nEquivalent resistance: {result['equivalent_resistance_ohm']:.4g} ohm")
    print(f"Total current: {result['total_current_a']:.4g} A")
    print(f"Total power: {result['total_power_w']:.4g} W")
    for branch_index, branch in enumerate(result["branches"], start=1):
        print(f"\nBranch {branch_index}: {branch['current_a']:.4g} A")
        for resistor_index, resistor in enumerate(branch["resistors"], start=1):
            print(
                f"  R{branch_index}.{resistor_index} = {resistor['resistance_ohm']:.4g} ohm, "
                f"{resistor['voltage_v']:.4g} V, {resistor['current_a']:.4g} A, "
                f"{resistor['power_w']:.4g} W"
            )


if __name__ == "__main__":
    try:
        main()
    except (ValueError, OverflowError) as error:
        print(f"Error: {error}")