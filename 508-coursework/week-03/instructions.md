# Week 3

Before our next class, Wednesday 23 September.

## Tasks

Learn to write and understand Markdown, so you can write a skill in Markdown.
Then build a small database from historical material, and write one skill that
turns it into an agent of your own invention.

Do everything through opencode, and make it explain what it is doing.

## Challenges

### 1. Learn Markdown

Learn to write and understand Markdown — headings, lists, links. Enough to
write your own skill file.

### 2. Build a small database

Choose historical material you care about, and have opencode pull the facts
into rows — an `id`, a date, the fact, names and places, and where each row
comes from. Store them in an SQLite file; check a few rows back against the
original. Any size works; bigger is better.

Examples you can read and copy:

- `skills/extraction/SKILL.md` — how to turn a page into rows and a database
- `demo-history-db/` — one page from 1908, its rows, and its database
- `demo-buildings/` — six Lingnan buildings, each with a photo, a description
  and a row in the database

### 3. Write your skill

One Markdown file. It says what the database is, and how the agent should
behave: how it uses the data, how much of it, the tone it speaks in. These are
your choices — make the agent you want. Give it a name.

### 4. Try it

Ask your agent questions, and see whether it does what you wanted.

## Bring to class

A five-minute demo of your named agent — in the demo you must be able to
prove:

- **It really uses your data** — what it says could only come from the
  database, not from what the model already knew.
- **Everything it says is grounded** — whenever you ask, it can point to where
  it comes from.

Your database and skill go in your fork; keep API keys and large files out of
Git. Unresolved questions go to `questions.md`.
