"""基于pygame模拟艾奥星体上的特瓦什塔尔火山羽流"""
import sys
import math
import random
import pygame as pg

pg.init()  # 初始化pygame

# 定义颜色表
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
LT_GRAY = (180, 180, 180)
GRAY = (120, 120, 120)
DK_GRAY = (80, 80, 80)


class Particle(pg.sprite.Sprite):
    """生成模拟火山喷射出的粒子。"""

    gases_colors = {'SO2': LT_GRAY, 'CO2': GRAY, 'H2S': DK_GRAY, 'H2O': WHITE}

    VENT_LOCATION_XY = (320, 300)  # 火山口，也表示所有粒子的“发射点”
    IO_SURFACE_Y = 308
    # 二氧化硫羽流的外边缘与艾奥星体表面相交处的最高点的值。将在该值处让所有下落的粒子都停下来，因此最终显示的图像是针对二氧化硫粒子优化过的。
    GRAVITY = 0.5  # 像素/帧的值，游戏每次循环时，dy都会累加上该值
    VELOCITY_SO2 = 8  # 像素/帧的值

    # 速度（二氧化硫原子质量/粒子原子质量）的标量
    vel_scalar = {'SO2': 1, 'CO2': 1.45, 'H2S': 1.9, 'H2O': 3.6}

    def __init__(self, screen, background):
        super().__init__()
        self.screen = screen
        self.background = background
        self.image = pg.Surface((4, 4))
        self.rect = self.image.get_rect()
        self.gas = random.choice(list(Particle.gases_colors.keys()))
        self.color = Particle.gases_colors[self.gas]
        self.vel = Particle.VELOCITY_SO2 * Particle.vel_scalar[self.gas]
        self.x, self.y = Particle.VENT_LOCATION_XY
        self.vector()

    def vector(self):
        """计算粒子在发射时的运动矢量。"""
        orient = random.uniform(60, 120)  # 90 表示垂直
        radians = math.radians(orient)
        self.dx = self.vel * math.cos(radians)
        self.dy = -self.vel * math.sin(radians)
        # 粒子的喷射方向朝上，则pygame中坐标的值要向下增加，因此必须确保self.dy的值是负数。

    def update(self):
        """向粒子施加重力，绘制粒子运动轨迹，处理边界条件。"""
        self.dy += Particle.GRAVITY
        pg.draw.line(self.background, self.color, (self.x, self.y),
                     (self.x + self.dx, self.y + self.dy))
        self.x += self.dx
        self.y += self.dy
        if self.x < 0 or self.x > self.screen.get_width():
            self.kill()
        if self.y < 0 or self.y > Particle.IO_SURFACE_Y:
            self.kill()


def main():
    """设置游戏屏幕显示的信息，执行游戏循环"""
    screen = pg.display.set_mode((639, 360))
    pg.display.set_caption('Io Volcano Simulator')
    background = pg.image.load('tvashtar_plume.gif')

    # 置带颜色的图例说明
    legend_font = pg.font.SysFont('None', 24)
    water_label = legend_font.render('--- H2O', True, WHITE, BLACK)
    co2_label = legend_font.render('--- CO2', True, GRAY, BLACK)
    so2_label = legend_font.render('--- SO2/S2', True, LT_GRAY, BLACK)
    h2s_label = legend_font.render('--- H2S', True, DK_GRAY, BLACK)

    particles = pg.sprite.Group()

    clock = pg.time.Clock()

    while True:
        clock.tick(25)
        particles.add(Particle(screen, background))
        for event in pg.event.get():
            if event.type == pg.QUIT:
                pg.quit()
                sys.exit()

        screen.blit(background, (0, 0))
        screen.blit(water_label, (40, 20))
        screen.blit(h2s_label, (40, 40))
        screen.blit(co2_label, (40, 60))
        screen.blit(so2_label, (40, 80))

        particles.update()
        particles.draw(screen)

        pg.display.flip()


if __name__ == "__main__":
    main()
