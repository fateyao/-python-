"""在重力模拟游戏中将卫星推入火星轨道。"""
import os
import math
import random
import pygame as pg

WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
LT_BLUE = (173, 216, 230)

class Satellite(pg.sprite.Sprite):
    """定义朝向火星旋转的卫星图像，以及呈坠毁和燃烧状态的卫星图像。"""
    
    def __init__(self, background):
        super().__init__()
        self.background = background
        self.image_sat = pg.image.load("satellite.png").convert()
        self.image_crash = pg.image.load("satellite_crash_40x33.png").convert()
        self.image = self.image_sat
        self.rect = self.image.get_rect()
        self.image.set_colorkey(BLACK)  # 设置透明色
        self.x = random.randrange(315, 425)
        self.y = random.randrange(70, 180) 
        self.dx = random.choice([-3, 3])
        self.dy = 0
        self.heading = 0  # 初始化遥感天线方向
        self.fuel = 100
        self.mass = 1
        self.distance = 0  # 设置卫星和火星之间的初始距离
        self.thrust = pg.mixer.Sound('thrust_audio.ogg')
        self.thrust.set_volume(0.07)  # 有效值范围为0~1

    def thruster(self, dx, dy):
        """点燃推进器时，程序执行的相关动作"""
        self.dx += dx
        self.dy += dy
        self.fuel -= 2
        self.thrust.play()     

    def check_keys(self):
        """检查用户是否按下方向键，并调用thruster() 函数。"""
        keys = pg.key.get_pressed()       
        # 点燃推进器
        if keys[pg.K_RIGHT]:
            self.thruster(dx=0.05, dy=0)
        elif keys[pg.K_LEFT]:
            self.thruster(dx=-0.05, dy=0)
        elif keys[pg.K_UP]:
            self.thruster(dx=0, dy=-0.05)  
        elif keys[pg.K_DOWN]:
            self.thruster(dx=0, dy=0.05)
            
    def locate(self, planet):
        """计算卫星与火星之间的距离，让卫星天线朝向火星所在的方向。"""
        px, py = planet.x, planet.y
        dist_x = self.x - px
        dist_y = self.y - py
        # 计算卫星指向行星的方向
        planet_dir_radians = math.atan2(dist_x, dist_y)
        self.heading = planet_dir_radians * 180 / math.pi
        self.heading -= 90  # 精灵的飞行方式为尾巴先飞
        self.distance = math.hypot(dist_x, dist_y)

    def rotate(self):
        """根据角度数旋转卫星方向，使卫星的天线朝向火星。"""
        self.image = pg.transform.rotate(self.image_sat, self.heading)
        self.rect = self.image.get_rect()

    def path(self):
        """改变卫星所处的位置，并绘制卫星的运动轨迹"""
        last_center = (self.x, self.y)
        self.x += self.dx
        self.y += self.dy
        pg.draw.line(self.background, WHITE, last_center, (self.x, self.y))

    def update(self):
        """在游戏运行期间更新卫星对象。"""
        self.check_keys()
        self.rotate()
        self.path()
        self.rect.center = (self.x, self.y)        
        # 将卫星图像更改为大气中呈燃烧状态的红色卫星图像
        if self.dx == 0 and self.dy == 0:
            self.image = self.image_crash
            self.image.set_colorkey(BLACK)
            
class Planet(pg.sprite.Sprite):
    """定义火星的旋转方式，计算其向卫星施加的重力。"""
    
    def __init__(self):
        super().__init__()
        self.image_mars = pg.image.load("mars.png").convert()
        self.image_water = pg.image.load("mars_water.png").convert() 
        self.image_copy = pg.transform.scale(self.image_mars, (100, 100)) 
        self.image_copy.set_colorkey(BLACK) 
        self.rect = self.image_copy.get_rect()
        self.image = self.image_copy
        self.mass = 2000 
        self.x = 400 
        self.y = 320
        self.rect.center = (self.x, self.y)
        self.angle = math.degrees(0)
        self.rotate_by = math.degrees(0.01)

    def rotate(self):
        """在每次游戏循环中，旋转火星图片。"""
        last_center = self.rect.center
        self.image = pg.transform.rotate(self.image_copy, self.angle)
        self.rect = self.image.get_rect()
        self.rect.center = last_center
        self.angle += self.rotate_by

    def gravity(self, satellite):
        """计算重力对卫星运行方式的影响。"""
        G = 1.0  # 本游戏采用的万有引力常数
        dist_x = self.x - satellite.x
        dist_y = self.y - satellite.y
        distance = math.hypot(dist_x, dist_y)     
        # 标准化为单位向量
        dist_x /= distance
        dist_y /= distance
        # 计算重力
        force = G * (satellite.mass * self.mass) / (math.pow(distance, 2))
        satellite.dx += (dist_x * force)
        satellite.dy += (dist_y * force)
        
    def update(self):
        """调用rotate()函数。"""
        self.rotate()

def calc_eccentricity(dist_list):
    """根据半径列表计算离心率，并返回计算结果。"""
    apoapsis = max(dist_list)
    periapsis = min(dist_list)
    eccentricity = (apoapsis - periapsis) / (apoapsis + periapsis)
    return eccentricity

def instruct_label(screen, text, color, x, y):
    """按照给定的颜色，将字符串列表中的文本显示到屏幕的指定坐标位置上。"""
    instruct_font = pg.font.SysFont(None, 25)
    line_spacing = 22
    for index, line in enumerate(text):
        label = instruct_font.render(line, True, color, BLACK)
        screen.blit(label, (x, y + index * line_spacing))

def box_label(screen, text, dimensions):
    """根据文本内容生成一些固定大小的标签。"""
    readout_font = pg.font.SysFont(None, 27)
    base = pg.Rect(dimensions)
    pg.draw.rect(screen, WHITE, base, 0)
    label = readout_font.render(text, True, BLACK)
    label_rect = label.get_rect(center=base.center)
    screen.blit(label, label_rect)

def mapping_on(planet):
    """显示代表火星土壤水分的图像"""
    last_center = planet.rect.center
    planet.image_copy = pg.transform.scale(planet.image_water, (100, 100))
    planet.image_copy.set_colorkey(BLACK)
    planet.rect = planet.image_copy.get_rect()
    planet.rect.center = last_center

def mapping_off(planet):
    """恢复成正常的火星图像。"""
    planet.image_copy = pg.transform.scale(planet.image_mars, (100, 100))
    planet.image_copy.set_colorkey(BLACK)

def cast_shadow(screen):
    """在屏幕上添加可选的明暗分界线和火星后面的阴影区。"""
    shadow = pg.Surface((400, 100), flags=pg.SRCALPHA)  # 用元组表示宽和高
    shadow.fill((0, 0, 0, 210))  # 最后一个数字表示设置的透明度
    screen.blit(shadow, (0, 270))  # 用元组表示左上角坐标

def main():
    """设置读数标签和游戏说明，创建游戏对象，执行游戏循环。"""
    pg.init()  # 初始化pygame模块
    
    # 设置显示器
    os.environ['SDL_VIDEO_WINDOW_POS'] = '700, 100'  # 设置窗口原点
    screen = pg.display.set_mode((800, 645), pg.FULLSCREEN) 
    pg.display.set_caption("Mars Orbiter")
    background = pg.Surface(screen.get_size())

    # 启用混音器
    pg.mixer.init()

    intro_text = [
        ' The Mars Orbiter experienced an error during Orbit insertion.',
        ' Use thrusters to correct to a circular mapping orbit without',
        ' running out of propellant or burning up in the atmosphere.'
        ]
 
    instruct_text1 = [
        'Orbital altitude must be within 69-120 miles',
        'Orbital Eccentricity must be < 0.05',
        'Avoid top of atmosphere at 68 miles'    
        ]

    instruct_text2 = [
        'Left Arrow = Decrease Dx', 
        'Right Arrow = Increase Dx', 
        'Up Arrow = Decrease Dy', 
        'Down Arrow = Increase Dy', 
        'Space Bar = Clear Path',
        'Escape = Exit Full Screen'        
        ]  

    # 分别实例化一个火星对象和卫星对象
    planet = Planet()
    planet_sprite = pg.sprite.Group(planet)
    sat = Satellite(background)    
    sat_sprite = pg.sprite.Group(sat)

    # 设置轨道圆化的验证方式
    dist_list = []  
    eccentricity = 1
    eccentricity_calc_interval = 5  # 对高为120英里的运行轨道进行采样率优化
    
    # 设置时间间隔
    clock = pg.time.Clock()
    fps = 30
    tick_count = 0

    # 跟踪是否开启了土壤水分测绘功能
    mapping_enabled = False
    
    running = True
    while running:
        clock.tick(fps)
        tick_count += 1
        dist_list.append(sat.distance)
        
        # 获取玩家的按键输入
        for event in pg.event.get():
            if event.type == pg.QUIT:  # 关闭游戏窗口
                running = False
            elif event.type == pg.KEYDOWN and event.key == pg.K_ESCAPE:
                screen = pg.display.set_mode((800, 645))  # 游戏退出全屏模式
            elif event.type == pg.KEYDOWN and event.key == pg.K_SPACE:
                background.fill(BLACK)  # 清除卫星运动轨迹
            elif event.type == pg.KEYUP:
                sat.thrust.stop()  # 关闭音效
                mapping_off(planet)  # 将卫星土壤水分含量切换至正常的卫星图像
            elif mapping_enabled:
                if event.type == pg.KEYDOWN and event.key == pg.K_m:
                    mapping_on(planet)

        # 获取卫星到火星的距离，计算卫星所受的重力
        sat.locate(planet)  
        planet.gravity(sat)

        # 计算轨道离心率
        if tick_count % (eccentricity_calc_interval * fps) == 0:
            eccentricity = calc_eccentricity(dist_list)
            dist_list = []              

        # 用绘图命令重绘窗口背景，避免擦除卫星的运动轨迹
        screen.blit(background, (0, 0))
        
        # 处理燃料耗尽或运行轨迹高度偏低的情况
        if sat.fuel <= 0:
            instruct_label(screen, ['Fuel Depleted!'], RED, 340, 195)
            sat.fuel = 0
            sat.dx = 2
        elif sat.distance <= 68:
            instruct_label(screen, ['Atmospheric Entry!'], RED, 320, 195)
            sat.dx = 0
            sat.dy = 0

        # 启用土壤湿度测绘功能
        if eccentricity < 0.05 and sat.distance >= 69 and sat.distance <= 120:
            map_instruct = ['Press & hold M to map soil moisture']
            instruct_label(screen, map_instruct, LT_BLUE, 250, 175)
            mapping_enabled = True
        else:
            mapping_enabled = False

        planet_sprite.update()
        planet_sprite.draw(screen)
        sat_sprite.update()
        sat_sprite.draw(screen)

        # 显示游戏介绍文本，并使其持续15秒
        if pg.time.get_ticks() <= 15000:  # 单位：毫秒
            instruct_label(screen, intro_text, GREEN, 145, 100)

        # 显示遥测结果和说明
        box_label(screen, 'Dx', (70, 20, 75, 20))
        box_label(screen, 'Dy', (150, 20, 80, 20))
        box_label(screen, 'Altitude', (240, 20, 160, 20))
        box_label(screen, 'Fuel', (410, 20, 160, 20))
        box_label(screen, 'Eccentricity', (580, 20, 150, 20))
        
        box_label(screen, '{:.1f}'.format(sat.dx), (70, 50, 75, 20))     
        box_label(screen, '{:.1f}'.format(sat.dy), (150, 50, 80, 20))
        box_label(screen, '{:.1f}'.format(sat.distance), (240, 50, 160, 20))
        box_label(screen, '{}'.format(sat.fuel), (410, 50, 160, 20))
        box_label(screen, '{:.8f}'.format(eccentricity), (580, 50, 150, 20))
          
        instruct_label(screen, instruct_text1, WHITE, 10, 575)
        instruct_label(screen, instruct_text2, WHITE, 570, 510)
      
        # 添加明暗分界线和阴影边框
        cast_shadow(screen)
        pg.draw.rect(screen, WHITE, (1, 1, 798, 643), 1)

        pg.display.flip()

if __name__ == "__main__":
    main()
