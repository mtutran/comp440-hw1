"""User viewer.

Builds one self-contained HTML page about ten users: the student, plus nine drawn uniformly at
random from every user who rated anything, with seed 440. Per user it shows, as the student
specified:

  * the rating distribution: min, max, mean and standard deviation;
  * the ten top tags under `score(user, tag)` from `part3_users.py`;
  * the ten favorite movies (highest-rated) and the ten least favorite (lowest-rated), each with
    that movie's ten most-used tags.

Tags are cleaned by the student's rule (case and surrounding whitespace ignored), and a movie's
most-used tags are counted by applications. Ties in a user's ratings are broken by title, and
ties in scores and counts by tag, so the page is reproducible.

    uv run python user_results.py            # writes user_results.html
    uv run python user_results.py --text     # the same content as plain text
"""

import argparse
import html
from pathlib import Path

import numpy as np

from load_data import load_all
from part3_users import ME, add_me, clean_tag, read_my_ratings, score

REPO = Path(__file__).resolve().parent
SEED, OTHERS = 440, 9   # the student's rule: nine other users, drawn at random
MOVIES = 10             # favorite and least favorite movies shown per user
TAGS = 10               # tags shown per movie, and top score() tags per user

CSS = """body { font-family: Helvetica, Arial, sans-serif; margin: 20px; max-width: 1100px; }
table { border-collapse: collapse; margin-bottom: 12px; }
th, td { border: 1px solid #999999; padding: 4px 8px; text-align: left; vertical-align: top; }"""


def pick_users(ratings):
    """The student, then nine others drawn uniformly from every user who rated anything."""
    real = np.sort(ratings.loc[ratings["userId"] != ME, "userId"].unique())
    return [ME] + sorted(np.random.default_rng(SEED).choice(real, size=OTHERS, replace=False).tolist())


def build(ratings, tags, movies):
    users = pick_users(ratings)
    titles = movies.set_index("movieId")["title"]
    cleaned = tags.assign(tag=clean_tag(tags["tag"]))
    counts = cleaned.groupby(["movieId", "tag"]).size().rename("n").reset_index()
    counts = counts.sort_values(["movieId", "n", "tag"], ascending=[True, False, True])
    top_tags = counts.groupby("movieId").head(TAGS).groupby("movieId")["tag"].apply(list)
    scored = score(ratings, tags, movies, users=users)

    out = []
    for user in users:
        theirs = ratings[ratings["userId"] == user].assign(title=lambda d: d["movieId"].map(titles))
        best = theirs.sort_values(["rating", "title"], ascending=[False, True]).head(MOVIES)
        worst = theirs.sort_values(["rating", "title"], ascending=[True, True]).head(MOVIES)
        mine = scored[scored["userId"] == user].sort_values(["score", "tag"], ascending=[False, True])
        out.append({
            "user": user,
            "label": "you" if user == ME else "random draw",
            "stats": (len(theirs), theirs["rating"].min(), theirs["rating"].max(),
                      theirs["rating"].mean(), theirs["rating"].std()),
            "score": [(r.tag, f"{r.score:.2f}", r.movies) for r in mine.head(TAGS).itertuples()],
            "best": [(r.title, r.rating, ", ".join(top_tags.get(r.movieId, []))) for r in best.itertuples()],
            "worst": [(r.title, r.rating, ", ".join(top_tags.get(r.movieId, []))) for r in worst.itertuples()],
        })
    return out


def table_html(headers, rows):
    head = "".join("<th>%s</th>" % html.escape(h) for h in headers)
    body = "".join("<tr>%s</tr>" % "".join("<td>%s</td>" % html.escape(str(c)) for c in row)
                   for row in rows)
    return "<table><tr>%s</tr>%s</table>" % (head, body)


def stats_line(stats):
    n, lo, hi, mean, sd = stats
    return "%d ratings: min %.1f, max %.1f, mean %.2f, sd %.2f" % (n, lo, hi, mean, sd)


def render(users):
    body = ["<h1>User viewer</h1>"]
    for u in users:
        body += [
            "<h2>User %d (%s)</h2>" % (u["user"], u["label"]),
            "<p>%s</p>" % html.escape(stats_line(u["stats"])),
            "<h3>Top %d tags by score(user, tag)</h3>" % TAGS,
            table_html(["Tag", "score", "movies carrying it"], u["score"]),
            "<h3>%d favorite movies</h3>" % MOVIES,
            table_html(["Movie", "Rating", "Its %d most-used tags" % TAGS], u["best"]),
            "<h3>%d least favorite movies</h3>" % MOVIES,
            table_html(["Movie", "Rating", "Its %d most-used tags" % TAGS], u["worst"]),
        ]
    return ('<!doctype html>\n<html lang="en">\n<head>\n<meta charset="utf-8">\n'
            '<meta name="viewport" content="width=device-width, initial-scale=1">\n'
            "<title>User Viewer</title>\n<style>\n%s\n</style>\n</head>\n<body>\n%s\n</body>\n</html>\n"
            % (CSS, "\n".join(body)))


def render_text(users):
    out = ["User viewer", ""]
    for u in users:
        out += ["User %d (%s)" % (u["user"], u["label"]), "  " + stats_line(u["stats"]),
                "  Top %d tags by score(user, tag)" % TAGS]
        out += ["    %s  %s  (%d movies)" % (s, t, m) for t, s, m in u["score"]]
        for name, rows in (("favorite", u["best"]), ("least favorite", u["worst"])):
            out.append("  %d %s movies" % (MOVIES, name))
            out += ["    %.1f  %s\n          %s" % (r, t, tg) for t, r, tg in rows]
        out.append("")
    return "\n".join(out)


def main():
    parser = argparse.ArgumentParser(description="Look at ten users and their score() tags.")
    parser.add_argument("--out", default=str(REPO / "user_results.html"))
    parser.add_argument("--text", action="store_true")
    args = parser.parse_args()
    ratings, tags, movies, _ = load_all()
    mine, _ = read_my_ratings()
    users = build(add_me(ratings, mine), tags, movies)
    if args.text:
        print(render_text(users))
        return
    Path(args.out).write_text(render(users), encoding="utf-8")
    print("wrote %s" % args.out)


if __name__ == "__main__":
    main()
