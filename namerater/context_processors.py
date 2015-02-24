# coding=utf-8
from namerater.models import User
from common import update_session

def get_session(request):
    # Update totals
    if request.session.get("logged_in"):
        user = User.objects.get(id=request.session.get("user_id"))
        update_session(request, user)
    return {"session":request.session}