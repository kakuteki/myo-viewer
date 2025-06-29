import sys
from PyQt5.QtWidgets import QApplication, QMainWindow
from PyQt5.QtOpenGL import QGLWidget
from PyQt5.QtCore import QTimer
from OpenGL.GL import *
from OpenGL.GLU import *
import math

class OpenGLWidget(QGLWidget):
    def __init__(self):
        super().__init__()
        self.rotation = 0
        
        # タイマーでアニメーション
        self.timer = QTimer()
        self.timer.timeout.connect(self.update_rotation)
        self.timer.start(16)  # 約60FPS
    
    def initializeGL(self):
        # 背景色を設定
        glClearColor(0.0, 0.0, 0.0, 1.0)
        
        # 深度テストを有効化
        glEnable(GL_DEPTH_TEST)
        
        # ライティングを有効化
        glEnable(GL_LIGHTING)
        glEnable(GL_LIGHT0)
        
        # ライトの位置と色を設定
        glLightfv(GL_LIGHT0, GL_POSITION, [1.0, 1.0, 1.0, 0.0])
        glLightfv(GL_LIGHT0, GL_DIFFUSE, [1.0, 1.0, 1.0, 1.0])
        
        # マテリアルを設定
        glMaterialfv(GL_FRONT, GL_DIFFUSE, [0.8, 0.8, 0.8, 1.0])
    
    def resizeGL(self, width, height):
        # ビューポートを設定
        glViewport(0, 0, width, height)
        
        # 投影行列を設定
        glMatrixMode(GL_PROJECTION)
        glLoadIdentity()
        gluPerspective(45, width/height, 0.1, 100.0)
        
        # モデルビュー行列に切り替え
        glMatrixMode(GL_MODELVIEW)
    
    def paintGL(self):
        # 画面をクリア
        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
        
        # モデルビュー行列をリセット
        glLoadIdentity()
        
        # カメラ位置を設定
        gluLookAt(0, 0, 5,    # カメラ位置
                  0, 0, 0,    # 注視点
                  0, 1, 0)    # 上方向
        
        # 回転を適用
        glRotatef(self.rotation, 1, 1, 0)
        
        # 立方体を描画
        self.draw_cube()
    
    def draw_cube(self):
        # 立方体の面を定義
        faces = [
            # 前面
            [[-1, -1, 1], [1, -1, 1], [1, 1, 1], [-1, 1, 1]],
            # 背面
            [[-1, -1, -1], [-1, 1, -1], [1, 1, -1], [1, -1, -1]],
            # 上面
            [[-1, 1, -1], [-1, 1, 1], [1, 1, 1], [1, 1, -1]],
            # 下面
            [[-1, -1, -1], [1, -1, -1], [1, -1, 1], [-1, -1, 1]],
            # 右面
            [[1, -1, -1], [1, 1, -1], [1, 1, 1], [1, -1, 1]],
            # 左面
            [[-1, -1, -1], [-1, -1, 1], [-1, 1, 1], [-1, 1, -1]]
        ]
        
        # 面の法線ベクトル
        normals = [
            [0, 0, 1],   # 前面
            [0, 0, -1],  # 背面
            [0, 1, 0],   # 上面
            [0, -1, 0],  # 下面
            [1, 0, 0],   # 右面
            [-1, 0, 0]   # 左面
        ]
        
        # 各面を描画
        glBegin(GL_QUADS)
        for i, face in enumerate(faces):
            glNormal3fv(normals[i])
            for vertex in face:
                glVertex3fv(vertex)
        glEnd()
    
    def update_rotation(self):
        self.rotation += 1
        if self.rotation >= 360:
            self.rotation = 0
        self.updateGL()  # QGLWidgetの場合はupdateGL()を使用

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("PyQt5 3D Model Display")
        self.setGeometry(100, 100, 800, 600)
        
        # OpenGLウィジェットを中央に配置
        self.opengl_widget = OpenGLWidget()
        self.setCentralWidget(self.opengl_widget)

def main():
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())

if __name__ == "__main__":
    main()