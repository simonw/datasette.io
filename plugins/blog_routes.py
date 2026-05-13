from datasette import hookimpl
from datasette.utils.asgi import Response


async def blog_index(datasette, request):
    return Response.html(
        await datasette.render_template(
            "pages/blog.html",
            request=request,
            view_name="page",
        )
    )


async def blog_post(datasette, request):
    yyyy = request.url_vars["yyyy"]
    slug = request.url_vars["slug"]
    db = datasette.get_database("content")
    rows = (
        await db.execute(
            "select 1 from blog_posts where year = :year and slug = :slug",
            {"year": yyyy, "slug": slug},
        )
    ).rows
    if not rows:
        return Response.html("Blog post not found", status=404)
    return Response.html(
        await datasette.render_template(
            "pages/blog/{yyyy}/{slug}.html",
            {"yyyy": yyyy, "slug": slug},
            request=request,
            view_name="page",
        )
    )


@hookimpl
def register_routes():
    return [
        (r"^/blog/$", blog_index),
        (r"^/blog/(?P<yyyy>\d{4})/(?P<slug>[^/]+)/$", blog_post),
    ]
