"""
Part 1: whose data is this?

    uv run python part1_data.py

Write your own cut rule and your two checks before you run anything here. Doing it in that
order is what Part 1 is asking for. What this script must print, under the labels shown:

    == (a) how much ==
        Rows in each of the four files, distinct users, distinct movies, and the share of
        all 32,000,204 MovieLens ratings this set holds.

    == (b) spread ==
        Ratings per user and ratings per movie: median, minimum and maximum of each. Tag
        applications per user and per movie: the same three. How many of the users who
        rated anything ever applied a tag, as a count and as a share.

    == (c) top tags, two ways ==
        The 20 most-used tags by number of applications, and the 20 most-used tags by number
        of distinct users who applied them. Print the two lists one after the other, with
        both numbers on every row, so you can see where a tag's two ranks differ.

    == (d) two checks ==
        Two claims from (a) to (c) re-derived by a route that does not reuse the code that
        produced them, printed with both numbers side by side and the word MATCH or DIFFER.
        Targets that exist in this data: the share of all 32M ratings the set holds
        (`data/README.md` says 15.6 percent); the number of distinct users who applied a
        tag (14,019); the rating count of the least-rated kept movie (83); the 6 tag
        rows whose text is literally `NA`, which vanish if a reader is built without
        `keep_default_na=False`.

No figures are required in Part 1. `WRITEUP.md` takes one interesting thing from
`data/README.md`, your own cut rule and the rule you rejected, how `data/make_compact.py`'s
rule differs from yours, and your two checks.
"""

import subprocess

import pandas as pd

from load_data import REPO, load_all

FULL_RATINGS = 32_000_204   # rows in the full MovieLens 32M ratings.csv, from data/README.md


def spread(counts, label):
    """Median, minimum and maximum of one per-user or per-movie count."""
    print(f"  {label:<28} median {counts.median():>8,.0f}   min {counts.min():>7,}   max {counts.max():>8,}")


def part1_data(ratings, tags, movies, links):
    print("== (a) how much ==")
    for name, df in [("ratings", ratings), ("tags", tags), ("movies", movies), ("links", links)]:
        print(f"  {name:<8} {len(df):>10,} rows")
    print(f"  distinct users (in ratings)   {ratings['userId'].nunique():>8,}")
    print(f"  distinct movies (in ratings)  {ratings['movieId'].nunique():>8,}")
    print(f"  share of all {FULL_RATINGS:,} MovieLens ratings: {len(ratings) / FULL_RATINGS:.1%}")

    print("== (b) spread ==")
    spread(ratings.groupby("userId").size(), "ratings per user")
    spread(ratings.groupby("movieId").size(), "ratings per movie")
    spread(tags.groupby("userId").size(), "tag applications per user")
    spread(tags.groupby("movieId").size(), "tag applications per movie")
    raters = ratings["userId"].unique()
    tagging_raters = pd.Series(raters).isin(tags["userId"]).sum()
    print(f"  users who rated anything: {len(raters):,}; of those, ever applied a tag: "
          f"{tagging_raters:,} ({tagging_raters / len(raters):.1%})")

    print("== (c) top tags, two ways ==")
    print("  (raw tag strings, exactly as typed: `Cult classic` and `cult classic` are two rows)")
    per_tag = tags.groupby("tag").agg(applications=("userId", "size"), users=("userId", "nunique"))
    for col in ["applications", "users"]:
        print(f"  top 20 by {col}:")
        top = per_tag.sort_values([col, "tag"], ascending=[False, True]).head(20)
        for rank, (tag, row) in enumerate(top.iterrows(), 1):
            print(f"    {rank:>2}. {tag:<30} applications {row['applications']:>6,}   users {row['users']:>5,}")

    print("== (d) two checks ==")
    # The student's route for both checks: shell tools on the raw gzipped file, no pandas.
    shell_taggers = int(shell("gzip -dc data/tags.csv.gz | tail -n +2 | cut -d, -f1 | sort -u | wc -l"))
    report("distinct users who applied a tag", tagging_raters, shell_taggers)
    pandas_na = int((tags["tag"] == "NA").sum())
    shell_na = int(shell(r"gzip -dc data/tags.csv.gz | grep -cE '^[0-9]+,[0-9]+,NA,[0-9]+'$'\r''?$'"))
    report("tag rows whose text is literally NA", pandas_na, shell_na)


def shell(cmd):
    """Run one shell pipeline from the repo root and return what it prints."""
    return subprocess.run(cmd, shell=True, cwd=REPO, capture_output=True, text=True, check=True).stdout.strip()


def report(claim, script_number, check_number):
    verdict = "MATCH" if script_number == check_number else "DIFFER"
    print(f"  {claim:<38} script {script_number:>8,}   shell {check_number:>8,}   {verdict}")


if __name__ == "__main__":
    ratings, tags, movies, links = load_all()
    part1_data(ratings, tags, movies, links)
