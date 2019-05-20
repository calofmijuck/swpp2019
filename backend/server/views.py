from .models import Profile, Meeting, Comment, Notification, User
from .serializers import ProfileSerializer, MeetingSerializer, CommentSerializer, NotificationSerializer, UserSerializer
from rest_framework.response import Response
from rest_framework import status, permissions, generics
from rest_framework.authtoken.models import Token
from django.contrib.auth import authenticate
from django.views.decorators.csrf import csrf_exempt
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from .permissions import IsOwner


from rest_framework.status import (
    HTTP_400_BAD_REQUEST,
    HTTP_404_NOT_FOUND,
    HTTP_200_OK
)

class ProfileList(generics.ListCreateAPIView):
    queryset = Profile.objects.all()
    serializer_class = ProfileSerializer

class ProfileDetail(generics.RetrieveUpdateDestroyAPIView):
    queryset = Profile.objects.all()
    serializer_class = ProfileSerializer

class MeetingList(generics.ListCreateAPIView):
    permission_classes = (AllowAny, )
    queryset = Meeting.objects.all()
    serializer_class = MeetingSerializer

class MeetingDetail(generics.RetrieveUpdateDestroyAPIView):
    queryset = Meeting.objects.all()
    serializer_class = MeetingSerializer

class CommentDetail(generics.RetrieveUpdateDestroyAPIView):
    permission_classes = (permissions.IsAuthenticatedOrReadOnly, IsOwner, )
    queryset = Comment.objects.all()
    serializer_class = CommentSerializer

    # Put Works
    # http -v PUT http://127.0.0.1:8000/comment/1/ comment_text='수정할 댓글' parent_meeting='1' writer='3'
    # http -v PUT http://127.0.0.1:8000/comment/1/ "Authorization: Token 4a015be3f94e08809fed54b07c9520009b41098a" comment_text='수정할 댓글2' parent_meeting='1' writer='3'

class CommentList(generics.ListCreateAPIView):
    permission_classes = (permissions.IsAuthenticatedOrReadOnly, )
    queryset = Comment.objects.all()
    serializer_class = CommentSerializer

    # Post Works
    # http -v POST http://127.0.0.1:8000/comment/ comment_text='테스트 댓글' parent_meeting='1' writer='2'


class NotificationDetail(generics.RetrieveUpdateDestroyAPIView):
    queryset = Notification.objects.all()
    serializer_class = NotificationSerializer

class UserMeetingList(generics.ListCreateAPIView):
    queryset = None
    serializer_class = MeetingSerializer

    def get(self, request, *args, **kwargs):
        user = Profile.objects.get(pk=kwargs['pk'])
        self.queryset = user.meeting_hosted.all()
        self.queryset.union(user.meeting_set.all(), all=False) # Needs to be modified
        return self.list(request, *args, **kwargs)


class SearchResult(generics.ListCreateAPIView):
    queryset = None
    serializer_class = MeetingSerializer

    def get(self, request, *args, **kwargs):
        self.queryset = Meeting.objects.filter(name__contains=kwargs['keyword'])
        self.queryset.union(Meeting.objects.filter(tag_set__name__contains=kwargs['keyword']), all=False)
        return self.list(request, *args, **kwargs)

@csrf_exempt
@api_view(["POST"])
@permission_classes((AllowAny,))
def Login(request):
    username = request.data.get("username")
    password = request.data.get("password")
    if username is None or password is None:
        return Response({"error": "Error!"}, status=HTTP_400_BAD_REQUEST)

    user = authenticate(username=username, password=password)

    if not user:
        return Response({"error", "Invalid Credentials"}, status=HTTP_404_NOT_FOUND)
    token, _ = Token.objects.get_or_create(user=user)
    key = {'token': token.key}
    profile = Profile.objects.get(pk=user.id) # get user's profile
    ret = {**ProfileSerializer(profile).data, **key} # Merge two dictionaries
    return Response(ret, status=HTTP_200_OK)

    # Post Works
    # http -v POST http://127.0.0.1:8000/signin/ username="zx" password="123"

class Register(generics.ListCreateAPIView):
    permission_classes = (AllowAny, )

    def post(self, request, *args, **kwargs):
        data = request.data
        user = User.objects.create_user(username=data['username'], password=request.data['password'])
        Profile.objects.create(user_id=user.id, gender=data['gender'], nickname=data['nickname'], name=data['name'])
        return Response(status=HTTP_200_OK)

    # http -v POST http://127.0.0.1:8000/signup/ username="zxc" password="123" gender="1" nickname="cxz" name="zxc zxc"