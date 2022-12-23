from testing.testcase import TestCase
from accounts.models import UserProfile


# Create your tests here.
class UserProfileModelTests(TestCase):
    def setUp(self):
        pass

    def test_user_profile(self):
        user = self.create_user(username='user1')
        self.assertEqual(UserProfile.objects.count(), 0)
        profile = user.profile
        self.assertEqual(isinstance(profile, UserProfile), True)
        self.assertEqual(UserProfile.objects.count(), 1)
