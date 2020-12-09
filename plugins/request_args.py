from datasette import hookimpl


@hookimpl
def extra_template_vars(request):
    return {"args": request.args}
