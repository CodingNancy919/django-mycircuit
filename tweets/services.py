from tweets.models import TweetPhoto


class TweetService(object):
    @classmethod
    def create_photos_from_files(cls, tweet, files):
        tweet_photos = []
        for index, photo in enumerate(files):
            tweet_photo = TweetPhoto(
                tweet=tweet,
                file=photo,
                order=index,
                user=tweet.user,
            )
            tweet_photos.append(tweet_photo)
        TweetPhoto.objects.bulk_create(tweet_photos)

