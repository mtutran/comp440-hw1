# HW1 writeup

**Name:** Tu Tran
**Date:** 2026-09-18

Every placeholder below gets your answer, told to Claude or typed in here yourself. Every number
you give comes from a script in this repo; say which one. Claude may format tables and figures
here; the words are yours.

## Part 0. Predictions

Give these to Claude before any analysis runs. One sentence each, plus one sentence on why you
think so.

**(1) A movie you know well, and what its three most-used tags will be:** Coco (2017) - I think music, family, emotional

**(1) Why you think so:** Music and family because the main story is Miguel's conflict between music and family. Emotional because of the idea that the dead fade away when nobody remembers.

**(2) Out of every 100 people who rated movies here, how many ever added a tag?** 10 out of 100

**(2) Why you think so:** Because tagging requires more effort than rating (choosing words instead of just choose a number on a scale 1-5)

**(3) Can one person's tags take over a movie's tag list? Yes or no:** yes

**(3) Why you think so:** Because there are movies rated by very few people and one person can add many tags to a movie, so a person's tags can make up most of what appears.

## Part 1. Whose data is this?

Code: `part1_data.py`.

**My rule for cutting 32 million ratings to 5 million** (written before reading `data/make_compact.py`)**:** Drawing ratings at random. It preserves the characteristics of the full data, thus, we could make statistics inference about the full data population using the subset.

**One rule I considered and rejected, and why:** I also considered keeping users with the highest number of ratings. However, I rejected it because it would introduce selection bias and the resulting sample would contain only active users who are likely very different from low activity users.

**One interesting thing from `data/README.md`:** I found the number of tagging users interesting, most tagging users remain in the subset.

**How the script's rule differs from mine, and what each keeps that the other drops:** The script's rule is not random, it first filters based on the number of ratings per movies, then filter users based on how many they have among those movies, then randomly samples only among the remaining eligible non-tagging users. My rule will keep movies with lower rating counts, low activity users and the overall characteristics of the data, while the script's rule focused on active users' ratings on popular movies.

**First check. Which of Claude's numbers, the different route you took, and whether it matched** (one good target: 6 tags are the literal text `NA`, which pandas drops unless told not to)**:** I checked distinct users who applied a tag using shell tools. The numbers matched, however, they calculate different things (users who rated something and also tagged vs every distinct userId in the tags file, whether or not they rated).

**Second check. Which of Claude's numbers, the different route you took, and whether it matched:** I checked tag rows whose text is literally NA using shell tools and it matched.

## Part 2. What tags best describe a movie?

Code: `part2_tags.py`.

**My movie, and why I picked it:** I picked Coco because I like musical and family-related movies. I also feel like the movie is very heartwarming.

**Its most misleading tag in the count-ordered list, and why it misleads:** I think none of the tags is really misleading, but the most misleading one is probably death since the story's overall theme is not about being died, it is a warm and colorful continuation of life.

**What I learned about how MovieLens collects ratings and tags, from rating and tagging my movie myself (about 100 words):** When I hovered over the stars to rate, there are words to describe what that rating means (from awful to must watch). Once I rated, the date rated will appear, but it is also really easy to clear the rating. For adding tags, I can easily click to add a tag to my list and it allows me to choose whether I like it or neutral or dislike it about the movie, or even to say that the tag does not apply to the movie. I could also type any word and add it as a tag.

### Up close

One sentence on the figure written before you saw it and one after. The two tables are where the
details below come from. Say which script made them.

**The figure, when the tags and the ratings arrived. What I expected:** I expect both to rise at the start, then fall.
**The figure, what it shows:** The overall trends of both lines match my expectation, they both rise at first, then fall. The ratings line stays above the tag applications line most of the time. The tag line has a sudden spike at the beginning of 2021.

**Two interesting details I learned up close that the counts did not show:** 1. One person has multiple distinct tags for the movie (user 78213 made 234 tags on Coco, most of them are very detail, not many of them get in top 10). 2. There is not much variation in ratings among people with different tags.

**Anything up close that contradicted something I had already written down. Which one, what the data showed, and what you now think. Or "nothing yet":** My prediction about Coco's tags in part 0 has 2 tags in top 10 and 1 did not get in top 10. My prediction about whether one person's tags can take over a movie's tag list in part 0 also does not match the results shown as the person with multiple tags does not have a lot of tags in the top 10. Now I think the answer to Can one person's tags take over a movie's tag list? in part 0 would be no.

### My definition

**My `score(movie, tag)`** (one or two sentences, precise enough that a classmate could code it)**:** A tag should score higher than another on the same movie if many users use that tag for the movie. The score should count each user once.

**One definition I considered and rejected, and why:** One definition I considered is weighted by the user's rating of the movie since if they like the movie, they probably have tags that describe the movie better (less misleading tags). However, I rejected this since it will bias the results, people who like the movie may describe the movie very different from general audience or people who do not like the movie.

**Which tags I merged as the same tag, which I kept apart, and why:** I merged strings that differ only in case or in leading and trailing whitespace since they are the same concept, just different format. I kept everything else apart since they may reflect a slight difference in the user's intention. For example, music could describe an element of the movie, while musical refers to its genre. Similarly, someone might tag "day of the dead" as they do not know or do not associate the movie with mexican culture.

**Why my definition, in about 150 words. Name one thing it gains and one thing it loses:**

I chose to score a tag by the number of distinct users applied it since this avoids allowing one user to inflate a tag's score by applying it multiple times. However, it can not assess the quality of the tag, as most people might just apply tags that are already there instead of coming up with their own words.

### The judge

The two slots below are read by scripts, so write them as bare lines: one item to a line, the
movieId first, no bullets and no numbering. A movie line looks like `296, Pulp Fiction (1994)`.
An order line looks like `296: nonlinear, hit men, dark comedy, ...`, the tags best first.

**My ten movies:**

177765, Coco (2017)
260667, Encanto (2021)
134853, Inside Out (2015)
192283, Crazy Rich Asians (2018)
180985, The Greatest Showman (2017)
202439, Parasite (2019)
72998, Avatar (2009)
152081, Zootopia (2016)
76093, How to Train Your Dragon (2010)
111659, Maleficent (2014)

**My own order of the ten most-used tags, written before looking at any data: my movie from step 1, then my nine others from step 4:**

177765: family, heartwarming, music, afterlife, colorful, Pixar, animation, Dia de los Muertos, mexico, death
260667: family, family relationships, magic, musical, colorful, shapeshifting, Animation, spanish language, colombia, simple story
134853: introspective, imaginative, psychology, emotions, coming of age, childhood, emotional, creative, bittersweet, Pixar
192283: romantic comedy, romcom, romance, wealth, visually appealing, Asian culture, Asian, based on a book, Awkwafina, Chinese culture
180985: diversity, Positive message, circus, music, musical, great soundtrack, visually stunning, colorful, based on a true story, Hugh Jackman
202439: social satire, class themes, social commentary, intelligent, dark comedy, black comedy, twists & turns, intense, korean, great writing
72998: sci-fi, futuristic, aliens, environmental, thought-provoking, beautiful scenery, visually stunning, graphic design, James Cameron, predictable
152081: xenophobia, racism, friendship, social commentary, cute, funny, tolerance, attention to detail, creative, visually stunning
76093: friendship, adventure, dragons, depth of emotion, cute, funny, fantasy, vikings, predictable, animation
111659: non-romantic love, twist ending, sleeping beauty, fairy tale, fantasy, visual effects, strong female lead, dragon, Disney, Angelina Jolie

**One criterion I considered for the judge and rejected, and why** (the one I used is in `judge/criterion.md`)**:** I considered weighted by how relevant the tag is based on the movie's genre. However, I rejected it because this would make the whole list describes the movie's genre.

**Agreement. The number `agreement.py` gives for your `score()`, for popularity and for your own order, and which of the three came closest to the judge:** score() and popularity are both 2.35 while my own order is 2.9 which is the closest to the judge. However, both score() and popularity are compared over 109 movies and 12 tags compared on the middle one while mine is only over 10 movies and 6 tags.

**How the judge skill is built: the files it is made of and what each one does (about 150 words):**

SKILL.md makes /judge a command, using the description to know when the skill applies and point to README.md which explains how to run the judge and what happends at each step. judge.py is the code that implements those steps. It builds the prompt, send to CLAUDE and writes ratings back to CSV. system.md is the system prompt sent with every request. criterion.md has the paragraph that describes the criterion for the judge to apply. The inputs are movies.csv and vocabulary.txt which include all movies and tags that the judge can rate.

**What happens when I run `/judge`, from the first check to the CSV (about 150 words):**

judge.py first checks that movies.csv exists and ratings_movies.csv is not already there unless I passed --force. It then reads criterion.md, system.md and movies.csv, adding my movies from WRITEUP.md. It rates the movies and writes the ratings to ratings_movies.csv.

**Why a skill: what a skill like this gives you that a script or a prompt alone does not, and where you would use one next (about 100 words):**

A script alone runs the steps but would not allow me to ask for explanation, a prompt alone would require me to have one conversation per movie. The skill helped me run the same steps efficiently and explain things (noted things) along the way. I would use one like this in other homeworks for this course.

### The viewer and the disagreements

**One thing `movie_results.html` showed me that was useful, and one thing about it that got in my way:** If the purpose is only comparing score() with the judge's ratings, I think it's helpful to have the definition of disagreement at the beginning and ranking of them right on top of each other. It might be better if we do not include all data on tags on this movie which includes each user that applied that tag for the movie and the data they applied.

Then three improvements. For each: what the page would not let you see, what you had Claude
change, and what the changed page shows that the first draft did not.

**Improvement 1:** The first draft would require me to scroll through many lines of raw data before reaching the next useful data. I had you remove the tags on this movie section. The page now has rankings for 4 methods and the biggest disagrement table for each movie, which is cleaner to look at.

**Improvement 2:** Before, I could not see disagreements across movies since they are in different tables. I ask you to create a table with all disagreements. Now I see all disagreements in one table.

**Improvement 3:** Before, the table allows me to see all disagreements but I can not see the patterns clearly. I ask you to add the difference column and sorted the table by that. Now I can see where the largest disagrements are.

Then the three disagreements. A disagreement is a movie and a tag where your `score()` and the
judge are furthest apart. For each: the movie and the tag, where your `score()` put it and where
the judge put it, and what you think accounts for the gap.

**Disagreement 1:** Avatar (2009) — 7,342 ratings, love story. score() rank is 46 while Judge rank is 5. I think the gap accounts for how specific that tag is for the movie's story. Love story is the main thread of the plot (relationship between Jake and Neytiri), thus, it would rank high for the judge. However, most people would use more simple, obvious tags like sci-fi, which is why it ranks low for the score().

**Disagreement 2:** Parasite (2019) — 2,790 ratings, surprise ending. score() rank is 37 while Judge rank is 9. I think the gap also accounts for how the tag describes the plot. The twist at the end is central to the story, which fits the judge criterion. But most people would use a more general tag like dark comedy (to describe the genre of the movie).

**Disagreement 3:** Coco (2017) — 2,094 ratings, memory. score() rank is 22 while Judge rank is 2. I think the gap accounts for the same thing as the above two disagreements. Coco's story is built around being remembered by your family across generations, thus, it matches the judge's criterion and ranks very high (2). However, most people would use more generic tags like music or pixar to describe the movie.

**One other high-level pattern in the results, and what you think is behind it:** The other pattern is that score() ranks generic mood, genre, studio higher while the judge ranks them lower. (Examples: Avatar (2009) — 7,342 ratings - predictable - score() rank 6 - judge rank 49, Parasite (2019) — 2,790 ratings - suspenseful - score() rank 7 - judge rank 34, Inside Out (2015) — 4,353 ratings - pixar - score() rank 2 - judge rank 22) Tags like generic mood descriptor, studio or genre are things that anyone will agree on, thus, score() will rank them high due to the number of people applied them. The judge's criterion requires user to use a tag that is specific to the movie, thus, requires more effort.

## Predictions revisited

**Which of my three predictions were wrong, and what I make of each miss:** The first wrong prediction is my tag emotional for Coco, it is not in the top 10 most popular tags of the movie. I think this is because of the word I use, it should be heartwarming instead of emotional. The second wrong prediction is that I predict 10 out of 100 people rated will tag, I think the difference might come from how the subset of data is created in this assignment (filter to active users and popular movies). My last wrong prediction is that a person's tag can make up most of what appears, I think this is because the movie I chose has a good amount of ratings, so it did not happen that way.

## Part 3. What tags best describe a user?

Code: `part3_users.py`.

The slot below is read by a script, so write it as bare lines: one rating to a line, no bullets
and no numbering, the movieId first and the rating last, as in `296, Pulp Fiction (1994), 4.5`.

**My 20 ratings:**

177765, Coco (2017), 4.0
260667, Encanto (2021), 3.5
134853, Inside Out (2015), 4.0
192283, Crazy Rich Asians (2018), 3.0
180985, The Greatest Showman (2017), 3.5
202439, Parasite (2019), 4.5
72998, Avatar (2009), 3.5
152081, Zootopia (2016), 3.5
76093, How to Train Your Dragon (2010), 4.0
111659, Maleficent (2014), 3.0
81847, Tangled (2010), 3.5
166461, Moana (2016), 3.5
1907, Mulan (1998), 4.0
2081, Little Mermaid, The (1989), 2.5
164909, La La Land (2016), 3.5
5816, Harry Potter and the Chamber of Secrets (2002), 4.5
106696, Frozen (2013), 3.0
168366, Beauty and the Beast (2017), 3.5
59784, Kung Fu Panda (2008), 3.5
2355, Bug's Life, A (1998), 3.5

**My `score(user, tag)`, in a sentence, and why I started there (about 100 words):**

The score shows the average ratings of the user for movies that has at least 10 distinct users applied the tag. I started with this because this is an easy way to estimate how much the user likes that tag.

**What my score says about me: my top ten tags, and whether they describe my taste (about 100 words):**

Top ten from `part3_users.py` section (2), first version, all scored 4.50 from 1 of my movies each: alan rickman, allegorical, anticapitalist, black comedy, boarding school, bong joon-ho, capitalism, cinematography, class divide, class struggle.

It seems like my top 10 are mostly from the same movie - Parasite, which I rate the highest among the 20 movies. They do not necessarily describe my taste, this is because of the small sample size with selection bias and maybe because the threshold of at least 10 distinct users applied the tag is too low.

**What my user viewer shows and why I chose that (about 100 words):**

My user viewer shows their rating stats, top 10 tags by score, 10 favorite and 10 least favorite movies. I chose these so that I could see whether their top tags fit their taste.

**What I put in the description column for a person, and why (about 150 words):**

XXXX

**My criterion for people: what it asks the judge to do that the movie criterion did not (about 60 words):**

XXXX

**The user-tag pairs I chose to judge, how many, and why those (about 100 words):**

XXXX

**Improvement 1: what I changed in the scoring function, what the judge and the viewer showed before and after (about 150 words):**

I changed score from a normal average to a shrunken average, so a tag appears in only one movie would be pulled toward the user's average. Before, top 10 are mostly dominated by tags from a single highest rating movie. After, more common tags rise to the top. The judege comparison also fixed some disagreements. For example, "black comedy" went from a score rank of 1 to 4 against a judge rank of 9 which makes its difference went from −8 to −5.

**Improvement 2: the same (about 150 words):**

I changed the score so that each movie counts toward a tag based on how much the tag is applied on that movie and lowered k to 0.1. The judge's mean gap did not change much, only 0.17 (changed from 9.18 to 9.01 from part3_users.py section (5)). part3_users.py section (5) shows that my top ten went from having seven single movie tag to nine since the weighting only measures how much a tag applied to a movie, not how many movies support the tag. My predictions was wrong, cause the sum of weights measures how much a tag applies to a movie, not how many movies support it. The gaps did not change much (0.17), so it just reorder the tags, not actually improving.

## Part 4. Working with Claude

Give these to Claude the way you gave it the rest. Graded on the catch and the candor, not on
making Claude look good or bad.

**A moment where Claude was wrong or overconfident, how you caught it, and where it
happened. Name the part and the step, so the moment can be found:** XXXX

**One call where you overrode Claude, and why:** XXXX

**What you would hand to Claude sooner next time:** XXXX

**Did Claude name the misleading tag in Part 2 step 1 before you did? What happened:** XXXX

**The figure. Would asking Claude "what does this show?" have produced your sentence, and what
would have been missing from it:** XXXX

**Hours spent:** XXXX

**Anyone who helped you, or "no one":** XXXX
