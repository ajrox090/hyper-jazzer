import re
from itertools import repeat


def extract_steps_and_coverage(file_path, seed, param, fuzz_target):
    steps = []
    coverages = []
    with open(file_path, 'r') as file:
        for line in file:
            if line.startswith("#"):
                # Define the regular expression pattern
                pattern = r"#(\d+)\s+.*?cov:\s*(\d+).*"  # extracts both file number and coverage

                # Search for the coverage information in the line
                match = re.search(pattern, line)

                if match:
                    steps.append(int(match.group(1)))
                    coverages.append(int(match.group(2)))

    return [(seed, step, cov, param, fuzz_target) for step, cov in zip(steps, coverages)]
