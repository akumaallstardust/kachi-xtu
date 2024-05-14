import re

# ファイルを読み込む関数
def read_and_convert(file_path):
    # ファイルを読み込む
    with open(file_path, 'r', encoding='utf-8', errors='replace') as file:
        content = file.read()


    # vw単位の数値を見つけて変換する関数
    def convert_vw(match):
        value = float(match.group(1))
        return f"${{v_w({value})}}px"

    # 正規表現を使用してvw単位の数値を検索し、convert_vw関数で変換する
    converted_content = re.sub(r'(-?\d+(?:\.\d+)?)vw', convert_vw, content)

    return converted_content

# 変換したいファイルのパス
file_path = "C:\\Users\\user02\\Documents\\my_app_r\\style_moblie.css"

# 変換結果を取得
converted = read_and_convert(file_path)
# テキストファイルを作成して文字列を書き込む関数
def write_to_file(file_path, text):
    # 'w'モードでファイルを開く（ファイルが存在しない場合は新しく作成される）
    with open(file_path, 'w') as file:
        file.write(text)  # 文字列をファイルに書き込む

# 書き込みたいテキスト

# ファイルパス（例: 'example.txt'）
file_path = 'C:\\Users\\user02\\Documents\\sss.txt'

# 関数を呼び出してファイルに書き込む
write_to_file(file_path, converted)

