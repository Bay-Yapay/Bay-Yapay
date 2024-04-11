import discord
from discord.ext import commands
import requests
import json

intents = discord.Intents.default()
intents.guilds = True
intents.guild_messages = True
intents.message_content = True

bot = commands.Bot(command_prefix='BR. ', intents=intents)

# Banlama ve unvan verme komutları
@bot.command()
async def ban(ctx, member: discord.Member, *, reason=None):
    await member.ban(reason=reason)
    await ctx.send(f'{member.mention} başarıyla banlandı.')

@bot.command()
async def unban(ctx, *, member):
    banned_users = await ctx.guild.bans()
    member_name, member_discriminator = member.split('#')

    for ban_entry in banned_users:
        user = ban_entry.user

        if (user.name, user.discriminator) == (member_name, member_discriminator):
            await ctx.guild.unban(user)
            await ctx.send(f'{user.mention} başarıyla yasak kaldırıldı.')
            return

    await ctx.send(f'{member} bulunamadı.')

@bot.command()
async def unvan_ver(ctx, member: discord.Member, role: discord.Role):
    await member.add_roles(role)
    await ctx.send(f'{member.mention} başarıyla "{role.name}" unvanını aldı.')

@bot.command()
async def unvan_al(ctx, member: discord.Member, role: discord.Role):
    await member.remove_roles(role)
    await ctx.send(f'{member.mention} başarıyla "{role.name}" unvanını kaybetti.')
    
# Mute ve unmute komutları
@bot.command()
async def mute(ctx, member: discord.Member, *, reason=None):
    muted_role = discord.utils.get(ctx.guild.roles, name="Muted")

    if not muted_role:
        muted_role = await ctx.guild.create_role(name="Muted")
        for channel in ctx.guild.channels:
            await channel.set_permissions(muted_role, speak=False, send_messages=False)

    await member.add_roles(muted_role, reason=reason)
    await ctx.send(f'{member.mention} başarıyla susturuldu.')

@bot.command()
async def unmute(ctx, member: discord.Member):
    muted_role = discord.utils.get(ctx.guild.roles, name="Muted")

    if muted_role in member.roles:
        await member.remove_roles(muted_role)
        await ctx.send(f'{member.mention} başarıyla konuşturuldu.')
    else:
        await ctx.send(f'{member.mention} zaten konuşabilir durumda.')
        
# Uyarı verme komutu
@bot.command()
async def uyari_ver(ctx, member: discord.Member, *, reason=None):
    embed = discord.Embed(title="Uyarı", color=discord.Color.orange())
    embed.add_field(name="Kullanıcı", value=member.mention, inline=False)
    embed.add_field(name="Yönetici", value=ctx.author.mention, inline=False)
    embed.add_field(name="Sebep", value=reason, inline=False)

    await ctx.send(embed=embed)

# Uyarı silme komutu
@bot.command()
async def uyari_sil(ctx, message_id: int):
    message = await ctx.channel.fetch_message(message_id)
    await message.delete()
    await ctx.send(f"Uyarı (ID: {message_id}) başarıyla silindi.")

# Uyarılara bakma komutu
@bot.command()
async def uyari_liste(ctx):
    embed = discord.Embed(title="Uyarılar", color=discord.Color.orange())

    async for message in ctx.channel.history(limit=None):
        if message.author == bot.user:
            embed.add_field(name=f"Uyarı (ID: {message.id})", value=message.content, inline=False)

    await ctx.send(embed=embed)
    
# Sunucudan atma komutu
@bot.command()
async def at(ctx, member: discord.Member, *, reason=None):
    await member.kick(reason=reason)
    await ctx.send(f'{member.mention} başarıyla sunucudan atıldı.')

# Force ban (ID'ye göre banlama) komutu
@bot.command()
async def force_ban(ctx, user_id: int, *, reason=None):
    user = await bot.fetch_user(user_id)
    await ctx.guild.ban(user, reason=reason)
    await ctx.send(f'{user.mention} başarıyla ID\'ye göre banlandı.')

# Unforce ban (ID'ye göre banı kaldırma) komutu
@bot.command()
async def unforce_ban(ctx, user_id: int):
    banned_users = await ctx.guild.bans()
    for ban_entry in banned_users:
        if ban_entry.user.id == user_id:
            await ctx.guild.unban(ban_entry.user)
            await ctx.send(f'{ban_entry.user.mention} başarıyla ID\'ye göre banı kaldırıldı.')
            return
    await ctx.send(f'ID\'ye göre banlı kullanıcı bulunamadı.')
    
# Kullanıcı ismini değiştirme komutu
@bot.command()
async def isim_degistir(ctx, member: discord.Member, new_name):
    await member.edit(nick=new_name)
    await ctx.send(f'{member.mention} kullanıcısının ismi başarıyla "{new_name}" olarak değiştirildi.')

# Rol alma komutu
@bot.command()
async def rol_al(ctx, member: discord.Member, role: discord.Role):
    await member.remove_roles(role)
    await ctx.send(f'{member.mention} kullanıcısından "{role.name}" rolü başarıyla alındı.')

# Rol verme komutu
@bot.command()
async def rol_ver(ctx, member: discord.Member, role: discord.Role):
    await member.add_roles(role)
    await ctx.send(f'{member.mention} kullanıcısına "{role.name}" rolü başarıyla verildi.')
    

# Yardım komutu
@bot.command()
async def yardim(ctx):
    embed = discord.Embed(title="Komut Listesi", description="Mevcut komutlar:", color=discord.Color.blue())

    # Komutlar ve açıklamaları
    embed.add_field(name="!at", value="Belirtilen kullanıcıyı sunucudan atar.", inline=False)
    embed.add_field(name="!ban", value="Belirtilen kullanıcıyı sunucudan yasaklar.", inline=False)
    embed.add_field(name="!force_ban", value="Belirtilen kullanıcının ID'sine göre sunucudan yasaklar.", inline=False)
    embed.add_field(name="!unforce_ban", value="Belirtilen kullanıcının ID'sine göre sunucudaki yasağını kaldırır.", inline=False)
    embed.add_field(name="!mute", value="Belirtilen kullanıcıyı metin ve ses kanallarında susturur.", inline=False)
    embed.add_field(name="!unmute", value="Belirtilen kullanıcının susturmasını kaldırır.", inline=False)
    embed.add_field(name="!uyari_ver", value="Belirtilen kullanıcıya uyarı verir.", inline=False)
    embed.add_field(name="!uyari_sil", value="Belirtilen uyarıyı siler.", inline=False)
    embed.add_field(name="!uyari_liste", value="Sunucudaki tüm uyarıları listeler.", inline=False)
    embed.add_field(name="!isim_degistir", value="Belirtilen kullanıcının ismini değiştirir.", inline=False)
    embed.add_field(name="!rol_al", value="Belirtilen kullanıcının rolünü alır.", inline=False)
    embed.add_field(name="!rol_ver", value="Belirtilen kullanıcıya rol verir.", inline=False)

    await ctx.send(embed=embed)
    
# Zaman aşımına alma komutu
@bot.command()
async def zaman_asimi_al(ctx, member: discord.Member, timeout: int):
    await ctx.send(f"{member.mention} artık {timeout} saniye boyunca zaman aşımında.")

    await asyncio.sleep(timeout)
    await member.kick(reason="Zaman aşımı")

    await ctx.send(f"{member.mention} zaman aşımından dolayı atıldı.")

# Zaman aşımından çıkarma komutu
@bot.command()
async def zaman_asimi_cikar(ctx, member: discord.Member):
    await ctx.send(f"{member.mention} artık zaman aşımında değil.")
    
# WP kur komutu
@bot.command()
async def kur(ctx, para_birimi, miktar: float):
    if para_birimi.lower() == 'dolar':
        response = requests.get('https://api.exchangerate-api.com/v4/latest/USD')
        data = response.json()
        kur = data['rates']['TRY']
        toplam = miktar * kur
        await ctx.send(f'{miktar} USD toplamda {toplam} TRY yapar.')

    elif para_birimi.lower() == 'euro':
        response = requests.get('https://api.exchangerate-api.com/v4/latest/EUR')
        data = response.json()
        kur = data['rates']['TRY']
        toplam = miktar * kur
        await ctx.send(f'{miktar} EUR toplamda {toplam} TRY yapar.')

    elif para_birimi.lower() == 'sterlin' or para_birimi.lower() == 'pound':
        response = requests.get('https://api.exchangerate-api.com/v4/latest/GBP')
        data = response.json()
        kur = data['rates']['TRY']
        toplam = miktar * kur
        await ctx.send(f'{miktar} GBP toplamda {toplam} TRY yapar.')

    else:
        await ctx.send('Geçersiz para birimi. Lütfen "dolar", "euro" veya "sterlin" olarak belirtin.')
        
def load_auto_responses():
    try:
        with open('auto_responses.json', 'r') as file:
            auto_responses = json.load(file)
    except FileNotFoundError:
        auto_responses = {}
    return auto_responses

def save_auto_responses(auto_responses):
    with open('auto_responses.json', 'w') as file:
        json.dump(auto_responses, file, indent=4)

async def process_auto_responses(message):
    content = message.content.lower()
    auto_responses = load_auto_responses()

    for keyword, response in auto_responses.items():
        if keyword in content:
            await message.channel.send(response)
            break

# Yeni otomatik cevap eklemek için komut
@bot.command()
async def oto_cevap_ekle(ctx, keyword, *, response):
    auto_responses = load_auto_responses()
    auto_responses[keyword.lower()] = response
    save_auto_responses(auto_responses)
    await ctx.send(f'{keyword} kelimesine özel cevap başarıyla eklendi.')

# Botun cevap vereceği olaylar
@bot.event
async def on_message(message):
    if message.author == bot.user:
        return
    
    await process_auto_responses(message)
    await bot.process_commands(message)

# Tokeninizi Buraya Yapıştırın 
bot.run('token'')