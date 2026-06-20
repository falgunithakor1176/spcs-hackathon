import os
import csv
import sys

# Add backend directory to sys.path to allow importing services
backend_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(backend_dir)

from services.mock_service import (
    generate_crimes,
    generate_cybercrime,
    generate_patrol_units,
    generate_hotspots,
    generate_alerts,
    generate_patrol_routes,
    get_predictions
)

def export_to_csv(data_list, filename):
    if not data_list:
        print(f"Skipping {filename}: No data provided.")
        return

    # Extract headers from the first dictionary
    keys = data_list[0].keys()
    
    with open(filename, 'w', newline='', encoding='utf-8') as f:
        dict_writer = csv.DictWriter(f, fieldnames=keys)
        dict_writer.writeheader()
        dict_writer.writerows(data_list)
    print(f"Exported {len(data_list)} records to {filename}")

def main():
    seed_dir = os.path.join(backend_dir, 'data', 'seed')
    os.makedirs(seed_dir, exist_ok=True)

    print("Generating seeded datasets...")

    # Generate data
    crimes = generate_crimes(count=10000)
    cyber = generate_cybercrime(count=1200)
    patrols = generate_patrol_units(count=24)
    hotspots = generate_hotspots()
    alerts = generate_alerts(count=50)
    predictions = get_predictions()
    routes = generate_patrol_routes()

    print("Writing to CSV...")
    
    export_to_csv(crimes, os.path.join(seed_dir, 'crimes.csv'))
    export_to_csv(cyber, os.path.join(seed_dir, 'cybercrime.csv'))
    export_to_csv(patrols, os.path.join(seed_dir, 'patrol_units.csv'))
    export_to_csv(hotspots, os.path.join(seed_dir, 'hotspots.csv'))
    export_to_csv(alerts, os.path.join(seed_dir, 'alerts.csv'))
    export_to_csv(predictions, os.path.join(seed_dir, 'predictions.csv'))
    export_to_csv(routes, os.path.join(seed_dir, 'patrol_routes.csv'))

    print("Data export complete!")

if __name__ == '__main__':
    main()
