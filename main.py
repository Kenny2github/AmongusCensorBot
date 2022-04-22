import sys
import os
import time
import re
import traceback
import praw
from praw.exceptions import PRAWException
from praw.models import Comment

os.chdir(os.path.dirname(__file__))
sys.path.append(os.getcwd())

from amongus import amongusify_censored, reddit_spoiler

with open('credentials.txt') as f:
    client_id = f.readline().strip()
    client_secret = f.readline().strip()
    refresh_token = f.readline().strip()
SUBREDDITS = '+'.join([
    'AbyxDev', # This is me
    'Dildont', # I mod this
    'Formatwars', # Permission given by mod
    'iwantmytimeback', # I mod this
    'ExplainLikeImStoned', # I mod this
    'vanaffy', # I mod this
])
DEBUG = '-v' in sys.argv

reddit = praw.Reddit(
    client_id=client_id,
    client_secret=client_secret,
    refresh_token=refresh_token,
    user_agent='Amongus spoilerer by u/Kenny2reddit')

print('\n=== Logged in on', time.strftime('%Y-%m-%d %H:%M:%S'), '===\n', flush=True)

OLD_TIME = 24 * 60 * 60 # one day
TEXTUAL = re.compile(r'''^[-a-zA-Z0-9_'"\u2018-\u201f \u00a0\n?!:;.,()&$+=]+$''')
FOOTER = """

^(>!I !<am>! a b!<o>!t. !<g>!ot q!<u>!e!<s>!tion!<s>!? b!<u>!g!<s? \
>!say so on [GitHub](https://github.com/Kenny2github/AmongusCensorBot). \
inspired by [this comment](https://www.reddit.com/r/CuratedTumblr/comments/si1apq/comment/hv7167w/?context=3)!<)"""

me = reddit.user.me()

seen: dict[str, int] = {}

for comment in reddit.subreddit(SUBREDDITS).stream.comments(skip_existing=True):
    # don't maintain cache older than a day, those get ignored anyway
    seen = {k: v for k, v in seen.items() if v > time.time() - OLD_TIME}
    if DEBUG: print('Considering:', comment.permalink)
    comment: Comment
    if comment.author.name == me.name:
        # comment done by me
        if DEBUG: print(' Comment is mine')
        continue
    if not comment.is_root:
        # only reply to top-level comments (increase visibility)
        if DEBUG: print(' Comment not top-level')
        continue
    if comment.submission.created_utc < time.time() - OLD_TIME:
        # don't reply to day-old posts
        if DEBUG: print(' Post too old')
        continue
    if comment.submission.id in seen:
        # only comment once per submission
        if DEBUG: print(' Post already commented on')
        continue
    if not TEXTUAL.match(comment.body):
        # markup and stuff that might break the spoiler
        if DEBUG: print(' Comment too complicated')
        continue
    amongusified = amongusify_censored(comment.body)
    # if the text is unchanged or completely spoiled, it wasn't amongusified
    if amongusified in {comment.body, reddit_spoiler(comment.body)}:
        # so don't just echo the comment
        if DEBUG: print(' Comment not amogusified')
        continue
    print('Replying to comment:', comment.permalink)
    print('', amongusified)
    try:
        comment.reply(amongusified + FOOTER)
    except PRAWException:
        print(' Error replying:', flush=True)
        traceback.print_exc()
    finally:
        seen[comment.submission.id] = comment.submission.created_utc
