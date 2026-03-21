import pygame, sys
from config import *
from mundo import GerenciadorMundo
from camera import Camera

pygame.init()
clock = pygame.time.Clock()
font = pygame.font.SysFont("arial", 22)
font_menu = pygame.font.SysFont("arial", 40)

# Música
if not pygame.mixer.music.get_busy():
    try: pygame.mixer.music.play(-1)
    except: pass

# ---------------- ESTADO ----------------
mundo = GerenciadorMundo()
camera = Camera()
estado = "menu"
dinheiro = 500; populacao = 0; nivel = 1; xp = 0; xp_max = 100
selected_index = 0
contagem_global = {item:0 for item in ITENS}
arrastando = False; drag_start = (0,0); drag_offset_start = (0,0)
ignorar_clique = False

# ---------------- FUNÇÕES ----------------
def resetar_jogo():
    global dinheiro,populacao,nivel,xp,xp_max,selected_index,contagem_global
    mundo.reset()
    camera.resetar()
    dinheiro=500; populacao=0; nivel=1; xp=0; xp_max=100
    selected_index=0; contagem_global={item:0 for item in ITENS}

def construir(gx, gy):
    global dinheiro, xp, populacao
    grid = mundo.get_grid_ativo()
    base = mundo.get_base_tile()
    item = ITENS[selected_index]
    if not (0<=gx<COLS and 0<=gy<ROWS): return
    if grid[gy][gx]!=base: return
    if dinheiro<CUSTOS[item]: return
    if item=="elevador":
        if mundo.superficie[gy][gx]=="grama" and mundo.caverna[gy][gx]=="pedra":
            mundo.superficie[gy][gx] = "elevador"
            mundo.caverna[gy][gx] = "elevador"
        else: return
    else: grid[gy][gx] = item
    # Inicializa upgrade: level 1, custo 50% do item
    mundo.upgrades[gy][gx] = {"level":1, "upgrade_cost":int(CUSTOS[item]*0.5)}
    dinheiro -= CUSTOS[item]; contagem_global[item]+=1; xp+=XP_ITENS[item]
    if item=="casa": populacao+=5
    if CLICK_SOUND: CLICK_SOUND.play()

def abrir_painel_upgrade(item, gx, gy):
    global dinheiro, populacao
    dados = mundo.upgrades[gy][gx]
    painel_w, painel_h = 300, 150
    painel_x, painel_y = WIDTH//2 - painel_w//2, HEIGHT//2 - painel_h//2
    running = True
    while running:
        mouse = pygame.mouse.get_pos()
        for event in pygame.event.get():
            if event.type==pygame.QUIT: pygame.quit(); sys.exit()
            if event.type==pygame.KEYDOWN and event.key==pygame.K_ESCAPE: running=False
            if event.type==pygame.MOUSEBUTTONDOWN and event.button==1:
                # Upgrade
                if painel_x+50<mouse[0]<painel_x+250 and painel_y+80<mouse[1]<painel_y+120:
                    if dinheiro>=dados["upgrade_cost"]:
                        dinheiro-=dados["upgrade_cost"]
                        dados["level"]+=1
                        dados["upgrade_cost"]=int(dados["upgrade_cost"]*1.5)
                        if item=="casa": populacao+=2
                        if CLICK_SOUND: CLICK_SOUND.play()
        # Painel
        pygame.draw.rect(screen,(40,40,50),(painel_x,painel_y,painel_w,painel_h),border_radius=12)
        pygame.draw.rect(screen,BRANCO,(painel_x,painel_y,painel_w,painel_h),2,border_radius=12)
        screen.blit(font.render(f"{item.upper()} - Nível {dados['level']}",True,DOURADO),(painel_x+20,painel_y+20))
        screen.blit(font.render(f"Custo upgrade: ${dados['upgrade_cost']}",True,BRANCO),(painel_x+20,painel_y+50))
        pygame.draw.rect(screen,VERDE,(painel_x+50,painel_y+80,200,40),border_radius=10)
        screen.blit(font.render("UPGRADE",True,BRANCO),(painel_x+90,painel_y+85))
        pygame.display.flip()
        clock.tick(60)

def desenhar_botao(texto,x,y,w,h,mouse):
    hover = x<mouse[0]<x+w and y<mouse[1]<y+h
    cor = (70,160,70) if hover else (50,120,50)
    pygame.draw.rect(screen,cor,(x,y,w,h),border_radius=12)
    pygame.draw.rect(screen,(255,255,255),(x,y,w,h),2,border_radius=12)
    txt=font_menu.render(texto,True,BRANCO)
    screen.blit(txt,(x+w//2-txt.get_width()//2, y+h//2-txt.get_height()//2))

def desenhar_painel():
    pygame.draw.rect(screen,(30,34,40),(MAP_WIDTH,0,PANEL_WIDTH,HEIGHT))
    titulo=font.render("V.T. UNDERGROUND",True,DOURADO)
    screen.blit(titulo,(MAP_WIDTH+PANEL_WIDTH//2-titulo.get_width()//2,15))
    pygame.draw.line(screen,(70,70,80),(MAP_WIDTH+15,45),(WIDTH-15,45),2)
    cor_camada=VERDE if mundo.camada_atual=="superficie" else DOURADO
    screen.blit(font.render(f"MAPA: {mundo.camada_atual.upper()}",True,cor_camada),(MAP_WIDTH+20,65))
    recursos=[f"Dinheiro: ${int(dinheiro)}",f"População: {populacao}",f"Nível: {nivel}",f"XP: {xp}/{xp_max}"]
    for i,txt in enumerate(recursos):
        screen.blit(font.render(txt,True,BRANCO),(MAP_WIDTH+20,105+i*30))
    screen.blit(font.render("CONSTRUIR (1-6):",True,(150,150,150)),(MAP_WIDTH+20,250))
    for i,item in enumerate(ITENS):
        cor = DOURADO if i==selected_index else BRANCO
        screen.blit(font.render(f"{i+1}-{item.upper()} (${CUSTOS[item]})",True,cor),(MAP_WIDTH+20,285+i*35))

# ---------------- LOOP PRINCIPAL ----------------
while True:
    mouse=pygame.mouse.get_pos()
    for event in pygame.event.get():
        if event.type==pygame.QUIT: pygame.quit(); sys.exit()
        if event.type==pygame.KEYDOWN:
            if pygame.K_1<=event.key<=pygame.K_6: selected_index=event.key-pygame.K_1
            if event.key==pygame.K_ESCAPE: estado="menu"
            if event.key==pygame.K_r and estado=="jogo": camera.resetar()
        if estado=="menu" and event.type==pygame.MOUSEBUTTONDOWN:
            if WIDTH//2-150<mouse[0]<WIDTH//2+150 and 320<mouse[1]<390:
                resetar_jogo(); estado="jogo"; ignorar_clique=True
            elif WIDTH//2-150<mouse[0]<WIDTH//2+150 and 410<mouse[1]<480:
                pygame.quit(); sys.exit()
        if estado=="jogo":
            if event.type==pygame.MOUSEBUTTONDOWN:
                if mouse[0]<MAP_WIDTH and event.button==3:
                    arrastando=True; drag_start=mouse; drag_offset_start=(camera.offset_x,camera.offset_y)
                if mouse[0]<MAP_WIDTH and event.button==1:
                    if ignorar_clique: ignorar_clique=False; continue
                    gx,gy=camera.tela_para_mundo(mouse[0],mouse[1])
                    grid=mundo.get_grid_ativo()
                    item=grid[gy][gx]
                    if item not in ["grama","pedra","elevador"] and mundo.upgrades[gy][gx]:
                        abrir_painel_upgrade(item,gx,gy)
                    else:
                        construir(gx,gy)
            if event.type==pygame.MOUSEBUTTONUP and event.button==3: arrastando=False
            if event.type==pygame.MOUSEMOTION and arrastando:
                dx=mouse[0]-drag_start[0]; dy=mouse[1]-drag_start[1]
                camera.offset_x=drag_offset_start[0]+dx; camera.offset_y=drag_offset_start[1]+dy
                camera.offset_x=max(-(COLS*GRID_SIZE-MAP_WIDTH),min(0,camera.offset_x))
                camera.offset_y=max(-(ROWS*GRID_SIZE-HEIGHT),min(0,camera.offset_y))
    # -------- RENDER --------
    if estado=="menu":
        screen.fill((18,18,28))
        titulo=font_menu.render("VOXEL TYCOON",True,DOURADO)
        screen.blit(titulo,(WIDTH//2-titulo.get_width()//2,180))
        sub=font.render("UNDERGROUND",True,BRANCO)
        screen.blit(sub,(WIDTH//2-sub.get_width()//2,240))
        desenhar_botao("INICIAR",WIDTH//2-150,320,300,70,mouse)
        desenhar_botao("SAIR",WIDTH//2-150,410,300,70,mouse)
    elif estado=="jogo":
        # cálculo da renda com upgrades
        renda = 0
        grid = mundo.get_grid_ativo()
        for y in range(ROWS):
            for x in range(COLS):
                tile = grid[y][x]
                if tile=="casa": renda += 2 * mundo.upgrades[y][x]["level"]
                elif tile=="fazenda": renda += 10 * mundo.upgrades[y][x]["level"]
                elif tile=="silo": renda += 25 * mundo.upgrades[y][x]["level"]
        dinheiro += renda/60
        if xp>=xp_max:
            nivel+=1; xp=0; xp_max=int(xp_max*1.5); dinheiro+=500
        mundo.desenhar(screen,camera)
        desenhar_painel()
    pygame.display.flip()
    clock.tick(60)