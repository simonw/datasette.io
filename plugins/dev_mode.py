"""
Live-reload "dev mode" for working on the site locally, enabled with:

    datasette . -c datasette.yml -s plugins.datasette-io-blog.dev_mode 1

Every page polls /-/dev-mode and reloads itself when templates, static
files or blog posts change, or when the server restarts (--reload).
Changes to blog-content/*.md also rebuild the blog_posts table first.
"""

import asyncio
import hashlib
import importlib.util
import json
import traceback
import uuid
from pathlib import Path

from datasette import hookimpl
from datasette.utils.asgi import Response
from markupsafe import Markup

ROOT = Path(__file__).resolve().parent.parent
BLOG_DIR = ROOT / "blog-content"
WATCH_DIRS = [ROOT / "templates", ROOT / "static"]
POLL_INTERVAL_MS = 1000

# Changes every time the server process starts, so pages reload after
# a --reload restart picks up plugin or config changes
BOOT_ID = uuid.uuid4().hex

_state = {"blog_fingerprint": None, "error": None}
_lock = asyncio.Lock()


def dev_mode_enabled(datasette):
    config = datasette.plugin_config("datasette-io-blog") or {}
    return str(config.get("dev_mode", "")).lower() in ("1", "true", "on", "yes")


def fingerprint(paths):
    hasher = hashlib.sha1()
    for path in paths:
        for file in sorted(p for p in path.rglob("*") if p.is_file()):
            stat = file.stat()
            hasher.update(
                "{}:{}:{}\n".format(file, stat.st_mtime_ns, stat.st_size).encode()
            )
    return hasher.hexdigest()


def current_version():
    # Uses the blog fingerprint as of the last rebuild, not the files on
    # disk, so a page rendered from stale blog_posts rows still reloads
    # once the rebuild has happened
    return hashlib.sha1(
        "{}:{}:{}".format(
            BOOT_ID, fingerprint(WATCH_DIRS), _state["blog_fingerprint"]
        ).encode()
    ).hexdigest()


def load_build_blog_posts():
    spec = importlib.util.spec_from_file_location(
        "build_blog_posts", ROOT / "build_blog_posts.py"
    )
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


async def rebuild_blog_if_changed(datasette):
    async with _lock:
        blog_fingerprint = await asyncio.to_thread(fingerprint, [BLOG_DIR])
        if blog_fingerprint == _state["blog_fingerprint"]:
            return
        db_path = datasette.get_database("content").path
        try:
            build_blog_posts = load_build_blog_posts()
            await asyncio.to_thread(
                build_blog_posts.load_blog_posts, db_path=db_path, blog_dir=BLOG_DIR
            )
            _state["error"] = None
            print("dev_mode: rebuilt blog_posts from {}".format(BLOG_DIR))
        except Exception:
            _state["error"] = traceback.format_exc()
            print("dev_mode: failed to rebuild blog_posts\n" + _state["error"])
        _state["blog_fingerprint"] = blog_fingerprint


async def dev_mode_status(datasette):
    if not dev_mode_enabled(datasette):
        return Response.text("Not found", status=404)
    await rebuild_blog_if_changed(datasette)
    return Response.json(
        {
            "version": await asyncio.to_thread(current_version),
            "error": _state["error"],
        },
        headers={"cache-control": "no-store"},
    )


@hookimpl
def register_routes():
    return [(r"^/-/dev-mode$", dev_mode_status)]


@hookimpl
def startup(datasette):
    if not dev_mode_enabled(datasette):
        return

    # --reload only watches modules in sys.modules, which doesn't include
    # the plugins directory - so restart on edits to those files too
    try:
        import hupper

        if hupper.is_active():
            hupper.get_reloader().watch_files(
                [str(path) for path in (ROOT / "plugins").glob("*.py")]
            )
    except ImportError:
        pass

    async def inner():
        await rebuild_blog_if_changed(datasette)

    return inner


async def dev_mode_script(datasette):
    return DEV_MODE_JS % {
        "version": json.dumps(await asyncio.to_thread(current_version)),
        "url": json.dumps(datasette.urls.path("/-/dev-mode")),
        "interval": POLL_INTERVAL_MS,
    }


@hookimpl
def extra_body_script(datasette):
    # Covers Datasette's own pages, which extend its base.html
    if not dev_mode_enabled(datasette):
        return None

    async def inner():
        return await dev_mode_script(datasette)

    return inner


@hookimpl
def extra_template_vars(datasette):
    # The site's page_base.html and index.html don't render body_scripts,
    # so they include _dev_mode.html which outputs this instead
    if not dev_mode_enabled(datasette):
        return {}

    async def inner():
        return {"dev_mode_script": Markup(await dev_mode_script(datasette))}

    return inner


DEV_MODE_JS = """
(function () {
  var version = %(version)s;
  var banner = null;

  function showError(error) {
    if (!banner) {
      banner = document.createElement("pre");
      banner.style.cssText =
        "position:fixed;left:0;right:0;bottom:0;max-height:40vh;overflow:auto;" +
        "margin:0;padding:1em;z-index:99999;background:#3b0a0a;color:#ffd7d7;" +
        "font-size:12px;white-space:pre-wrap;border-top:3px solid #d33";
      document.body.appendChild(banner);
    }
    banner.textContent = "dev mode: blog rebuild failed\\n\\n" + error;
  }

  function hideError() {
    if (banner) {
      banner.remove();
      banner = null;
    }
  }

  async function poll() {
    try {
      var response = await fetch(%(url)s, { cache: "no-store" });
      var data = await response.json();
      if (data.error) {
        showError(data.error);
      } else {
        hideError();
      }
      if (data.version !== version) {
        location.reload();
        return;
      }
    } catch (e) {
      // Server is probably restarting - keep polling
    }
    setTimeout(poll, %(interval)d);
  }

  setTimeout(poll, %(interval)d);
})();
"""
