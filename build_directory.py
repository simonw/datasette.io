import click
from github_to_sqlite.cli import (
    releases as github_to_sqlite_releases,
    repos as github_to_sqlite_repos,
)
import httpx
import json
from python_graphql_client import GraphqlClient
import sqlite_utils


REPO_FIELDS = """
fragment repoFields on Repository {
  id
  nameWithOwner
  createdAt
  openGraphImageUrl
  usesCustomOpenGraphImage
  defaultBranchRef {
    target {
      oid
    }
  }
  repositoryTopics(first: 100) {
    totalCount
    nodes {
      topic {
        name
      }
    }
  }
  openIssueCount: issues(states: [OPEN]) {
    totalCount
  }
  closedIssueCount: issues(states: [CLOSED]) {
    totalCount
  }
  releases(orderBy: {field: CREATED_AT, direction: DESC}, first: 1) {
    totalCount
    nodes {
      tagName
    }
  }
}
"""


def build_query(repos):
    repo_fragments = []
    for i, repo in enumerate(repos):
        owner, name = repo.split("/")
        repo_fragments.append(
            """
        repo_{i}: repository(name: "{name}", owner: "{owner}") {open_curly}
          ...repoFields
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
    REPO_FIELDS
    { REPOS }
    """.replace(
        "REPOS", "\n".join(repo_fragments)
    ).replace(
        "REPO_FIELDS", REPO_FIELDS
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


def fetch_plugins(oauth_token, repos):
    chunks = []
    repos_copy = list(repos)
    while repos_copy:
        chunk, repos_copy = repos_copy[:20], repos_copy[20:]
        chunks.append(chunk)
    all_nodes = []
    for chunk in chunks:
        query = build_query(chunk)
        print(query)
        data = client.execute(
            query=query,
            headers={"Authorization": "Bearer {}".format(oauth_token)},
        )
        assert "errors" not in data, data["errors"]
        nodes = []
        for key in data["data"]:
            if key.startswith("repo_"):
                nodes.append(data["data"][key])
        all_nodes.extend(nodes)
    return all_nodes


@click.command()
@click.argument(
    "db_filename",
    type=click.Path(file_okay=True, dir_okay=False),
)
@click.option("--github-token", envvar="GITHUB_TOKEN", required=True)
@click.option("--fetch-missing-releases", is_flag=True)
@click.option("--always-fetch-releases-for-repo", multiple=True)
def cli(
    db_filename,
    github_token,
    fetch_missing_releases,
    always_fetch_releases_for_repo,
):
    db = sqlite_utils.Database(db_filename)
    repos_to_fetch_releases_for = {"simonw/datasette"}
    if "latest_commit" not in db["datasette_repos"].columns_dict:
        previous_hashes = {
            row["nameWithOwner"]: None for row in db["datasette_repos"].rows
        }
    else:
        previous_hashes = {
            row["nameWithOwner"]: row["latest_commit"]
            for row in db["datasette_repos"].rows
        }
    repos = [
        r[0]
        for r in db.execute(
            "select repo from tool_repos union select repo from plugin_repos"
        ).fetchall()
    ]
    nodes = fetch_plugins(github_token, repos)
    for node in nodes:
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
                if (
                    (full_name in always_fetch_releases_for_repo)
                    or not db["repos"].exists()
                    or not list(
                        db["releases"].rows_where(
                            "repo = (select id from repos where full_name = ?) and tag_name = ?",
                            [full_name, tag_name],
                        )
                    )
                ):
                    repos_to_fetch_releases_for.add(full_name)

    if repos_to_fetch_releases_for:
        github_to_sqlite_releases.callback(
            db_filename, list(repos_to_fetch_releases_for), auth="auth.json"
        )

    # Fetch details for any repos that have changed since last time
    repos_to_fetch = []
    for row in db["datasette_repos"].rows:
        if row["latest_commit"] != previous_hashes.get(row["nameWithOwner"]):
            repos_to_fetch.append(row["nameWithOwner"])

    # Fix up 3 repos with camo.githubusercontent.com at random
    # https://github.com/simonw/datasette.io/issues/156#issuecomment-1894795880
    fix_repo_names = [
        row[0]
        for row in db.execute(
            """
        select full_name from repos
        where readme_html like '%camo.githubusercontent.com%'
        and readme not like '%camo.githubusercontent.com%'
        limit 3
    """
        ).fetchall()
    ]
    print("Fixing HTML for {}".format(fix_repo_names))
    repos_to_fetch.extend(fix_repo_names)

    if repos_to_fetch:
        print("Fetching repo details for {}".format(repos_to_fetch))
        github_to_sqlite_repos.callback(
            db_filename,
            usernames=[],
            auth="auth.json",
            repo=repos_to_fetch,
            load=None,
            readme=False,
            readme_html=False,
        )

    # Separate step to fetch their READMEs
    for repo in repos_to_fetch:
        print("Fetching README for {}".format(repo))
        # curl 'https://api.github.com/repos/simonw/datasette/readme' -H 'Accept: application/vnd.github.raw'
        response = httpx.get(
            "https://api.github.com/repos/{}/readme".format(repo),
            headers={
                "Accept": "application/vnd.github.raw",
                "Authorization": "Bearer {}".format(github_token),
            },
        )
        response.raise_for_status()
        readme_md = response.text
        # Now convert that markdown to HTML
        response2 = httpx.post(
            "https://api.github.com/markdown",
            json={
                "text": readme_md,
                "mode": "markdown",
                "context": repo,
            },
            headers={
                "Accept": "application/vnd.github.v3+json",
                "Authorization": "Bearer {}".format(github_token),
            },
        )
        response2.raise_for_status()
        readme_html = response2.text
        with db.conn:
            db.execute(
                "update repos set readme = :readme, readme_html = :readme_html where full_name = :full_name",
                {
                    "readme": readme_md,
                    "readme_html": readme_html,
                    "full_name": repo,
                },
            )

    for view_name, repo_table in (("plugins", "plugin_repos"), ("tools", "tool_repos")):
        db.create_view(
            view_name,
            """
select
  repos.name as name,
  repos.full_name as full_name,
  users.login as owner,
  repos.description as description,
  {repo_table}.extra_search as extra_search,
  {repo_table}.tags as tags,
  repos.stargazers_count,
  pypi_versions.name as tag_name,
  max(pypi_releases.upload_time) as latest_release_at,
  repos.created_at as created_at,
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
  ) as downloads_this_week,
  (
    select
      count(*)
    from
      plugin_repos
    where
      repo = repos.full_name
  ) as is_plugin,
  (
    select
      count(*)
    from
      tool_repos
    where
      repo = repos.full_name
  ) as is_tool
from
  datasette_repos
  join repos on datasette_repos.id = repos.node_id
  left join pypi_releases on (
    pypi_releases.package = repos.name or pypi_releases.package = 'datasette-' || repos.name
  )
  left join pypi_versions on pypi_releases.version = pypi_versions.id
  join users on users.id = repos.owner
  join {repo_table} on {repo_table}.repo = datasette_repos.nameWithOwner
group by
  repos.id
order by
  latest_release_at desc;
""".format(
                repo_table=repo_table
            ).strip(),
            replace=True,
        )


if __name__ == "__main__":
    cli()
