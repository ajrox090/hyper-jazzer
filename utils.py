import re


def extract_steps_and_coverage(file_path, seed, param):
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

    return list(zip([seed for _ in range(len(steps))], steps, coverages, zip([param for _ in range(len(steps))])))
