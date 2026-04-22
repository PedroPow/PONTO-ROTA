import discord
from discord.ext import commands
from discord.ui import View, Button
from datetime import datetime
from config import GUILD_ID, CANAL_BOTOES_PONTO, CANAL_LOG_PONTO, CANAL_PAINEL_PONTO
from datetime import datetime
import pytz
import os

brasil = pytz.timezone("America/Sao_Paulo")

inicio = datetime.now(brasil)
fim = datetime.now(brasil)

intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix="!", intents=intents)

TOKEN = os.getenv("TOKEN_PRF")  # Certifique-se de definir o TOKEN no .env ou variáveis de ambiente # Certifique-se de definir o TOKEN no .env ou variáveis de ambiente

# guard para não reenviar painel/verify em reconexões
bot._ready_sent = False


# CONFIG
CANAL_BOTOES_PONTO = 1496348445403779082
CANAL_LOG_PONTO = 1496349596090106027
CANAL_PAINEL_PONTO = 1496350066389160039

# MEMÓRIA
pontos_ativos = {}
mensagem_painel_id = None

# ----------------- PAINEL -----------------
async def atualizar_painel(guild):
    global mensagem_painel_id

    canal = guild.get_channel(CANAL_PAINEL_PONTO)
    if not canal:
        return

    if pontos_ativos:
        lista = "\n".join([f"🟢・<@{uid}>" for uid in pontos_ativos])
    else:
        lista = "Nenhum Policial em serviço."

    embed = discord.Embed(
        title="<:PRF:1495964314539130980> Painel de Ponto - PRF",
        description=f"**Policiais em serviço:**\n\n{lista}",
        color=discord.Color.yellow()
    )

    embed.set_thumbnail(url="https://media.discordapp.net/attachments/1444735189765849320/1495965745400516708/PRF.png?ex=69e8d2eb&is=69e7816b&hm=013711d4e7c3d7c993284918738c7994c16ddb24a8ffbf7c3ca0f6a6368b7be9&format=webp&quality=lossless&width=518&height=648&")

    embed.set_image(url="https://cdn.discordapp.com/attachments/1444735189765849320/1496323086155255949/FAIXA_PONTO_ELETRONICO.png?ex=69e976f8&is=69e82578&hm=ff8d1d2cf4c4bcb69ea310707e18a5dfc3d0da9ec625d8292fb2bcfe8fe59b03&")

    embed.set_footer(text="Batalhão PRF Virtual® Todos direitos reservados.", icon_url="https://media.discordapp.net/attachments/1496035727241121955/1496048035652964412/PRF.png?ex=69e91f8e&is=69e7ce0e&hm=ed2125666f9e2f5036aef0eadd58f3d3ca2f8ea9755f5ad63a164c3d0febf6d1&")    

    try:
        if mensagem_painel_id:
            msg = await canal.fetch_message(mensagem_painel_id)
            await msg.edit(embed=embed)
        else:
            msg = await canal.send(embed=embed)
            mensagem_painel_id = msg.id
    except:
        msg = await canal.send(embed=embed)
        mensagem_painel_id = msg.id

# ----------------- VIEW -----------------
class PontoView(View):
    def __init__(self):
        super().__init__(timeout=None)

    @discord.ui.button(
        label="Iniciar Ponto",
        style=discord.ButtonStyle.gray,
        emoji="<:PORTAABERTA:1496324630036877322> ",
        custom_id="abrir_ponto"
    )
    async def abrir(self, interaction: discord.Interaction, button: Button):
        user_id = interaction.user.id

        if user_id in pontos_ativos:
            await interaction.response.send_message("❌ Você já está em serviço.", ephemeral=True)
            return

        inicio = datetime.now(brasil)
        pontos_ativos[user_id] = inicio

        embed = discord.Embed(
            title="<:PORTAABERTA:1496324630036877322>  Ponto Iniciado",
            description=(
                f"> 👮🏽 Policial: {interaction.user.mention}\n"
                f"> \n"
                f"> 📅 Início: {inicio.strftime('%d/%m/%Y %H:%M:%S')}\n\n"
            ),
            color=discord.Color.yellow()
        )

        embed.set_thumbnail(url="https://media.discordapp.net/attachments/1444735189765849320/1495965745400516708/PRF.png?ex=69e8d2eb&is=69e7816b&hm=013711d4e7c3d7c993284918738c7994c16ddb24a8ffbf7c3ca0f6a6368b7be9&format=webp&quality=lossless&width=518&height=648&")

        embed.set_image(url="https://cdn.discordapp.com/attachments/1444735189765849320/1496323086155255949/FAIXA_PONTO_ELETRONICO.png?ex=69e976f8&is=69e82578&hm=ff8d1d2cf4c4bcb69ea310707e18a5dfc3d0da9ec625d8292fb2bcfe8fe59b03&")

        embed.set_footer(text="Batalhão PRF Virtual® Todos direitos reservados.", icon_url="https://media.discordapp.net/attachments/1496035727241121955/1496048035652964412/PRF.png?ex=69e91f8e&is=69e7ce0e&hm=ed2125666f9e2f5036aef0eadd58f3d3ca2f8ea9755f5ad63a164c3d0febf6d1&")          

        await interaction.response.send_message(embed=embed, ephemeral=True)

        canal_log = interaction.guild.get_channel(CANAL_LOG_PONTO)
        if canal_log:
            await canal_log.send(embed=embed)

        await atualizar_painel(interaction.guild)

    @discord.ui.button(
        label="Finalizar Ponto",
        style=discord.ButtonStyle.gray,
        emoji="<:PORTAFECHADA:1496324604996747284>",
        custom_id="fechar_ponto"
    )
    async def fechar(self, interaction: discord.Interaction, button: Button):
        user_id = interaction.user.id

        if user_id not in pontos_ativos:
            await interaction.response.send_message("❌ Você não está em serviço.", ephemeral=True)
            return

        inicio = pontos_ativos.pop(user_id)
        fim = datetime.now(brasil)

        duracao = int((fim - inicio).total_seconds())
        horas, resto = divmod(duracao, 3600)
        minutos, _ = divmod(resto, 60)

        embed = discord.Embed(
            title="<:PORTAFECHADA:1496324604996747284> Ponto Finalizado",
            description=(
                f"> 👮🏽 Policial: {interaction.user.mention}\n"
                f"> \n"
                f"> 📅 Início: {inicio.strftime('%d/%m/%Y %H:%M:%S')}\n"
                f"> \n"
                f"> 📅 Fim: {fim.strftime('%d/%m/%Y %H:%M:%S')}\n"
            ),
            color=discord.Color.yellow()
        )

        embed.set_thumbnail(url="https://media.discordapp.net/attachments/1444735189765849320/1495965745400516708/PRF.png?ex=69e8d2eb&is=69e7816b&hm=013711d4e7c3d7c993284918738c7994c16ddb24a8ffbf7c3ca0f6a6368b7be9&format=webp&quality=lossless&width=518&height=648&")

        embed.set_image(url="https://cdn.discordapp.com/attachments/1444735189765849320/1496323086155255949/FAIXA_PONTO_ELETRONICO.png?ex=69e976f8&is=69e82578&hm=ff8d1d2cf4c4bcb69ea310707e18a5dfc3d0da9ec625d8292fb2bcfe8fe59b03&")

        embed.set_footer(text="Batalhão PRF Virtual® Todos direitos reservados.", icon_url="https://media.discordapp.net/attachments/1496035727241121955/1496048035652964412/PRF.png?ex=69e91f8e&is=69e7ce0e&hm=ed2125666f9e2f5036aef0eadd58f3d3ca2f8ea9755f5ad63a164c3d0febf6d1&")        

        await interaction.response.send_message(embed=embed, ephemeral=True)

        canal_log = interaction.guild.get_channel(CANAL_LOG_PONTO)
        if canal_log:
            await canal_log.send(embed=embed)

        await atualizar_painel(interaction.guild)

# ----------------- COMANDO -----------------
@bot.event
async def on_ready():
    print(f"Logado como {bot.user}")

    guild = bot.get_guild(GUILD_ID)

    if not guild:
        print("❌ Servidor não encontrado.")
        return

    print(f"✅ Servidor conectado: {guild.name}")

    bot.add_view(PontoView())  # persistência

    await atualizar_painel(guild)

    # 🔥 ENVIO DO PAINEL DE BOTÕES (AGORA CERTO)
    canal_botoes = guild.get_channel(CANAL_BOTOES_PONTO)

    if canal_botoes:
        embed = discord.Embed(
            title="<:RELOGIO:1496308882560123000> Sistema de Ponto eletrônico - PRF",
            description="> **Clique no botão** para iniciar ou finalizar seu ponto, após iniciar você precisa seguir as regras para continuar contando!\n\n"
            "> 📢 LEIA ANTES DE COMECAR:\n\n" \
            "> Caso você fique offline ou ausente no Discord\n"
            "> seu ponto será fechado automaticamente\n\n"
            "> Clique no botão Iniciar para começar o expediente e\n"
            "> Clique no botão Fechar para finalizar o expediente.\n\n"
            "> Caso queira ver o painel de serviço, acesse o canal <#1496313782224552007>",
            color=discord.Color.yellow()
        )

        embed.set_thumbnail(url="https://media.discordapp.net/attachments/1444735189765849320/1495965745400516708/PRF.png?ex=69e8d2eb&is=69e7816b&hm=013711d4e7c3d7c993284918738c7994c16ddb24a8ffbf7c3ca0f6a6368b7be9&format=webp&quality=lossless&width=518&height=648&")

        embed.set_image(url="https://cdn.discordapp.com/attachments/1444735189765849320/1496323086155255949/FAIXA_PONTO_ELETRONICO.png?ex=69e976f8&is=69e82578&hm=ff8d1d2cf4c4bcb69ea310707e18a5dfc3d0da9ec625d8292fb2bcfe8fe59b03&")

        embed.set_footer(text="Batalhão PRF Virtual® Todos direitos reservados.", icon_url="https://media.discordapp.net/attachments/1496035727241121955/1496048035652964412/PRF.png?ex=69e91f8e&is=69e7ce0e&hm=ed2125666f9e2f5036aef0eadd58f3d3ca2f8ea9755f5ad63a164c3d0febf6d1&")

        try:
            await canal_botoes.send(embed=embed, view=PontoView())
            print("✅ Painel de ponto enviado.")
        except Exception as e:
            print(f"❌ Erro ao enviar painel: {e}")
    else:
        print("❌ Canal de botoes não encontrado.")

# ----------------- READY -----------------

    bot.add_view(PontoView())  # persistência

    # já cria/atualiza painel automaticamente ao ligar
    await atualizar_painel(guild)

    

# ----------------- RUN -----------------
if not TOKEN:
    print("ERRO: TOKEN não definido. Coloque TOKEN no .env ou variáveis de ambiente.")
else:
    bot.run(TOKEN)