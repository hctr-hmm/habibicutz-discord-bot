import discord
from discord.ext import commands
import psycopg2
import os
from dotenv import load_dotenv
from datetime import datetime

load_dotenv()

intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix='!', intents=intents)

def get_db():
    return psycopg2.connect(
        host=os.getenv('DB_HOST', 'localhost'),
        port=os.getenv('DB_PORT', '5432'),
        database=os.getenv('DB_NAME', 'barber'),
        user=os.getenv('DB_USER', 'barber'),
        password=os.getenv('DB_PASSWORD', 'barber'),
        client_encoding='UTF8'
    )

@bot.event
async def on_ready():
    print(f'{bot.user} connected to Discord!')

@bot.command(name='appointments')
async def appointments(ctx, limit: int = 10):
    """Show upcoming appointments"""
    try:
        conn = get_db()
        cur = conn.cursor()
        cur.execute("""
            SELECT id, name, phone, service, datetime 
            FROM appointments 
            WHERE datetime >= NOW()
            ORDER BY datetime 
            LIMIT %s
        """, (limit,))
        
        rows = cur.fetchall()
        cur.close()
        conn.close()
        
        if not rows:
            await ctx.send("No upcoming appointments.")
            return
        
        msg = "**Upcoming Appointments:**\n```"
        for row in rows:
            dt = row[4].strftime('%Y-%m-%d %H:%M')
            msg += f"\n{row[0]}: {row[1]} | {row[2]} | {row[3]} | {dt}"
        msg += "```"
        
        await ctx.send(msg)
    except Exception as e:
        await ctx.send(f"Error: {str(e)}")

@bot.command(name='today')
async def today(ctx):
    """Show today's appointments"""
    try:
        conn = get_db()
        cur = conn.cursor()
        cur.execute("""
            SELECT id, name, phone, service, datetime 
            FROM appointments 
            WHERE DATE(datetime) = CURRENT_DATE
            ORDER BY datetime
        """)
        
        rows = cur.fetchall()
        cur.close()
        conn.close()
        
        if not rows:
            await ctx.send("No appointments today.")
            return
        
        msg = "**Today's Appointments:**\n```"
        for row in rows:
            dt = row[4].strftime('%H:%M')
            msg += f"\n{row[0]}: {row[1]} | {row[2]} | {row[3]} | {dt}"
        msg += "```"
        
        await ctx.send(msg)
    except Exception as e:
        await ctx.send(f"Error: {str(e)}")

@bot.command(name='prices')
async def prices(ctx):
    """Show service prices"""
    try:
        conn = get_db()
        cur = conn.cursor()
        cur.execute("SELECT service, price FROM prices ORDER BY id")
        
        rows = cur.fetchall()
        cur.close()
        conn.close()
        
        msg = "**Prices:**\n```"
        for row in rows:
            msg += f"\n{row[0]}: {row[1]} Ft"
        msg += "```"
        
        await ctx.send(msg)
    except Exception as e:
        await ctx.send(f"Error: {str(e)}")

@bot.command(name='hours')
async def hours(ctx):
    """Show business hours"""
    try:
        conn = get_db()
        cur = conn.cursor()
        cur.execute("""
            SELECT day_of_week, open_time, close_time, is_closed 
            FROM daily_hours 
            ORDER BY day_of_week
        """)
        
        rows = cur.fetchall()
        cur.close()
        conn.close()
        
        days = ['Vasárnap', 'Hétfő', 'Kedd', 'Szerda', 'Csütörtök', 'Péntek', 'Szombat']
        
        msg = "**Nyitvatartás:**\n```"
        for row in rows:
            day_name = days[row[0]]
            if row[3]:
                msg += f"\n{day_name}: Zárva"
            else:
                msg += f"\n{day_name}: {row[1]} - {row[2]}"
        msg += "```"
        
        await ctx.send(msg)
    except Exception as e:
        await ctx.send(f"Error: {str(e)}")

@bot.command(name='stats')
async def stats(ctx):
    """Show database statistics"""
    try:
        conn = get_db()
        cur = conn.cursor()
        
        cur.execute("SELECT COUNT(*) FROM appointments")
        total = cur.fetchone()[0]
        
        cur.execute("SELECT COUNT(*) FROM appointments WHERE datetime >= NOW()")
        upcoming = cur.fetchone()[0]
        
        cur.execute("SELECT COUNT(*) FROM appointments WHERE DATE(datetime) = CURRENT_DATE")
        today = cur.fetchone()[0]
        
        cur.close()
        conn.close()
        
        msg = f"**Statistics:**\n```"
        msg += f"\nTotal appointments: {total}"
        msg += f"\nUpcoming: {upcoming}"
        msg += f"\nToday: {today}"
        msg += "```"
        
        await ctx.send(msg)
    except Exception as e:
        await ctx.send(f"Error: {str(e)}")

@bot.command(name='query')
@commands.has_permissions(administrator=True)
async def query(ctx, *, sql: str):
    """Execute raw SQL query (admin only)"""
    try:
        conn = get_db()
        cur = conn.cursor()
        cur.execute(sql)
        
        if cur.description:
            rows = cur.fetchall()
            msg = "```"
            for row in rows[:20]:
                msg += f"\n{row}"
            if len(rows) > 20:
                msg += f"\n... and {len(rows) - 20} more rows"
            msg += "```"
        else:
            conn.commit()
            msg = "Query executed successfully."
        
        cur.close()
        conn.close()
        
        await ctx.send(msg)
    except Exception as e:
        await ctx.send(f"Error: {str(e)}")

bot.run(os.getenv('DISCORD_TOKEN'))
