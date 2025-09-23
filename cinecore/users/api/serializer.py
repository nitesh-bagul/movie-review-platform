from django.contrib.auth.models import User

from rest_framework import serializers

class RegistrationSerializer(serializers.ModelSerializer):
    password2=serializers.CharField(style={'input_type':'password'},write_only=True)
    
    class Meta:
        model=User
        fields=['username','email','password','password2']
        extra_kwargs={
            'password':{'write_only':True}
        }
    
    def save(self, **kwargs):
        print(self.validated_data)
        password = self.validated_data.get('password')
        password2 = self.validated_data.get('password2')
        if password != password2:
            raise serializers.ValidationError("Passwords must match")

        user = User(
            username=self.validated_data.get('username'),
            email=self.validated_data.get('email')
        )
        user.set_password(password)
        user.save()
        print(user)
        return user
