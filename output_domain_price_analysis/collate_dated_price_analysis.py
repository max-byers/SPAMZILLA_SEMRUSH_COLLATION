import os
import re
import glob
import traceback
from datetime import datetime
from typing import List, Optional, Tuple

import pandas as pd


DATE_FILENAME_REGEX = re.compile(r"^(\d{4}-\d{2}-\d{2})_price_analysis\.csv$", re.IGNORECASE)


def find_price_analysis_files(directory: str) -> List[Tuple[str, Optional[str]]]:
    """Return list of (path, date_string) for files named like YYYY-MM-DD_price_analysis.csv.

    Only searches the provided directory (no recursion). Excludes non-matching files
    such as collated aggregates.
    """
    pattern = os.path.join(directory, "*_price_analysis.csv")
    paths = glob.glob(pattern)
    results: List[Tuple[str, Optional[str]]] = []
    for path in paths:
        filename = os.path.basename(path)
        m = DATE_FILENAME_REGEX.match(filename)
        if not m:
            # Skip files that do not strictly follow the date prefix pattern
            continue
        date_str = m.group(1)
        results.append((path, date_str))
    # Sort by parsed date
    results.sort(key=lambda t: t[1])
    return results


def collate_dated_price_analysis(
    directory: str = os.path.dirname(__file__),
) -> Optional[str]:
    """Collate all YYYY-MM-DD_price_analysis.csv files in `directory` into a single CSV.

    - Adds Source_File and Report_Date columns
    - Writes output to `collated_price_analysis.csv` in the same directory
    - Returns path to the written file, or None if nothing to do
    """
    try:
        files_with_dates = find_price_analysis_files(directory)
        # Keep only files dated on or after August 1 (within their respective years)
        filtered_files_with_dates: List[Tuple[str, Optional[str]]] = []
        for path, date_str in files_with_dates:
            if not date_str:
                continue
            try:
                d = datetime.strptime(date_str, "%Y-%m-%d").date()
                august_first_same_year = datetime(year=d.year, month=8, day=1).date()
                if d >= august_first_same_year:
                    filtered_files_with_dates.append((path, date_str))
            except ValueError:
                # Skip files with unparsable dates just in case
                continue

        files_with_dates = filtered_files_with_dates
        if not files_with_dates:
            print(f"No *_price_analysis.csv files found in: {directory}")
            return None

        print("Found the following price analysis files to collate:")
        for path, date_str in files_with_dates:
            print(f"- {os.path.basename(path)} (date: {date_str})")

        frames: List[pd.DataFrame] = []
        for path, date_str in files_with_dates:
            df = pd.read_csv(path)
            df["Source_File"] = os.path.basename(path)
            df["Report_Date"] = date_str
            frames.append(df)

        combined = pd.concat(frames, ignore_index=True, sort=False)

        output_path = os.path.join(directory, "collated_price_analysis.csv")
        combined.to_csv(output_path, index=False)
        print(f"\nWrote collated file: {output_path}")
        print(f"Total rows: {len(combined)} | Total files: {len(frames)}")
        return output_path

    except Exception as exc:
        print("Error during collate_dated_price_analysis:")
        print(type(exc).__name__, str(exc))
        print(traceback.format_exc())
        return None


if __name__ == "__main__":
	collate_dated_price_analysis()


