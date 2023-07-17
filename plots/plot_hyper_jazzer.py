import os
import datetime
import subprocess
from pathlib import Path

import pandas as pd
from tqdm import tqdm
from utils import extract_steps_and_coverage

ROOT_DIR = Path(os.path.dirname(os.path.abspath(__file__)))
JAZZER_DIR = os.path.join(ROOT_DIR.parent, 'jazzer')


def process_examples(test_filenames, num_runs=10, other_params=None, fuzzer_runtime=30):
    if other_params is None:
        other_params = [dict()]
    coverage_data = []

    for test_filename in test_filenames:
        for variant in [""] + [str(x) for x in range(2, 5)]:
            variant_failed = False
            for param in other_params:
                param_str = " ".join([f"{k}={v}" for k, v in param.items()])
                complete_fuzz_target = f"{test_filename}{variant}"
                for seed in tqdm(range(num_runs)):
                    command = f"bazel run {complete_fuzz_target} -- -max_total_time={fuzzer_runtime} --keep_going" \
                              f"=100000 -timeout=0 " \
                              f"-seed={seed} " + \
                              param_str
                    print(command)
                    process = subprocess.Popen(command, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                                               cwd=f"{JAZZER_DIR}/examples/")
                    stdout, stderr = process.communicate()
                    stderr = stderr.decode("utf-8")
                    stdout = stdout.decode("utf-8")

                    if any([x in stderr + stdout for x in
                            ["0000000000000000000000000000000000000000", "Build failed",
                             "Failed to construct mutator"]]):
                        if "no such target" in stdout + stderr:
                            print(f"Target not found, skipping variant {variant}")
                            variant_failed = True
                        print(stderr)
                        break
                    coverage_data.extend(extract_steps_and_coverage(
                        f'{JAZZER_DIR}/bazel-out/k8-opt/testlogs/examples/{complete_fuzz_target}/test.xml', seed=seed,
                        param=param_str + " " + complete_fuzz_target,
                        fuzz_target=test_filename))
                if variant_failed:
                    break
            if variant_failed:
                break

    df = pd.DataFrame(coverage_data, columns=['Seed', 'Step', 'Coverage', 'Param', 'Fuzz Target'])
    df.to_csv(f'plotdata_{datetime.datetime.now()}.csv')


test_filenames = ["ProtobufFuzzer"]
# test_filenames = ["JsonSanitizerDenylistFuzzer", "MazeFuzzer"]
#  "--experimental_cross_over_frequency": "1"
other_params = [{"--experimental_mutator": "true", "--prng_closed_range_alpha": "2", },
                {"--experimental_mutator": "true", "--prng_closed_range_beta": "2"},
                {"--experimental_mutator": "true"}, ]
# other_params = ["old_style"]
# process_examples(test_filenames, other_params=other_params)
process_examples(test_filenames, other_params=other_params, num_runs=10, fuzzer_runtime=5)
