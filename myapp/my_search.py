import whoosh.index
from whoosh.fields import *
from pathlib import Path
from whoosh import qparser
import whoosh.analysis
import os
import unicodedata
from whoosh.sorting import FieldFacet

index_dir = str(Path(__file__).resolve().parent) + ("/indices")
post_index_schema = Schema(
    content_id=NUMERIC(stored=True),
    title=NGRAMWORDS(minsize=1, maxsize=15),
    overview=NGRAMWORDS(minsize=1, maxsize=10),
    content=NGRAMWORDS(minsize=1, maxsize=8),
    tags=NGRAMWORDS(minsize=1, maxsize=20),
    user_id=KEYWORD(analyzer=analysis.StandardAnalyzer(stoplist=None)),
    posted_date=DATETIME,
    for_all=KEYWORD(analyzer=analysis.StandardAnalyzer(stoplist=None))
)

user_index_schema = Schema(
    user_id=ID(stored=True),
    username_whole=KEYWORD(analyzer=analysis.StandardAnalyzer(stoplist=None)),
    username_n_gram=KEYWORD(analyzer=analysis.StandardAnalyzer(stoplist=None)),
    #mailaddress_whole=KEYWORD(analyzer=analysis.StandardAnalyzer(stoplist=None)),
    for_all=KEYWORD(analyzer=analysis.StandardAnalyzer(stoplist=None))
    )

"""def to_wordset(
    text: str, min_gram_parent: int, max_gram_parent: int, includ_whole_text=False
) -> set:
    m = MeCab.Tagger("-Ochasen")
    hukugou = ""  # 複合名詞
    word_set = set()  # 抜き出した名詞集合

    # 不要語集合
    remove_words = {
        "(",
        ")",
        "（",
        "）",
        "[",
        "]",
        "「",
        "」",
        "+",
        "-",
        "*",
        "$",
        "'",
        '"',
        "、",
        ".",
        "”",
        "’",
        ":",
        ";",
        "_",
        "/",
        "?",
        "!",
        "。",
        ",",
        "=",
        "＝",
        "{",
        "}",
        "【",
        "】",
        "『",
        "』",
        "＊",
        "※",
        "▼",
        "　",
        " ",
    }

    # 分かち書きして分割された語を順にループ
    for chunk in m.parse(text.rstrip()).splitlines()[
        :-1
    ]:  # 改行ごとに分割して順番を逆にしたリストを作って
        if chunk == "" or ord(chunk[0])==9 or len(chunk.rstrip().split("\t"))<=2:
            word = ""  # 分かち書きされた語
            tok = ""  # 上の語の品詞
        else:
            word = chunk.rstrip().split("\t")[0]  # 分かち書きされた語
            tok = chunk.rstrip().split("\t")[3]  # 上の語の品詞

        # 分かち書きした語の中に不要語集合内の語が出てきたら、flagに1以上の整数
        flag = len([r for r in word if r in remove_words])
        if flag > 0:
            # もし複合語があったら
            if hukugou != "":
                word_set.add(hukugou)  # 集合なので同じものは複数回入ることがない
            hukugou = ""  # リセット
            continue

        # もしtokが名詞か動詞か助詞ならhukugouに追加して、wordもword_setに追加
        if (
            tok.startswith("名詞")
            or tok.startswith("動詞")
            or tok.startswith("連用形")
            or tok.startswith("助詞")
        ):
            hukugou = hukugou + word
            word_set.add(word)
        else:
            # もし複合語があったら
            if hukugou != "":
                word_set.add(hukugou)
            hukugou = ""  # リセット
    word_set = list(word_set)
    word_and_letter_set = set()
    for c in word_set:
        word_and_letter_set = word_and_letter_set.union(
            create_n_gram(text=c, min_gram=min_gram_parent, max_gram=max_gram_parent)
        )
    if includ_whole_text:
        word_and_letter_set.add(text)
    return word_and_letter_set
"""

def create_n_gram(text: str, min_gram: int, max_gram: int, includ_whole_text=False,split_by_new_line=True) -> set:
    analysis_of_text = set()
    text_temp: str
    text=text.replace("\n\r", "\n")#こっちが先じゃないと改行の数が倍になる
    text=text.replace("\r", "\n")
    if(split_by_new_line):
        text=text.replace("\n", " ")
    else:
        text=text.replace("\n", "")
    text_split=text.split(" ")
    for part_text in text_split:
        for i in range(max_gram - min_gram):  # 小さいgramからやる
            if len(part_text) >= min_gram + i:
                text_temp = part_text
                for j in range(len(part_text) - (min_gram + i) + 1):
                    analysis_of_text.add(
                        text_temp[0 : min_gram + i]
                    )  # [start:stop]とすると、start <= x < stop 0から始まる
                    text_temp = text_temp[1:]  # なぜか"abcd"[1:]=bcd
    if(includ_whole_text):
        analysis_of_text.add(text)
    return analysis_of_text

def add_post_to_index(post: list):
    # start = time.time()
    content_id = int(post[0])
    title = unicodedata.normalize('NFKC', post[1])
    overview = unicodedata.normalize('NFKC', post[4])
    content = unicodedata.normalize('NFKC', post[2])
    tags=" ".join(post[5])
    user_id=post[3]
    posted_time=post[6]
    if not os.path.exists(index_dir):
        os.mkdir(index_dir)
    if whoosh.index.exists_in(dirname=index_dir, indexname="post_index"):
        ix = whoosh.index.open_dir(
            dirname=index_dir, indexname="post_index", schema=post_index_schema
        )
    else:
        ix = whoosh.index.create_in(
            dirname=index_dir, indexname="post_index", schema=post_index_schema
        )
    writer = ix.writer()
    writer.add_document(
        content_id=content_id,
        title=title,
        overview=overview,
        content=content,
        tags=tags,
        user_id=str(user_id),
        posted_date=posted_time,
        for_all="inculde_all"
    )
    writer.commit()  # 必ず必要

def delete_post_from_index(content_id:int):
    if not os.path.exists(index_dir):
        os.mkdir(index_dir)
    if whoosh.index.exists_in(dirname=index_dir, indexname="post_index"):
        ix = whoosh.index.open_dir(
            dirname=index_dir, indexname="post_index", schema=post_index_schema
        )
    else:
        ix = whoosh.index.create_in(
            dirname=index_dir, indexname="post_index", schema=post_index_schema
        )
    writer = ix.writer()
    writer.delete_by_term('content_id', str(content_id))
    writer.commit()

def add_user_to_index(user: list):
    # start = time.time()
    user_id = int(user[0])
    username_whole = unicodedata.normalize('NFKC', user[1]).replace("\n", "").replace("\r", "")
    #mailaddress_whole=unicodedata.normalize('NFKC', user[2]).replace("\n", "").replace("\r", "")
    if not os.path.exists(index_dir):
        os.mkdir(index_dir)
    if whoosh.index.exists_in(dirname=index_dir, indexname="user_index"):
        ix = whoosh.index.open_dir(
            dirname=index_dir, indexname="user_index", schema=user_index_schema
        )
    else:
        ix = whoosh.index.create_in(
            dirname=index_dir, indexname="user_index", schema=user_index_schema
        )

    writer = ix.writer()
    writer.add_document(
        user_id=str(user_id),
        username_whole=username_whole,
        username_n_gram=" ".join(
            create_n_gram(text=username_whole,min_gram=1,max_gram=30,includ_whole_text=True)
        ),
        #mailaddress_whole=mailaddress_whole,
        for_all="inculde_all"
    )
    writer.commit()  # 必ず必要
    # print(str((time.time() - start)*10000//10)+"ms")

def search_post_index(include_text="",exclude_text="",search_subjects=["title"]) -> list:
    include_text=unicodedata.normalize('NFKC',include_text)
    exclude_text=unicodedata.normalize('NFKC',exclude_text)
    if not os.path.exists(index_dir):
        os.mkdir(index_dir)
    if whoosh.index.exists_in(dirname=index_dir, indexname="post_index"):
        ix = whoosh.index.open_dir(
            dirname=index_dir, indexname="post_index", schema=post_index_schema
        )
    else:
        ix = whoosh.index.create_in(
            dirname=index_dir, indexname="post_index", schema=post_index_schema
        )
    with ix.searcher() as searcher:
        # QueryParserに"content"内を検索することを指定
        parser = qparser.MultifieldParser(
            search_subjects, ix.schema
        )
        # OperatorsPluginはAnd,orなどに好きな記号を割り当てることが出来る
        op = qparser.OperatorsPlugin(And="&", Or=">", Not="<")#誤作動防止のためnotとorは禁止された文字
        parser.replace_plugin(op)  # opをセット
        search_words = include_text.split()  # この部分をwords = words.split(" ")から訂正しました
        search_words = " ".join(search_words)  # 空白の処理
        if(exclude_text!=""):
            exclude_words=exclude_text.split()
            for i in exclude_words:
                search_words+=" <("+i+")"
        query = parser.parse(search_words)  # parserに検索語を入れる
        results = searcher.search(query, limit=None,sortedby=FieldFacet("content_id", reverse=False))  # 検索語で全文検索
        # print(results)
        matched_posts = [int(result.values()[0]) for result in results]  # resultはlist
        #print(str((time.time() - start)*10000//10)+"ms")
        return matched_posts
