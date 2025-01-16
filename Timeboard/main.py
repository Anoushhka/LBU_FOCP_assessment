import csv
import json
import sys
from statistics import mean, stdev


class Driver:
    def __init__(self, code, name='', team='', number=0):
        self.code = code
        self.name = name
        self.team = team
        self.number = number
        self.lap_times = []
        self.fastest_lap = float('inf')

    def add_lap(self, lap_time):
        self.lap_times.append(lap_time)
        if lap_time < self.fastest_lap:
            self.fastest_lap = lap_time

    def average_lap(self):
        return mean(self.lap_times) if self.lap_times else 0

    def standard_deviation(self):
        return stdev(self.lap_times) if len(self.lap_times) > 1 else 0


class TimingBoard:
    def __init__(self, location):
        self.location = location
        self.drivers = {}
        self.driver_details = {}

    def load_driver_details(self, driver_details_file):
        """Load driver details from a CSV file."""
        with open(driver_details_file, 'r') as file:
            for line in file:
                try:
                    # Expecting format: code,name,team,number
                    code, name, team, number = line.strip().split(',')
                    self.driver_details[code] = {
                        'name': name,
                        'team': team,
                        'number': int(number)  # Ensure number is an integer
                    }
                except ValueError as e:
                    print(f"Error parsing line: {line}. Error: {e}")

    def process_timing_file(self, timing_file):
        """Process the lap times for each driver."""
        with open(timing_file, 'r') as file:
            for line in file:
                try:
                    if ',' not in line:  # Skip lines that don't match the expected format
                        continue
                    
                    driver_code, lap_time = line.strip().split(',')
                    lap_time = float(lap_time)
                    if driver_code not in self.drivers:
                        # Create driver if not already present
                        details = self.driver_details.get(driver_code, {})
                        self.drivers[driver_code] = Driver(driver_code, **details)
                    self.drivers[driver_code].add_lap(lap_time)
                except ValueError as e:
                    print(f"Error parsing line: {line}. Error: {e}")

    def display_results(self):
        """Display results including fastest lap, average lap, etc."""
        if not self.drivers:
            print("No drivers found. Please check the input files.")
            return

        print(f"Formula 1 Grand Prix - {self.location}")
        print("=" * 50)

        fastest_driver = min(self.drivers.values(), key=lambda d: d.fastest_lap)
        print(f"Fastest Lap: {fastest_driver.name} ({fastest_driver.code}) - {fastest_driver.fastest_lap:.3f}")
        all_lap_times = [lap_time for driver in self.drivers.values() for lap_time in driver.lap_times]
        print(f"Overall Average Lap Time: {mean(all_lap_times):.3f}")
        print(f"Overall Median Lap Time: {sorted(all_lap_times)[len(all_lap_times) // 2]:.3f}")

        most_laps_driver = max(self.drivers.values(), key=lambda d: len(d.lap_times))
        print(f"Driver with Most Laps: {most_laps_driver.name} ({most_laps_driver.code}) - {len(most_laps_driver.lap_times)} laps")

        least_laps_driver = min(self.drivers.values(), key=lambda d: len(d.lap_times))
        print(f"Driver with Least Laps: {least_laps_driver.name} ({least_laps_driver.code}) - {len(least_laps_driver.lap_times)} laps")

        most_consistent_driver = min(
            (driver for driver in self.drivers.values() if len(driver.lap_times) > 1),
            key=lambda d: d.standard_deviation(),
            default=None
        )
        least_consistent_driver = max(
            (driver for driver in self.drivers.values() if len(driver.lap_times) > 1),
            key=lambda d: d.standard_deviation(),
            default=None
        )
        if most_consistent_driver and least_consistent_driver:
            print(f"Most Consistent Driver: {most_consistent_driver.name} ({most_consistent_driver.code}) "
                  f"with std dev {most_consistent_driver.standard_deviation():.3f}")
            print(f"Least Consistent Driver: {least_consistent_driver.name} ({least_consistent_driver.code}) "
                  f"with std dev {least_consistent_driver.standard_deviation():.3f}")

        print("\nDriver Rankings (Fastest Lap):")
        ranked_drivers = sorted(self.drivers.values(), key=lambda d: d.fastest_lap)
        for rank, driver in enumerate(ranked_drivers, start=1):
            print(f"{rank}. {driver.name} ({driver.code}) - {driver.fastest_lap:.3f}")

        print("\nDetailed Results:")
        print("+-----+----------------+-----------------+------------+-----------+-----------+--------+-----------+")
        print("|   # | Driver         | Team            |   Best Lap |   Avg Lap |   Std Dev |   Laps | Notes     |")
        print("+=====+================+=================+============+===========+===========+========+===========+")
        for code, driver in sorted(self.drivers.items(), key=lambda x: x[1].fastest_lap):
            avg_time = driver.average_lap()
            std_dev = driver.standard_deviation()
            highlight = ""
            if code == fastest_driver.code:
                highlight = "*Fastest*"
            table_data = [
                driver.number,
                driver.name,
                driver.team,
                f"{driver.fastest_lap:.3f}",
                f"{avg_time:.3f}",
                f"{std_dev:.3f}",
                len(driver.lap_times),
                highlight
            ]
            print(f"| {table_data[0]:<3} | {table_data[1]:<15} | {table_data[2]:<15} | {table_data[3]:<10} | "
                  f"{table_data[4]:<9} | {table_data[5]:<9} | {table_data[6]:<6} | {table_data[7]:<9} |")
        print("+-----+----------------+-----------------+------------+-----------+-----------+--------+-----------+")

    def export_results_json(self, output_file):
        """Export results to a JSON file."""
        data = {
            "location": self.location,
            "drivers": [
                {
                    "number": driver.number,
                    "name": driver.name,
                    "team": driver.team,
                    "fastest_lap": driver.fastest_lap,
                    "average_lap": driver.average_lap(),
                    "laps": driver.lap_times,
                }
                for driver in self.drivers.values()
            ],
        }
        with open(output_file, 'w') as f:
            json.dump(data, f, indent=4)
        print(f"Results exported to {output_file}")

    def export_results_csv(self, output_file):
        """Export results to a CSV file."""
        with open(output_file, 'w', newline='') as csvfile:
            fieldnames = ['Driver', 'Team', 'Fastest Lap', 'Average Lap', 'Laps']
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)

            writer.writeheader()
            for driver in self.drivers.values():
                writer.writerow({
                    'Driver': driver.name,
                    'Team': driver.team,
                    'Fastest Lap': driver.fastest_lap,
                    'Average Lap': driver.average_lap(),
                    'Laps': len(driver.lap_times),
                })
        print(f"Results exported to {output_file}")


def main():
    if len(sys.argv) < 3:
        print("Usage: python main.py <lap_files> [--export-json] [--export-csv]")
        sys.exit(1)

    lap_files = []
    export_json = False
    export_csv = False

    # Parse command-line arguments
    for arg in sys.argv[1:]:
        if arg.endswith(".txt"):
            lap_files.append(arg)
        elif arg == "--export-json":
            export_json = True
        elif arg == "--export-csv":
            export_csv = True

    # Load driver details (you should provide the path to the driver details file)
    board = TimingBoard(location="Monaco Grand Prix")  # Example location
    board.load_driver_details('f1_drivers.txt')

    # Process timing files
    for lap_file in lap_files:
        board.process_timing_file(lap_file)

    # Display results
    board.display_results()

    # Export results if requested
    if export_json:
        board.export_results_json('season_results.json')
    if export_csv:
        board.export_results_csv('season_results.csv')


if __name__ == "__main__":
    main()
