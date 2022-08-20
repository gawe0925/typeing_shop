from base.tasks import is_authenticated
from rest_framework.views import APIView
from rest_framework.response import Response

from members.models import User
from members.tasks import valid_member

class AddUserView(APIView):
    def post(self, request):
        authenticated_result = is_authenticated(self)
        if type(authenticated_result) == tuple:
            error, status_code = authenticated_result
            return Response(error, status=status_code)

        try:
            self.request.data
        except:
            return Response({"error" : "none data"}, status=400)
        
        data = self.request.data
        
        try:
            data['members']
        except:
            return Response({"error" : "none data"}, status=400)

        members = data['members']

        valid_result = valid_member(members)

        if type(valid_result) == tuple:
            error, status = valid_result
            return Response(error, status=status)
        elif not valid_result:
            return Response({'error':'failed to create'}, status=500)
        else:
            return Response({'success':'created'},status=200)