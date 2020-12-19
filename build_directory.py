import click
from github_to_sqlite.cli import (
    releases as github_to_sqlite_releases,
    repos as github_to_sqlite_repos,
)
from python_graphql_client import GraphqlClient
import sqlite_utils


REPO_FIELDS = """
        id
        nameWithOwner
        openGraphImageUrl
        usesCustomOpenGraphImage
        defaultBranchRef {
          target {
            oid
          }
        }
        repositoryTopics(first:100) {
          totalCount
          nodes {
            topic {
              name
            }
          }
        }
        openIssueCount: issues(states:[OPEN]) {
          totalCount
        }
        closedIssueCount: issues(states:[CLOSED]) {
          totalCount
        }
        releases(last: 1) {
          totalCount
          nodes {
            tagName
          }
        }
"""


def build_query(extra_repos=None):
    extra_repos = extra_repos or []
    extra_repo_fragments = []
    for i, repo in enumerate(extra_repos):
        owner, name = repo.split("/")
        extra_repo_fragments.append(
            """
        repo_{i}: repository(name: "{name}", owner: "{owner}") {open_curly}
          {REPO_FIELDS}
        {close_curly}
        """.format(
                REPO_FIELDS=REPO_FIELDS,
                i=i,
                name=name,
                owner=owner,
                open_curly="{",
                close_curly="}",
            )
        )

    return """
    query {
      EXTRA_REPOS
      plugins: search(query:"topic:datasette-io topic:datasette-plugin" type:REPOSITORY, first:100) {
        repositoryCount
        nodes {
          ... on Repository {
            REPO_FIELDS
          }
        }
      }
      tools: search(query:"topic:datasette-io topic:datasette-tool" type:REPOSITORY, first:100) {
        repositoryCount
        nodes {
          ... on Repository {
            REPO_FIELDS
          }
        }
      }
    }
    """.replace(
        "REPO_FIELDS", REPO_FIELDS
    ).replace(
        "EXTRA_REPOS", "\n".join(extra_repo_fragments)
    )


def transform_node(node):
    releases = node.pop("releases")
    node["releaseCount"] = releases["totalCount"]
    for key in ("openIssueCount", "closedIssueCount"):
        node[key] = node[key]["totalCount"]
    repository_topics = node.pop("repositoryTopics")
    node["topics"] = [n["topic"]["name"] for n in repository_topics["nodes"]]
    default_branch_ref = node.pop("defaultBranchRef")
    node["latest_commit"] = default_branch_ref["target"]["oid"]
    return node, releases["nodes"]


client = GraphqlClient(endpoint="https://api.github.com/graphql")


def fetch_plugins(oauth_token, extra_repos):
    query = build_query(extra_repos)
    data = client.execute(
        query=query,
        headers={"Authorization": "Bearer {}".format(oauth_token)},
    )
    assert "errors" not in data, data["errors"]
    nodes = data["data"]["plugins"]["nodes"] + data["data"]["tools"]["nodes"]
    # Add any repo_i keys too
    for key in data["data"]:
        if key.startswith("repo_"):
            nodes.append(data["data"][key])
    return nodes


@click.command()
@click.argument(
    "db_filename",
    type=click.Path(file_okay=True, dir_okay=False),
)
@click.option("--github-token", envvar="GITHUB_TOKEN", required=True)
@click.option("--fetch-missing-releases", is_flag=True)
@click.option("--force-fetch-readmes", is_flag=True)
@click.option("-r", "--extra-repo", "extra_repos", multiple=True)
@click.option(
    "--owner",
    "owners",
    multiple=True,
    help="Only repos by these owners will be imported",
)
def cli(
    db_filename,
    github_token,
    fetch_missing_releases,
    force_fetch_readmes,
    extra_repos,
    owners,
):
    db = sqlite_utils.Database(db_filename)
    if "plugin_repos" in db.table_names():
        # Rename to datasette_repos
        db.execute("alter table plugin_repos rename to datasette_repos")
    repos_to_fetch_releases_for = {"simonw/datasette", "simonw/sqlite-utils"}
    if "latest_commit" not in db["datasette_repos"].columns_dict:
        previous_hashes = {
            row["nameWithOwner"]: None for row in db["datasette_repos"].rows
        }
    else:
        previous_hashes = {
            row["nameWithOwner"]: row["latest_commit"]
            for row in db["datasette_repos"].rows
        }
    nodes = fetch_plugins(github_token, extra_repos=extra_repos)
    for node in nodes:
        if owners and not any(
            node["nameWithOwner"].startswith("{}/".format(owner)) for owner in owners
        ):
            # Skip this one
            continue
        plugin, releases = transform_node(node)
        db["datasette_repos"].insert(
            plugin,
            pk="id",
            column_order=("id", "nameWithOwner"),
            replace=True,
            alter=True,
        )
        full_name = plugin["nameWithOwner"]
        if fetch_missing_releases:
            for release in releases:
                tag_name = release["tagName"]
                # Does this release exist for this repo?
                if not db["repos"].exists() or not list(
                    db["releases"].rows_where(
                        "repo = (select id from repos where full_name = ?) and tag_name = ?",
                        [full_name, tag_name],
                    )
                ):
                    repos_to_fetch_releases_for.add(full_name)

    if repos_to_fetch_releases_for:
        github_to_sqlite_releases.callback(
            db_filename, list(repos_to_fetch_releases_for), auth="auth.json"
        )

    # Fetch README for any repos that have changed since last time
    repos_to_fetch_readme_for = []
    for row in db["datasette_repos"].rows:
        if (
            row["latest_commit"] != previous_hashes.get(row["nameWithOwner"])
            or force_fetch_readmes
        ):
            repos_to_fetch_readme_for.append(row["nameWithOwner"])
    if repos_to_fetch_readme_for:
        print("Fetching README for {}".format(repos_to_fetch_readme_for))
        github_to_sqlite_repos.callback(
            db_filename,
            usernames=[],
            auth="auth.json",
            repo=repos_to_fetch_readme_for,
            load=None,
            readme=True,
            readme_html=True,
        )

    for view_name, topic in (("plugins", "datasette-plugin"), ("tools", "datasette-tool")):
        db.create_view(
            view_name,
        """
select
  repos.name as name,
  repos.full_name as full_name,
  repos.description as description,
  repos.stargazers_count,
  releases.tag_name,
  max(releases.created_at) as latest_release_at,
  datasette_repos.openGraphImageUrl,
  datasette_repos.usesCustomOpenGraphImage,
  (
    select
      sum(downloads)
    from
      stats
    where
      stats.package = repos.name
      and stats.date > date('now', '-7 days')
  ) as downloads_this_week
from
  datasette_repos
  join repos on datasette_repos.id = repos.node_id
  join releases on repos.id = releases.repo
where
  datasette_repos.rowid in (
    select
      datasette_repos.rowid
    from
      datasette_repos,
      json_each(datasette_repos.topics) j
    where
      j.value = '{}'
  )
group by
  repos.id
order by
  latest_release_at desc
""".format(topic).strip(),
        replace=True,
    )


if __name__ == "__main__":
    cli()
