import pygame,sys,os.path

palette=[]

def clip(value, minval=0, maxval=255):
    return min(maxval, max(minval, int(value)))

def YCoCgtoRGB(Y, Co, Cg):
    Co//=2
    Cg//=2
    tmp = Y   - Cg
    return (clip(tmp + Co), clip(Y + Cg), clip(tmp - Co))

#generate palette
for y, val in enumerate([0,36,73,109,146,182,219,255]):
    palette.append(YCoCgtoRGB(val,      0,        0))
for y, val in enumerate([0,36,73,109,146,182,219,255]):
    palette.append(YCoCgtoRGB(val,    128,   -y*8-y))
for y, val in enumerate([0,36,73,109,146,182,219,255]):
    palette.append(YCoCgtoRGB(val,    128, 64-y*8-y))
for y, val in enumerate([0,36,73,109,146,182,219,255]):
    palette.append(YCoCgtoRGB(val, 64-y*8-y,     64))
for y, val in enumerate([0,36,73,109,146,182,219,255]):
    palette.append(YCoCgtoRGB(val,-64-y*8-y,      0))
for y, val in enumerate([0,36,73,109,146,182,219,255]):
    palette.append(YCoCgtoRGB(val,      0,-64+y*8+y))
for y, val in enumerate([0,36,73,109,146,182,219,255]):
    palette.append(YCoCgtoRGB(val,     64,        0))
for y, val in enumerate([0,36,73,109,146,182,219,255]):
    palette.append(YCoCgtoRGB(val,      0, 64-y*8-y))

#draw isometric shapes
def draw_losange(surface,color,x,y,size,outline=None,timesw=1,timesh=1):
    p1=(x,y-size)
    doublesize=size<<1
    p2=(x+doublesize*timesw,y+(timesw-1)*size)
    p3=(x+size*(timesw-timesh)*2,y+size*timesw+size*(timesh-1))
    p4=(x-doublesize*timesh,y+(timesh-1)*size)
    if color is not None:
        pygame.draw.polygon(surface,color,(p1,p2,p3,p4))
    if outline is not None:
        pygame.draw.aalines(surface,outline,True,(p1,p2,p3,p4))

def draw_side(surface,color,x,y,size,height,sign,outline=None,timesw=1,timesh=1,closed=True):
    height*=timesh
    p1=(x-size*2*sign,y)
    p2=(x-size*2*sign,y+height)
    p3=(x+size*(timesw*2-2)*sign,y+height+size*(timesw))
    p4=(x+size*(timesw*2-2)*sign,y+size*(timesw-1))
    if color is not None:
        pygame.draw.polygon(surface,color,(p1,p2,p3,p4))
    if outline is not None:
        pygame.draw.aalines(surface,outline,closed,(p1,p2,p3,p4))

def draw_cube(surface,color,x,y,size,height,outline=None,timesw1=1,timesw2=1,timesh=1,highlight=0):
    if outline is None:
        outline=color
    draw_side(surface,palette[color+1+(highlight==1)],x-(timesw2-1)*size*2,y+(timesw2-1)*size,size,height, 1,palette[outline+1],timesw1,timesh,False)
    draw_side(surface,palette[color-1+(highlight==2)],x+(timesw1-1)*size*2,y+(timesw1-1)*size,size,height,-1,palette[outline-1],timesw2,timesh,False)
    draw_losange(surface,palette[color+(highlight==3)],x,y,size,palette[outline],timesw1,timesw2)

def draw_mouse_cube(surface,x,y,size,height,timesw1=1,timesw2=1,timesh=1,ax=0,ay=0,az=0):
    draw_side(surface,(ax,ay,az,1),x-(timesw2-1)*size*2,y+(timesw2-1)*size,size,height, 1,None,timesw1,timesh,False)
    draw_side(surface,(ax,ay,az,2),x+(timesw1-1)*size*2,y+(timesw1-1)*size,size,height,-1,None,timesw2,timesh,False)
    draw_losange(surface,(ax,ay,az,3),x,y,size,None,timesw1,timesw2)

#draw main interface
def apply_scale_function(value):
    size=1
    corse=value//6
    fine=value%6
    value = corse*10
    if fine==3 or fine==5:
        size=3
    if fine>3:
        fine+=2
    value+=fine
    return (value,size)

if __name__=="__main__":
    pygame.init()
    d=pygame.display.set_mode((0,0))
    display_width=d.get_width()
    display_height=d.get_height()
    mouse=pygame.Surface((display_width,display_height),pygame.SRCALPHA)
    originx=display_width//2
    originy=display_height//2
    basescale=display_width>>7
    scale=basescale
    scaleh=0
    cubemap={}
    selected_color=4
    colpal_w=display_width>>6
    selected_cube=(0,0,0,0)
    changed=False
    if len(sys.argv)>1:
        #load model
        with open(sys.argv[1]) as f:
            wx=ord(f.read(1))
            wy=ord(f.read(1))
            wz=ord(f.read(1))
            for x in range(wx+1):
                for y in range(wy+1):
                    for z in range(wz+1):
                        value=ord(f.read(1))
                        if value != 0:
                            cubemap[(x,y,z)]=value
    else:
        for i in range(7):
            cubemap[(1,1,i)]=4
        for x in range(-6,9):
            for y in range(-6,9):
                cubemap[(x,y,-1)]=28
    while 1:
        for event in pygame.event.get():
            if event.type==pygame.QUIT or (event.type==pygame.KEYDOWN and event.key==pygame.K_ESCAPE):
                #save model
                font=pygame.font.Font(size=colpal_w)
                backup=pygame.Surface(d.get_size())
                backup.blit(d,(0,0))
                text=""
                if len(sys.argv)>1:
                    text+=sys.argv[1].rstrip(".vox")
                pygame.key.start_text_input()
                confirm_exists=False
                while changed:
                    for event in pygame.event.get():
                        if event.type==pygame.QUIT or (event.type==pygame.KEYDOWN and event.key==pygame.K_ESCAPE):
                            pygame.quit()
                            sys.exit()
                        if event.type==pygame.KEYDOWN:
                            if event.key==pygame.K_BACKSPACE and len(text)>0:
                                text=text[:-1]
                            elif event.key==pygame.K_RETURN and text!="":
                                if os.path.exists(text+".vox") and not confirm_exists:
                                    confirm_exists=True
                                    continue
                                minx=miny=minz=maxx=maxy=maxz=None
                                for x,y,z in cubemap:
                                    if minx is None or x<minx:
                                        minx=x
                                    if maxx is None or x>maxx:
                                        maxx=x
                                    if miny is None or y<miny:
                                        miny=y
                                    if maxy is None or y>maxy:
                                        maxy=y
                                    if minz is None or z<minz:
                                        minz=z
                                    if maxz is None or z>maxz:
                                        maxz=z
                                minx-=minx%6
                                miny-=miny%6
                                minz-=minz%6
                                with open(text+".vox","wb") as f:
                                    f.write(b"%c%c%c"%(maxx-minx,maxy-miny,maxz-minz))
                                    for x in range(minx,maxx+1):
                                        for y in range(miny,maxy+1):
                                            for z in range(minz,maxz+1):
                                                if (x,y,z) in cubemap:
                                                    f.write(b"%c"%cubemap[(x,y,z)])
                                                else:
                                                    f.write(b"\0")
                                pygame.quit()
                                sys.exit()
                            elif event.unicode:
                                text+=event.unicode
                                confirm_exists=False
                    d.blit(backup,(0,0))
                    if confirm_exists:
                        s=font.render("File exists. Save anyways?> "+text+".vox", True, (255,255,255))
                    else:
                        s=font.render("Save as> "+text+".vox", True, (255,255,255))
                    d.blit(s,(colpal_w*9,colpal_w))
                    pygame.display.flip()
                pygame.quit()
                sys.exit()
            if event.type==pygame.MOUSEWHEEL:
                if pygame.key.get_mods()&pygame.KMOD_CTRL:
                    basescale+=event.precise_y
                else:
                    originx+=event.precise_x*-16
                    originy+=event.precise_y*16
            if event.type==pygame.KEYDOWN:
                if event.key==pygame.K_m:
                    newmap={}
                    for x,y,z in cubemap:
                        newmap[(-x+2,y,z)]=cubemap[(x,y,z)]
                    cubemap=newmap
                if event.key==pygame.K_n:
                    newmap={}
                    for x,y,z in cubemap:
                        newmap[(x,-y+2,z)]=cubemap[(x,y,z)]
                    cubemap=newmap
                if event.key==pygame.K_RIGHT:
                    newmap={}
                    for x,y,z in cubemap:
                        newmap[(y,-x+2,z)]=cubemap[(x,y,z)]
                    cubemap=newmap
                if event.key==pygame.K_LEFT:
                    newmap={}
                    for x,y,z in cubemap:
                        newmap[(-y+2,x,z)]=cubemap[(x,y,z)]
                    cubemap=newmap
                if event.key==pygame.K_DOWN:
                    basescale+=1
                if event.key==pygame.K_UP:
                    basescale-=1
                if event.key==pygame.K_w:
                    originy+=16
                if event.key==pygame.K_s:
                    originy-=16
                if event.key==pygame.K_a:
                    originx+=16
                if event.key==pygame.K_d:
                    originx-=16
            if event.type==pygame.MOUSEBUTTONDOWN:
                if event.pos[0]<colpal_w*8 and event.pos[1]<colpal_w*8:
                    selected_color=(event.pos[0]//colpal_w)+(event.pos[1]//colpal_w)*8
                elif event.button==3 or (event.button==1 and selected_color==0):
                    if selected_cube[3]!=0 and (selected_cube[0]-128,selected_cube[1]-128,selected_cube[2]-128) in cubemap:
                        del cubemap[(selected_cube[0]-128,selected_cube[1]-128,selected_cube[2]-128)]
                elif event.button==2:
                    x,y,z,s=selected_cube
                    x-=128
                    y-=128
                    z-=128
                    if (x,y,z) in cubemap:
                        selected_color=cubemap[(x,y,z)]
                elif event.button==1 and selected_cube[3]!=0:
                    x,y,z,s=selected_cube
                    x-=128
                    y-=128
                    z-=128
                    if cubemap[(x,y,z)]!=selected_color:
                        cubemap[(x,y,z)]=selected_color
                    elif s==3: #top
                        cubemap[(x,y,z+1)]=selected_color
                    elif s==2: #right
                        cubemap[(x+1,y,z)]=selected_color
                    elif s==1: #left
                        cubemap[(x,y+1,z)]=selected_color
                    changed=True
        scale=int(basescale)
        scaleh=int(scale*1.5)
        d.fill((0,0,0))
        mouse.fill((0,0,0,0))
        for rx,ry,rz in sorted(cubemap, key=lambda a: (a[2],a[1]+a[0])):
            color=cubemap[(rx,ry,rz)]
            highlight=0
            if selected_cube[0]-128==rx and selected_cube[1]-128==ry and selected_cube[2]-128==rz and selected_cube[3]!=0:
                highlight=selected_cube[3]
            x,sx=apply_scale_function(rx)
            y,sy=apply_scale_function(ry)
            z,sz=apply_scale_function(-rz)
            outline=color
            if not pygame.key.get_pressed()[pygame.K_SPACE] and outline&7>2:
                outline -= 2
            draw_cube(d,color,originx+x*scale*2-y*scale*2,originy+y*scale+x*scale+z*scaleh*2,scale,scaleh*2,outline,sx,sy,sz,highlight)
            draw_mouse_cube(mouse,originx+x*scale*2-y*scale*2,originy+y*scale+x*scale+z*scaleh*2,scale,scaleh*2,sx,sy,sz,rx+128,ry+128,rz+128)
        selected_cube = mouse.get_at(pygame.mouse.get_pos())
        for y in range(8):
            for x in range(8):
                px=x*colpal_w
                py=y*colpal_w
                if x+y*8==selected_color:
                    d.fill(palette[x+y*8],(px+1,py+1,colpal_w-2,colpal_w-2))
                else:
                    d.fill(palette[x+y*8],(px,py,colpal_w,colpal_w))
        pygame.display.flip()
