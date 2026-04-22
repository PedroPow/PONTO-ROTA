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
TOKEN = os.getenv("TOKEN_ROTA")  # Certifique-se de definir o TOKEN no .env ou variáveis de ambiente # Certifique-se de definir o TOKEN no .env ou variáveis de ambiente

# guard para não reenviar painel/verify em reconexões
bot._ready_sent = False


# CONFIG
GUILD_ID = 1492395180119293962

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
        title="<:FT:1496355093476278404> Painel de Ponto - FT",
        description=f"**Policiais em serviço:**\n\n{lista}",
        color=discord.Color.yellow()
    )

    embed.set_thumbnail(url="https://cdn.discordapp.com/attachments/1444735189765849320/1495479496084557834/FT.png?ex=69e90850&is=69e7b6d0&hm=6f1b2ae4ab83875f692a56c82576c6cb3adf38e214c81d7e1a0522f80519aa3c&")

    embed.set_image(url="https://cdn.discordapp.com/attachments/1444735189765849320/1496356400673067128/FAIXA_PONTO_ELETRONICO_FT.png?ex=69e995fe&is=69e8447e&hm=24ff17046f115679f3326dfb9664f5f9a97fb9c69b1545e12a14e13f1f4be759&")

    embed.set_footer(text="Batalhão FT Virtual® Todos direitos reservados.", icon_url="https://cdn.discordapp.com/attachments/1444735189765849320/1495479496084557834/FT.png?ex=69e90850&is=69e7b6d0&hm=6f1b2ae4ab83875f692a56c82576c6cb3adf38e214c81d7e1a0522f80519aa3c&")    

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
            title="<:PORTAABERTA:1496357008884895935>  Ponto Iniciado",
            description=(
                f"> 👮🏽 Policial: {interaction.user.mention}\n"
                f"> \n"
                f"> 📅 Início: {inicio.strftime('%d/%m/%Y %H:%M:%S')}\n\n"
            ),
            color=discord.Color.yellow()
        )

        embed.set_thumbnail(url="https://cdn.discordapp.com/attachments/1444735189765849320/1495479496084557834/FT.png?ex=69e90850&is=69e7b6d0&hm=6f1b2ae4ab83875f692a56c82576c6cb3adf38e214c81d7e1a0522f80519aa3c&")

        embed.set_image(url="https://cdn.discordapp.com/attachments/1444735189765849320/1496356400673067128/FAIXA_PONTO_ELETRONICO_FT.png?ex=69e995fe&is=69e8447e&hm=24ff17046f115679f3326dfb9664f5f9a97fb9c69b1545e12a14e13f1f4be759&")

        embed.set_footer(text="Batalhão FT Virtual® Todos direitos reservados.", icon_url="https://cdn.discordapp.com/attachments/1444735189765849320/1495479496084557834/FT.png?ex=69e90850&is=69e7b6d0&hm=6f1b2ae4ab83875f692a56c82576c6cb3adf38e214c81d7e1a0522f80519aa3c&")          

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
            title="<:PORTAFECHADA:1496357051956199515> Ponto Finalizado",
            description=(
                f"> 👮🏽 Policial: {interaction.user.mention}\n"
                f"> \n"
                f"> 📅 Início: {inicio.strftime('%d/%m/%Y %H:%M:%S')}\n"
                f"> \n"
                f"> 📅 Fim: {fim.strftime('%d/%m/%Y %H:%M:%S')}\n"
            ),
            color=discord.Color.yellow()
        )

        embed.set_thumbnail(url="https://cdn.discordapp.com/attachments/1444735189765849320/1495479496084557834/FT.png?ex=69e90850&is=69e7b6d0&hm=6f1b2ae4ab83875f692a56c82576c6cb3adf38e214c81d7e1a0522f80519aa3c&")

        embed.set_image(url="https://cdn.discordapp.com/attachments/1444735189765849320/1496356400673067128/FAIXA_PONTO_ELETRONICO_FT.png?ex=69e995fe&is=69e8447e&hm=24ff17046f115679f3326dfb9664f5f9a97fb9c69b1545e12a14e13f1f4be759&")

        embed.set_footer(text="Batalhão FT Virtual® Todos direitos reservados.", icon_url="https://cdn.discordapp.com/attachments/1444735189765849320/1495479496084557834/FT.png?ex=69e90850&is=69e7b6d0&hm=6f1b2ae4ab83875f692a56c82576c6cb3adf38e214c81d7e1a0522f80519aa3c&")        

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
            title="<:RELOGIO:1496355225722814616> Sistema de Ponto eletrônico - FT",
            description="> **Clique no botão** para iniciar ou finalizar seu ponto, após iniciar você precisa seguir as regras para continuar contando!\n\n"
            "> 📢 LEIA ANTES DE COMECAR:\n\n" \
            "> Caso você fique offline ou ausente no Discord\n"
            "> seu ponto será fechado automaticamente\n\n"
            "> Clique no botão Iniciar para começar o expediente e\n"
            "> Clique no botão Fechar para finalizar o expediente.\n\n"
            "> Caso queira ver o painel de serviço, acesse o canal <#1496350066389160039>",
            color=discord.Color.yellow()
        )

        embed.set_thumbnail(url="https://cdn.discordapp.com/attachments/1444735189765849320/1495479496084557834/FT.png?ex=69e90850&is=69e7b6d0&hm=6f1b2ae4ab83875f692a56c82576c6cb3adf38e214c81d7e1a0522f80519aa3c&")

        embed.set_image(url="https://cdn.discordapp.com/attachments/1444735189765849320/1496356400673067128/FAIXA_PONTO_ELETRONICO_FT.png?ex=69e995fe&is=69e8447e&hm=24ff17046f115679f3326dfb9664f5f9a97fb9c69b1545e12a14e13f1f4be759&")

        embed.set_footer(text="Batalhão FT Virtual® Todos direitos reservados.", icon_url="https://cdn.discordapp.com/attachments/1444735189765849320/1495479496084557834/FT.png?ex=69e90850&is=69e7b6d0&hm=6f1b2ae4ab83875f692a56c82576c6cb3adf38e214c81d7e1a0522f80519aa3c&")

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