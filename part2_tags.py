"""
Part 2: what tags best describe a movie?

    uv run python part2_tags.py

Steps 1 to 4 of the handout's Part 2 live here, plus the scores and the rankings that steps 5
and 6 need. The judge itself runs through `/judge`, and its answer is read through
`agreement.py` and `results_viewer.py`. What this script must print, under the labels shown,
and what it must write:

    == (1) the obvious answer ==
        Your chosen movie's title, its rating count and its tag-application count, then
        every tag applied to it with how many times it was applied, most-applied first.
        Pick a movie with at least 500 ratings and 30 tag applications. The most misleading
        entry in that list is your sentence in `WRITEUP.md`, not this script's.

    == (2) up close ==
        The numbers behind the one required figure and the two tables, so that everything
        shown here has printed output a reader can check it against. Write, to `figures/`:

            figures/part2_when.png          when the tags arrived: tag applications over
                                            time, with the movie's ratings over time behind
                                            them.

        The figure has labeled axes and a caption naming the question it answers. Claude
        may draw and label it; the sentence in `WRITEUP.md` about what it shows is yours.

        Then two tables, each printed under its own label:

            who added each tag              the movie's heaviest taggers, how many tag
                                            applications each made, and what share of the
                                            movie's applications that is.
            how the taggers rated it        for each of the movie's top tags, how the
                                            people who applied it rated the movie, beside
                                            how everyone else rated it.

        Claude prints the tables and says what the columns are. What they show is your two
        interesting details in `WRITEUP.md`, not this script's.

    == (3) my definition ==
        Your `score` over the whole set. Write it in this file as

            score(tags_df, ratings_df, movies_df) -> DataFrame[movieId, tag, score]

        one row per movie-tag pair, higher score meaning the tag describes the movie better.
        Print its top 15 rows for your chosen movie, and the number of rows and distinct
        movies it returned over the whole set. Families you could use, none of them
        preferred: distinct users who applied the tag; a rarity weight, the count times how
        few movies carry the tag; a damped version of either; something of your own. Whatever
        you choose, `WRITEUP.md` gets what you chose, what you rejected, and why.

    == (4) cleaning ==
        Whatever cleaning your `score()` does, and its size: how many raw tag strings went
        in, how many distinct tags came out, and the five mergers that absorbed the most
        applications. If you clean nothing, print that and say why in `WRITEUP.md`.
        Merging `Sci-Fi`, `sci-fi` and `scifi` is a decision, and so is not merging them.

    == (5) scores.csv ==
        `scores.csv` in the repo root, columns `movieId,tag,score`, holding a score for every
        movie and tag the judge will be asked about. That is two sets put together:

            every movie and tag in `judge/movies.csv`, which has one row per movie and a
            `tags` column of tags joined by `|`;
            plus, for each of the ten movies in your "My ten movies" slot, every tag from
            `judge/vocabulary.txt` that appears on it, matched after stripping and
            lowercasing, which is the same rule `judge/movies.csv` used.

        The second set matters because the judge adds your ten movies to its list, and
        `agreement.py` compares exactly what the two files share: a tag you never scored is
        dropped without a number. Print how many were asked for and how many you wrote.

    == (6) the four rankings ==
        For each of the ten movies in your "My ten movies" slot, four rankings of the same tags,
        printed one after another and never in one table:

            the counts: the ten most-used tags, by how many times each was applied;
            your own order, from the `WRITEUP.md` slot you filled before seeing any data;
            the judge's order, from `judge/ratings_movies.csv`;
            your `score()`'s order.

        Print each list under its own heading, best first. `results_viewer.py` builds the same
        four lists as a page you can read. Which tag is the artifact, and what the
        disagreements mean, is your paragraph in `WRITEUP.md`.
"""

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import pandas as pd

from load_data import REPO, load_all

FIGURES = REPO / "figures"

MY_MOVIE = 177765   # Coco (2017), the student's claimed movie


def part2_tags(ratings, tags, movies, links):
    print("== (1) the obvious answer ==")
    title = movies.set_index("movieId").loc[MY_MOVIE, "title"]
    mine = tags[tags["movieId"] == MY_MOVIE]
    print(f"  {title}: {(ratings['movieId'] == MY_MOVIE).sum():,} ratings, {len(mine):,} tag applications")
    print("  (raw tag strings, exactly as typed: `Cult classic` and `cult classic` are two rows)")
    counts = mine["tag"].value_counts()
    print(f"  {len(counts):,} distinct tag strings, most-applied first:")
    for tag, n in counts.items():
        print(f"    {n:>4}  {tag}")

    print("== (2) up close ==")
    when_figure(ratings, mine, title)
    who_tagged(mine)
    taggers_ratings(ratings, mine)

    print("== (3) my definition ==")
    scored = score(tags, ratings, movies)
    print(f"  top 15 for {title}:")
    top = scored[scored["movieId"] == MY_MOVIE].sort_values(["score", "tag"], ascending=[False, True]).head(15)
    for _, row in top.iterrows():
        print(f"    {row['score']:>4}  {row['tag']}")
    print(f"  over the whole set: {len(scored):,} movie-tag rows, {scored['movieId'].nunique():,} distinct movies")

    print("== (4) cleaning ==")
    cleaning_report(tags)

    print("== (5) scores.csv ==")

    print("== (6) the four rankings ==")


def clean_tag(raw):
    """The student's rule: strings that differ only in case, or in leading or trailing
    whitespace, are one tag. So lowercase, then strip whitespace at both ends (str.strip also
    removes the non-breaking space, U+00A0)."""
    return raw.str.lower().str.strip()


def score(tags_df, ratings_df, movies_df):
    """The student's score(movie, tag): the number of distinct users who applied the tag to
    the movie, after clean_tag. Each user counts once."""
    cleaned = tags_df.assign(tag=clean_tag(tags_df["tag"]))
    out = cleaned.groupby(["movieId", "tag"])["userId"].nunique().rename("score").reset_index()
    return out[["movieId", "tag", "score"]]


def cleaning_report(tags, top=5):
    """How many raw strings went in, how many tags came out, and the biggest mergers."""
    raw = tags["tag"]
    clean = clean_tag(raw)
    print(f"  raw tag strings in: {raw.nunique():,}   distinct tags out: {clean.nunique():,}")
    variants = tags.assign(clean=clean).groupby(["clean", "tag"]).size().rename("applications").reset_index()
    groups = variants.groupby("clean")["applications"].agg(["size", "sum", "max"])
    groups = groups[groups["size"] > 1]
    groups["absorbed"] = groups["sum"] - groups["max"]
    print(f"  tags formed from more than one raw string: {len(groups):,}")
    print(f"  the {top} mergers that absorbed the most applications "
          "(absorbed = applications not in the merged tag's most-used raw string):")
    for tag, g in groups.sort_values(["absorbed", "sum"], ascending=False).head(top).iterrows():
        parts = variants[variants["clean"] == tag].sort_values("applications", ascending=False)
        shown = ", ".join(f"{t!r} {n:,}" for t, n in zip(parts["tag"], parts["applications"]))
        print(f"    {tag!r}: {g['sum']:,} applications, {g['absorbed']:,} absorbed  <- {shown}")


def who_tagged(mine, top=15):
    """The movie's heaviest taggers: applications each made and their share of the movie's."""
    per_user = mine.groupby("userId").agg(applications=("tag", "size"), distinct_tags=("tag", "nunique"))
    per_user = per_user.sort_values(["applications", "distinct_tags"], ascending=False)
    per_user["share"] = per_user["applications"] / len(mine)
    per_user["cumulative share"] = per_user["share"].cumsum()
    print(f"  who added each tag: {len(per_user):,} users tagged this movie; the {top} heaviest")
    table = per_user.head(top).copy()
    table["share"] = table["share"].map("{:.1%}".format)
    table["cumulative share"] = table["cumulative share"].map("{:.1%}".format)
    print(table.to_string(line_width=100))


def taggers_ratings(ratings, mine, top=10):
    """For each of the movie's top tags: how its appliers rated the movie, beside everyone else."""
    rated = ratings[ratings["movieId"] == MY_MOVIE].set_index("userId")["rating"]
    rows = []
    for tag in mine["tag"].value_counts().head(top).index:
        appliers = set(mine.loc[mine["tag"] == tag, "userId"])
        inside = rated[rated.index.isin(appliers)]
        outside = rated[~rated.index.isin(appliers)]
        rows.append({"tag": tag, "appliers": len(appliers), "appliers who rated": len(inside),
                     "their mean rating": inside.mean(), "everyone else rated": len(outside),
                     "everyone else mean": outside.mean()})
    table = pd.DataFrame(rows).set_index("tag")
    print(f"  how the taggers rated it: the {top} most-applied tags")
    print(table.to_string(float_format="{:.2f}".format, line_width=120))


def when_figure(ratings, mine, title):
    """figures/part2_when.png: tag applications and ratings per month for the chosen movie."""
    def per_month(df):
        return pd.to_datetime(df["timestamp"], unit="s").dt.to_period("M").value_counts().sort_index()
    rated = per_month(ratings[ratings["movieId"] == MY_MOVIE])
    tagged = per_month(mine)
    months = pd.period_range(min(rated.index.min(), tagged.index.min()),
                             max(rated.index.max(), tagged.index.max()), freq="M")
    monthly = pd.DataFrame({"ratings": rated.reindex(months, fill_value=0),
                            "tag applications": tagged.reindex(months, fill_value=0)})
    print("  figure numbers: ratings and tag applications per month")
    print(monthly.to_string(line_width=100))

    x = monthly.index.to_timestamp()
    fig, ax = plt.subplots(figsize=(10, 4.5))
    ax.plot(x, monthly["ratings"], color="#eb6834", linewidth=2, alpha=0.55, label="ratings", zorder=1)
    ax.plot(x, monthly["tag applications"], color="#2a78d6", linewidth=2, label="tag applications", zorder=2)
    ax.set_xlabel("month")
    ax.set_ylabel("count per month")
    ax.set_title(f"When did the tags and the ratings for {title} arrive?", loc="left")
    ax.legend(frameon=False)
    ax.grid(axis="y", color="#e5e4df", linewidth=0.8)
    ax.spines[["top", "right"]].set_visible(False)
    fig.text(0.01, 0.01, "Tag applications (blue) and ratings (orange, behind) per calendar month, "
             "from this movie's rows in data/tags.csv.gz and data/ratings.csv.gz.",
             fontsize=8, color="#52514e")
    fig.tight_layout(rect=(0, 0.04, 1, 1))
    FIGURES.mkdir(exist_ok=True)
    fig.savefig(FIGURES / "part2_when.png", dpi=150)
    plt.close(fig)
    print("  wrote figures/part2_when.png")


if __name__ == "__main__":
    ratings, tags, movies, links = load_all()
    part2_tags(ratings, tags, movies, links)
