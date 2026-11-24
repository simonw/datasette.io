# How to Build a Blog with Datasette, Fly.io, and GitHub Actions

A step-by-step guide for Mac users. By the end, you'll have a blog powered by Datasette where you just write markdown files, push to GitHub, and your site automatically rebuilds and deploys.

## What You're Building

The architecture is simple: markdown files on disk → a Python script builds a SQLite database → Datasette serves it with custom templates → Fly.io hosts it → GitHub Actions automates the whole thing.

---

## Part 1: Build and Deploy the Blog Manually

### Prerequisites

Make sure you have the following installed:

- **Homebrew**: https://brew.sh
- **uv**: `brew install uv`
- **Git**: `brew install git`
- **Fly.io CLI**: `brew install flyctl`
- **GitHub CLI**: `brew install gh`

You don't need to install Python separately — uv will manage that for you.

### Step 1: Create Your Project and Install Dependencies

```bash
mkdir my-blog
cd my-blog
git init
uv init
```

This creates a `pyproject.toml` and a `.python-version` file. Now add your dependencies:

```bash
uv add datasette datasette-template-sql datasette-publish-fly sqlite-utils markdown
```

uv automatically creates a `.venv`, installs Python if needed, resolves dependencies, and writes a `uv.lock` lockfile. Both `pyproject.toml` and `uv.lock` should be committed to git — they ensure your local environment and GitHub Actions use the exact same versions.

Verify installation:

```bash
uv run datasette --version
```

### Step 2: Create Your Directory Structure

```bash
mkdir -p daily
mkdir -p templates/pages/post
```

Your project will look like this:

```
my-blog/
├── daily/
│   ├── 2025-01-15-my-first-post.md
│   ├── 2025-01-16-hello-world.md
│   └── ...
├── templates/
│   ├── index.html
│   └── pages/
│       ├── home.html
│       └── post/
│           └── {slug}.html
├── build_database.py
├── pyproject.toml
├── uv.lock
└── .gitignore
```

### Step 3: Write Some Blog Posts

Blog posts are markdown files that live in topic folders (like `daily/`). The filename starts with a date in `YYYY-MM-DD-` format, followed by the slug. The first line is the title (starting with `#`), and everything after is the body.

Create your first post:

```bash
cat > daily/2025-01-15-my-first-post.md << 'EOF'
# My First Blog Post

This is my first post on my new Datasette-powered blog.
It's built from plain markdown files and served with SQLite.
Pretty neat!
EOF
```

Create a second post:

```bash
cat > daily/2025-01-16-hello-world.md << 'EOF'
# Hello World

Welcome to my blog. I built this using Datasette, Fly.io,
and GitHub Actions. Every time I push a new markdown file,
the site automatically rebuilds.
EOF
```

You can create as many topic folders as you want (e.g., `daily/`, `tech/`, `travel/`). The folder name becomes the "topic" field in the database.

**Note on slugs:** The slug is derived from the filename (minus the date prefix). If two files in different folders have the same slug (e.g., `daily/2025-01-15-intro.md` and `tech/2025-01-20-intro.md`), the slug is made unique by prepending the topic: `daily-intro` vs `tech-intro`. This way URLs always resolve to a single post.

### Step 4: Create the Build Script

This Python script reads all your markdown files and builds a SQLite database from them.

Create `build_database.py`:

```python
import pathlib
import re
import sqlite_utils
import markdown

root = pathlib.Path(__file__).parent.resolve()

DATE_PREFIX_RE = re.compile(r"^\d{4}-\d{2}-\d{2}-")


def parse_post(filepath, root):
    """Read a markdown file and return a post dict."""
    with open(filepath, "r", encoding="utf-8") as f:
        title = f.readline().lstrip("#").strip()
        body = f.read().strip()

    path = str(filepath.relative_to(root))
    topic = filepath.parent.name

    # Strip date prefix from filename to get the base slug
    stem = filepath.stem
    date_match = DATE_PREFIX_RE.match(stem)
    if date_match:
        date = date_match.group(0).rstrip("-")  # e.g. "2025-01-15"
        base_slug = stem[date_match.end():]      # e.g. "my-first-post"
    else:
        date = ""
        base_slug = stem

    slug = f"{topic}-{base_slug}" if topic else base_slug
    url = f"https://github.com/YOUR_USERNAME/YOUR_REPO/blob/main/{path}"
    html = markdown.markdown(body)

    return {
        "path": path,
        "slug": slug,
        "topic": topic,
        "title": title,
        "date": date,
        "url": url,
        "body": body,
        "html": html,
    }


def build_database(root):
    db = sqlite_utils.Database(root / "blog.db")
    table = db.table("posts", pk="path")

    # Sort files for deterministic build order
    md_files = sorted(root.glob("*/*.md"))

    posts = [parse_post(fp, root) for fp in md_files]

    if posts:
        table.insert_all(posts, replace=True)

    print(f"Built blog.db with {len(posts)} posts")


if __name__ == "__main__":
    build_database(root)
```

**Important:** Replace `YOUR_USERNAME/YOUR_REPO` with your actual GitHub username and repo name.

Build the database:

```bash
uv run python build_database.py
```

You should see: `Built blog.db with 2 posts`

### Step 5: Create the Templates

You need three template files.

**templates/index.html** — Redirects `/` to your blog homepage:

```html
<!DOCTYPE html>
<html>
<head>
  <meta http-equiv="refresh" content="0;url=/home">
</head>
<body>
  <a href="/home">Redirecting to blog...</a>
</body>
</html>
```

**templates/pages/home.html** — Your blog homepage:

```html
{% extends "base.html" %}

{% block content %}
<div style="max-width: 700px; margin: 2em auto; padding: 0 1em;">

  <h1>My Blog</h1>
  <p style="color: #666;">{{ sql("SELECT COUNT(*) FROM posts", database="blog")[0][0] }} posts so far.</p>

  <hr>

  {% for post in sql("SELECT title, slug, topic, date, html FROM posts ORDER BY date DESC, rowid DESC LIMIT 5", database="blog") %}
  <article style="margin-bottom: 3em;">

    <h2><a href="/post/{{ post.slug }}" style="text-decoration: none;">{{ post.title }}</a></h2>
    <p style="color: #666; font-size: 0.9em;">
      {% if post.date %}{{ post.date }} &middot; {% endif %}
      Topic: <strong>{{ post.topic }}</strong>
    </p>

    <div class="blog-content">
      {{ post.html | safe }}
    </div>

    <p><a href="/post/{{ post.slug }}">&rarr; Read more</a></p>
    <hr>

  </article>
  {% endfor %}

  <h2>All Posts by Topic</h2>
  {% for topic in sql("SELECT DISTINCT topic FROM posts ORDER BY topic", database="blog") %}
    <h3>{{ topic[0] }}</h3>
    <ul>
      {% for link in sql("SELECT title, slug, date FROM posts WHERE topic = ? ORDER BY date DESC", [topic[0]], database="blog") %}
      <li>
        {% if link.date %}<span style="color: #999;">{{ link.date }}</span> &ndash; {% endif %}
        <a href="/post/{{ link.slug }}">{{ link.title }}</a>
      </li>
      {% endfor %}
    </ul>
  {% endfor %}

</div>
{% endblock %}
```

**templates/pages/post/{slug}.html** — Individual post pages:

```html
{% extends "base.html" %}

{% block content %}
<div style="max-width: 700px; margin: 2em auto; padding: 0 1em;">

  {% for post in sql("SELECT title, topic, date, html FROM posts WHERE slug = ?", [slug], database="blog") %}
    <h1>{{ post.title }}</h1>
    <p style="color: #666; font-size: 0.9em;">
      {% if post.date %}{{ post.date }} &middot; {% endif %}
      Topic: <strong>{{ post.topic }}</strong>
    </p>
    <div class="blog-content">
      {{ post.html | safe }}
    </div>
  {% endfor %}

  <p><a href="/home">&larr; Back to all posts</a></p>

</div>
{% endblock %}
```

### Step 6: Test Locally

```bash
uv run datasette serve blog.db --template-dir templates/
```

Visit http://localhost:8001/ — it should redirect to `/home` and show your blog.

Click on a post title to see the individual post page. Use Ctrl+C to stop the server when you're done.

### Step 7: Deploy to Fly.io

First, log in to Fly.io (create an account at https://fly.io if you don't have one):

```bash
fly auth login
```

Create your app:

```bash
fly apps create your-app-name
```

Deploy:

```bash
uv run datasette publish fly blog.db \
  --app your-app-name \
  --template-dir templates/ \
  --install datasette-template-sql
```

Your blog is now live at `https://your-app-name.fly.dev/`

### Step 8: Create .gitignore

```bash
cat > .gitignore << 'EOF'
blog.db
__pycache__/
*.pyc
.DS_Store
.venv/
EOF
```

**Important:** Do NOT add `uv.lock` to `.gitignore`. The lockfile should be committed — it's what guarantees reproducible builds in CI.

---

## Part 2: Automate with GitHub Actions

Now we'll set it up so that every time you push a new markdown file to GitHub, the blog automatically rebuilds and deploys.

### Step 1: Create a GitHub Repository

Go to https://github.com/new and create a new repo, or use the CLI:

```bash
gh repo create your-repo-name --public --source=. --remote=origin
```

### Step 2: Get Your Fly.io API Token

```bash
fly tokens create deploy --app your-app-name
```

Copy the token that's printed.

### Step 3: Add the Token as a GitHub Secret

Go to your repo on GitHub: **Settings → Secrets and variables → Actions → New repository secret**

- Name: `FLY_API_TOKEN`
- Value: paste the token from the previous step

### Step 4: Create the GitHub Actions Workflow

```bash
mkdir -p .github/workflows
```

Create `.github/workflows/deploy.yml`:

```yaml
name: Build and Deploy Blog

on:
  push:
    branches: [main]
  workflow_dispatch:

jobs:
  deploy:
    runs-on: ubuntu-latest
    steps:
      - name: Checkout repo
        uses: actions/checkout@v4

      - name: Install uv
        uses: astral-sh/setup-uv@v4

      - name: Set up Python
        run: uv python install

      - name: Install dependencies
        run: uv sync

      - name: Build database
        run: uv run python build_database.py

      - name: Install flyctl
        uses: superfly/flyctl-actions/setup-flyctl@master

      - name: Deploy to Fly.io
        env:
          FLY_API_TOKEN: ${{ secrets.FLY_API_TOKEN }}
        run: |
          uv run datasette publish fly blog.db \
            --app your-app-name \
            --template-dir templates/ \
            --install datasette-template-sql
```

**Important:** Replace `your-app-name` with your actual Fly.io app name.

### Step 5: Push Everything

If you haven't already authenticated git with the right permissions for pushing workflow files:

```bash
gh auth login
```

Select **GitHub.com** and **HTTPS** when prompted.

Then push:

```bash
git add .
git commit -m "Initial blog setup with GitHub Actions"
git push -u origin main
```

### Step 6: Watch It Deploy

Go to `https://github.com/YOUR_USERNAME/YOUR_REPO/actions` to watch the workflow run. It should take 2-3 minutes.

---

## Daily Workflow

From now on, publishing a new blog post is this simple:

```bash
# Write a new post (use today's date in the filename)
cat > daily/2025-03-03-my-new-post.md << 'EOF'
# My New Post Title

Write your content here in markdown.
EOF

# Push it
git add daily/2025-03-03-my-new-post.md
git commit -m "New post: My New Post Title"
git push
```

GitHub Actions will automatically rebuild the database and deploy to Fly.io. Your new post will be live in about 2-3 minutes.

---

## Adding a New Dependency Later

If you ever need to add another Datasette plugin or Python package:

```bash
uv add datasette-cluster-map
```

This updates both `pyproject.toml` and `uv.lock`. Commit both files and push — GitHub Actions will pick up the new dependency automatically via `uv sync`.

---

## Troubleshooting

**"sql is undefined" error**: Make sure `datasette-template-sql` is in your `pyproject.toml` dependencies. Run `uv add datasette-template-sql` if it's missing.

**Templates not loading**: Make sure you're passing `--template-dir templates/` when running Datasette.

**Homepage shows default Datasette view instead of your blog**: The `templates/index.html` redirect only works as a template override (not in `pages/`). Make sure `templates/index.html` exists at the top level and `templates/pages/home.html` has your blog content.

**Port already in use**: Kill the existing process with `lsof -ti :8001 | xargs kill` or use a different port with `--port 8002`.

**GitHub Actions can't push workflow files**: Run `gh auth login` and re-authenticate with HTTPS to get the right permissions.

**Fly.io "app not found"**: You need to create the app first with `fly apps create your-app-name` before deploying.

**Deploy fails with "No such command 'fly'"**: Make sure `datasette-publish-fly` is in your `pyproject.toml` and that the workflow includes the "Install flyctl" step.

**Posts appear in wrong order**: Make sure your filenames use the `YYYY-MM-DD-` date prefix. The homepage sorts by the `date` field descending.

**Two posts with the same URL**: Slugs are made unique by prepending the topic folder name. If you have `daily/2025-01-15-intro.md` and `tech/2025-01-20-intro.md`, their URLs will be `/post/daily-intro` and `/post/tech-intro`.

**uv not found in GitHub Actions**: Make sure the workflow includes the `astral-sh/setup-uv@v4` step before any `uv` commands.

**"No Python version found"**: uv reads from `.python-version` in your repo. Make sure it was committed (it's created by `uv init`).
