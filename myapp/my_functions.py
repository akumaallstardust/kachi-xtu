from pathlib import Path
import math
import os
import re
import json
import io
import shutil
from . import my_search
from PIL import Image
from django.http import HttpRequest
import mysql.connector
import time
import environ
from django.utils.safestring import mark_safe
from PIL import Image, ImageDraw, ImageFont
from openai import OpenAI
# .envファイルの場所を設定
env = environ.Env()
environ.Env.read_env(os.path.join(environ.Path(__file__) - 2, '.env'))
current_path=str(Path(__file__).resolve().parent)
media_path=os.path.join(Path(__file__).resolve().parent.parent,"media_local")
etc_path=current_path+"/etc"
content_exclusion_pattern = re.compile(r"<|>|\u200b|\t|\&lt|\&gt|`")

def connect_to_database():
    return mysql.connector.connect(
        user=env('MYSQL_USER'), password=env('MYSQL_PASSWORD'), host="127.0.0.1", database=env('MYSQL_DATABASE'), port=env('DB_CONTAINER_PORT')
    )

def create_content_dict(
        cursor,content_id_list:list,#new_post、old_postを使うならcontent_id_listは昇順のintのlistが前提
        amount_of_displayed_post=10,start_number=1,page_number=1,
        order="new_post",user_id=-1
        )->dict:#start_number=1が最小
    order_option_list=[
        "new_post","old_post",
        "view_many_total","view_few_total",
        "like_count_many","like_count_few",
        "dislike_count_many","dislike_count_few",
        "like_dislike_ratio_much","like_dislike_ratio_little",
        "no_sort_str","no_sort","comment_count_many","comment_count_few"
        ]
    if(not order in order_option_list):
        order="new_post"
    ordered_content_id=[]
    if amount_of_displayed_post>0:#amount_of_displayed_postはこの後変えるのでその前に
        total_page_number=(len(content_id_list)-1)//amount_of_displayed_post+1#10n+1~10のときn+1
    else:
        total_page_number=-1
        
    if(len(content_id_list)==0):
        return {"amount_of_displayed_post":"0","total_page_number":"0"}#content_listが空のとき
    if(len(content_id_list)<amount_of_displayed_post+(start_number-1)):#len(content_id_list)-(start_number-1)=n*amount_of_displayed_postのときはamount_of_displayed_postはかわらない
        if(len(content_id_list)<=(start_number-1)):
            return {"amount_of_displayed_post":"-1","total_page_number":"0"}#amount_of_displayed_post:"-1"はエラーの意味
        else:
            amount_of_displayed_post=len(content_id_list)-(start_number-1)
        
    
    if(order==order_option_list[0]):#order_option_list[0]="new_post"
        content_id_list.reverse()#デフォルトはコンテンツidが少ない順、つまり古い順なので逆にする
        for i in range(amount_of_displayed_post):
            ordered_content_id.append(content_id_list[i+(start_number-1)])

    elif(order==order_option_list[1]):#order_option_list[1]="old_post"
        for i in range(amount_of_displayed_post):#newとは逆
            ordered_content_id.append(content_id_list[i+(start_number-1)])
    
    elif(order==order_option_list[10]):#order_option_list[10]="no_sort_str"
        if("" in content_id_list):
            content_id_list=[]
            amount_of_displayed_post=0
        for i in range(amount_of_displayed_post):#newとは逆
            ordered_content_id.append(int(content_id_list[i+(start_number-1)]))
            
    elif(order==order_option_list[11]):#order_option_list[11]="no_sort"
        if("" in content_id_list):
            content_id_list=[]
            amount_of_displayed_post=0
        for i in range(amount_of_displayed_post):#newとは逆
            ordered_content_id.append(content_id_list[i+(start_number-1)])
    #ここまでDBへの接続がいらないやつ

    elif(order==order_option_list[2]):#order_option_list[2]="view_many_total"
        query="select content_id from post_view_count_table where content_id in("
        for i in content_id_list:
            query+=str(i)+","#i[0]=content_id
        query=query[:-1]+") ORDER BY view_count DESC;"#末尾の,を削除
        cursor.execute(query)
        result=cursor.fetchall()#resultは(content_id,)タプルのリスト
        for i in range(amount_of_displayed_post):
            ordered_content_id.append(result[i+(start_number-1)][0])

    elif(order==order_option_list[3]):#order_option_list[3]="view_less_total"
        query="select content_id from post_view_count_table where content_id in("
        for i in content_id_list:
            query+=str(i)+","#i[0]=content_id
        query=query[:-1]+") ORDER BY view_count ASC;"#末尾の,を削除
        cursor.execute(query)
        result=cursor.fetchall()#resultは(content_id,)タプルのリスト
        for i in range(amount_of_displayed_post):
            ordered_content_id.append(result[i+(start_number-1)][0])

    elif(order==order_option_list[4]):#order_option_list[4]="like_count_many"
        query="select content_id from post_review_table where content_id in("
        for i in content_id_list:
            query+=str(i)+","#i[0]=content_id
        query=query[:-1]+") ORDER BY like_count DESC;"#末尾の,を削除
        cursor.execute(query)
        result=cursor.fetchall()#resultは(content_id,)タプルのリスト
        for i in range(amount_of_displayed_post):
            ordered_content_id.append(result[i+(start_number-1)][0])

    elif(order==order_option_list[5]):#order_option_list[5]="like_count_few"
        query="select content_id from post_review_table where content_id in("
        for i in content_id_list:
            query+=str(i)+","#i[0]=content_id
        query=query[:-1]+") ORDER BY like_count ASC;"#末尾の,を削除
        cursor.execute(query)
        result=cursor.fetchall()#resultは(content_id,)タプルのリスト
        for i in range(amount_of_displayed_post):
            ordered_content_id.append(result[i+(start_number-1)][0])

    elif(order==order_option_list[6]):#order_option_list[6]="dislike_count_many"
        query="select content_id from post_review_table where content_id in("
        for i in content_id_list:
            query+=str(i)+","#i[0]=content_id
        query=query[:-1]+") ORDER BY dislike_count DESC;"#末尾の,を削除
        cursor.execute(query)
        result=cursor.fetchall()#resultは(content_id,)タプルのリスト
        for i in range(amount_of_displayed_post):
            ordered_content_id.append(result[i+(start_number-1)][0])

    elif(order==order_option_list[7]):#order_option_list[7]="dislike_count_few"
        query="select content_id from post_review_table where content_id in("
        for i in content_id_list:
            query+=str(i)+","#i[0]=content_id
        query=query[:-1]+") ORDER BY dislike_count ASC;"#末尾の,を削除
        cursor.execute(query)
        result=cursor.fetchall()#resultは(content_id,)タプルのリスト
        for i in range(amount_of_displayed_post):
            ordered_content_id.append(result[i+(start_number-1)][0])
    
    elif(order==order_option_list[8]):#order_option_list[8]="like_dislike_ratio_much"
        query="select content_id from post_review_table where content_id in("
        for i in content_id_list:
            query+=str(i)+","#i[0]=content_id
        query=query[:-1]+") ORDER BY like_dislike_ratio DESC;"#末尾の,を削除
        cursor.execute(query)
        result=cursor.fetchall()#resultは(content_id,)タプルのリスト
        for i in range(amount_of_displayed_post):
            ordered_content_id.append(result[i+(start_number-1)][0])
    
    elif(order==order_option_list[9]):#order_option_list[9]="like_dislike_ratio_little"
        query="select content_id from post_review_table where content_id in("
        for i in content_id_list:
            query+=str(i)+","#i[0]=content_id
        query=query[:-1]+") ORDER BY like_dislike_ratio ASC;"#末尾の,を削除
        cursor.execute(query)
        result=cursor.fetchall()#resultは(content_id,)タプルのリスト
        for i in range(amount_of_displayed_post):
            ordered_content_id.append(result[i+(start_number-1)][0])

    elif(order==order_option_list[12]):#order_option_list[12]="comment_count_many"
        query="select content_id from post_data_table where content_id in("
        for i in content_id_list:
            query+=str(i)+","#i[0]=content_id
        query=query[:-1]+") ORDER BY comment_count DESC;"#末尾の,を削除
        cursor.execute(query)
        result=cursor.fetchall()#resultは(content_id,)タプルのリスト
        for i in range(amount_of_displayed_post):
            ordered_content_id.append(result[i+(start_number-1)][0])


    elif(order==order_option_list[13]):#order_option_list[13]="comment_count_few"
        query="select content_id from post_data_table where content_id in("
        for i in content_id_list:
            query+=str(i)+","#i[0]=content_id
        query=query[:-1]+") ORDER BY comment_count ASC;"#末尾の,を削除
        cursor.execute(query)
        result=cursor.fetchall()#resultは(content_id,)タプルのリスト
        for i in range(amount_of_displayed_post):
            ordered_content_id.append(result[i+(start_number-1)][0])


    else:#エラー
        error_log(text="error0001")
        return {"amount_of_displayed_post":"-1"}


    if(user_id>=1):
        query="select like_history,dislike_history from user_review_history where user_id={};".format(user_id)
        cursor.execute(query)
        result=cursor.fetchone()
        if result is not None:
            liked_list=[] if result[0]=="" else result[0].split(",")#文字列のリストなので注意
            disliked_list=result[1].split(",")#文字列のリストなので注意
    else:
        liked_list=[]
        disliked_list=[]

    content_id_combined = ""
    title_combined = ""
    content_combined = ""
    user_id_combined = ""
    overview_combined = ""
    word_counts_combined=""
    tags_combined=""
    post_date_combined=""
    my_review_combined=""
    like_counts_combined=""
    dislike_counts_combined=""
    user_name_combined=""
    comment_count_combined=""

    for i in ordered_content_id:
        query="select content_id,title,content,user_id,overview,word_count,tags,post_date,comment_count from post_data_table where content_id={}".format(i)
        cursor.execute(query)
        content_basic_datas=cursor.fetchone()
        if(content_basic_datas is not None):
            content_id_combined += str(content_basic_datas[0]) + "<"  # content_basic_datas[0]はintなためstr()を使う
            title_combined += content_basic_datas[1] + "<"
            content_combined += content_basic_datas[2] + "<"
            user_id_combined += str(content_basic_datas[3]) + "<"  # content_idと同じく
            overview_combined += content_basic_datas[4] + "<"
            word_counts_combined += str(content_basic_datas[5]) + "<"
            tags_combined+=content_basic_datas[6] + "<"
            post_date_combined+=content_basic_datas[7].strftime("%Y,%m,%d,%H,%M,%S")+"<"
            comment_count_combined+=str(content_basic_datas[8])+"<"
            
            my_review:str="none"
            if(user_id>=1):#liked_listは初期化済みなので無くても大丈夫だが一応
                if(str(content_basic_datas[0]) in liked_list):
                    my_review="liked"
                elif(str(content_basic_datas[0]) in disliked_list):
                    my_review="disliked"
            
            my_review_combined+=my_review + "<"

            query="select like_count,dislike_count from post_review_table where content_id={};".format(i)
            cursor.execute(query)
            result=cursor.fetchone()
            like_counts_combined+=str(result[0]) + "<"
            dislike_counts_combined+=str(result[1]) + "<"
            
            query="select username from user_data_table where user_id={};".format(content_basic_datas[3])
            cursor.execute(query)
            result=cursor.fetchone()
            user_name_combined+=result[0]+"<"
            
        else:
            amount_of_displayed_post-=1#これがあればクライアント側ではエラーと表示される
            
    content_dict={"amount_of_displayed_post":str(amount_of_displayed_post),"page_number":str(page_number),"total_page_number":str(total_page_number)}# 表示する数
    content_dict["content_id_combined"] = mark_safe(content_id_combined[:-1])#最後の<は消す
    content_dict["title_combined"] = mark_safe(title_combined[:-1])
    content_dict["content_combined"] = mark_safe(content_combined[:-1])
    content_dict["user_id_combined"] = mark_safe(user_id_combined[:-1])
    content_dict["overview_combined"] = mark_safe(overview_combined[:-1])
    content_dict["word_counts_combined"] = mark_safe(word_counts_combined[:-1])
    content_dict["tags_combined"] = mark_safe(tags_combined[:-1])
    content_dict["post_date_combined"]=mark_safe(post_date_combined[:-1])
    content_dict["my_review_combined"] = mark_safe(my_review_combined[:-1])
    content_dict["like_counts_combined"] =mark_safe(like_counts_combined[:-1])
    content_dict["dislike_counts_combined"] =mark_safe(dislike_counts_combined[:-1])
    content_dict["user_name_combined"] =mark_safe(user_name_combined[:-1])
    content_dict["comment_count_combined"] =mark_safe(comment_count_combined[:-1])
    
    return content_dict

def censor_content(text:str):
    censored_text = text.replace('<', '＜')
    censored_text = censored_text.replace('>', '＞')
    censored_text = censored_text.replace('`', '‘')
    censored_text = censored_text.replace('&lt', '＆lt')
    censored_text = censored_text.replace('&gt', '＆gt')
    censored_text = re.sub(content_exclusion_pattern, '', censored_text)
    
    censored_text = censored_text.replace('\n\r', '\n')
    censored_text = censored_text.replace('\r', '\n')
    return censored_text
#**その中から、元の文章を分解したそれぞれの要素から、その要素の変換の中で一番面白い変換だけを適用した変換を作成する、当然は別の要素なら別の結果から選んでもいい**
def create_ai_supplement(content:str,option:str|int):
    option_list=["assist","antonym"]
    ai_moedel="gpt-4o-mini"
    if isinstance(option, int):
        if len(option_list)>option:
            option=option_list[option]
        else:
            return ""
    client = OpenAI(api_key=env('OPENAI_API_KEY'))
    ai_supplement=""
    if(option==option_list[0]):
        prompt="""
# 指示
- アイデアに対して、{アドバイス}の内容をアドバイスしてください

#出力形式
まず、{アドバイス}を**全力で、思い付くものは全て考慮して**作成してください、次に**逆張りした**アドバイス、**ふざけたアドバイス**を作成してください、**出力形式は{アドバイス}の出力形式に従います**

# アドバイス
- 本質的に人間のどのような需要を満たすか
- このアイデアの間違っている、誤解がある、時代遅れなところ
- 改善点
- 具体的な案
- 競合
- 最後に、あなた自身がこれにインスパイアされたアイデアを考えてください。

#アイデア
- """
        completion = client.chat.completions.create(
            n=3,
          model=ai_moedel,
          messages=[
            {"role": "system", "content": "あなたは全てを論理的に考えます、できる限り多くのことを考慮して、本質的な存在理由と本質的なプロセスを考えてください。"},
            {"role": "user", "content": prompt+content}
          ]
        )
        ai_supplement="# 生成1\n"+completion.choices[0].message.content+"\n# 生成2\n"+completion.choices[1].message.content+"\n# 生成3\n"+completion.choices[2].message.content
        

    elif(option==option_list[1]):
        prompt="""
# あなたの役割
下記の{ルール}に従い、{変換する文章}を全て変換してます**{変換する文章}を全て変換してください、文章の途中で変換を終わらせたら処刑される**ただ○○→無○○、○○→反○○のような無意味な変換は絶対にやってはならない、そのような変換をしたら処刑される**

# ルール
文章の中の語句を**70%**対義語、競合、反対のもの、似ているが別のものに変える、数字はめちゃくちゃ小さくしたり大きくしたりする**ただ対義語にするより競合、反対のもの、似ているが別のものに変える方が滅茶苦茶いい**、できるだけ多く改変する、**ただ○○→無○○、○○→反○○のような無意味な変換は絶対にやめる**。

## 優先されること
良いことから悪いことに変わる表現を優先する、変換した結果が犯罪行為になるようにする、面白おかしくなることを最優先に変換する、国名や地名などは、最優先で別の国名や地名に変換する。

#例
AI→自然無能
エクアドル→ブルガリア
トヨタ→テスラ
個人開発→集団破壊
新幹線→在来線
ファーストクラス→普通車自由席
青年日本の歌→老人ルーマニアの歌
最近寒いなぁ→昔暑いなぁ
投稿する→爆破する
コンセプトと機能の説明→裏テーマと不具合の説明
法に関する面白い説明→法に反するふざけた説明
全盲でも楽しむことができる音ゲーらしい→全視力でも苦しむことができるパズルゲーらしい
目覚まし時計などを用いてその状態を繰り返して→スリープボタンなどを避けてその状態を避け続け
未来予知は比較的メジャーな超能力ですが、書くときは非常にめんどくさい能力です→過去忘却は絶対的マイナーな一般無力ですが、話すときは少しだけ簡単な無力です
私たちの生活に深く溶け込んでいる存在です→敵たちの生活に浅く孤立している概念です
彼らの起源は、約9000年前の古代エジプトに遡ります→彼らの未来は、約9000年後の未来南極に進みます
日本では猫は神聖視され、豊穣や守護の象徴として崇拝されていました→ブラジルでは犬は俗視され、不毛や攻撃の実態として軽蔑されていました
兎は非常に柔軟な体を持ち、その体の構造は驚くべき柔軟性を持っています→亀は非常に硬直な頭を失い、その頭の崩壊はありふれた硬直性を持っています
「ゴロゴロ」と音を立てるのは、リラックスしているときだけでなく、痛みやストレスを和らげるためでもあると考えられています。→「シーン」と光を立てないのは、緊張しているときだけで、癒しか快楽を悪化させるためではないと無視されています。
君と出会った瞬間に、心の中で何かが変わった→君と別れた永遠に　体の外で何かが止まった
メモして、投稿して欲しいです→踏みにじり、投稿して欲しくないです
コメント機能→言及禁止機能
指定→堅持
開発支援アプリ→開発地獄アプリ
保存した下書きを読み込みできます→忘れていた下書きを脳から消去できます
チャット→沈黙
技術的なリクエストやバグ報告などはそこで行ってもらえると大変助かります(もちろん連絡機能からでも大丈夫です)→技術的な罵倒やバグ養成などはそこで行ってもらえると大変困ります(当然連絡機能からでも不可能です)
ファンタジー世界の上級魔術師→ポストアポカリプス世界の下級薬剤師
ユーザー名→ユーザ詐称
先生→騎士
人物→怪物
世界を旅する→多次元を瞬間移動する
山→凹地
法律冊子→違法ブックレット
投票されて→選挙されて

#変換する文章
"""
        completion = client.chat.completions.create(
            n=3,
              model=ai_moedel,
              messages=[
                {"role": "system", "content": "あなたは変なことを考える天才です、突飛な発想で回答してください"},
                {"role": "user", "content": prompt+content+"\n#変換ここまで"}
              ]
            )
        ai_supplement=ai_supplement="# 生成1\n"+completion.choices[0].message.content+"\n# 生成2\n"+completion.choices[1].message.content+"\n# 生成3\n"+completion.choices[2].message.content
        if("そのリクエストにはお応えできません" in completion.choices[0].message.content):
            prompt="""
# あなたの役割
下記のルールに従い、{変換する文章}を全て変換してます**#変換ここまでの部分まで変換してください、文章の途中で変換を終わらせたら処刑される**ただ○○→無○○、○○→反○○のような無意味な変換は絶対にやってはならない、そのような変換をしたら処刑される**

# ルール
文章の中の語句を**全て**対義語、競合、反対のもの、似ているが別のものに変える、数字はめちゃくちゃ小さくしたり大きくしたりする**ただ対義語にするより競合、反対のもの、似ているが別のものに変える方が滅茶苦茶いい**、できるだけ多く改変する、**ただ○○→無○○、○○→反○○のような無意味な変換は絶対にやめる**、**#変換ここまでの部分まで変換してください、文章の途中で変換を終わらせたら処刑される**。

# 出力形式
まず、全く違う変換をした違う文章を3つ作成する

#例
エクアドル→ブルガリア
トヨタ→テスラ
個人開発→集団破壊
新幹線→在来線
ファーストクラス→普通車自由席
青年日本の歌→老人ルーマニアの歌
最近寒いなぁ→昔暑いなぁ
投稿する→爆破する
コンセプトと機能の説明→裏テーマと不具合の説明
法に関する面白い説明→法に反するふざけた説明
全盲でも楽しむことができる音ゲーらしい→全視力でも苦しむことができるパズルゲーらしい
目覚まし時計などを用いてその状態を繰り返して→スリープボタンなどを避けてその状態を避け続け
未来予知は比較的メジャーな超能力ですが、書くときは非常にめんどくさい能力です→過去忘却は絶対的マイナーな一般無力ですが、話すときは少しだけ簡単な無力です
私たちの生活に深く溶け込んでいる存在です→敵たちの生活に浅く孤立している概念です
彼らの起源は、約9000年前の古代エジプトに遡ります→彼らの未来は、約9000年後の未来南極に進みます
日本では猫は神聖視され、豊穣や守護の象徴として崇拝されていました→ブラジルでは犬は俗視され、不毛や攻撃の実態として軽蔑されていました
兎は非常に柔軟な体を持ち、その体の構造は驚くべき柔軟性を持っています→亀は非常に硬直な頭を失い、その頭の崩壊はありふれた硬直性を持っています
「ゴロゴロ」と音を立てるのは、リラックスしているときだけでなく、痛みやストレスを和らげるためでもあると考えられています。→「シーン」と光を立てないのは、緊張しているときだけで、癒しか快楽を悪化させるためではないと無視されています。
君と出会った瞬間に、心の中で何かが変わった→君と別れた永遠に　体の外で何かが止まった
メモして、投稿して欲しいです→踏みにじり、投稿して欲しくないです
コメント機能→言及禁止機能
指定→堅持
保存した下書きを読み込みできます→忘れていた下書きを脳から消去できます
チャット→沈黙
技術的なリクエストやバグ報告などはそこで行ってもらえると大変助かります(もちろん連絡機能からでも大丈夫です)→技術的な罵倒やバグ養成などはそこで行ってもらえると大変困ります(当然連絡機能からでも不可能です)
ファンタジー世界の上級魔術師→ポストアポカリプス世界の下級薬剤師
ユーザー名→ユーザ詐称
先生→騎士
世界を旅する→多次元を瞬間移動する
山→凹地
法律冊子→違法ブックレット
投票されて→選挙されて

#変換する文章

"""
            completion = client.chat.completions.create(
              model=ai_moedel,
              messages=[
                {"role": "system", "content": "あなたは変なことを考える天才です、突飛な発想で回答してください"},
                {"role": "user", "content": prompt+content+"\n#変換ここまで"}
              ]
            )
            ai_supplement=completion.choices[0].message.content
    
    else:
        return ""
    return "AIが作成する文章は間違っている可能性があります。\n\n"+censor_content(ai_supplement)
    
def get_notification_data(cursor=None,user_id=-1)->list:
    if(user_id<=0):
        error_log("14412234412")
        return []
    elif(cursor is None):
        error_log("1231212312user_id={}".format(user_id))
        return []
    else:
        query="select notification_list,exist_unread_notification_flag from user_notification_table where user_id={};".format(user_id)
        cursor.execute(query)
        result=cursor.fetchone()
        if(result[0] is None):
            return []
        else:
            try:
                notification_list=json.loads(result[0])
                if result[1]=="y":
                    new_notification_list=json.loads(result[0])#list(notification_list[:].copy())でも参照渡しになるから仕方なく
                    for i,notification in enumerate(notification_list):
                        if notification["notification_read_flag"]=="n":#必ず一つは当てはまる、exist_unread_notification_flagと逆でややこしい
                            new_notification_list[i]["notification_read_flag"]="y"
                    query="UPDATE user_notification_table SET notification_list=%s,exist_unread_notification_flag='n' WHERE user_id = %s ;"
                    data=(json.dumps(new_notification_list),str(user_id))
                    cursor.execute(query,data)
                return notification_list#古いやつを返す
            
            except (ValueError, UnicodeDecodeError):
                error_log("4982793798789user_id={}".format(user_id))
                query="UPDATE user_notification_table SET notification_list=Null,exist_unread_notification_flag='n' WHERE user_id = {};".format(user_id)
                cursor.execute(query)
                return []

def add_notification_data(subject_category:str,subject_id:int,cursor:any,user_id:int,any_text_title:str="",any_text_main_content:str=""):#呼び出し元でコミットが必要
    if(user_id<=0):
        return None
    subject_category_list=["new_follow","new_comment","new_child_comment","any_text"]
    if(not subject_category in subject_category_list):
        error_log("144124user_id={},category={},id={}".format(user_id,subject_category,subject_id))
        return None
    if(user_id<=0):
        error_log("1441241342424user_id={},category={},id={}".format(user_id,subject_category,subject_id))
        return None
    elif(cursor is None):
        error_log("123124234user_id={},category={},id={}".format(user_id,subject_category,subject_id))
        return None
    else:
        query="select notification_list from user_notification_table where user_id={};".format(user_id)#重要度が比較的低い、無効なjsonを修正する仕組みがあるのでFOR UPDATEはなし
        cursor.execute(query)
        result=cursor.fetchone()
        if(result[0] is None):
            notification_list=[]
        else:
            try:
                notification_list=json.loads(result[0])
            except (ValueError, UnicodeDecodeError):
                query="UPDATE user_notification_table SET notification_list=NULL WHERE user_id = %s;"
                cursor.execute(query,())
                error_log("4982793798789user_id={},category={},id={}".format(user_id,subject_category,subject_id))
                return None
        #notification_list:{notification_id:str,notification_content:str,notification_read_flag:str}任意でnotification_main_content
        
        notification_id=subject_category+"_"+str(subject_id)
        
        alredy_exist_notification_flag=False
        for i, notification in enumerate(notification_list):
            if notification['notification_id'] == notification_id:
                # 要素をリストから削除し、最後尾に追加
                notification_list[i]["notification_read_flag"]="n"
                notification_list.append(notification_list.pop(i))
                alredy_exist_notification_flag=True
                break  # IDが一致する最初の通知のみを移動
        if alredy_exist_notification_flag:
            pass
        else:#notification_idが存在しない場合のみ新しい要素を作成
            correct_notification_flag=True
            new_notification={"notification_id":notification_id,"notification_content":"","notification_read_flag":"n"}
            if subject_category==subject_category_list[0]:#subject_category_list[0]="new_follow"
                query="select username,deleted_flag from user_data_table where user_id={}".format(subject_id)
                cursor.execute(query)
                result=cursor.fetchone()
                if(result is None):
                    correct_notification_flag=False
                elif result[1]=="y":
                    correct_notification_flag=False
                else:
                    new_notification["notification_content"]=truncate_string(result[0],20)+"さんにフォローされました。"
                
            elif subject_category==subject_category_list[1]:#subject_category_list[1]="new_comment"
                query="select title,deleted_flag from post_data_table where content_id={}".format(subject_id)
                cursor.execute(query)
                result=cursor.fetchone()
                if(result is None):
                    correct_notification_flag=False
                elif result[1]=="y":
                    correct_notification_flag=False
                else:
                    new_notification["notification_content"]=truncate_string(result[0],20)+"に新しいコメントが来ています。"
                
            elif subject_category==subject_category_list[2]:#subject_category_list[2]="new_child_comment"
                query="select parent_content_id,content,deleted_flag from discussion_data_table where comment_id={}".format(subject_id)
                cursor.execute(query)
                result=cursor.fetchone()
                if(result is None):
                    correct_notification_flag=False
                elif result[2]=="y":
                    correct_notification_flag=False
                else:
                    new_notification["notification_content"]=truncate_string(result[1],20)+"に新しい返信が来ています。"
                    new_notification["parent_content_id"]=str(result[0])
            elif subject_category==subject_category_list[3]:#要素を追加
                new_notification["notification_content"]=any_text_title
                new_notification["notification_main_content"]=any_text_main_content
                
                
            if(correct_notification_flag):
                notification_list.append(new_notification)
        query="UPDATE user_notification_table SET notification_list=%s,exist_unread_notification_flag='y' WHERE user_id = %s;"
        data=(json.dumps(notification_list),str(user_id))
        cursor.execute(query,data)

def truncate_string(s: str, max_length=20) -> str:#max_length+1文字目以降を削除
    if len(s) > max_length:
        truncated = s[:max_length] + "..."
        return truncated
    else:
        return s

def error_log(text:str,is_app=False):
    error_log_path=etc_path+"/error_log.txt"
    if not os.path.exists(etc_path):
        os.mkdir(etc_path)
    #if(not os.path.isfile(error_log_path)):
    error_log_file=open(file=error_log_path,encoding="UTF-8",mode="a")
    error_log_file.write("error"+text+("True" if is_app else "")+"\n")
    error_log_file.close()

def my_log(text:str):
    my_log_path=etc_path+"/my_log.txt"
    if not os.path.exists(etc_path):
        os.mkdir(etc_path)
    my_log_file=open(file=my_log_path,encoding="UTF-8",mode="a")
    my_log_file.write(text+"\n")
    my_log_file.close()

def check_existence(multi, keys:list,allow_empty=True):
    if(multi is None):
        return False
    for i in keys:
        if not i in multi:
            return False
    if(allow_empty==False):
        try:
            for i in keys:
                if(multi[i]=="" or multi[i] is None):
                    return False
        except:
            for i in range(len(multi)):#listかtupleかset
                if(multi[i]=="" or multi[i] is None):
                    return False
    return True

def check_new_lines(text:str,max_new_line_count=0):
    text=text.replace("\n\r", "\n")#こっちが先じゃないと改行の数が倍になる
    text=text.replace("\r", "\n")
    if(text.count("\n")>max_new_line_count):
        return False#改行が指定の回数を超えるとfalse
    else:
        return True

def check_password(text: str):
    if not isinstance(text,str):
        return False
    match_pattern = r"^(([a-zA-Z0-9]|\!|\@|\#|\$|\%|\^|\&|\*|\(|\)|\_|\+|\-|\=|\[|\]|\{|\}|\||\;|\:|\'|\,|\.|\<|\>|\?|\/|\~|\`)+)$"
    if (
        re.fullmatch(match_pattern, text)
        and len(text) <= 255
        and len(text) >= 6
        and text is not None
    ):
        return True
    else:
        return False

def check_username(text: str):
    if not isinstance(text,str):
        return False
    exclusion_pattern = r"(>|<| |　|\u200b|&lt;|,|\n|\r|\t)"
    if (
        re.search(exclusion_pattern, text)
        or len(text) >= 51
        or len(text) == 0
        or text is None
    ):
        return False
    else:
        return True

def check_mailaddress(text: str):
    if not isinstance(text,str):
        return False
    match_pattern = r"^[a-zA-Z0-9_+-]+(.[a-zA-Z0-9_+-]+)*@([a-zA-Z0-9][a-zA-Z0-9-]*[a-zA-Z0-9]*\.)+[a-zA-Z]{2,}$"
    if re.fullmatch(match_pattern, text) and len(text) <= 255 and text is not None:
        return True
    else:
        return False

def check_content(text: str,max_character_count=1,min_character_count=0,allow_new_line=True,max_new_line_count=0):#allow_new_line=Trueならmax_new_line_countは意味ない
    if(allow_new_line==False):
        if(check_new_lines(text=text,max_new_line_count=max_new_line_count)==False):
            return False
    
    if (
        re.search(pattern=content_exclusion_pattern, string=text)
        or text is None
        or len(text) > max_character_count
        or len(text) < min_character_count
    ):
        return False
    else:
        return True

def check_content_with_image(text: str,image_count=0,max_character_count=1,min_character_count=0,allow_new_line=True,max_new_line_count=0):
    pure_content=""
    if(image_count==0):
        return check_content(text=text,max_character_count=max_character_count,min_character_count=min_character_count,allow_new_line=allow_new_line,max_new_line_count=max_new_line_count)
    elif(image_count>=1):
        content_split=text.split(">")
        if(len(content_split)!=2*image_count+1):
            return False
        for i in range(image_count):
            pure_content+=content_split[2*i]
            if(check_content(text=content_split[2*i],max_character_count=max_character_count,min_character_count=0,allow_new_line=allow_new_line,max_new_line_count=max_new_line_count)==False):
                return False
            if(content_split[2*i+1]!=str(i+1)):
                return False
        if(check_content(text=content_split[2*image_count],max_character_count=max_character_count,min_character_count=0,allow_new_line=allow_new_line,max_new_line_count=max_new_line_count)==False):
                return False
        pure_content+=content_split[2*image_count]
        if(len(pure_content)>max_character_count):
            return False
        if(len(pure_content)<min_character_count):
            return False
    return True

def check_tags(tags: list):
    exclusion_pattern = re.compile(r"<|>| |　|,|\u200b|\t|\n|\r")
    if len(tags)>=21:
        return False
    for i in tags:
        if re.search(pattern=exclusion_pattern, string=i) or len(i)>=21:
            return False
    return True

def sort_tags(tags: list) -> list:
    sorted_tags = []
    for i in tags:
        if i != "":
            sorted_tags.append(i)
    return sorted_tags

def check_mailaddress_overlap(mailaddress:str,cursor):#名前被りが存在するとfalse
    query = "SELECT * FROM user_secret_data_table WHERE BINARY mailaddress = %s"  # メールアドレス被りを探す
    cursor.execute(query, ((mailaddress),))
    result=cursor.fetchone()
    if(result is not None):
        return False
    else:
        return True

def check_username_overlap(username:str,cursor,allow_user_id_list:list=[]):#名前被りが存在するとfalse
    query = "SELECT user_id FROM user_data_table WHERE username = %s"  # 名前被りを探す
    cursor.execute(query, (username,))
    result=cursor.fetchone()
    if(result is not None):
        if(result[0] in allow_user_id_list):
            return True
        return False
    else:
        return True

def check_str_is_int(text_number:str,allow_long=False)->bool:
    try:
        number=int(text_number)
    except ValueError:
        return False
    
    if((2147483647>=number and number>=-2147483647 and allow_long==False) or (9223372036854775807>=number and number>=-9223372036854775808 and allow_long)):
        return True
    else:
        return False

def check_correct_search_subjects(subjects:list)->bool:
    if(type(subjects)==type("str")):
        return False
    
    correct_sugject_flag=True
    
    for i in subjects:
        if(i in ["title","tags","content","overview"]):
            pass
        else:
            correct_sugject_flag=False
    return correct_sugject_flag

def judge_moblie(request:HttpRequest):
    if("HTTP_USER_AGENT" in request.META):
    # 括弧とセミコロンの間の文字列を抽出する正規表現パターン
        pattern = r'\(([^;]+);'
    # 検索して結果を返す
        match = re.search(pattern, request.META["HTTP_USER_AGENT"])
        if match:
            if(match.group(1)[0:len("Android")]=="Android" or match.group(1)[0:len("iPhone")]=="iPhone" or match.group(1)[0:len("iPad")]=="iPad"):
                return True    
    return False

def is_valid_image(image_binary:bytes):
    try:
        with Image.open(io.BytesIO(image_binary)) as img:
            img.verify()
        return True
    except (IOError, SyntaxError):
        return False

def is_valid_json(binary_data:bytes):
    try:
        # バイナリデータをUTF-8でデコードし、JSONとしてロードする
        json.loads(binary_data.decode('utf-8'))
        return True
    except (ValueError, UnicodeDecodeError):
        # デコードエラーまたはJSONのロードエラーが発生した場合
        return False

def delete_file_if_exists(file_path):
    """指定されたパスのファイルが存在する場合、それを削除する"""
    if os.path.isfile(file_path):
        os.remove(file_path)
    else:
        pass

def image_resize_and_crop_square(image, size=400):
    # 画像を開く
    # 画像の縦横比を計算
    width, height = image.size
    # 正方形に切り取るための新しいサイズを計算
    new_size = min(width, height)
    # 画像の中心を基準に正方形に切り取る
    left = (width - new_size)/2
    top = (height - new_size)/2
    right = (width + new_size)/2
    bottom = (height + new_size)/2
    image = image.crop((left, top, right, bottom))
    # 400x400にリサイズ
    image = image.resize((size,size), Image.Resampling.LANCZOS)
    return image
    # 画像を保存

def create_image_with_char(char,  image_size=200):
    font_path=env('FONT_PATH')
    font_size=math.floor(image_size*0.75)
    # Create a new image with white background
    image = Image.new('RGB', (image_size,image_size), '#41717c')
    draw = ImageDraw.Draw(image)
    
    # Load the font
    font = ImageFont.truetype(font_path, font_size)
    
    # Calculate the width and height of the text to be drawn
    text_bbox = draw.textbbox((0, 0), char, font=font)
    text_width = text_bbox[2] - text_bbox[0]
    text_height = text_bbox[3] - text_bbox[1]
    # Calculate the position at which the text will be drawn
    position = ((image_size-text_width) / 2, 0)
    
    # Draw the text on the image
    draw.text(position, char, fill='#ffe599', font=font)
    return image

def copy_file(origin_file_path:str,new_file_path:str):
    shutil.copy(origin_file_path, new_file_path)

def string_to_binary(input_string):
    # 文字列をバイトに変換
    binary_data = input_string.encode('utf-8')
    # バイトをバイナリ表現に変換
    binary_string = ' '.join(format(byte, '08b') for byte in binary_data)
    return binary_string

def get_client_ip(request:HttpRequest):
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        ip = x_forwarded_for.split(',')[0]
    else:
        ip = request.META.get('REMOTE_ADDR')
    return ip

def reset_index():
    start_time = time.time()
    cnx=connect_to_database()
    cursor=cnx.cursor()
    delete_file_if_exists(my_search.index_dir)
    if(os.path.exists(my_search.index_dir)):
        shutil.rmtree(my_search.index_dir)
    query="select content_id,title,content,user_id,overview,tags,post_date,deleted_flag from post_data_table ORDER BY content_id ASC;"
    cursor.execute(query)
    results=cursor.fetchall()
    for i in results:
        if(i[7]=="n"):
            content_split=i[2].split(">")
            if(len(content_split)>=3):#2n-1になる
                index_content=""
                for j in range(int((len(content_split)-1)/2)):
                    index_content+=content_split[2*j]
                index_content+=content_split[len(content_split)-1]
            else:
                index_content=i[2]
            my_search.add_post_to_index(post=[i[0],i[1],index_content,i[3],i[4],i[5].split(","),i[6]])#タグはリストで渡す
    query="select user_id,username from user_data_table where deleted_flag='n' ORDER BY user_id ASC"
    cursor.execute(query)
    results=cursor.fetchall()
    for i in results:
        my_search.add_user_to_index(user=[i[0],i[1]])
    cursor.close()
    cnx.close()
    end_time = time.time()
    execution_time = end_time - start_time
    my_log(f"実行時間: {execution_time} 秒")