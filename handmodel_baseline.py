import sys
import os
from PyQt5.QtWidgets import QApplication, QMainWindow
from PyQt5.QtOpenGL import QGLWidget
from PyQt5.QtCore import QTimer, Qt
from OpenGL.GL import *
from OpenGL.GLU import *
import math

class OBJLoader:
    def __init__(self, filename):
        self.vertices = []
        self.faces = []
        self.normals = []
        self.texture_coords = []
        self.materials = {}
        self.current_material = None
        self.load_obj(filename)
    
    def load_obj(self, filename):
        """OBJファイルを読み込む"""
        if not os.path.exists(filename):
            print(f"エラー: {filename} が見つかりません")
            return
        
        try:
            with open(filename, 'r') as file:
                for line in file:
                    line = line.strip()
                    if line.startswith('v '):  # 頂点
                        parts = line.split()
                        vertex = [float(parts[1]), float(parts[2]), float(parts[3])]
                        self.vertices.append(vertex)
                    
                    elif line.startswith('vn '):  # 法線
                        parts = line.split()
                        normal = [float(parts[1]), float(parts[2]), float(parts[3])]
                        self.normals.append(normal)
                    
                    elif line.startswith('vt '):  # テクスチャ座標
                        parts = line.split()
                        tex_coord = [float(parts[1]), float(parts[2])]
                        self.texture_coords.append(tex_coord)
                    
                    elif line.startswith('mtllib '):  # マテリアルファイル
                        mtl_file = line.split()[1]
                        self.load_mtl(mtl_file)
                    
                    elif line.startswith('usemtl '):  # マテリアル使用
                        self.current_material = line.split()[1]
                    
                    elif line.startswith('f '):  # 面
                        parts = line.split()[1:]  # 'f'を除く
                        face_vertices = []
                        face_normals = []
                        face_textures = []
                        
                        for part in parts:
                            # v/vt/vn または v//vn または v の形式に対応
                            indices = part.split('/')
                            vertex_index = int(indices[0]) - 1  # OBJは1から始まる
                            face_vertices.append(vertex_index)
                            
                            # テクスチャ座標インデックス
                            if len(indices) >= 2 and indices[1]:
                                texture_index = int(indices[1]) - 1
                                face_textures.append(texture_index)
                            
                            # 法線インデックスがある場合
                            if len(indices) >= 3 and indices[2]:
                                normal_index = int(indices[2]) - 1
                                face_normals.append(normal_index)
                        
                        self.faces.append({
                            'vertices': face_vertices,
                            'normals': face_normals,
                            'textures': face_textures,
                            'material': self.current_material
                        })
            
            print(f"OBJファイル読み込み完了: {len(self.vertices)}頂点, {len(self.faces)}面")
        
        except Exception as e:
            print(f"OBJファイル読み込みエラー: {e}")
    
    def load_mtl(self, filename):
        """MTLファイルを読み込む"""
        if not os.path.exists(filename):
            print(f"MTLファイルが見つかりません: {filename}")
            return
        
        try:
            current_material = None
            with open(filename, 'r') as file:
                for line in file:
                    line = line.strip()
                    if line.startswith('newmtl '):
                        current_material = line.split()[1]
                        self.materials[current_material] = {}
                    elif current_material and line.startswith('Kd '):  # 拡散反射色
                        parts = line.split()
                        self.materials[current_material]['diffuse'] = [
                            float(parts[1]), float(parts[2]), float(parts[3])
                        ]
            print(f"MTLファイル読み込み完了: {len(self.materials)}マテリアル")
        except Exception as e:
            print(f"MTLファイル読み込みエラー: {e}")
    
    def calculate_normals(self):
        """法線が無い場合の法線計算"""
        if self.normals:
            return  # 既に法線がある場合は何もしない
        
        # 各面の法線を計算
        for face in self.faces:
            if len(face['vertices']) >= 3:
                v1 = self.vertices[face['vertices'][0]]
                v2 = self.vertices[face['vertices'][1]]
                v3 = self.vertices[face['vertices'][2]]
                
                # 外積で法線を計算
                edge1 = [v2[i] - v1[i] for i in range(3)]
                edge2 = [v3[i] - v1[i] for i in range(3)]
                
                normal = [
                    edge1[1] * edge2[2] - edge1[2] * edge2[1],
                    edge1[2] * edge2[0] - edge1[0] * edge2[2],
                    edge1[0] * edge2[1] - edge1[1] * edge2[0]
                ]
                
                # 正規化
                length = math.sqrt(sum(n*n for n in normal))
                if length > 0:
                    normal = [n/length for n in normal]
                
                face['computed_normal'] = normal

class OpenGLWidget(QGLWidget):
    def __init__(self):
        super().__init__()
        self.rotation_x = 20
        self.rotation_y = 0
        self.camera_distance = 5.0
        self.obj_model = None
        
        # マウス操作用の変数
        self.last_mouse_pos = None
        self.mouse_dragging = False
        
        # OBJファイルを読み込み
        self.load_model()
        
        # 自動回転を無効化（手動操作を優先）
        # self.timer = QTimer()
        # self.timer.timeout.connect(self.update_rotation)
        # self.timer.start(16)  # 約60FPS
    
    def load_model(self):
        """hand.OBJを読み込む"""
        obj_path = "hand.OBJ"
        self.obj_model = OBJLoader(obj_path)
        self.obj_model.calculate_normals()
    
    def initializeGL(self):
        # 背景色を設定
        glClearColor(0.2, 0.2, 0.2, 1.0)
        
        # 深度テストを有効化
        glEnable(GL_DEPTH_TEST)
        
        # ライティングを有効化
        glEnable(GL_LIGHTING)
        glEnable(GL_LIGHT0)
        
        # ライトの位置と色を設定
        glLightfv(GL_LIGHT0, GL_POSITION, [2.0, 2.0, 2.0, 0.0])
        glLightfv(GL_LIGHT0, GL_DIFFUSE, [1.0, 1.0, 1.0, 1.0])
        glLightfv(GL_LIGHT0, GL_AMBIENT, [0.3, 0.3, 0.3, 1.0])
        
        # マテリアルを設定
        glMaterialfv(GL_FRONT, GL_DIFFUSE, [0.8, 0.6, 0.4, 1.0])
        glMaterialfv(GL_FRONT, GL_AMBIENT, [0.2, 0.2, 0.2, 1.0])
        
        # 裏面カリングを有効化
        glEnable(GL_CULL_FACE)
        glCullFace(GL_BACK)
    
    def resizeGL(self, width, height):
        # ビューポートを設定
        glViewport(0, 0, width, height)
        
        # 投影行列を設定
        glMatrixMode(GL_PROJECTION)
        glLoadIdentity()
        gluPerspective(45, width/height if height != 0 else 1, 0.1, 100.0)
        
        # モデルビュー行列に切り替え
        glMatrixMode(GL_MODELVIEW)
    
    def paintGL(self):
        # 画面をクリア
        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
        
        # モデルビュー行列をリセット
        glLoadIdentity()
        
        # カメラ位置を設定（距離を変数で制御）
        gluLookAt(0, 0, self.camera_distance,    # カメラ位置
                  0, 0, 0,                       # 注視点
                  0, 1, 0)                       # 上方向
        
        # 回転を適用
        glRotatef(self.rotation_x, 1, 0, 0)
        glRotatef(self.rotation_y, 0, 1, 0)
        
        # OBJモデルを描画
        if self.obj_model:
            self.draw_obj_model()
    
    def draw_obj_model(self):
        """OBJモデルを描画"""
        if not self.obj_model.vertices or not self.obj_model.faces:
            return
        
        # 三角形と四角形の面を描画
        for face in self.obj_model.faces:
            vertices = face['vertices']
            normals = face.get('normals', [])
            material = face.get('material')
            
            # マテリアルが指定されている場合は色を設定
            if material and material in self.obj_model.materials:
                mat = self.obj_model.materials[material]
                if 'diffuse' in mat:
                    diffuse = mat['diffuse'] + [1.0]  # アルファ値を追加
                    glMaterialfv(GL_FRONT, GL_DIFFUSE, diffuse)
            
            if len(vertices) == 3:  # 三角形
                glBegin(GL_TRIANGLES)
            elif len(vertices) == 4:  # 四角形
                glBegin(GL_QUADS)
            else:  # その他の多角形（三角形ファンで描画）
                glBegin(GL_TRIANGLE_FAN)
            
            # 計算された法線がある場合は使用
            if 'computed_normal' in face:
                glNormal3fv(face['computed_normal'])
            
            for i, vertex_index in enumerate(vertices):
                # 頂点ごとの法線がある場合
                if i < len(normals) and normals[i] < len(self.obj_model.normals):
                    glNormal3fv(self.obj_model.normals[normals[i]])
                
                # 頂点座標
                if vertex_index < len(self.obj_model.vertices):
                    glVertex3fv(self.obj_model.vertices[vertex_index])
            
            glEnd()
    
    def mousePressEvent(self, event):
        """マウスクリック時の処理"""
        if event.button() == Qt.LeftButton:
            self.last_mouse_pos = event.pos()
            self.mouse_dragging = True
    
    def mouseMoveEvent(self, event):
        """マウス移動時の処理"""
        if self.mouse_dragging and self.last_mouse_pos is not None:
            # マウスの移動量を計算
            dx = event.x() - self.last_mouse_pos.x()
            dy = event.y() - self.last_mouse_pos.y()
            
            # 回転角度を更新（感度を調整）
            self.rotation_y += dx * 0.5
            self.rotation_x += dy * 0.5
            
            # X軸回転も360度で循環
            if self.rotation_x >= 360:
                self.rotation_x -= 360
            elif self.rotation_x < 0:
                self.rotation_x += 360
            
            # Y軸回転は360度で循環
            if self.rotation_y >= 360:
                self.rotation_y -= 360
            elif self.rotation_y < 0:
                self.rotation_y += 360
            
            self.last_mouse_pos = event.pos()
            self.updateGL()
    
    def mouseReleaseEvent(self, event):
        """マウスリリース時の処理"""
        if event.button() == Qt.LeftButton:
            self.mouse_dragging = False
            self.last_mouse_pos = None
    
    def wheelEvent(self, event):
        """マウスホイール時の処理（ズーム）"""
        # ホイールの回転方向を取得
        delta = event.angleDelta().y()
        
        # ズーム倍率を調整
        zoom_factor = 0.1
        if delta > 0:  # 上向きスクロール（ズームイン）
            self.camera_distance = max(0.5, self.camera_distance - zoom_factor)
        else:  # 下向きスクロール（ズームアウト）
            self.camera_distance = min(20.0, self.camera_distance + zoom_factor)
        
        self.updateGL()
    
    def update_rotation(self):
        # 自動回転は無効化
        pass
        # self.rotation_x += 0.5
        # self.rotation_y += 1.0
        # if self.rotation_x >= 360:
        #     self.rotation_x = 0
        # if self.rotation_y >= 360:
        #     self.rotation_y = 0
        # self.updateGL()

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("PyQt5 OBJ Model Viewer - hand.OBJ")
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