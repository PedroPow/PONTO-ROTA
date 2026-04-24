import discord
from discord.ext import commands
from discord.ui import View, Button
from datetime import datetime
from config import GUILD_ID, CANAL_BOTOES_PONTO, CANAL_LOG_PONTO, CANAL_PAINEL_PONTO
from datetime import datetime
import pytz
import os
import asyncio

brasil = pytz.timezone("America/Sao_Paulo")

inicio = datetime.now(brasil)
fim = datetime.now(brasil)

intents = discord.Intents.default()
intents.message_content = True
intents.members = True
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
confirmacoes_pendentes = {}
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
        title="<:FT:1496355093476278404>  Painel de Ponto - FT",
        description=f"**Policiais em serviço:**\n\n{lista}",
        color=discord.Color.yellow()
    )

    embed.set_thumbnail(url="https://cdn.discordapp.com/attachments/1444735189765849320/1495479496084557834/FT.png?ex=69ebab50&is=69ea59d0&hm=ea01d5b5c6a81a64f829e72687eeee1596c655bf7a1cedd2868436f5190f1e1b&")

    embed.set_image(url="https://cdn.discordapp.com/attachments/1444735189765849320/1496356400673067128/FAIXA_PONTO_ELETRONICO_FT.png?ex=69eb903e&is=69ea3ebe&hm=9e6bfbf60ce233110dfa4304f0a77d1e7d28b652dc769de69cdfe0520ea45fef&")

    embed.set_footer(text="Batalhão FT Virtual® Todos direitos reservados.", icon_url="https://cdn.discordapp.com/attachments/1444735189765849320/1495479496084557834/FT.png?ex=69ebab50&is=69ea59d0&hm=ea01d5b5c6a81a64f829e72687eeee1596c655bf7a1cedd2868436f5190f1e1b&")    

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
            title="<:PORTAABERTA:1496357008884895935> Ponto Iniciado",
            description=(
                f"> 👮🏽 Policial: {interaction.user.mention}\n"
                f"> \n"
                f"> 📅 Início: {inicio.strftime('%d/%m/%Y %H:%M:%S')}\n\n"
            ),
            color=discord.Color.green()
        )

        embed.set_thumbnail(url="https://cdn.discordapp.com/attachments/1444735189765849320/1495479496084557834/FT.png?ex=69ebab50&is=69ea59d0&hm=ea01d5b5c6a81a64f829e72687eeee1596c655bf7a1cedd2868436f5190f1e1b&")

        embed.set_image(url="https://cdn.discordapp.com/attachments/1444735189765849320/1496356400673067128/FAIXA_PONTO_ELETRONICO_FT.png?ex=69eb903e&is=69ea3ebe&hm=9e6bfbf60ce233110dfa4304f0a77d1e7d28b652dc769de69cdfe0520ea45fef&")

        embed.set_footer(text="Batalhão FT Virtual® Todos direitos reservados.", icon_url="https://cdn.discordapp.com/attachments/1444735189765849320/1495479496084557834/FT.png?ex=69ebab50&is=69ea59d0&hm=ea01d5b5c6a81a64f829e72687eeee1596c655bf7a1cedd2868436f5190f1e1b&")           

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
            color=discord.Color.red()
        )

        embed.set_thumbnail(url="https://cdn.discordapp.com/attachments/1444735189765849320/1495479496084557834/FT.png?ex=69ebab50&is=69ea59d0&hm=ea01d5b5c6a81a64f829e72687eeee1596c655bf7a1cedd2868436f5190f1e1b&")

        embed.set_image(url="https://cdn.discordapp.com/attachments/1444735189765849320/1496356400673067128/FAIXA_PONTO_ELETRONICO_FT.png?ex=69eb903e&is=69ea3ebe&hm=9e6bfbf60ce233110dfa4304f0a77d1e7d28b652dc769de69cdfe0520ea45fef&")

        embed.set_footer(text="Batalhão FT Virtual® Todos direitos reservados.", icon_url="https://cdn.discordapp.com/attachments/1444735189765849320/1495479496084557834/FT.png?ex=69ebab50&is=69ea59d0&hm=ea01d5b5c6a81a64f829e72687eeee1596c655bf7a1cedd2868436f5190f1e1b&")        

        await interaction.response.send_message(embed=embed, ephemeral=True)

        canal_log = interaction.guild.get_channel(CANAL_LOG_PONTO)
        if canal_log:
            await canal_log.send(embed=embed)

        await atualizar_painel(interaction.guild)

# ----------------- CONFIRMAR PONTO -----------------

class ConfirmarPresencaView(View):
    def __init__(self, user_id):
        super().__init__(timeout=60)
        self.user_id = user_id

    @discord.ui.button(
        label="Estou em serviço",
        style=discord.ButtonStyle.gray,
        emoji="<:AMARELO:1496016145902338069>",
        custom_id="confirmar_presenca"
    )
    async def confirmar(self, interaction: discord.Interaction, button: Button):
        if interaction.user.id != self.user_id:
            return await interaction.response.send_message(
                "❌ Esse botão não é pra você.",
                ephemeral=True
            )

        confirmacoes_pendentes[self.user_id] = True

        await interaction.response.send_message(
            "✅ Presença confirmada!",
            ephemeral=True
        )


# ----------------- LOOP DE VERIFICAÇÃO DE ATIVIDADE -----------------

async def sistema_check_ativo():
    await bot.wait_until_ready()

    while not bot.is_closed():
        await asyncio.sleep(3000)  # espera 50 minutos (3000 segundos) entre cada verificação

        for user_id in list(pontos_ativos.keys()):
            guild = bot.get_guild(GUILD_ID)
            membro = guild.get_member(user_id)

            if not membro:
                try:
                    membro = await guild.fetch_member(user_id)  # 🔥 FORÇA buscar
                except:
                    print(f"❌ Não achei o membro {user_id}")
                    continue

            if not membro:
                continue

            confirmacoes_pendentes[user_id] = False

            view = ConfirmarPresencaView(user_id)

            embed = discord.Embed(
                title="✅ Verificação de Atividade",
                description=(
                    f"{membro.mention}, confirme que você está em serviço.\n\n"
                    f"> Caso você não confirme, seu ponto será encerrado por inatividade.\n"
                    f"> ㅤ\n"
                    f"> Se você estiver presente, clique no botão abaixo para confirmar sua presença.\n\n"
                    f" Você tem `60 segundos` para responder."
                ),
                color=discord.Color.yellow()
            )

            embed.set_thumbnail(url="https://cdn.discordapp.com/attachments/1444735189765849320/1495479496084557834/FT.png?ex=69ebab50&is=69ea59d0&hm=ea01d5b5c6a81a64f829e72687eeee1596c655bf7a1cedd2868436f5190f1e1b&")

            embed.set_image(url="https://cdn.discordapp.com/attachments/1444735189765849320/1496356400673067128/FAIXA_PONTO_ELETRONICO_FT.png?ex=69eb903e&is=69ea3ebe&hm=9e6bfbf60ce233110dfa4304f0a77d1e7d28b652dc769de69cdfe0520ea45fef&")

            embed.set_footer(text="Batalhão FT Virtual® Todos direitos reservados.", icon_url="https://cdn.discordapp.com/attachments/1444735189765849320/1495479496084557834/FT.png?ex=69ebab50&is=69ea59d0&hm=ea01d5b5c6a81a64f829e72687eeee1596c655bf7a1cedd2868436f5190f1e1b&")  

            try:
                msg = await membro.send(embed=embed, view=view)
            except:
                # Se não conseguir DM, manda no canal de log
                canal = guild.get_channel(CANAL_LOG_PONTO)
                if canal:
                    msg = await canal.send(content=membro.mention, embed=embed, view=view)
                else:
                    continue

            await asyncio.sleep(60)

            if not confirmacoes_pendentes.get(user_id):
                inicio = pontos_ativos.pop(user_id)
                fim = datetime.now(brasil)

                duracao = int((fim - inicio).total_seconds()) # calcula duração total em segundos
                horas, resto = divmod(duracao, 3600) # calcula horas
                minutos, _ = divmod(resto, 60) # calcula minutos

                embed_fechado = discord.Embed(
                    title="<:PORTAFECHADA:1496357051956199515> Ponto Finalizado por Inatividade",
                    description=(
                    f"> 👮🏽 Policial: {membro.mention}\n"
                    f"> \n"
                    f"> 📅 Início: {inicio.strftime('%d/%m/%Y %H:%M:%S')}\n"
                    f"> \n"
                    f"> 📅 Fim: {fim.strftime('%d/%m/%Y %H:%M:%S')}\n\n"
                    f">  Motivo: Não confirmou presença."
                    ),
                    color=discord.Color.red()
                )
                embed_fechado.set_thumbnail(url="https://cdn.discordapp.com/attachments/1444735189765849320/1495479496084557834/FT.png?ex=69ebab50&is=69ea59d0&hm=ea01d5b5c6a81a64f829e72687eeee1596c655bf7a1cedd2868436f5190f1e1b&")

                embed_fechado.set_image(url="https://cdn.discordapp.com/attachments/1444735189765849320/1496356400673067128/FAIXA_PONTO_ELETRONICO_FT.png?ex=69eb903e&is=69ea3ebe&hm=9e6bfbf60ce233110dfa4304f0a77d1e7d28b652dc769de69cdfe0520ea45fef&")

                embed_fechado.set_footer(text="Batalhão FT Virtual® Todos direitos reservados.", icon_url="https://cdn.discordapp.com/attachments/1444735189765849320/1495479496084557834/FT.png?ex=69ebab50&is=69ea59d0&hm=ea01d5b5c6a81a64f829e72687eeee1596c655bf7a1cedd2868436f5190f1e1b&")                

                canal_log = guild.get_channel(CANAL_LOG_PONTO)
                if canal_log:
                    await canal_log.send(embed=embed_fechado)

                await atualizar_painel(guild)        

# ----------------- COMANDO -----------------
@bot.event
async def on_ready():
    print(f"Logado como {bot.user}")

    guild = bot.get_guild(GUILD_ID)

    if not guild:
        print("❌ Servidor não encontrado.")
        return

    print(f"✅ Servidor conectado: {guild.name}")

    bot.add_view(PontoView())

    await atualizar_painel(guild)

    # ✅ CHECK ATIVO (CORRETO)
    if not hasattr(bot, "check_loop_started"):
        bot.loop.create_task(sistema_check_ativo())
        bot.check_loop_started = True

    # 🔥 ENVIO DO PAINEL DE BOTÕES (AGORA CERTO)
    canal_botoes = guild.get_channel(CANAL_BOTOES_PONTO)

    if canal_botoes:
        embed = discord.Embed(
            title="<:RELOGIO:1496355225722814616> Sistema de Ponto eletrônico - FT Virtual",
            description="> **Clique no botão** para iniciar ou finalizar seu ponto, após iniciar você precisa seguir as regras para continuar contando!\n\n"
            "> 📢 LEIA ANTES DE COMECAR:\n\n" \
            "> Caso você fique offline ou ausente no Discord\n"
            "> seu ponto será fechado automaticamente\n\n"
            "> Clique no botão Iniciar para começar o expediente e\n"
            "> Clique no botão Fechar para finalizar o expediente.\n\n"
            "> Caso queira ver o painel de serviço, acesse o canal <#1496313782224552007>",
            color=discord.Color.yellow()
        )

        embed.set_thumbnail(url="https://cdn.discordapp.com/attachments/1444735189765849320/1495479496084557834/FT.png?ex=69ebab50&is=69ea59d0&hm=ea01d5b5c6a81a64f829e72687eeee1596c655bf7a1cedd2868436f5190f1e1b&")

        embed.set_image(url="https://cdn.discordapp.com/attachments/1444735189765849320/1496356400673067128/FAIXA_PONTO_ELETRONICO_FT.png?ex=69eb903e&is=69ea3ebe&hm=9e6bfbf60ce233110dfa4304f0a77d1e7d28b652dc769de69cdfe0520ea45fef&")

        embed.set_footer(text="Batalhão FT Virtual® Todos direitos reservados.", icon_url="https://cdn.discordapp.com/attachments/1444735189765849320/1495479496084557834/FT.png?ex=69ebab50&is=69ea59d0&hm=ea01d5b5c6a81a64f829e72687eeee1596c655bf7a1cedd2868436f5190f1e1b&")       

        try:
            await canal_botoes.send(embed=embed, view=PontoView())
            print("✅ Painel de ponto enviado.")
        except Exception as e:
            print(f"❌ Erro ao enviar painel: {e}")
    else:
        print("❌ Canal de botoes não encontrado.")

# ----------------- READY -----------------

    # já cria/atualiza painel automaticamente ao ligar
    await atualizar_painel(guild)

# ----------------- RUN -----------------
if not TOKEN:
    print("ERRO: TOKEN não definido. Coloque TOKEN no .env ou variáveis de ambiente.")
else:
    bot.run(TOKEN)