"""
Part 3: what tags best describe a user?

    uv run python part3_users.py

The handout's Part 3 is the spec. One piece is written for you, the piece that has to agree
with `WRITEUP.md` line for line: reading the 20 ratings out of your "My 20 ratings" slot and
adding you to the ratings table as a user of your own. Everything after that is yours.

You are added under userId 999999. Real userIds in `data/ratings.csv.gz` stop at 200,935, so
that number cannot be a real person's, and it is easy to pick out of a printout.

What this script must print, under the labels shown:

    == (1) my ratings ==
        How many ratings were read out of your slot, how many lines it could not read a
        rating from, and how many rows the ratings table has with yours in it. Twenty
        ratings is what the handout asks for; the script reports what it found and leaves
        the count to you.

    == (2) score(user, tag) ==
        Your `score(user, tag)` over the users you are looking at, your own row included.
        Write it in this file as

            score(ratings_df, tags_df, movies_df) -> DataFrame[userId, tag, score]

        one row per user-tag pair, higher score meaning the tag describes the user better.
        Print your own ten best tags, and the number of rows and distinct users it returned.
        What the score is, and why you started there, is yours and goes in `WRITEUP.md`.
"""

from __future__ import annotations

import re
from pathlib import Path

import pandas as pd

from load_data import load_all

REPO = Path(__file__).resolve().parent
WRITEUP = REPO / "WRITEUP.md"

ME = 999999                 # your userId: above every real one, so it collides with nobody
SLOT = "My 20 ratings"      # the WRITEUP.md slot your ratings are read from


def read_my_ratings(writeup: Path = WRITEUP) -> tuple[pd.DataFrame, int]:
    """Your ratings from the "My 20 ratings" slot in WRITEUP.md, as movieId and rating.

    The same rule the judge uses for "My ten movies": every line in that slot starts with a
    movieId. The rating is the last number on the line, so the title between them is for
    people and may hold anything, the year included. Bare lines only: a bulleted or a
    numbered list reads as no ratings at all, or reads the list numbers as movieIds.

        296, Pulp Fiction (1994), 4.5

    A line whose last number is not a rating between 0.5 and 5.0 is left out and counted,
    because the year in a title is a number too: `296, Pulp Fiction (1994)` with the rating
    forgotten would otherwise be read as a rating of 1994. So is the `XXXX` an unfilled slot
    holds, which is why this is safe to run before you have written anything.

    Returns the ratings and how many lines were left out."""
    rows, skipped, inside = [], 0, False
    for line in writeup.read_text(encoding="utf-8").splitlines():
        if line.startswith("**"):            # a bold label opens the next slot
            inside = SLOT in line
            continue
        if not inside or not re.match(r"\s*\d", line):
            continue
        numbers = re.findall(r"\d+(?:\.\d+)?", line)
        rating = float(numbers[-1]) if len(numbers) > 1 else 0.0
        if not 0.5 <= rating <= 5.0:
            skipped += 1
            continue
        rows.append({"movieId": int(numbers[0].split(".")[0]), "rating": rating})
    return pd.DataFrame(rows, columns=["movieId", "rating"]), skipped


def add_me(ratings: pd.DataFrame, mine: pd.DataFrame) -> pd.DataFrame:
    """Your ratings appended to everybody else's, under userId ME.

    The timestamp is the newest one in the data: you rated these after everyone else did."""
    if mine.empty:
        return ratings
    mine = mine.assign(userId=ME, timestamp=int(ratings["timestamp"].max()))
    return pd.concat([ratings, mine[ratings.columns]], ignore_index=True)


# ------------------------------------------------------------------- yours to write ---

MIN_TAGGERS = 10   # the student's rule: a movie carries a tag once this many distinct users applied it


def clean_tag(raw):
    """The student's Part 2 rule, reused: strings that differ only in case or in leading or
    trailing whitespace are one tag."""
    return raw.str.lower().str.strip()


K = 0.1   # the student's damping strength (5 in improvement 1, 0.1 in improvement 2)


def score(ratings: pd.DataFrame, tags: pd.DataFrame, movies: pd.DataFrame, users=(ME,), k=None, weighted=True):
    """The student's score(user, tag).

    First version: the average of the user's ratings on the movies that carry the tag, where a
    movie carries a tag once at least MIN_TAGGERS distinct users applied it (after clean_tag).
    Improvement 1: that average is damped toward the user's overall average rating, more
    strongly when few of their movies carry the tag:

        (sum of their ratings on those movies + K * their overall average) / (those movies + K)

    Improvement 2: each movie counts by how much the tag applies to it, relative to that
    movie: the distinct users who applied the tag to the movie, over the movie's distinct
    user-tag pairs. The weights replace the plain movie count:

        (sum of weight * rating + K * their overall average) / (sum of weight + K)

    `movies` is how many of the user's rated movies carry the tag, and `weight` is the sum of
    their weights.

    `k` defaults to K. weighted=False gives every movie a weight of 1, which is improvement 1
    again; section (5) uses k=5, weighted=False as the before.

    Computed for the users in `users` only: joining every rating to every tag its movie
    carries is about 74 million rows over the whole set."""
    k = K if k is None else k
    cleaned = tags.assign(tag=clean_tag(tags["tag"]))
    pairs = cleaned[["movieId", "userId", "tag"]].drop_duplicates()
    per_movie = pairs.groupby("movieId").size().rename("pairs")
    taggers = pairs.groupby(["movieId", "tag"]).size().rename("taggers").reset_index()
    carried = taggers[taggers["taggers"] >= MIN_TAGGERS].join(per_movie, on="movieId")
    carried["weight"] = carried["taggers"] / carried["pairs"] if weighted else 1.0
    theirs = ratings[ratings["userId"].isin(users)][["userId", "movieId", "rating"]]
    overall = theirs.groupby("userId")["rating"].mean().rename("overall")
    joined = theirs.merge(carried[["movieId", "tag", "weight"]], on="movieId")
    joined["weighted"] = joined["weight"] * joined["rating"]
    out = joined.groupby(["userId", "tag"]).agg(total=("weighted", "sum"), weight=("weight", "sum"),
                                                movies=("rating", "size")).reset_index()
    out = out.join(overall, on="userId")
    out["score"] = (out["total"] + k * out["overall"]) / (out["weight"] + k)
    return out[["userId", "tag", "score", "movies", "weight"]]


# The student's rules for judge/users.csv.
JUDGE_USERS = [ME, 11912, 23753, 66408, 73741, 132067, 144545, 158334, 167647, 189485]
LISTED = 10        # favorite and least favorite movies in each description
MOVIE_TAGS = 10    # most-used tags shown for each listed movie


def write_judge_users(ratings, tags, movies, out=REPO / "judge" / "users.csv"):
    """judge/users.csv: id, description, tags.

    description: the person's LISTED favorite and LISTED least favorite movies, each with the
    person's rating and the movie's MOVIE_TAGS most-used tags (cleaned, by applications). Ties
    in a person's ratings go to the movie more users rated; any tie left after that goes to the
    lower movieId.
    tags: every vocabulary tag that appears in the description, alphabetical, so the order
    says nothing about how common a tag is."""
    vocab = {w.strip() for w in (REPO / "judge" / "vocabulary.txt").read_text(encoding="utf-8").splitlines()
             if w.strip()}
    titles = movies.set_index("movieId")["title"]
    raters = ratings.groupby("movieId").size().rename("raters")
    cleaned = tags.assign(tag=clean_tag(tags["tag"]))
    counts = cleaned.groupby(["movieId", "tag"]).size().rename("n").reset_index()
    counts = counts.sort_values(["movieId", "n", "tag"], ascending=[True, False, True])
    top = counts.groupby("movieId").head(MOVIE_TAGS).groupby("movieId")["tag"].apply(list)

    rows = []
    for user in JUDGE_USERS:
        theirs = ratings[ratings["userId"] == user].join(raters, on="movieId")
        best = theirs.sort_values(["rating", "raters", "movieId"], ascending=[False, False, True]).head(LISTED)
        worst = theirs.sort_values(["rating", "raters", "movieId"], ascending=[True, False, True]).head(LISTED)

        def listing(frame):
            return "; ".join(f"{titles[m]} (rated {r}): {', '.join(top.get(m, []))}"
                             for m, r in zip(frame["movieId"], frame["rating"]))
        description = (f"Favorite movies, with this person's rating and each movie's most-used tags: "
                       f"{listing(best)}. Least favorite movies, the same way: {listing(worst)}.")
        shown = {t for m in pd.concat([best, worst])["movieId"] for t in top.get(m, [])}
        rows.append({"id": user, "description": description, "tags": "|".join(sorted(shown & vocab))})
    frame = pd.DataFrame(rows)
    frame.to_csv(out, index=False)
    return frame


def original_score(ratings, tags, movies, users):
    """The first version of score(user, tag), kept fixed so the tie rule below does not move
    when score() is improved: the user's average rating on the movies carrying the tag, where
    a movie carries a tag once at least 10 distinct users applied it."""
    cleaned = tags.assign(tag=clean_tag(tags["tag"]))
    taggers = cleaned.groupby(["movieId", "tag"])["userId"].nunique()
    carried = taggers[taggers >= 10].reset_index()[["movieId", "tag"]]
    raters = ratings.groupby("movieId").size().rename("raters")
    theirs = ratings[ratings["userId"].isin(users)][["userId", "movieId", "rating"]].join(raters, on="movieId")
    joined = theirs.merge(carried, on="movieId")
    return joined.groupby(["userId", "tag"]).agg(original=("rating", "mean"), raters=("raters", "sum")).reset_index()


def side_by_side(ratings, tags, movies, out=REPO / "judge_vs_score.csv", **opts):
    """score(user, tag) beside the judge's rating on every judged pair that has a score.

    The student's measure: per user, rank the pairs by score and by the judge's rating, best
    first, and take score rank minus judge rank. Ties, both rankings: the user's original
    average rating on the movies carrying the tag, higher first; then the total number of
    users who rated those movies, more first; then the tag, alphabetically."""
    judged = pd.read_csv(REPO / "judge" / "ratings_users.csv", keep_default_na=False)
    judged = judged.rename(columns={"id": "userId", "rating": "judge"})
    users = sorted(judged["userId"].unique())
    both = judged.merge(score(ratings, tags, movies, users=users, **opts), on=["userId", "tag"])
    both = both.merge(original_score(ratings, tags, movies, users), on=["userId", "tag"])
    for col, rank in (("score", "score_rank"), ("judge", "judge_rank")):
        both = both.sort_values(["userId", col, "original", "raters", "tag"],
                                ascending=[True, False, False, False, True])
        both[rank] = both.groupby("userId").cumcount() + 1
    both["difference"] = both["score_rank"] - both["judge_rank"]
    both = both.sort_values(["userId", "difference", "tag"], ascending=[True, False, True])
    cols = ["userId", "tag", "score", "movies", "judge", "score_rank", "judge_rank", "difference", "original", "raters"]
    both[cols].to_csv(out, index=False)
    return both[cols], len(judged)


def part3_users(ratings, tags, movies, links):
    print("== (1) my ratings ==")
    mine, skipped = read_my_ratings()
    print(f'{len(mine)} rating(s) read from the "{SLOT}" slot in WRITEUP.md.')
    if not len(mine):
        print(f'Nothing was read out of the "{SLOT}" slot. It is read one rating to a line, '
              f"with no bullets and no numbering: the movieId first, then the title, then "
              f"your rating, as in `296, Pulp Fiction (1994), 4.5`.")
    if skipped:
        print(f"{skipped} line(s) in that slot had no rating between 0.5 and 5.0 at the "
              f"end and were left out.")
    ratings = add_me(ratings, mine)
    if len(mine):
        print(f"{len(ratings):,} ratings with yours in, as userId {ME}.")
    else:
        print(f"{len(ratings):,} ratings, none of them yours yet.")

    print("== (2) score(user, tag) ==")
    scored = score(ratings, tags, movies)
    top = scored[scored["userId"] == ME].sort_values(["score", "tag"], ascending=[False, True]).head(10)
    print(f"  my ten best tags (userId {ME}), ties alphabetical:")
    for _, row in top.iterrows():
        print(f"    {row['score']:.2f}  from {row['movies']:>2} of my movies  {row['tag']}")
    print(f"  {len(scored):,} user-tag rows, {scored['userId'].nunique():,} distinct user(s)")

    print("== (3) judge/users.csv ==")
    judged = write_judge_users(ratings, tags, movies)
    per = judged["tags"].str.split("|").str.len()
    have = score(ratings, tags, movies, users=JUDGE_USERS)
    pairs = judged.assign(tag=judged["tags"].str.split("|")).explode("tag")[["id", "tag"]]
    covered = pairs.merge(have, left_on=["id", "tag"], right_on=["userId", "tag"]).shape[0]
    print(f"  wrote judge/users.csv: {len(judged)} people, {per.sum():,} tag ratings to ask for "
          f"({per.min()} to {per.max()} per person); {covered:,} of those pairs have a score(user, tag)")

    print("== (4) score() beside the judge ==")
    if (REPO / "judge" / "ratings_users.csv").exists():
        both, rated = side_by_side(ratings, tags, movies)
        print(f"  {rated:,} judged pairs, {len(both):,} with a score(user, tag); wrote judge_vs_score.csv")
        print("  every pair, all users together, sorted by difference (score rank - judge rank), largest first:")
        table = both.sort_values(["difference", "userId", "tag"], ascending=[False, True, True])
        print(table[["userId", "tag", "score", "movies", "judge", "score_rank", "judge_rank", "difference"]]
              .to_string(index=False, float_format="{:.2f}".format))
    else:
        print("  judge/ratings_users.csv is not here yet")

    print("== (5) before and after improvement 2 ==")
    print("  before: improvement 1, k = 5, every movie weighted 1; after: improvement 2, k = "
          f"{K}, weighted")
    versions = (("before", dict(k=5, weighted=False)), ("after", {}))
    for name, opts in versions:
        mine = score(ratings, tags, movies, **opts)
        top = mine.sort_values(["score", "tag"], ascending=[False, True]).head(10)
        print(f"  {name}: my ten best tags, ties alphabetical; {(top['movies'] == 1).sum()} of the "
              f"ten come from 1 of my movies")
        for _, row in top.iterrows():
            print(f"    {row['score']:.2f}  from {row['movies']:>2} of my movies  {row['tag']}")
    if (REPO / "judge" / "ratings_users.csv").exists():
        files = {"before": REPO / "judge_vs_score_v2.csv", "after": REPO / "judge_vs_score.csv"}
        for name, opts in versions:
            both, _ = side_by_side(ratings, tags, movies, out=files[name], **opts)
            gap = both["difference"].abs()
            print(f"  {name}: |score rank - judge rank| over {len(both):,} judged pairs, all users: "
                  f"mean {gap.mean():.2f}, median {gap.median():.1f}; wrote {files[name].name}")


if __name__ == "__main__":
    ratings, tags, movies, links = load_all()
    part3_users(ratings, tags, movies, links)
