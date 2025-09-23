from users.api.serializer import RegistrationSerializer
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework_simplejwt.tokens import RefreshToken

@api_view(['GET','POST'])
def registration_view(request):
    print()
    serializer=RegistrationSerializer(data=request.data)
    
    data={}
    if serializer.is_valid():
        print(serializer.validated_data)
        user=serializer.save()
        print('user',user)
        data['response']='Registration sucessfull'
        data['username']=user.username
        data['email']=user.email

        refresh = RefreshToken.for_user(user)
        data['token']={
                        'refresh': str(refresh),
                        'access': str(refresh.access_token),
                      }
        print(serializer.data)
  
    else:
        return Response(serializer.errors, status=400)

    return Response(data)

