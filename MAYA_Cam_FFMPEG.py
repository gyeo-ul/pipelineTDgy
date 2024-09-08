import maya.cmds as cmds
import datetime
import os
import subprocess

def make_playblast():
    """ 
    마야의 플레이 블라스트 기능을 이용해서 뷰포트를 이미지로 렌더링하고,
    슬레이트 정보를 삽입하여 동영상을 인코딩한다.
    image : jpg
    mov codec : h264
    """ 
    proxy_path = "/home/rapa/phoenix/FCG"
    proxy_format = "jpg"
    image_path = os.path.join(proxy_path, 'phoenix_0020_shot_v001.%04d.' + proxy_format)
    mov_path = f"{proxy_path}/phoenix_0020_shot_review.mov"

    start_frame = 1001
    last_frame = 1230
    render_width = 1920
    render_height = 1080

    # 카메라 선택
    cameras = cmds.ls(type='camera')
    if not cameras:
        raise Exception("카메라가 존재하지 않습니다.")
    
    cam_transform = cmds.listRelatives(cameras[0], parent=True)[0]

    
    # 해당 카메라로 뷰포트 설정
    cmds.lookThru(cam_transform)
    
    # PLAYBLAST MAYA API
    cmds.playblast(filename=os.path.join(proxy_path, 'phoenix_0020_shot_v001'), format='image', compression=proxy_format,
               startTime=start_frame, endTime=last_frame, forceOverwrite=True,
               widthHeight=(render_width, render_height), percent=100,
               showOrnaments=True, framePadding=4, quality=100, viewer=False)
    
    # FFMPEG를 이용한 동영상 인코딩
    first = 1001
    frame_rate = 24 
    ffmpeg = "ffmpeg"
    slate_size = 60
    font_path = "/show/4th_academy/rnd/fonts/cour.ttf"
    font_size = 40
    frame_count = last_frame - start_frame
    text_x_padding = 10
    text_y_padding = 20

    top_left = "phoenix_0020_shot_v001"
    top_center = "gyeoul"
    top_right = datetime.date.today().strftime("%Y/%m/%d")
    bot_left = ""
    bot_center = ""

    frame_cmd = "'Frame \: %{eif\:n+"
    frame_cmd += "%s\:d}' (%s)"  % (first, frame_count+1)
    bot_right = frame_cmd

    cmd = '%s -framerate %s -y -start_number %s ' % (ffmpeg, frame_rate, first)
    cmd += '-i %s' % (image_path)
    cmd += ' -vf "drawbox=y=0 :color=black :width=iw: height=%s :t=fill, ' % (slate_size)
    cmd += 'drawbox=y=ih-%s :color=black :width=iw: height=%s :t=fill, ' % (slate_size, slate_size)
    cmd += 'drawtext=fontfile=%s :fontsize=%s :fontcolor=white@0.7 :text=%s :x=%s :y=%s,' % (font_path, font_size, top_left, text_x_padding, text_y_padding)
    cmd += 'drawtext=fontfile=%s :fontsize=%s :fontcolor=white@0.7 :text=%s :x=(w-text_w)/2 :y=%s,' % (font_path, font_size, top_center, text_y_padding)
    cmd += 'drawtext=fontfile=%s :fontsize=%s :fontcolor=white@0.7 :text=%s :x=w-tw-%s :y=%s,' % (font_path, font_size, top_right, text_x_padding, text_y_padding)
    cmd += 'drawtext=fontfile=%s :fontsize=%s :fontcolor=white@0.7 :text=%s :x=%s :y=h-th-%s,' % (font_path, font_size, bot_left, text_x_padding, text_y_padding)
    cmd += 'drawtext=fontfile=%s :fontsize=%s :fontcolor=white@0.7 :text=%s :x=(w-text_w)/2 :y=h-th-%s,' % (font_path, font_size, bot_center, text_y_padding)
    cmd += 'drawtext=fontfile=%s :fontsize=%s :fontcolor=white@0.7 :text=%s :x=w-tw-%s :y=h-th-%s' % (font_path, font_size, bot_right, text_x_padding, text_y_padding)
    cmd += '"'
    cmd += ' -c:v prores_ks -profile:v 3 -colorspace bt709 %s' % mov_path
    
    subprocess.call(cmd, shell=True)

make_playblast()
