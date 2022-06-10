import cv2
import datetime
import glob
import os
import sys
import shutil
import time
from typing import List, Tuple
from multiprocessing import Pool
from multiprocessing.pool import AsyncResult

from natsort.natsort import natsorted, List_ns

class Video2Image(object):
    TARGET_EXTENSION = ("mp4", "MP4", "mov", "MOV")
    
    def __init__(self, output_fps) -> None:
        # 出力FPSのチェック
        if (output_fps < -1):
            self.output_fps = -1
        else:
            self.output_fps = output_fps
    
    def convert_frame(self, file_path:str, converted_path:str, ext:str="jpg") -> bool:
        """フレーム変換処理

        Args:
            file_path (str): 変換対象ファイルパス
            converted_path (str): 変換後ファイル格納先
            ext (str, optional): 変換後フレーム画像拡張子. Defaults to "jpg".

        Returns:
            bool: 成功/失敗
        """
        
        filename = os.path.basename(file_path)
        
        # キャプチャオブジェクト生成
        cap = cv2.VideoCapture(file_path)
        if not cap.isOpened():
            print(f"Failed to acquire capture object to be converted. : {file_path}")
            return False
        
        # 変換対象の情報を取得
        frame_num, width, height, fps = Video2Image.get_target_info(cap)
        print(f"Target information --> [Filename:({filename}), FrameNum:({frame_num:.0f}), Resolution :({width:.0f}, {height:.0f}), Fps:({fps:.0f}))]")
        
        digit = len(str(int(frame_num))) # フレーム桁数
        serial_number = 0 # ファイル名連番
        
        # フレームの間引き間隔を算出する
        i = 0
        if self.output_fps < 0:
            interval = round(fps) / round(fps)
        else:
            interval = round(fps) / round(self.output_fps)
        
        start_time = time.perf_counter()
        # 全フレーム切り出し
        while True:
            ret, frame = cap.read()
            if ret:
                # フレームを指定数に間引きながら切り出す
                if ((i % interval) == 0):
                    # 連番.拡張子
                    img_name = f"{converted_path}/{str(serial_number).zfill(digit)}.{ext}"
                    cv2.imwrite(img_name, frame)
                    serial_number += 1
            else:
                break
            i += 1
        
        end_time = time.perf_counter() - start_time
        print(f"The conversion of ({filename}) is now complete. Convert time: {end_time:.2f}[sec]")
        cap.release()
        
        return True
    
    def convert_multiproc(self, file_path:str, output_path:str) -> None:
        """フレーム変換処理(マルチプロセス用)

        Args:
            file_path (str): 変換対象ファイルパス
            output_path (str): 変換対象の出力先ディレクトリパス
        """
        
        # 変換対象の出力先ディレクトリを生成
        converted_path = self.generate_per_filename_dir(str(file_path), output_path)
        # フレーム変換実行
        self.convert_frame(str(file_path), converted_path, "jpg")
        
        return

    @staticmethod
    def get_target_info(cap) -> Tuple[float, float, float,float]:
        """変換対象の情報取得

        Args:
            cap (_type_): VideoCaptureオブジェクト

        Returns:
            Tuple[float, float, float,float]: 変換対象情報
        """
        
        target_info = (cap.get(cv2.CAP_PROP_FRAME_COUNT), cap.get(cv2.CAP_PROP_FRAME_WIDTH), cap.get(cv2.CAP_PROP_FRAME_HEIGHT), cap.get(cv2.CAP_PROP_FPS))
        return target_info

    def get_target_list(self, input_dir:str="input") -> List_ns:
        """対象ファイル一覧取得

        Args:
            input_dir (str, optional): 変換対象が格納されたディレクトリ名. Defaults to "input".

        Returns:
            List_ns: 変換対象一覧
        """
        
        targets = []
        for ext in Video2Image.TARGET_EXTENSION:
            target_path = f"{input_dir}/*.{ext}"
            targets.extend(glob.glob(target_path))
        
        targets = natsorted(targets)
        print(f"Target List:{targets}")
        return targets

    def generate_output_dir(self, base_output_path:str="output") -> str:
        """出力先ディレクトリ(日付毎)生成

        Args:
            base_output_path (str, optional): 出力先ディレクトリ名. Defaults to "output".

        Returns:
            str: 出力先ディレクトリパス名
        """
        
        dt_now = datetime.datetime.now()
        date_output_path = f"{base_output_path}/{dt_now.strftime('%Y%m%d')}"
        
        # 出力先ディレクトリが存在しなければ作成
        if not os.path.exists(base_output_path):
            os.mkdir(base_output_path)
        if not os.path.exists(date_output_path):
            os.mkdir(date_output_path)
        else:
            shutil.rmtree(date_output_path)
            os.mkdir(date_output_path)
        
        return date_output_path

    def generate_per_filename_dir(self, file_path:str, base_output_path:str) -> str:
        """変換対象出力先ディレクトリ生成

        Args:
            file_path (str): 変換対象パス
            base_output_path (str): 出力先ディレクトリ名

        Returns:
            str: 変換対象出力先ディレクトリ名
        """
        
        filename_no_ext = os.path.splitext(os.path.basename(file_path))[0]
        output_path = f"{base_output_path}/{filename_no_ext}"
        if not os.path.exists(output_path):
            os.mkdir(output_path)
        
        return output_path
    

def main(output_fps:int=-1):
    """メイン処理

    Args:
        output_fps (int, optional): 出力FPS.負値の場合、入力ソースのFPSで出力する Defaults to -1.
    """
    
    v2i = Video2Image(output_fps)
    
    # 変換対象のファイル一覧を取得
    file_paths = v2i.get_target_list()
    
    # 出力先ディレクトリを生成
    output_path = v2i.generate_output_dir()
    
    start_proc_time = time.perf_counter()
    
    # フレーム変換を並列処理で実行する
    # cpu_cnt = os.cpu_count()
    # with Pool(processes=cpu_cnt) as pool:
    #     proc_results:List[AsyncResult] = []
    #     for file_path in file_paths:
    #         # 変換処理に渡す引数
    #         args = [file_path, output_path]
    #         # フレーム変換処理を並列実行
    #         proc_results.append(pool.apply_async(v2i.convert_multiproc, args=args))
    #     # 終了待機
    #     for proc_result in proc_results:
    #         proc_result.get()
    
    for file_path in file_paths:
        # 変換対象の出力先ディレクトリを生成
        converted_path = v2i.generate_per_filename_dir(str(file_path), output_path)
        # フレーム変換実行
        v2i.convert_frame(str(file_path), converted_path, "jpg")
    
    total_proc_time = time.perf_counter() - start_proc_time
    print(f"Total processing time: {total_proc_time:.2f}[sec]")
    
    return

if __name__ == "__main__":
    try:
        # 引数に応じて動作切り替えを行うようにする
        args = sys.argv[1:]
        if len(args) == 1:
            output_fps = int(args[0])
            main(output_fps)
        elif len(args) == 0:
            main()
        else:
            print("The specified argument is invalid.\nThe arguments that can be specified are (output_fps).")
    except Exception as e:
        print(f"Exception occurrence. :{e}")
    
    exit(0)