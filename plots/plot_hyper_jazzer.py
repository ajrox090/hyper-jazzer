import subprocess
import pandas as pd
import seaborn.objects as so
from tqdm import tqdm

from utils import extract_steps_and_coverage


def process_examples(test_filenames, num_runs=10, other_params=None):
    if other_params is None:
        other_params = [dict()]
    coverage_data = []
    for test_filename in test_filenames:
        for param in other_params:
            for seed in tqdm(range(num_runs)):
                param_str = " ".join([f"{k}={v}" for k, v in param.items()])
                command = f"bazel run {test_filename} -- --experimental_mutator -seed={seed} -max_total_time=10 " \
                          f"--keep_going=100000 " + param_str
                process = subprocess.Popen(command, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                                           cwd="./jazzer/examples/")
                _, _ = process.communicate()  # this executes once the subprocess is finished, maybe not needed
                coverage_data.extend(
                    extract_steps_and_coverage(f'./jazzer/bazel-out/k8-opt/testlogs/examples/{test_filename}/test.xml',
                                               seed=seed, param=param_str))

    df = pd.DataFrame(coverage_data, columns=['Seed', 'Step', 'Coverage', 'Param'])
    df.to_csv("results/plotdata.csv")

    # use jupyter-notebook :D
    # plot_coverage(df)


def plot_coverage(df: pd.DataFrame):
    p = (so.Plot(data=df, x="Step", y="Coverage")
         .add(so.Band(), so.Est(errorbar=('pi', 75)))
         .add(so.Line(), so.Agg()))
    p.show()


test_filenames = ["JsonSanitizerDenylistFuzzer"]
other_params = [{"--experimental_cross_over_frequency": "1"}, dict()]
process_examples(test_filenames, other_params=other_params)
