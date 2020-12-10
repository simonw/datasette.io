import click
from github_to_sqlite.cli import releases as github_to_sqlite_releases
from python_graphql_client import GraphqlClient
import sqlite_utils


QUERY = """
query {
  search(query:"topic:datasette-io topic:datasette-plugin user:simonw" type:REPOSITORY, first:100) {
    repositoryCount
    nodes {
      ... on Repository {
        id
        nameWithOwner
        openGraphImageUrl
        usesCustomOpenGraphImage
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
      }
    }
  }
}
"""


def transform_node(node):
    releases = node.pop("releases")
    node["releaseCount"] = releases["totalCount"]
    for key in ("openIssueCount", "closedIssueCount"):
        node[key] = node[key]["totalCount"]
    repository_topics = node.pop("repositoryTopics")
    node["topics"] = [n["topic"]["name"] for n in repository_topics["nodes"]]
    return node, releases["nodes"]


client = GraphqlClient(endpoint="https://api.github.com/graphql")


def fetch_plugins(oauth_token):
    data = client.execute(
        query=QUERY,
        headers={"Authorization": "Bearer {}".format(oauth_token)},
    )
    nodes = data["data"]["search"]["nodes"]
    return nodes


@click.command()
@click.argument(
    "db_filename",
    type=click.Path(file_okay=True, dir_okay=False),
)
@click.option("--github-token", envvar="GITHUB_TOKEN", required=True)
@click.option("--fetch-missing-releases", is_flag=True)
def cli(db_filename, github_token, fetch_missing_releases):
    db = sqlite_utils.Database(db_filename)
    repos_to_fetch_releases_for = set()
    nodes = fetch_plugins(github_token)
    for node in nodes:
        plugin, releases = transform_node(node)
        db["plugin_repos"].insert(
            plugin,
            pk="id",
            column_order=("id", "nameWithOwner"),
            replace=True,
        )
        full_name = plugin["nameWithOwner"]
        if fetch_missing_releases:
            for release in releases:
                tag_name = release["tagName"]
                # Does this release exist for this repo?
                if not list(
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

    db.create_view(
        "plugins",
        """
select
  repos.name as name,
  repos.full_name as full_name,
  repos.description as description,
  releases.tag_name,
  max(releases.created_at) as latest_release_at,
  plugin_repos.openGraphImageUrl,
  plugin_repos.usesCustomOpenGraphImage
from
  plugin_repos
  join repos on plugin_repos.id = repos.node_id
  join releases on repos.id = releases.repo
group by
  repos.id
order by
  latest_release_at desc
""".strip(),
        replace=True,
    )


if __name__ == "__main__":
    cli()
