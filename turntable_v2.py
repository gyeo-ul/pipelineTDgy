import maya.cmds as cmds
import os

class PlayblastSceneSetter:

    def __init__(self, file_path):
        self.file_path = file_path

    # white_bg.mb 파일 임포트
    def import_file(self):
        if os.path.exists(self.file_path):
            cmds.file(self.file_path, i=True, ra=True, mergeNamespacesOnClash=False, namespace=":", options="v=0;", pr=True)
            print("파일이 임포트되었습니다")
        else:
            print("파일을 찾을 수 없습니다")
            return False
        return True

    # white_bg.mb의 쉐이더 찾기
    def check_shader_exists(self, shader_name):
        shader_exists = cmds.objExists(shader_name)
        if shader_exists:
            print("쉐이더를 찾았습니다.")
        else:
            print("쉐이더를 찾을 수 없습니다.")
        return shader_exists

    # 쉐이더 임포트
    def import_shaders(self, shader_names):
        if self.import_file():
            for shader_name in shader_names:
                self.check_shader_exists(shader_name)

    # grp그룹 "rt_gr"로 한 번 더 그룹화
    def group_grp_objects(self):
        grp_groups = cmds.ls("*_grp", type="transform")
        if grp_groups:
            new_group = cmds.group(grp_groups, name="rt_gr")
            print("그룹화했습니다")
            return new_group
        else:
            print("_grp 그룹을 찾을 수 없습니다.")
            return None

    # "rt_gr" Y축으로 360도 회전 애니메이션 키 설정
    def animate_rotation(self, group_name, start_frame=1001, end_frame=1230, rotation_angle=360):
        if cmds.objExists(group_name):
            cmds.setKeyframe(group_name, attribute="rotateY", value=0, t=start_frame)
            cmds.setKeyframe(group_name, attribute="rotateY", value=rotation_angle, t=end_frame)
            cmds.selectKey(group_name, time=(start_frame, end_frame), attribute='rotateY')
            cmds.keyTangent(inTangentType="linear", outTangentType="linear")
            print("애니메이션이 설정되었습니다.")
        else:
            print("그룹을 찾을 수 없습니다.")

    # 뷰포트 패널에서 조명과 그림자 활성화, 그리드 비활성화
    def use_all_lights_and_shadows(self):
        model_panels = cmds.getPanel(type="modelPanel")
        if model_panels:
            for panel in model_panels:
                cmds.modelEditor(panel, e=True, displayLights="all")
                cmds.modelEditor(panel, e=True, shadows=True)
                cmds.modelEditor(panel, e=True, grid=False)
                print("조명과 그림자가 활성화, 그리드는 비활성화 되었습니다")
        else:
            print("모델 패널을 찾을 수 없습니다.")

    # 에셋의 위치와 크기에 따라 카메라 생성
    def create_camera(self, main_group):
        if cmds.objExists(main_group):

            # 바운딩 박스 계산
            bounding_box = cmds.exactWorldBoundingBox(main_group)
            center_x = (bounding_box[0] + bounding_box[3]) / 2
            center_y = (bounding_box[1] + bounding_box[4]) / 2
            center_z = (bounding_box[2] + bounding_box[5]) / 2

            # 크기 계산
            width = bounding_box[3] - bounding_box[0]
            height = bounding_box[4] - bounding_box[1]
            depth = bounding_box[5] - bounding_box[2]

            # 카메라 거리 계산 2배
            distance = max(width, height, depth) * 2

            # 새로운 카메라 생성
            camera_name = cmds.camera(name="turntable_camera")[0]

            # 카메라 위치 설정
            cmds.setAttr(f"{camera_name}.translateX", center_x)
            cmds.setAttr(f"{camera_name}.translateY", center_y)
            cmds.setAttr(f"{camera_name}.translateZ", center_z + distance)

            print("카메라가 생성되었습니다")
            return camera_name
        else:
            print(f"'{main_group}'를 찾을 수 없습니다.")
            return None

    def adjust_light_height(self, light_name, target_group, multiplier=5):
        if cmds.objExists(light_name) and cmds.objExists(target_group):
            # 타겟 그룹의 바운딩 박스 계산
            bounding_box = cmds.exactWorldBoundingBox(target_group)
            group_height = bounding_box[4] - bounding_box[1]  # Y축 기준 높이 계산

            # 새로운 높이 계산
            new_height = group_height * multiplier

            # 라이트의 현재 X, Z 좌표 유지, Y 좌표만 수정
            cmds.setAttr(f"{light_name}.translateY", new_height)

            print("라이트 높이가 설정되었습니다.")
        else:
            print("라이트 또는 타겟 그룹을 찾을 수 없습니다.")

    # 카메라 뷰포트에 설정
    def set_camera_view(self, camera_name):
        # 현재 뷰포트 가져오기
        current_panel = cmds.getPanel(withFocus=True)

        # 카메라 뷰포트 설정
        cmds.lookThru(current_panel, camera_name)
        print(f"{camera_name} 카메라 뷰가 활성화되었습니다.")

    # 모든 뷰포트에서 HUD 비활성화
    def disable_hud(self):
        model_panels = cmds.getPanel(type="modelPanel")
        if model_panels:
            for panel in model_panels:
                cmds.modelEditor(panel, e=True, hud=False)
            print("모든 뷰포트에서 HUD가 비활성화되었습니다.")
        else:
            print("모델 패널을 찾을 수 없습니다.")

if __name__ == "__main__":
    file_path = "/home/rapa/phoenix/white_bg_v2.mb"
    shaders = ["white_bg_lb"]

    importer = PlayblastSceneSetter(file_path)
    importer.import_shaders(shaders)
    
    importer.use_all_lights_and_shadows()

    # 그룹을 생성한 후 라이트 높이 조정
    group_name = importer.group_grp_objects()
    if group_name:
        importer.adjust_light_height("turntable_light", group_name, multiplier=3)
        importer.animate_rotation(group_name)
        camera_name = importer.create_camera(group_name)
        if camera_name:
            importer.set_camera_view(camera_name)
            importer.disable_hud()  # 모든 뷰포트에서 HUD 비활성화



















