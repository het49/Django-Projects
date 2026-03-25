from django.shortcuts import redirect, render
from django.template import RequestContext

def not_found(request, exception):
	return render(request,'error/404.html')

#def handler404(request, *args, **argv):
#    response = render(request,'brewery/web/admin/templates/404.html', context)
#    response.status_code = 404
#    return response

# def error_500(request,  exception):
#         data = {}
#         return render(request,'certman/500.html', data)