# 🤖 GitHub Auto Follow/Unfollow

**Automatically manages your GitHub followers and following.**

## What it does:
- ✅ **Follows** everyone who follows you
- ❌ **Unfollows** everyone who doesn't follow you back
- 🛡️ **Safe limits** (20 unfollows, 15 follows per run)
- 📊 **Detailed statistics** and logs

## Quick Setup:

1. **Create** a [Personal Access Token](https://github.com/settings/tokens) with `user` permissions
2. **Add** it as repository secret: `PERSONAL_GITHUB_TOKEN`
3. **Copy** the workflow file to `.github/workflows/`
4. **Done!** Runs automatically daily at 8:00 AM UTC

## Manual Run:
- Go to **Actions** → **GitHub Follower Automation** → **Run workflow**
- Choose: `both`, `follow_back`, `cleanup`, or `stats_only`

## Configuration:
Set variables in repository settings:
- `MAX_UNFOLLOWS_PER_RUN`: Max unfollows per day (default: 20)
- `MAX_FOLLOWS_PER_RUN`: Max follows per day (default: 15)
- `DELAY_SECONDS`: Seconds between actions (default: 5)

## Safety Features:
- 🛡️ Skips users with 10,000+ followers
- 🛡️ Skips GitHub organizations  
- ⏱️ Respects API rate limits
- 📊 Full transparency in logs

**Result**: Clean follower ratio where you only follow people who follow you back.

---

*Created with ❤️ by Claude and [@FabianIMV](https://github.com/FabianIMV)*
