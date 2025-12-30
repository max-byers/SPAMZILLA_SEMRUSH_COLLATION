import os
import traceback
from typing import List, Set, Optional

import pandas as pd


def normalize_domain(domain: str) -> str:
    """Normalize domain for reliable matching (case-insensitive, trim, strip trailing dot)."""
    if domain is None:
        return ""
    return domain.strip().strip(".").lower()


def load_purchased_domains(file_path: str) -> List[str]:
    """Load purchased domains from a text file (one per line).

    - Ignores blank lines and lines starting with '#'
    - Returns normalized domain strings
    """
    domains: List[str] = []
    with open(file_path, "r", encoding="utf-8") as f:
        for line in f:
            raw = line.strip()
            if not raw or raw.startswith("#"):
                continue
            domains.append(normalize_domain(raw))
    return domains


def filter_purchased_from_collated(
    directory: str = os.path.dirname(__file__),
    collated_filename: str = "collated_price_analysis.csv",
    purchased_list_filename: str = "domains_purchased",
) -> Optional[str]:
    """Create a CSV containing only purchased domains and their info from the collated sheet.

    - Reads `collated_price_analysis.csv` in the provided directory
    - Reads `domains_purchased` (text file, one domain per line) in the same directory
    - Writes `purchased_domains_collated.csv` with matching rows
    - Returns the output path or None if nothing was written
    """
    try:
        collated_path = os.path.join(directory, collated_filename)
        purchased_path = os.path.join(directory, purchased_list_filename)

        if not os.path.isfile(collated_path):
            print(f"Missing collated file: {collated_path}")
            return None
        if not os.path.isfile(purchased_path):
            print(f"Missing purchased list file: {purchased_path}")
            return None

        print(f"Reading collated data from: {collated_path}")
        df = pd.read_csv(collated_path)
        if "Name" not in df.columns:
            print("The collated CSV does not contain a 'Name' column.")
            return None

        print(f"Reading purchased domains from: {purchased_path}")
        purchased_domains: List[str] = load_purchased_domains(purchased_path)
        purchased_set: Set[str] = set(purchased_domains)
        if not purchased_set:
            print("No purchased domains found in the list. Nothing to filter.")
            return None

        # Prepare normalized name for matching
        df["__norm_name"] = df["Name"].astype(str).apply(normalize_domain)
        mask = df["__norm_name"].isin(purchased_set)
        filtered = df.loc[mask].drop(columns=["__norm_name"])  # drop helper column

        # Report missing ones (present in list but not in collated file)
        found_set = set(df.loc[mask, "Name"].astype(str).apply(normalize_domain))
        missing = sorted(purchased_set - found_set)
        if missing:
            print("Purchased domains not found in collated file:")
            for d in missing:
                print(f"- {d}")

        output_path = os.path.join(directory, "purchased_domains_collated.csv")
        filtered.to_csv(output_path, index=False)
        print(
            f"Wrote {len(filtered)} rows to: {output_path} (from {len(purchased_set)} purchased domains)"
        )
        return output_path

    except Exception as exc:
        print("Error while filtering purchased domains:")
        print(type(exc).__name__, str(exc))
        print(traceback.format_exc())
        return None


if __name__ == "__main__":
    filter_purchased_from_collated()


