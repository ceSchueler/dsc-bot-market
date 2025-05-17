import json
from datetime import datetime

# Round end timestamps
ROUND_ENDS = {
    "R01": "2025-05-16T23:54:59.944Z",
    "R02": "2025-05-17T00:16:58.652Z",
    "R03": "2025-05-17T00:25:46.024Z",
    "R04": "2025-05-17T00:33:45.215Z",
    "R05": "2025-05-17T00:43:10.634Z",
    "R06": "2025-05-17T00:43:10.634Z",
    "R07": "2025-05-17T00:53:09.935Z",
    "R08": "2025-05-17T00:59:31.789Z",
    "R09": "2025-05-17T01:05:29.897Z",
    "R10": "2025-05-17T01:10:18.513Z",
    "R11": "2025-05-17T01:15:33.437Z",
    "R12": "2025-05-17T01:20:24.475Z",
    "R13": "2025-05-17T01:25:45.485Z",
    "R14": "2025-05-17T01:30:27.362Z",
    "R15": "2025-05-17T01:35:18.427Z",
    "R16": "2025-05-17T01:40:18.568Z",
    "R17": "2025-05-17T01:45:52.839Z"
}


def load_transactions():
    """Load transactions from JSON file."""
    try:
        with open("data/transactions.json", 'r') as f:
            data = json.load(f)
            return data.get("transactions", []) if isinstance(data, dict) else data
    except (json.JSONDecodeError, FileNotFoundError):
        return []


def evaluate_penalties():
    """Evaluate penalties for players who accepted more than 2 offers in a round."""
    # Convert timestamps to datetime objects
    round_times = {k: datetime.fromisoformat(v.replace('Z', '+00:00'))
                   for k, v in ROUND_ENDS.items()}

    # Sort round times
    sorted_round_times = sorted(round_times.items(), key=lambda x: x[1])

    penalties = {}
    transactions = load_transactions()

    # For each transaction
    for trans in transactions:
        trans_time = datetime.fromisoformat(trans['timestamp'].replace('Z', '+00:00'))

        # Find which round this transaction belongs to
        current_round = None
        for round_num, (round_name, round_end) in enumerate(sorted_round_times):
            if trans_time <= round_end:
                current_round = round_name
                break

        if current_round:
            # Initialize round data if needed
            if current_round not in penalties:
                penalties[current_round] = {}

            # Count acceptances for each player in this round
            buyer_id = trans['buyer_id']
            if buyer_id not in penalties[current_round]:
                penalties[current_round][buyer_id] = 1
            else:
                penalties[current_round][buyer_id] += 1

    # Evaluate penalties
    final_penalties = []
    for round_name, round_data in penalties.items():
        for player_id, accept_count in round_data.items():
            if accept_count > 2:
                final_penalties.append({
                    'round': round_name,
                    'player_id': player_id,
                    'acceptances': accept_count
                })

    return final_penalties


def main():
    penalties = evaluate_penalties()

    if penalties:
        print("Players with penalties:")
        for penalty in penalties:
            print(f"Round {penalty['round']}: Player {penalty['player_id']} had {penalty['acceptances']} acceptances")
    else:
        print("No penalties found.")


if __name__ == "__main__":
    main()