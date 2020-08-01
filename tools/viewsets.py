from functools import wraps

from django.http import HttpResponse, QueryDict
from django.views.decorators.csrf import csrf_exempt

from rest_framework.authentication import TokenAuthentication
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import permissions, exceptions
from rest_framework.parsers import FileUploadParser

from tools.serializers import APISerializer

def validate_paramaters(params, checklist, *args, **kwargs):
    for item in checklist:
        if item not in params:
            return False
    return True


def validate_params(test_set):
    def decorator(func):
        @wraps(func)
        def wrapped_func(self, request, params=None, *args, **kwargs):
            if params is None:
                params = {}
            valid = validate_paramaters(params, test_set)
            if not valid:
                raise exceptions.ValidationError('Missing %s' % test_set)
            return func(self, request, params, *args, **kwargs)
        return wrapped_func
    return decorator


class ActionAPI(APIView):
    """
    A custom API view in order to make coding and routing a bit easier for everyone
    This will convert all requests to use the same function meaning that no matter what TYPE
    of requst you send it will go through
    """
    authentication_classes = [TokenAuthentication,]
    permission_classes = [permissions.IsAuthenticated]

    _last_action = None

    RESPONSE_KEYS = ['user', 'action', 'token', 'subject', 'type', 'messageid']
    @csrf_exempt
    def post(self, request, action, **kwargs):
        return self.get(request, action, **kwargs)

    @csrf_exempt
    def get(self, request, action, **kwargs):
        params = self.normalize_params(request)

        response_code = 200

        kwargs["params"] = params
        self._last_action = params.get("action", action)

        try:
            lv_action = self.__getattribute__(self._last_action)
        except AttributeError:
            response_code = 404
            lv_action = self.action_does_not_exist

        response = lv_action(request, **kwargs)

        # Cater for streaming HTTPResponse types so that we can stream camera feeds?
        if isinstance(response, (Response, )):
            response = response.data
        if isinstance(response, (HttpResponse, )):
            return response

        response_context = dict(
            filter(lambda item: item[1] is not None, {
                k: params.get(k, None) for k in self.RESPONSE_KEYS
            }.items())
        )

        serialised = APISerializer(response, context=response_context)
        return Response(serialised.data, response_code)


    def action_does_not_exist(self, *args, **kwargs):
        return {
            "success": False,
            "reason": "Action %s does not exist." % self._last_action
        }


    def normalize_params(self, request):
        """
        Normalizes paramaters to a dictionary like object sent via a request
        Pretty cool stuff
        """
        params = request.query_params.dict().copy()

        if isinstance(request.data, QueryDict):
            params.update(request.data.dict())
        else:
            params.update(request.data)
        return params

