from django.shortcuts import render


def server_error(request, template_name="500.html"):
    """
    Custom 500 error view to render a branded maintenance/technical issues page.
    """
    response = render(request, template_name, status=500)
    response.status_code = 500
    return response
