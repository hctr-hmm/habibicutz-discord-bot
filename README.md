# Habibi Cutz Discord Bot

Discord bot to check the barber shop database.

## Commands

- `!appointments [limit]` - Show upcoming appointments (default 10)
- `!today` - Show today's appointments
- `!prices` - Show service prices
- `!hours` - Show business hours
- `!stats` - Show database statistics
- `!query <sql>` - Execute raw SQL query (admin only)

## Setup

1. Create a Discord bot at https://discord.com/developers/applications
2. Enable "Message Content Intent" in Bot settings
3. Copy bot token

4. Install dependencies:
```bash
pip install -r requirements.txt
```

5. Create `.env` file:
```bash
cp .env.example .env
# Edit .env and add your DISCORD_TOKEN
```

6. Run:
```bash
python bot.py
```

## SSH Tunnel (if database not exposed)

```bash
ssh -L 5432:localhost:5432 root@ssh.hctr.xyz
```

Then use `DB_HOST=localhost` in `.env`
