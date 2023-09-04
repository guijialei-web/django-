from django.utils.deprecation import MiddlewareMixin
from django.shortcuts import render,redirect,HttpResponse


    # 如果有返回值,则不会跳到下一个中间件，如果没有，则会继续下一个中间件
class AuthMiddleware(MiddlewareMixin):
    def process_request(self, request):
        if request.path_info not in ['/login/','/image/code']:
            info_dict = request.session.get('info')
            if not info_dict:
                return redirect('/login/')

        # 如果请求的路径是'/login'或者info_dict不为空，则继续执行下一个中间件
        return None
