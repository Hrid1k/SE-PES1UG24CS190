"""Energy consumption and tariff calculator.

Records utility meter readings, computes a three-tier electricity bill,
flags meters with unusually high usage and persists readings to JSON.
"""
import ast
import json

from datetime import datetime

SPIKE_LIMIT = 500
TIER_1_LIMIT = 100
TIER_2_LIMIT = 300

# Shared state, mutated in place (no ``global`` statements needed).
meters = {}
rates = [3.5, 5.0, 7.5]

_ALLOWED_OPS = {
    ast.Add: lambda a, b: a + b,
    ast.Sub: lambda a, b: a - b,
    ast.Mult: lambda a, b: a * b,
    ast.Div: lambda a, b: a / b,
}


def _eval_node(node):
    """Recursively evaluate a whitelisted arithmetic AST node."""
    if isinstance(node, ast.Constant) and isinstance(
            node.value, (int, float)):
        return node.value
    if isinstance(node, ast.BinOp) and type(node.op) in _ALLOWED_OPS:
        return _ALLOWED_OPS[type(node.op)](
            _eval_node(node.left), _eval_node(node.right))
    if isinstance(node, ast.UnaryOp) and isinstance(
            node.op, (ast.UAdd, ast.USub)):
        value = _eval_node(node.operand)
        return value if isinstance(node.op, ast.UAdd) else -value
    raise ValueError("unsupported expression")


def safe_eval(expression):
    """Evaluate a plain arithmetic expression without using eval()."""
    try:
        return _eval_node(ast.parse(expression, mode="eval").body)
    except (SyntaxError, ZeroDivisionError, RecursionError) as exc:
        raise ValueError("invalid expression") from exc


def record_reading(meter_id, units, history=None):
    """Add a reading to a meter and append it to the history list.

    Raises ValueError for negative readings, which would otherwise
    produce negative bills.
    """
    if units < 0:
        raise ValueError(f"negative reading rejected for {meter_id}: {units}")
    if history is None:
        history = []
    history.append((meter_id, units, str(datetime.now())))
    meters[meter_id] = meters.get(meter_id, 0) + units
    return history


def compute_bill(meter_id, tier_rates):
    """Return the tiered bill for a meter (100 / next 200 / remainder)."""
    if meter_id not in meters:
        raise ValueError(f"unknown meter: {meter_id}")
    units = meters[meter_id]
    tier_1 = min(units, TIER_1_LIMIT)
    tier_2 = max(0, min(units, TIER_2_LIMIT) - TIER_1_LIMIT)
    tier_3 = max(0, units - TIER_2_LIMIT)
    return (tier_1 * tier_rates[0] + tier_2 * tier_rates[1]
            + tier_3 * tier_rates[2])


def raise_rates(percent):
    """Increase every tariff tier by the given percentage."""
    for i, rate in enumerate(rates):
        rates[i] = rate * (1 + percent / 100)


def flag_spikes():
    """Return the ids of meters whose usage exceeds SPIKE_LIMIT."""
    return [m for m, units in meters.items() if units > SPIKE_LIMIT]


def load_meter_data(file="meters.json"):
    """Load meters from a JSON file; start empty if missing or corrupt."""
    try:
        with open(file, encoding="utf-8") as handle:
            data = json.load(handle)
    except (OSError, json.JSONDecodeError):
        data = {}
    meters.clear()
    meters.update(data)


def save_meter_data(file="meters.json"):
    """Write the current meters to a JSON file."""
    with open(file, "w", encoding="utf-8") as handle:
        json.dump(meters, handle)


def main():
    """Run the demo workflow."""
    history = []
    record_reading("M-01", 120, history)
    record_reading("M-02", 640, history)
    try:
        record_reading("M-03", -50, history)
    except ValueError as err:
        print("Skipped:", err)
    print("Readings stored so far:", len(history))
    raise_rates(10)
    print(f"Bill M-01: {compute_bill('M-01', rates):.2f}")
    try:
        print(f"Bill M-03: {compute_bill('M-03', rates):.2f}")
    except ValueError as err:
        print("Bill M-03 unavailable:", err)
    print("Spikes:", flag_spikes())
    adjustment = input(
        "Extra units for M-01 as an expression (Enter for 0): ") or "0"
    try:
        record_reading("M-01", safe_eval(adjustment), history)
    except ValueError as err:
        print("Adjustment ignored:", err)
    save_meter_data()
    load_meter_data()
    print(f"Bill M-01 after reload: {compute_bill('M-01', rates):.2f}")


if __name__ == "__main__":
    main()
