import click
from python_graphql_client import GraphqlClient
import sqlite_utils


QUERY = """
query {
  search(query:"topic:datasette-io topic:datasette-plugin user:simonw" type:REPOSITORY, first:100) {
    repositoryCount
    nodes {
      ... on Repository {
        id
        name
        nameWithOwner
        homepageUrl
        description
        openGraphImageUrl
        usesCustomOpenGraphImage
        stargazerCount
        forkCount
        updatedAt
        createdAt
        pushedAt
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
            id
            name
            tagName
            description
            descriptionHTML
            shortDescriptionHTML
            createdAt
            publishedAt
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
def cli(db_filename, github_token):
    db = sqlite_utils.Database(db_filename)
    nodes = fetch_plugins(github_token)
    for node in nodes:
        plugin, releases = transform_node(node)
        db["plugin_repos"].insert(
            plugin,
            pk="id",
            column_order=("id", "name", "description", "homepageUrl", "topics"),
        )
        for release in releases:
            release["plugin_repo"] = plugin["id"]
            db["releases"].insert(release, pk="id", foreign_keys=("plugin_repos",))

    db.create_view(
        "plugins",
        """
select
  plugin_repos.name,
  plugin_repos.description,
  releases.tagName,
  max(releases.createdAt) as latestReleaseAt,
  homepageUrl,
  topics,
  nameWithOwner,
  openGraphImageUrl,
  usesCustomOpenGraphImage,
  stargazerCount,
  forkCount,
  plugin_repos.updatedAt,
  plugin_repos.createdAt,
  plugin_repos.pushedAt,
  openIssueCount,
  closedIssueCount,
  releaseCount
from
  plugin_repos
  join releases on plugin_repos.id = releases.plugin_repo
group by
  plugin_repos.id
order by
  latestReleaseAt desc
""".strip(),
    )


if __name__ == "__main__":
    cli()
