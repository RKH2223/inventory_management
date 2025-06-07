from django.shortcuts import redirect
from django.urls import reverse, resolve

class AuthenticationMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        # Public paths that don't require authentication
        public_paths = ['/login/', '/register/', '/admin/']
        
        # Check if the current path is the login page
        current_path = request.path_info
        
        # Check if the user is authenticated
        if not any(current_path.startswith(path) for path in public_paths) and \
           not current_path.startswith('/admin/') and \
           'user_id' not in request.session:
            return redirect('login')
            
        response = self.get_response(request)
        return response