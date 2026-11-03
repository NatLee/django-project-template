import pytest

from userprofile.models import UserProfile

pytestmark = pytest.mark.django_db


def test_profile_is_created_with_the_user(user):
    assert UserProfile.objects.get(user=user).displayname == ""


def test_profile_changes_are_kept_in_history(user):
    profile = user.userprofile
    profile.displayname = "Alice"
    profile.save()
    assert [h.displayname for h in profile.history.order_by("history_date")] == ["", "Alice"]
