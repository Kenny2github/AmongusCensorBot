# AmongusCensorBot
Echo comments with spoilers covering all but the letters that spell out things like "among us".

## Usage
Requires PRAW.

On first clone, create `credentials.txt`:
```
<Reddit client ID>
<client secret>
```
Then run `refresh_token.py` and follow its instructions **while logged into the bot account**. A refresh token will be written to `credentials.txt`.

After that has been done (it only needs to be done once) run `main.py`, with `-v` if you want to log every comment it looks at.