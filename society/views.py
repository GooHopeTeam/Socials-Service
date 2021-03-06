from django.forms import model_to_dict
from rest_framework import status
from rest_framework.generics import get_object_or_404
from rest_framework.response import Response
from rest_framework.viewsets import mixins, GenericViewSet

from friends.models import Friends
from socials.utils import IRepositoryExtender
from .models import Profile, Society
from .serializers import ProfileSerializer, SocietySerializer
from .repositories import ProfileRepository, SocietyRepository


class ProfileViewSet(IRepositoryExtender,
                     mixins.RetrieveModelMixin,
                     mixins.ListModelMixin,
                     mixins.CreateModelMixin,
                     GenericViewSet):
    repository = ProfileRepository()
    queryset = Profile.objects.all()
    serializer_class = ProfileSerializer

    @staticmethod
    def visibility_regulator(user: Profile.objects, profile: Profile) -> bool:
        """
        :param user: Current user
        :param profile: Opened profile
        :return: Profile status (hidden or visible)
        """
        hidden = False
        if not profile.publicity == Profile.publicity_choices[0][0]:
            profile_friends = profile.friend.all()
            hidden = True
            if profile_friends:
                # Friend and friends of friends
                if profile.publicity == Profile.publicity_choices[1][0]:
                    if not Friends.contains_friend(profile, user):
                        if [x for x in [Friends.contains_friend(user, x.user) for x in profile_friends if x] if x]:
                            hidden = False
                    else:
                        hidden = False

                # Just friends
                elif profile.publicity == Profile.publicity_choices[2][0]:
                    if Friends.contains_friend(profile, user):
                        hidden = False
        return hidden

    def retrieve(self, request, *args, **kwargs):
        user = get_object_or_404(self.queryset, user_id=request.query_params.get('user_id'))
        profile = get_object_or_404(self.queryset, user_id=kwargs.get('pk'))
        _profile = model_to_dict(profile, ('avatar', 'login', 'status', 'description'))
        _profile['avatar'] = profile.avatar.url if profile.avatar else ''

        return Response({
            'user': _profile,
            'hidden': ProfileViewSet.visibility_regulator(user, profile),
            'friends': Profile.objects.filter(id__in=profile.friend.all().values('user_id')).values(),
            'societies': Society.objects.filter(societymembers__user=profile).values()
        }, status=status.HTTP_200_OK)


class SocietyViewSet(IRepositoryExtender,
                     mixins.RetrieveModelMixin,
                     mixins.ListModelMixin,
                     mixins.CreateModelMixin,
                     mixins.UpdateModelMixin,
                     mixins.DestroyModelMixin,
                     GenericViewSet):
    repository = SocietyRepository
    queryset = Society.objects.all()
    serializer_class = SocietySerializer

    def create(self, request, *args, **kwargs):
        data = request.data.dict()
        creator = get_object_or_404(Profile, user_id=request.data['creator'])
        data['creator'] = creator

        return Response(model_to_dict(self.serializer_class().create(data)))

    def list(self, request, *args, **kwargs):
        def check_image(image) -> str:
            return image.url if image else ''

        societies = Society.objects.filter(societymembers__user__user_id=request.query_params.get('user_id'))
        data = []

        for society in societies:
            data.append(model_to_dict(society))
            data[-1]['image'] = check_image(society.image)
            data[-1]['members'] = [model_to_dict(x.user) for x in society.societymembers_set.all()]
            for member in data[-1]['members']:
                member['avatar'] = check_image(member.get('avatar'))

            data[-1]['creator'] = model_to_dict(society.creator)
            data[-1]['creator']['avatar'] = check_image(data[-1]['creator'].get('creator'))

        return Response(data, status=status.HTTP_200_OK)
