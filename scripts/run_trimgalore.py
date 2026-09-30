import argparse
import subprocess
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor


def main():
    parser = argparse.ArgumentParser(
        description="Run Trim Galore on paired-end samples."
    )
    parser.add_argument("--work-dir", required=True)
    parser.add_argument("--conda-path", required=True)
    parser.add_argument("--samples", nargs="+", required=True)
    parser.add_argument("--max-samples", type=int, default=2)
    parser.add_argument("--cores-per-sample", type=int, default=8)
    args = parser.parse_args()

    if args.max_samples < 1 or args.cores_per_sample < 1:
        parser.error("Sample and core counts must be positive.")

    if len(args.samples) != len(set(args.samples)):
        parser.error("Sample names must be unique.")

    # Set directories.
    work_dir = Path(args.work_dir).resolve()
    input_dir = work_dir / "rawdata"
    output_dir = work_dir / "trimgalore"
    log_dir = work_dir / "log" / "trimgalore"

    output_dir.mkdir(parents=True, exist_ok=True)
    log_dir.mkdir(parents=True, exist_ok=True)

    # Check all input files before starting.
    for sample in args.samples:
        for mate in (1, 2):
            read_file = input_dir / f"{sample}_{mate}.fq.gz"
            if not read_file.is_file():
                raise FileNotFoundError(f"Missing input: {read_file}")

    def run_sample(sample):
        log_file = log_dir / f"{sample}.trimgalore.log"

        command = [
            args.conda_path,
            "run",
            "--no-capture-output",
            "-n", "trimgalore",
            "trim_galore",
            "--cores", str(args.cores_per_sample),
            "--paired",
            str(input_dir / f"{sample}_1.fq.gz"),
            str(input_dir / f"{sample}_2.fq.gz"),
            "--output_dir", str(output_dir),
        ]

        print(f"Starting: {sample}", flush=True)

        with log_file.open("w") as log:
            try:
                result = subprocess.run(
                    command,
                    stdout=log,
                    stderr=subprocess.STDOUT,
                )
                return_code = result.returncode
            except OSError as error:
                log.write(f"Could not launch command: {error}\n")
                return_code = 1

        if return_code == 0:
            print(f"Finished: {sample}", flush=True)
        else:
            print(
                f"FAILED: {sample} — check {log_file}",
                flush=True,
            )

        return return_code

    # Process up to max_samples concurrently.
    with ThreadPoolExecutor(max_workers=args.max_samples) as executor:
        return_codes = list(executor.map(run_sample, args.samples))

    failed_samples = [
        sample
        for sample, code in zip(args.samples, return_codes)
        if code != 0
    ]

    if failed_samples:
        print(
            f"Failed samples: {', '.join(failed_samples)}",
            flush=True,
        )
        raise SystemExit(1)

    print("All samples completed successfully.", flush=True)


if __name__ == "__main__":
    main()