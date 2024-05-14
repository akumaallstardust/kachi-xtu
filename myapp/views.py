import random
import datetime
import json
from PIL import Image
import io
import time
from django.shortcuts import render
from django.http import HttpResponse
from django.http import HttpRequest
from django.http.response import JsonResponse
from passlib.hash import argon2
import re
import os
from pathlib import Path
from . import my_search
from . import my_functions
import sys
sys.path.append('../')
import secret_values
from pathlib import Path
from django.views.decorators.csrf import csrf_exempt
import base64

site_url="http://192.168.1.16:8000/"
current_path=str(Path(__file__).resolve().parent) + ("/indices")
t_delta = datetime.timedelta(hours=9)
JST = datetime.timezone(t_delta, "JST")
secret_values.password_salt
session_duration = 7 * 24 * 60 * 60
redirect_to_toppage = HttpResponse(
    "<head><meta http-equiv='refresh' content='0; url="+site_url+"'></head>"
)

redirect_to_error_page=HttpResponse(
    "<head><meta http-equiv='refresh' content='0; url="+site_url+"error/'></head>")

redirect_to_signup = HttpResponse(
    "<head><meta http-equiv='refresh' content='0; url="+site_url+"signup/'></head>"
)


class connection_to_user_db:  # 基本的にはこれを使ってセッション管理 update_valuesを無効化済み　後で絶対戻す
    def __init__(self, request: HttpRequest | None = None,request_json_data: dict | None = None,get_user_setting=False,from_app_flag=False):  # 最初にユーザー確認
        self.cnx = my_functions.connect_to_database()
        self.cursor = self.cnx.cursor(buffered=True)
        if request is not None:
            self.session = session_data(request=request,request_json_data=request_json_data,from_app_flag=from_app_flag)#request_json_dataがNoneでもsession_dataの方で判定
            self.session.authentication_session(self.cursor)
            if(get_user_setting):
                self.session.set_user_setting_dict(self.cursor)
        elif request_json_data is not None:
            self.session = session_data(request_json_data=request_json_data,from_app_flag=from_app_flag)
            self.session.authentication_session(self.cursor)
            if(get_user_setting):
                self.session.set_user_setting_dict(self.cursor)
    def terminate_connection(self) -> None:  # DBとの接続解除
        self.cursor.close()
        self.cnx.close()

    def set_response(
        self, response: HttpResponse
    ) -> HttpResponse:  # セッションの更新とDBとの接続解除、最後のreturn時に使う
        #self.session.update_values(self.cursor)
        self.cnx.commit()  # 必須
        self.session.set_cookie(response)
        self.terminate_connection()
        return response
    
    def get_full_user_data_dict(self,already_set_setting_dict=False):
        return self.session.get_full_user_data_dict(cursor=self.cursor,already_set_setting_dict=already_set_setting_dict)
    
    def return_error(self,requset:HttpRequest):
        if(self.session.is_moblie):
            html_file="myapp/moblie_site/unauthorized_request.html"
        else:
            html_file="myapp/unauthorized_request.html"
        return self.set_response(
            render(request=requset,
            template_name=html_file,
            context=self.session.user_id_dict,
            )
        )


class session_data:  # 基本的にcconnection_to_user_dbで使う
    user_id=-1
    self_declaration_user_id=-1
    user_id_dict = {"user_id": str}
    user_setting_dict={"auto_comment_open":str,"defalt_exclude_words":str}
    value_1=0
    value_2=0
    user_agent=""
    update_session_id_flag=True
    is_moblie=False
    ip_address=""
    is_app=False
    device_unique_id=""
    
    def __init__(self, request: HttpRequest | None = None,request_json_data:dict | None = None, user_id=-1,from_app_flag=False,uni_id:str | None = None):
        if user_id is not None:#ここ使ってない
            self.self_declaration_user_id = int(user_id)
        if request is not None:
            self.set_current_values(request=request)  # 未ログインでも基本的に使う
        
        if(request_json_data is not None):
            self.set_current_values(request_json_data=request_json_data)
        self.is_app=from_app_flag
        if uni_id is not None:#setcurrent_valuesでもここでも定義できるのは複雑なので整理しておきたい
            self.device_unique_id=uni_id


    def set_cookie(self, response: HttpResponse):  # 最後に使う
        response.set_cookie(
            key="session_id_1",
            value=(self.value_1),
            samesite="Strict",
            max_age=session_duration,
        )
        response.set_cookie(
            key="session_id_2",
            value=(self.value_2),
            samesite="Strict",
            max_age=session_duration,
        )

    def set_current_values(self, request: HttpRequest | None = None,request_json_data:dict | None = None):  # 基本最初に使う
        if request is not None:
            if "session_id_1" in request.COOKIES and "session_id_2" in request.COOKIES:
                if my_functions.check_str_is_int(request.COOKIES.get("session_id_1"),allow_long=True) and my_functions.check_str_is_int(request.COOKIES.get("session_id_2"),allow_long=True):
                    self.value_1 = int(request.COOKIES.get("session_id_1"))
                    self.value_2 = int(request.COOKIES.get("session_id_2"))

            if("HTTP_USER_AGENT" in request.META):
                self.user_agent = request.META.get("HTTP_USER_AGENT")
                self.is_moblie=my_functions.judge_moblie(request=request)

            if("HTTP_X_FORWARDED_FOR" in request.META or "REMOTE_ADDR" in request.META):
                self.ip_address=my_functions.get_client_ip(request=request)

        if request_json_data is not None:
            if "session_id_1" in request_json_data and "session_id_2" in request_json_data:
                if my_functions.check_str_is_int(request_json_data["session_id_1"],allow_long=True) and my_functions.check_str_is_int(request_json_data["session_id_2"],allow_long=True):
                    self.value_1 = int(request_json_data["session_id_1"])
                    self.value_2 = int(request_json_data["session_id_2"])
                
            if("user_id" in request_json_data):
                if my_functions.check_str_is_int(request_json_data["user_id"]):
                    self.self_declaration_user_id = int(request_json_data["user_id"])
                    
            if "device_unique_id" in request_json_data:
                self.device_unique_id=request_json_data["device_unique_id"]

    def update_values(self, cursor,create_record=False):  # この後commitしなきゃダメ ログイン時はcreate_record=True
        if self.user_id >= 1 and self.update_session_id_flag:
            if cursor is not None:
                if(create_record):
                    self.value_1 = random.randrange(start=0, stop=9223372036854775807, step=1)
                    self.value_2 = random.randrange(start=0, stop=9223372036854775807, step=1)
                    query="delete from user_session_table where user_id=%s and user_agent=%s"
                    data=(str(self.user_id),self.user_agent)
                    cursor.execute(query,data)
                    query = """
                    INSERT IGNORE INTO user_session_table
                    (user_id,session_id_1,session_id_2,user_agent,ip_address,is_app,uniqueid,last_access_time)
                    VALUES
                    (%s,%s,%s,%s,%s,%s,%s,%s) ;"""
                    now = datetime.datetime.now(JST)
                    data=(str(self.user_id),
                          str(self.value_1),
                          str(self.value_2),
                          self.user_agent,
                          self.ip_address,
                          "y" if self.is_app else "n",
                          self.device_unique_id,
                          now.strftime("%Y-%m-%d %H:%M:%S"),)
                    cursor.execute(query, data)
                else:
                    old_value_1=self.value_1
                    old_value_2=self.value_2
                    self.value_1 = random.randrange(start=0, stop=9223372036854775807, step=1)
                    self.value_2 = random.randrange(start=0, stop=9223372036854775807, step=1)
                    query = """
                    UPDATE user_session_table 
                    SET session_id_1=%s,session_id_2=%s,last_access_time=%s WHERE user_id=%s and session_id_1=%s and session_id_2=%s;
                    """
                    now = datetime.datetime.now(JST)
                    data=(
                        str(self.value_1),
                        str(self.value_2),
                        now.strftime("%Y-%m-%d %H:%M:%S"),
                        str(self.user_id),
                        str(old_value_1),
                        str(old_value_2),
                        )
                    cursor.execute(query,data)

    def set_user_setting_dict(self,cursor):
        if(self.user_id>=1):
            query="select * from user_setting_table where user_id={}".format(self.user_id)
            cursor.execute(query)
            result=cursor.fetchone()
            self.user_setting_dict["auto_comment_open"]=result[1]
            self.user_setting_dict["defalt_exclude_words"]=result[2]
        else:
            self.user_setting_dict["auto_comment_open"]="0"
            self.user_setting_dict["defalt_exclude_words"]=""

    def get_full_user_data_dict(self,cursor,already_set_setting_dict=False)->dict:
        response_dict={}
        if(self.user_id>=1):
            if(already_set_setting_dict==False):
                self.set_user_setting_dict(cursor)
            query="select username from user_data_table where user_id={};".format(self.user_id)
            cursor.execute(query)
            result=cursor.fetchone()
            response_dict={**{"username":result[0]},**self.user_setting_dict,**self.user_id_dict}
            query="select followed_users from user_relation_table where user_id={};".format(self.user_id)
            cursor.execute(query)
            result=cursor.fetchone()
            response_dict["followed_users_combined"]=result[0]
        return response_dict
    
    def authentication_session(self, cursor) -> None:
        if (self.value_1 is not None
            and self.value_2 is not None
        ):
            if cursor is not None:
                query = "SELECT user_id,is_app,uniqueid FROM user_session_table WHERE session_id_1=%s AND session_id_2=%s;"
                data = (str(self.value_1), str(self.value_2))
                cursor.execute(query, data)
                matched_session = cursor.fetchone()
                if matched_session is not None:
                    self.user_id = (matched_session[0] if (self.is_app and matched_session[1]=="y" and matched_session[2]==self.device_unique_id and self.self_declaration_user_id==matched_session[0])
                                    or (self.is_app==False and matched_session[1]=="n") else -1)
                    self.user_id_dict["user_id"] = str(self.user_id)
                else:
                    
                    self.user_id = -1
                    self.user_id_dict["user_id"] = str(self.user_id)
            else:
                self.user_id = -2
                self.user_id_dict["user_id"] = str(self.user_id)
        else:
            self.user_id = -3
            self.user_id_dict["user_id"] = str(self.user_id)

    def logout(self,cursor)->None:
        if(self.user_id>=1):
            query="DELETE FROM user_session_table WHERE session_id_1=%s AND session_id_2=%s;"
            data=(str(self.value_1),str(self.value_2),)
            cursor.excute(query,data)


def unauthorized_request(request: HttpRequest):
    cnx=my_functions.connect_to_database()
    cursor=cnx.cursor(buffered=True)
    return HttpResponse("assaa")


def tekitou(request:HttpRequest):
    cono=connection_to_user_db(request=request)
    my_functions.reset_index()
    return cono.set_response(HttpResponse("aaa"))


def test(request:HttpRequest):
    cnx1=my_functions.connect_to_database()
    cnx2=my_functions.connect_to_database()
    cursor1=cnx1.cursor()
    cursor2=cnx2.cursor()
    
    query1="UPDATE x_table SET x=x+1 WHERE id = 1;"
    cursor1.execute(query1)
    cnx1.commit()
    query2="UPDATE x_table SET x=x*2 WHERE id = 1;"
    cursor2.execute(query2)
    
    
    cnx2.commit()
    my_functions.my_log("あいうえお")
    return HttpResponse("assaa")


def index(request: HttpRequest):
    cono = connection_to_user_db(request=request)
    if(cono.session.is_moblie):
        html_file="myapp/moblie_site/index.html"
    else:
        html_file="myapp/index.html"
    return cono.set_response(
        render(
            request=request,
            template_name=html_file,
            context=cono.session.user_id_dict,
        )
    )


def post(request: HttpRequest):
    cono = connection_to_user_db(request=request)
    if(cono.session.is_moblie):
        html_file="myapp/moblie_site/post_page.html"
    else:
        html_file="myapp/post_page.html"
    return cono.set_response(
        render(request=request, template_name=html_file, context=cono.session.user_id_dict)
    )


def signup(request: HttpRequest):
    cono = connection_to_user_db(request=request)
    if(cono.session.is_moblie):
        html_file="myapp/moblie_site/signup_page.html"
    else:
        html_file="myapp/signup_page.html"
    return render(request=request, template_name=html_file,context=cono.session.user_id_dict)


def login_page(request: HttpRequest):
    cono = connection_to_user_db(request=request)
    if(cono.session.is_moblie):
        html_file="myapp/moblie_site/login_page.html"
    else:
        html_file="myapp/login_page.html"
    return render(request=request, template_name=html_file,context=cono.session.user_id_dict)


def my_page(request:HttpRequest):
    cono=connection_to_user_db(request=request)
    if(cono.session.user_id>=1):
        user_id=cono.session.user_id
        query="select username,user_profile from user_data_table where user_id={}".format(user_id)
        cono.cursor.execute(query)
        user_data=cono.cursor.fetchone()
        if(user_data is not None):
            username=user_data[0]
            mypage_dict_combined={**cono.session.user_id_dict,**{"username":username,"user_profile":user_data[1]}}
            if(cono.session.is_moblie):
                html_file="myapp/moblie_site/my_page/my_page.html"
            else:
                html_file="myapp/my_page.html"
            return cono.set_response(response=render(request=request,template_name=html_file,context=mypage_dict_combined))
            #if(False):
            #    query="select user_view_history_resent_100 from user_view_history where user_id={}".format(user_id)
            #    user_view_history=cono.cursor.fetchone()[0].split(",")
    return redirect_to_signup


def view_history(request: HttpRequest):
    cono=connection_to_user_db(request=request)
    if(cono.session.user_id>=1):
        user_id=cono.session.user_id
        query="select view_history_resent_100 from user_view_history where user_id={};".format(user_id)
        cono.cursor.execute(query)
        result=cono.cursor.fetchone()
        content_id_list=result[0].split(",")
        if(result[0]!=""):
            content_id_list.reverse()
            for i in content_id_list:
                query="select content_id from post_data_table where content_id={};".format(i)
                cono.cursor.execute(query)
                result=cono.cursor.fetchone()
                if(result is None):
                    content_id_list.remove(i)
        view_history_content_dict=my_functions.create_content_dict(
            cursor=cono.cursor,content_id_list=content_id_list,amount_of_displayed_post=50,start_number=1,page_number=1,order="no_sort_str",user_id=user_id
            )
        if(cono.session.is_moblie):
            html_file="myapp/moblie_site/view_history.html"
        else:
            html_file="myapp/view_history.html"
        response = cono.set_response(response=render(request=request,template_name=html_file,context={**cono.get_full_user_data_dict(),**view_history_content_dict}))
        return response
    return redirect_to_error_page


def posted_post(request:HttpRequest):
    cono=connection_to_user_db(request=request)
    if(cono.session.user_id>=1):
        user_id=cono.session.user_id
        query="select * from user_data_table where user_id={}".format(user_id)
        cono.cursor.execute(query)
        user_data=cono.cursor.fetchone()
        if(user_data is not None):
            username=user_data[1]
            user_posted_list = list(dict.fromkeys(my_search.search_post_index(include_text=str(user_id),search_conditions=["user_id"])))#何故か重複するので重複排除
            posted_post_=my_functions.create_content_dict(
                cursor=cono.cursor,
                content_id_list=user_posted_list,
                amount_of_displayed_post=10,
                start_number=1,
                page_number=1,
                order="new_post",
                user_id=cono.session.user_id
                )
            mypage_dict_combined={**posted_post_,**cono.session.user_id_dict,**{"username":username}}
            if(cono.session.is_moblie):
                html_file="myapp/moblie_site/my_page/posted_content.html"
            else:
                html_file="myapp/posted_content.html"
            return cono.set_response(response=render(request=request,template_name=html_file,context=mypage_dict_combined))
            #if(False):
            #    query="select user_view_history_resent_100 from user_view_history where user_id={}".format(user_id)
            #    user_view_history=cono.cursor.fetchone()[0].split(",")
    return redirect_to_error_page


def change_password(request:HttpRequest):
    cono=connection_to_user_db(request=request)
    if(cono.session.is_moblie):
        html_file="myapp/moblie_site/change_user_info/change_password.html"
    else:
        html_file="myapp/change_user_info/change_password.html"
    return cono.set_response(
        render(
            request=request,
            template_name=html_file,
            context=cono.session.user_id_dict,
        )
    )


def change_password_success(request:HttpRequest):
    cono=connection_to_user_db(request=request)
    if(cono.session.is_moblie):
        html_file="myapp/moblie_site/change_user_info/change_password_success.html"
    else:
        html_file="myapp/change_user_info/change_password_success.html"
    return cono.set_response(
        render(
            request=request,
            template_name=html_file,
            context=cono.session.user_id_dict,
        )
    )


def display_post(request: HttpRequest, content_id: int):
    if(not my_functions.check_str_is_int(content_id)):
       return redirect_to_error_page
    cono = connection_to_user_db(request=request,get_user_setting=True)
    max_display_number=10
    displayed_post=my_functions.create_content_dict(
        cursor=cono.cursor,
        content_id_list=[content_id],
        amount_of_displayed_post=max_display_number,
        start_number=1,
        page_number=1,
        order="no_sort",
        user_id=cono.session.user_id
        )
    search_dict_conbined = {**cono.get_full_user_data_dict(already_set_setting_dict=True), **displayed_post}
    if(cono.session.is_moblie):
        html_file="myapp/moblie_site/display_post.html"
    else:
        html_file="myapp/display_post.html"
    response = cono.set_response(response=render(request=request,template_name=html_file,context=search_dict_conbined))

    return response


def search(request: HttpRequest):
    cono = connection_to_user_db(request=request,get_user_setting=True)
    max_display_number=10
    if(my_functions.check_existence(multi=request.GET,keys=["post_order"],allow_empty=False)):
        order=request.GET["post_order"]#不正な文字列の判定はcreate_content_dictでやる
    else:
        order="new_post"
    if(my_functions.check_existence(multi=request.GET,keys=["page_number"],allow_empty=False)):
        if not re.fullmatch(pattern=r"[1-9][0-9]*", string=request.GET["page_number"]):  # 整数以外を送られたら
            page_number=1
        else:
            page_number=int(request.GET["page_number"])
    else:
        page_number=1
    
    search_conditions=["title","content","overview","tags"]
    search_word_dict={}
    if(my_functions.check_existence(multi=request.GET,keys=["search_words"],allow_empty=False)):
        search_words = request.GET["search_words"]
        search_word_dict["search_words"]=search_words
    else:
        search_words="inculde_all"
        search_conditions.append("for_all")
        search_word_dict["search_words"]=""
    if(my_functions.check_existence(multi=request.GET,keys=["search_words_exclude"],allow_empty=False)):
        exclude_words=request.GET["search_words_exclude"]
        search_word_dict["search_words_exclude"]=exclude_words
    else:
        exclude_words=""
        search_word_dict["search_words_exclude"]=""
    matched_post_list = my_search.search_post_index(include_text=search_words,exclude_text=exclude_words,search_conditions=search_conditions)
    displayed_post=my_functions.create_content_dict(
        cursor=cono.cursor,
        content_id_list=matched_post_list,
        amount_of_displayed_post=max_display_number,
        start_number=(page_number-1)*10+1,
        page_number=page_number,
        order=order,
        user_id=cono.session.user_id
        )
    search_dict_conbined = {**cono.get_full_user_data_dict(already_set_setting_dict=True), **displayed_post,**search_word_dict,**search_word_dict}
    if(cono.session.is_moblie):
        html_file="myapp/moblie_site/search.html"
    else:
        html_file="myapp/search.html"
    response = cono.set_response(response=render(request=request,template_name=html_file,context=search_dict_conbined))

    return response


def user_page(request: HttpRequest,owner_user_id: int):
    cono=connection_to_user_db(request=request)
    query="select user_id,username,user_profile from user_data_table where user_id={}".format(owner_user_id)
    cono.cursor.execute(query)
    user_data=cono.cursor.fetchone()
    if(user_data is not None):
        user_posted_list = list(dict.fromkeys(my_search.search_post_index(include_text=str(owner_user_id),search_conditions=["user_id"])))#何故か重複するので重複排除
        displayed_post=my_functions.create_content_dict(
            cursor=cono.cursor,
            content_id_list=user_posted_list,
            amount_of_displayed_post=1000,
            start_number=1,
            page_number=1,
            order="new_post",
            user_id=owner_user_id
            )
        query="select followed_users from user_relation_table where user_id={}".format(owner_user_id)
        cono.cursor.execute(query)
        result=cono.cursor.fetchone()
        owner_followed_users_id_combined=result[0]
        owner_followed_users_username_combined=""
        if(owner_followed_users_id_combined!=""):
            owner_followed_users_id_list=owner_followed_users_id_combined.split(",")
            owner_followed_users_id_list.reverse()#デフォルトだとフォローが古い順
            owner_followed_users_id_combined=",".join(owner_followed_users_id_list)
            query="select username from user_data_table where user_id in("
            for i in owner_followed_users_id_list:
                query+=i+","
            query=query[:-1]+");"
            cono.cursor.execute(query)
            results=cono.cursor.fetchall()
            
            for i in results:
                owner_followed_users_username_combined+=i[0]+"<"
            
            owner_followed_users_username_combined=owner_followed_users_username_combined[:-1]
        
        mypage_dict_combined={**displayed_post,**cono.session.get_full_user_data_dict(cursor=cono.cursor,already_set_setting_dict=False),
                              **{"owner_username":user_data[1],"owner_user_id":str(user_data[0]),"owner_user_profile":user_data[2],"owner_followed_users_id_combined":owner_followed_users_id_combined,
                                 "owner_followed_users_username_combined":owner_followed_users_username_combined}}
        if(cono.session.is_moblie):
            html_file="myapp/moblie_site/user_page.html"
        else:
            html_file="myapp/user_page.html"
        return cono.set_response(response=render(request=request,template_name=html_file,context=mypage_dict_combined))
            #if(False):
            #    query="select user_view_history_resent_100 from user_view_history where user_id={}".format(user_id)
            #    user_view_history=cono.cursor.fetchone()[0].split(",")
    return redirect_to_error_page


def change_user_info_page(request:HttpRequest):
    cono = connection_to_user_db(request=request)
    if(cono.session.user_id>=1):
        user_id=cono.session.user_id
        query="select username,user_profile from user_data_table where user_id={}".format(user_id)
        cono.cursor.execute(query)
        user_data=cono.cursor.fetchone()
        if(user_data is not None):
            username=user_data[0]
            mypage_dict_combined={**cono.session.user_id_dict,**{"username":username,"user_profile":user_data[1]}}
            if(cono.session.is_moblie):
                html_file="myapp/moblie_site/change_user_info/change_user_info.html"
            else:
                html_file="myapp/change_user_info/change_user_info.html"
            return cono.set_response(response=render(request=request,template_name=html_file,context=mypage_dict_combined))
            #if(False):
            #    query="select user_view_history_resent_100 from user_view_history where user_id={}".format(user_id)
            #    user_view_history=cono.cursor.fetchone()[0].split(",")
    return redirect_to_signup


def report_page(request:HttpRequest):
    cono=connection_to_user_db(request=request)
    if(not my_functions.check_existence(multi=request.GET,keys=["subject_category","subject_id"],allow_empty=False)):
        return cono.return_error(requset=request)
    report_page_dict_combined={**cono.get_full_user_data_dict(),**{"subject_category":request.GET["subject_category"],"subject_id":request.GET["subject_id"]}}
    if(cono.session.is_moblie):
        html_file="myapp/moblie_site/report_page.html"
    else:
        html_file="myapp/report_page.html"
    return cono.set_response(response=render(request=request,template_name=html_file,context=report_page_dict_combined))


def delete_account_page(request:HttpRequest):
    cono=connection_to_user_db(request=request)
    if(cono.session.is_moblie):
        html_file="myapp/moblie_site/delete_account_page.html"
    else:
        html_file="myapp/delete_account_page.html"
    return cono.set_response(
        render(
            request=request,
            template_name=html_file,
            context=cono.session.user_id_dict,
        )
    )
        
#ここからページ遷移しないやつ

def signup_process(request: HttpRequest):  # ユーザー登録
    response_data={}
    try:
        request_data = json.loads(request.body)
    except (ValueError, UnicodeDecodeError):
        request_data = {}
        response_data["result"]="request_broken_error"
        return JsonResponse(response_data)
    username = request_data["username"]
    mailaddress = request_data["mailaddress"]
    password = request_data["password"]
    cnx = my_functions.connect_to_database()
    cursor = cnx.cursor(buffered=True)
    if(not my_functions.check_username_overlap(username,cursor)):
        response_data["result"]="username_overlap"
        return JsonResponse(response_data)
    elif(not my_functions.check_mailaddress_overlap(mailaddress,cursor)):
        response_data["result"]="mailaddress_overlap"
        return JsonResponse(response_data)
    elif (
        my_functions.check_password(password)#ここらはフロントエンドで確認するのでここで違ったらエラー扱い
        and my_functions.check_mailaddress(mailaddress)
        and my_functions.check_username(username)
    ):
        query = "SELECT * FROM user_data_table ORDER BY user_id DESC LIMIT 1"
        cursor.execute(query)
        result = cursor.fetchone()
        query = "INSERT INTO user_data_table (user_id,username,mailaddress,password) VALUES (%s,%s,%s,%s) ;"
        if result is not None:  # ユーザーがいる時
            user_id=int(result[0]) + 1
        else:#いない時
            user_id=1
        data = (str(user_id),username,mailaddress,argon2.hash(password + secret_values.password_salt))
        cursor.execute(query, data)
        query = "INSERT INTO user_view_history (user_id) VALUES({});".format(user_id)
        cursor.execute(query)
        query = "INSERT INTO user_review_history (user_id) VALUES({});".format(user_id)
        cursor.execute(query)
        query = "INSERT INTO user_setting_table (user_id) VALUES({});".format(user_id)
        cursor.execute(query)
        query = "INSERT INTO user_relation_table (user_id) VALUES({});".format(user_id)
        cursor.execute(query)
        new_session = session_data(request=request)
        new_session.user_id=user_id
        new_session.update_values(cursor=cursor,create_record=True)
        cnx.commit()
        my_search.add_user_to_index(user=[user_id,username,mailaddress])
        cursor.close()
        cnx.close()
        my_functions.copy_file(origin_file_path=my_functions.media_path+"\\user_icons\\"+"defalt_icon.png",new_file_path=my_functions.media_path+"\\user_icons\\"+"user_icon_{}.png".format(user_id))
        my_functions.copy_file(origin_file_path=my_functions.media_path+"\\user_icons\\"+"defalt_icon_mini.png",new_file_path=my_functions.media_path+"\\user_icons\\"+"user_icon_mini_{}.png".format(user_id))
        response_data["result"]="success"
        response_data["session_id_1"]=str(new_session.value_1)
        response_data["session_id_2"]=str(new_session.value_2)
        return JsonResponse(response_data)
    else:
        response_data["result"]="failed_error"
        return JsonResponse(response_data)


def login_process(request: HttpRequest):
    response_data={}
    try:
        request_data = json.loads(request.body)
    except (ValueError, UnicodeDecodeError):
        request_data = {}
        response_data["result"]="request_broken_error"
        return JsonResponse(response_data)
    if not my_functions.check_existence(request_data, ["mailaddress", "password"]):
        response_data["result"]="failed_error"
        return JsonResponse(response_data)
    
    if my_functions.check_password(request_data["password"]) and my_functions.check_mailaddress(request_data["mailaddress"]):
        mailaddress = request_data["mailaddress"]
        password = request_data["password"]
        cnx = my_functions.connect_to_database()
        cursor = cnx.cursor(buffered=True)
        query = "SELECT user_id,password FROM user_data_table WHERE mailaddress = %s"
        cursor.execute(query, ((mailaddress),))
        mailaddress_matched_record = cursor.fetchone()
        if mailaddress_matched_record is not None:
            if argon2.verify(password + secret_values.password_salt, mailaddress_matched_record[1]):
                new_session = session_data(request=request)
                new_session.user_id=mailaddress_matched_record[0]#個別にやる
                new_session.update_values(cursor=cursor,create_record=True)
                cnx.commit()
                cursor.close()
                cnx.close()
                response_data["result"]="success"
                response_data["session_id_1"]=str(new_session.value_1)
                response_data["session_id_2"]=str(new_session.value_2)
            else:
                response_data["result"]="incorrect_password"
        else:
            response_data["result"]="incorrect_mailaddress"
    else:
        response_data["result"]="failed_error"
    return JsonResponse(response_data)


@csrf_exempt
def login_process_app(request: HttpRequest):
    response_data={}
    try:
        request_data = json.loads(request.body)
    except (ValueError, UnicodeDecodeError):
        request_data = {}
        response_data["result"]="request_broken_error"
        my_functions.error_log("088900890")
        return JsonResponse(response_data)
    if not my_functions.check_existence(multi=request_data, keys=["mailaddress", "password","device_unique_id"]):
        my_functions.error_log("797978979")
        response_data["result"]="failed_error"
        return JsonResponse(response_data)
    
    
    
    if my_functions.check_password(request_data["password"]) and my_functions.check_mailaddress(request_data["mailaddress"]) and len(request_data["device_unique_id"])<=36:
        mailaddress = request_data["mailaddress"]
        password = request_data["password"]
        unique_id=request_data["device_unique_id"]
        cnx = my_functions.connect_to_database()
        cursor = cnx.cursor(buffered=True)
        query = "SELECT user_id,password FROM user_data_table WHERE mailaddress = %s"
        cursor.execute(query, ((mailaddress),))
        mailaddress_matched_record = cursor.fetchone()
        if mailaddress_matched_record is not None:
            if argon2.verify(password + secret_values.password_salt, mailaddress_matched_record[1]):
                new_session = session_data(request=request,from_app_flag=True,uni_id=unique_id)
                new_session.user_id=mailaddress_matched_record[0]#個別にやる
                new_session.update_values(cursor=cursor,create_record=True)
                cnx.commit()
                cursor.close()
                cnx.close()
                response = redirect_to_toppage
                new_session.set_cookie(response)
                response_data["result"]="success"
                response_data["user_id"]=str(new_session.user_id)
                response_data["session_id_1"]=str(new_session.value_1)
                response_data["session_id_2"]=str(new_session.value_2)
            else:
                response_data["result"]="incorrect_password"
        else:
            response_data["result"]="incorrect_mailaddress"
    else:
        response_data["result"]="failed_error"
    return JsonResponse(response_data)


def logout_process(request: HttpRequest):
    response_data={}
    try:
        request_data = json.loads(request.body)
    except (ValueError, UnicodeDecodeError):
        request_data = {}
        response_data["result"]="request_broken_error"
        return JsonResponse(response_data)
    cono=connection_to_user_db(request=request,request_json_data=request_data,from_app_flag=False)
    cono.session.logout()
    return JsonResponse(response_data)



def post_process(request: HttpRequest):
    response_data={}
    print(request.__dict__)
    print(request.FILES)
    if("json" in request.FILES):
        json_binary=request.FILES['json'].read()
        if(my_functions.is_valid_json(json_binary)):
            request_data = json.loads(json_binary.decode('utf-8'))
        else:
            response_data["result"]="request_broken_error"
            my_functions.error_log("779876788")
            return JsonResponse(response_data)
    else:
        response_data["result"]="request_broken_error"
        my_functions.error_log("28193791")
        return JsonResponse(response_data)
    
    response_data={}
    if(my_functions.check_existence(multi=request_data,keys=["overview","joined_tags"],allow_empty=True) and
       my_functions.check_existence(multi=request_data,keys=["session_id_1","session_id_2","title","content","image_count"],allow_empty=False)):
        title = request_data["title"]
        content = request_data["content"]
        overview = request_data["overview"]
        tags = list(dict.fromkeys(my_functions.sort_tags(request_data["joined_tags"].split(","))))#重複削除
        joined_tags=",".join(tags)
        if(request_data["image_count"].isdigit()):
            image_count=int(request_data["image_count"])
        else:
            my_functions.error_log("217837179")
            response_data["result"]="request_broken_error"
            return JsonResponse(response_data)
    else:
        response_data["result"]="request_broken_error"
        return JsonResponse(response_data)
    
    if(my_functions.check_content(text=title,max_character_count=50,min_character_count=1,allow_new_line=False)==False or
       my_functions.check_content_with_image(text=content,image_count=image_count,max_character_count=20000,min_character_count=1)==False or
       my_functions.check_content(text=overview,max_character_count=100,min_character_count=0,allow_new_line=False,max_new_line_count=2)==False or
       my_functions.check_tags(tags=tags)==False
       ):
        my_functions.error_log("8786756567")
        response_data["result"]="failed_error"
        return JsonResponse(response_data)
    
    cono=connection_to_user_db(request=request,request_json_data=request_data,from_app_flag=False)
    query="SELECT content_id FROM post_data_table WHERE title=%s;"
    cono.cursor.execute(query,(title,))
    result = cono.cursor.fetchone()
    if(result is not None):
        cono.cursor.close()
        cono.cnx.close()
        my_functions.error_log("3422342423")
        response_data["result"]="title_overlap"
        return JsonResponse(response_data)
    
    if (cono.session.user_id>=1):
        user_id=cono.session.user_id
        query = "SELECT content_id FROM post_data_table ORDER BY content_id DESC LIMIT 1 ;"
        cono.cursor.execute(query)
        result = cono.cursor.fetchone()
        if result is not None:
            content_id=result[0] + 1
        else:
            content_id=1
        
        if(image_count>=1):
            image_list=[]
            content_split=content.split(">")
            content=""
            for i in range(image_count):
                if(not "image_file_{}".format(i+1) in request.FILES):
                    my_functions.error_log("687687688787")
                    response_data["result"]="request_broken_error"
                    return JsonResponse(response_data)
                
                image_binary=request.FILES["image_file_{}".format(i+1)].read()
                if(my_functions.is_valid_image(image_binary=image_binary)):
                    image_list.append(Image.open(io.BytesIO(image_binary)))
                else:
                    my_functions.error_log("768686876868")
                    response_data["result"]="failed_error"
                    return JsonResponse(response_data)
            
            content_image_dir=my_functions.media_path+"\\content_image\\{}".format(content_id)
            if not os.path.exists(content_image_dir):
                os.mkdir(content_image_dir)
            for i in range(image_count):
                content+=content_split[2*i]+">"
                content+=content_split[2*i+1]
                image_extension=image_list[i].format
                if(image_extension=="JPEG"):
                    image_name=os.path.join(content_image_dir,"{}.jpg".format(i+1))
                    content+=".jpg"
                elif(image_extension=="PNG"):
                    image_name=os.path.join(content_image_dir,"{}.png".format(i+1))
                    content+=".png"
                else:
                    response_data["result"]="incorrect_extension_error"
                    return JsonResponse(response_data)
                content+=">"
                my_functions.delete_file_if_exists(image_name)
                image_list[i].save(image_name)
            content+=content_split[2*image_count]
        
        if(image_count>=1):
            index_content=""
            for i in range(image_count+1):
                index_content+=content_split[2*i]
        else:
            index_content=content
        word_count = len(index_content)
        sql = """
               INSERT INTO post_data_table 
               (content_id,title,content,user_id,overview,word_count,tags,post_date)
               VALUES
               (%s,%s,%s,%s,%s,%s,%s,%s) ;
               """
        now = datetime.datetime.now(JST)
        data = (
                str(content_id),
                title,
                content,
                str(user_id),
                overview,
                str(word_count),
                joined_tags,
                now.strftime("%Y-%m-%d %H:%M:%S")
            )
        cono.cursor.execute(sql, data)
        sql="""
        INSERT INTO post_view_count_table
        (content_id)
        VALUES
        ({}) ;
        """.format(content_id)
        cono.cursor.execute(sql)
        sql="""
        INSERT INTO post_review_table
        (content_id)
        VALUES
        ({}) ;
        """.format(content_id)
        cono.cursor.execute(sql)
        sql="""
        INSERT INTO post_discussion_table
        (content_id)
        VALUES
        ({}) ;
        """.format(content_id)
        cono.cursor.execute(sql)
        cono.cnx.commit()
        if(image_count>=1):
            index_content=""
            for i in range(image_count+1):
                index_content+=content_split[2*i]
        else:
            index_content=content
        my_search.add_post_to_index([content_id, title, index_content, user_id, overview, tags,now])#タグはリストで渡す、インデックスは視覚的に操作出来ないのでDBの操作が成功してから
        response_data["content_id"]=str(content_id)
        response_data["result"]="success"
    else:
        response_data["result"]="incorrect_session"
        my_functions.error_log("09218293")
    cono.terminate_connection()
    return JsonResponse(response_data)

    
@csrf_exempt
def post_process_app(request: HttpRequest):
    response_data={}
    is_android=False
    if("json" in request.FILES or False):
        json_binary=request.FILES['json'].read()
        if(my_functions.is_valid_json(json_binary)):
            request_data = json.loads(json_binary.decode('utf-8'))
        else:
            response_data["result"]="request_broken_error"
            my_functions.error_log("774356788")
            return JsonResponse(response_data)
    else:
        try:
            request_data = json.loads(request.body)
            is_android=True
        except (ValueError, UnicodeDecodeError):
            request_data = {}
            response_data["result"]="request_broken_error"
            my_functions.error_log("13453310")
            return JsonResponse(response_data)
        except Exception as e:
            if e.__class__.__name__ == 'RequestDataTooBig':
                response_data["result"]="too_big_data_error"
                my_functions.error_log("23443242")
                return JsonResponse(response_data)
            else:
                # その他のエラーの処理
                raise
    
    response_data={}
    if(my_functions.check_existence(multi=request_data,keys=["overview","joined_tags"],allow_empty=True) and
       my_functions.check_existence(multi=request_data,keys=["session_id_1","session_id_2","title","content","image_count"],allow_empty=False)):
        title = request_data["title"]
        content = request_data["content"]
        overview = request_data["overview"]
        tags = list(dict.fromkeys(my_functions.sort_tags(request_data["joined_tags"].split(","))))#重複削除
        joined_tags=",".join(tags)
        if(request_data["image_count"].isdigit()):
            image_count=int(request_data["image_count"])
        else:
            my_functions.error_log("212417837179")
            response_data["result"]="request_broken_error"
            return JsonResponse(response_data)
    else:
        response_data["result"]="request_broken_error"
        return JsonResponse(response_data)
    
    if(my_functions.check_content(text=title,max_character_count=50,min_character_count=1,allow_new_line=False)==False or
       my_functions.check_content_with_image(text=content,image_count=image_count,max_character_count=20000,min_character_count=1)==False or
       my_functions.check_content(text=overview,max_character_count=100,min_character_count=0,allow_new_line=False,max_new_line_count=2)==False or
       my_functions.check_tags(tags=tags)==False
       ):
        print(content)
        print(my_functions.check_content_with_image(text=content,image_count=image_count,max_character_count=20000,min_character_count=1)==False)
        my_functions.error_log("8781426756567")
        response_data["result"]="failed_error"
        return JsonResponse(response_data)
    
    cono=connection_to_user_db(request=request,request_json_data=request_data,from_app_flag=True)
    query="SELECT content_id FROM post_data_table WHERE title=%s;"
    cono.cursor.execute(query,(title,))
    result = cono.cursor.fetchone()
    if(result is not None):
        cono.terminate_connection()
        my_functions.error_log("3422342421243")
        response_data["result"]="title_overlap"
        return JsonResponse(response_data)
    
    if (cono.session.user_id>=1):
        user_id=cono.session.user_id
        query = "SELECT content_id FROM post_data_table ORDER BY content_id DESC LIMIT 1 ;"
        cono.cursor.execute(query)
        result = cono.cursor.fetchone()
        if result is not None:
            content_id=result[0] + 1
        else:
            content_id=1
        
        if(image_count>=1):
            image_list=[]
            content_split=content.split(">")
            content=""
            for i in range(image_count):
                if(is_android):
                    if(not "image_blob_{}".format(i+1) in request_data):
                        cono.terminate_connection()
                        my_functions.error_log("121234279877")
                        response_data["result"]="request_broken_error"
                        return JsonResponse(response_data)
                    else:
                        image_binary= base64.b64decode(request_data["image_blob_{}".format(i+1)])

                    if(my_functions.is_valid_image(image_binary=image_binary)):
                        image_list.append(Image.open(io.BytesIO(image_binary)))
                    else:
                        cono.terminate_connection()
                        my_functions.error_log("7823424817897")
                        response_data["result"]="failed_error"
                        return JsonResponse(response_data)
                else:
                    if(not "image_file_{}".format(i+1) in request.FILES):
                        my_functions.error_log("63424688787")
                        response_data["result"]="request_broken_error"
                        return JsonResponse(response_data)
                    
                    image_binary=request.FILES["image_file_{}".format(i+1)].read()
                    if(my_functions.is_valid_image(image_binary=image_binary)):
                        image_list.append(Image.open(io.BytesIO(image_binary)))
                    else:
                        my_functions.error_log("768683428")
                        response_data["result"]="failed_error"
                        return JsonResponse(response_data)
            
            content_image_dir=my_functions.media_path+"\\content_image\\{}".format(content_id)
            if not os.path.exists(content_image_dir):
                os.mkdir(content_image_dir)
            for i in range(image_count):
                content+=content_split[2*i]+">"
                content+=content_split[2*i+1]
                image_extension=image_list[i].format
                if(image_extension=="JPEG"):
                    image_name=os.path.join(content_image_dir,"{}.jpg".format(i+1))
                    content+=".jpg"
                elif(image_extension=="PNG"):
                    image_name=os.path.join(content_image_dir,"{}.png".format(i+1))
                    content+=".png"
                else:
                    cono.terminate_connection()
                    response_data["result"]="incorrect_extension_error"
                    return JsonResponse(response_data)
                content+=">"
                my_functions.delete_file_if_exists(image_name)
                image_list[i].save(image_name)
            content+=content_split[2*image_count]
        
        if(image_count>=1):
            index_content=""
            for i in range(image_count+1):
                index_content+=content_split[2*i]
        else:
            index_content=content
        word_count = len(index_content)
        sql = """
               INSERT INTO post_data_table 
               (content_id,title,content,user_id,overview,word_count,tags,post_date)
               VALUES
               (%s,%s,%s,%s,%s,%s,%s,%s) ;
               """
        now = datetime.datetime.now(JST)
        data = (
                str(content_id),
                title,
                content,
                str(user_id),
                overview,
                str(word_count),
                joined_tags,
                now.strftime("%Y-%m-%d %H:%M:%S")
            )
        cono.cursor.execute(sql, data)
        sql="""
        INSERT INTO post_view_count_table
        (content_id)
        VALUES
        ({}) ;
        """.format(content_id)
        cono.cursor.execute(sql)
        sql="""
        INSERT INTO post_review_table
        (content_id)
        VALUES
        ({}) ;
        """.format(content_id)
        cono.cursor.execute(sql)
        sql="""
        INSERT INTO post_discussion_table
        (content_id)
        VALUES
        ({}) ;
        """.format(content_id)
        cono.cursor.execute(sql)
        cono.cnx.commit()
        
        my_search.add_post_to_index([content_id, title, index_content, user_id, overview, tags,now])#タグはリストで渡す、インデックスは視覚的に操作出来ないのでDBの操作が成功してから
        response_data["content_id"]=str(content_id)
        response_data["result"]="success"
    else:
        response_data["result"]="incorrect_session"
        my_functions.error_log("729139179879")
    cono.terminate_connection()
    return JsonResponse(response_data)


def delete_post_process(request:HttpRequest):
    response_data={}
    try:
        request_data = json.loads(request.body)
    except (ValueError, UnicodeDecodeError):
        response_data["result"]="request_broken_error"
        my_functions.error_log("281234234291")
        return JsonResponse(response_data)
    if(my_functions.check_existence(multi=request_data,keys=["session_id_1","session_id_2","content_id"],allow_empty=False)):
        if(my_functions.check_str_is_int(request_data["content_id"])):
            content_id=int(request_data["content_id"])
        else:
            response_data["result"]="request_broken_error"
            return JsonResponse(response_data)
    else:
        my_functions.error_log("723498342422")
        response_data["result"]="request_broken_error"
        return JsonResponse(response_data)
    cono=connection_to_user_db(request=request,request_json_data=request_data,from_app_flag=False)
    query="SELECT user_id FROM post_data_table WHERE content_id=%s;"
    cono.cursor.execute(query,(str(content_id),))
    result = cono.cursor.fetchone()
    if(result is None):
        cono.terminate_connection()
        my_functions.error_log("25873924235")
        response_data["result"]="none_content_error"
        return JsonResponse(response_data)
    
    if(cono.session.user_id==result[1]):
        query="INSERT INTO deleted_post_data_table SELECT * FROM post_data_table where content_id={};".format(content_id)
        cono.cursor.execute(query)
        query="UPDATE post_data_table SET title='削除された投稿',content='削除された投稿',overview='削除された投稿',tags='' where content_id={}".format(content_id)
        cono.cursor.execute(query)
        cono.cnx.commit()
        my_search.delete_post_from_index(content_id=content_id)#インデックスは視覚的に操作出来ないのでDBの操作が成功してから
        response_data["result"]="success"
    else:
        response_data["result"]="incrrect_session_error"
        my_functions.error_log("32423424232")
    cono.terminate_connection()
    return JsonResponse(response_data)


@csrf_exempt
def delete_post_process_app(request:HttpRequest):
    response_data={}
    try:
        request_data = json.loads(request.body)
    except (ValueError, UnicodeDecodeError):
        response_data["result"]="request_broken_error"
        my_functions.error_log("23434291")
        return JsonResponse(response_data)
    if(my_functions.check_existence(multi=request_data,keys=["session_id_1","session_id_2","content_id"],allow_empty=True)):
        if(my_functions.check_str_is_int(request_data["content_id"])):
            content_id=int(request_data["content_id"])
        else:
            response_data["result"]="request_broken_error"
            return JsonResponse(response_data)
    else:
        my_functions.error_log("7232342342422")
        response_data["result"]="request_broken_error"
        return JsonResponse(response_data)
    cono=connection_to_user_db(request=request,request_json_data=request_data,from_app_flag=True)
    query="SELECT user_id FROM post_data_table WHERE content_id=%s;"
    cono.cursor.execute(query,(str(content_id),))
    result = cono.cursor.fetchone()
    if(result is None):
        cono.terminate_connection()
        my_functions.error_log("25244235")
        response_data["result"]="none_content_error"
        return JsonResponse(response_data)
    
    if(cono.session.user_id==result[0]):
        query="INSERT INTO deleted_post_data_table SELECT * FROM post_data_table where content_id={};".format(content_id)
        cono.cursor.execute(query)
        query="UPDATE post_data_table SET title='削除された投稿',content='削除された投稿',overview='この投稿はユーザーによって削除されました',tags='' where content_id={}".format(content_id)
        cono.cursor.execute(query)
        cono.cnx.commit()
        my_search.delete_post_from_index(content_id=content_id)#インデックスは視覚的に操作出来ないのでDBの操作が成功してから
        response_data["result"]="success"
    else:
        response_data["result"]="incrrect_session_error"
        my_functions.error_log("3242342342")
    cono.terminate_connection()
    return JsonResponse(response_data)


def view_count_doubleplus(request: HttpRequest):
    try:
        request_data = json.loads(request.body)
    except (ValueError, UnicodeDecodeError):
        request_data = {}
    if("session_id_1" in request_data and
       "session_id_2" in request_data and
       "content_id" in request_data):
        content_id_str=request_data["content_id"]
        session_id_1_str=request_data["session_id_1"]
        session_id_2_str=request_data["session_id_2"]
        cono=connection_to_user_db(request=request,request_json_data=request_data,from_app_flag=False)
        query="SELECT content_id FROM post_data_table WHERE content_id=%s;"
        data=(content_id_str,)
        cono.cursor.execute(query,data)
        result02=cono.cursor.fetchone()
        if(cono.session.user_id>=1 and result02 is not None):
            user_id_str=str(cono.session.user_id)
            query="SELECT * FROM user_view_history WHERE user_id={};".format(user_id_str)
            cono.cursor.execute(query)
            result=cono.cursor.fetchone()#[user_id,user_view_history_today,user_view_history_resent_100]
            user_view_history_today = result[1].split(",")
            user_view_history_resent_100 =result[2].split(",")
            if(not content_id_str in user_view_history_today):
                query="UPDATE post_view_count_table SET view_count=view_count+1,hour=hour+1,day=day+1,week=week+1,month_30=month_30+1 WHERE content_id = {};".format(content_id_str)#基本の閲覧数の追加
                cono.cursor.execute(query)
                
                query="UPDATE user_view_history SET view_history_today='"#この後つなげる
                if(result[1]==""):#result[1]は,でリストを結合した文字列でこの分岐は何もなかったとき
                    query+="{}' WHERE user_id = {}".format(content_id_str,user_id_str)
                else:
                    query+="{}' WHERE user_id = {}".format(result[1]+","+content_id_str,user_id_str)
                cono.cursor.execute(query)
            
            if(result[2]==""):#result[1]と同じく
                query="UPDATE user_view_history SET view_history_resent_100='{}' WHERE user_id = {};".format(content_id_str,user_id_str)
            else:
                if(content_id_str in user_view_history_resent_100):
                    user_view_history_resent_100.remove(content_id_str)
                    user_view_history_resent_100.append(content_id_str)
                    query="UPDATE user_view_history SET view_history_resent_100='{}'WHERE user_id = {};".format(",".join(user_view_history_resent_100),user_id_str)
                else:
                    if(len(user_view_history_resent_100)>=100):#閲覧履歴が埋まってたら先頭を削除 elseはない
                        query="UPDATE user_view_history SET view_history_resent_100='{}' WHERE user_id = {}".format(
                            result[2][len(user_view_history_resent_100[0])+1:]+","+content_id_str,user_id_str)#+1は,の分
                    else:
                        query="UPDATE user_view_history SET view_history_resent_100='{}' WHERE user_id = {}".format(result[2]+","+content_id_str,user_id_str)
            cono.cursor.execute(query)
            cono.cnx.commit()
        cono.terminate_connection()
    return HttpResponse("")


@csrf_exempt
def view_count_doubleplus_app(request: HttpRequest):
    try:
        request_data = json.loads(request.body)
    except (ValueError, UnicodeDecodeError):
        request_data = {}
    if("session_id_1" in request_data and
       "session_id_2" in request_data and
       "content_id" in request_data):
        content_id_str=request_data["content_id"]
        cono=connection_to_user_db(request=request,request_json_data=request_data,from_app_flag=True)
        query="SELECT content_id FROM post_data_table WHERE content_id=%s;"
        data=(content_id_str,)
        cono.cursor.execute(query,data)
        result02=cono.cursor.fetchone()
        if(cono.session.user_id>=1 and result02 is not None):
            user_id_str=str(cono.session.user_id)
            query="SELECT * FROM user_view_history WHERE user_id={};".format(user_id_str)
            cono.cursor.execute(query)
            result=cono.cursor.fetchone()#[user_id,user_view_history_today,user_view_history_resent_100]
            user_view_history_today = result[1].split(",")
            user_view_history_resent_100 =result[2].split(",")
            if(not content_id_str in user_view_history_today):
                query="UPDATE post_view_count_table SET view_count=view_count+1,hour=hour+1,day=day+1,week=week+1,month_30=month_30+1 WHERE content_id = {};".format(content_id_str)#基本の閲覧数の追加
                cono.cursor.execute(query)
                
                query="UPDATE user_view_history SET view_history_today='"#この後つなげる
                if(result[1]==""):#result[1]は,でリストを結合した文字列でこの分岐は何もなかったとき
                    query+="{}' WHERE user_id = {}".format(content_id_str,user_id_str)
                else:
                    query+="{}' WHERE user_id = {}".format(result[1]+","+content_id_str,user_id_str)
                cono.cursor.execute(query)
            
            if(result[2]==""):#result[1]と同じく
                query="UPDATE user_view_history SET view_history_resent_100='{}' WHERE user_id = {};".format(content_id_str,user_id_str)
            else:
                if(content_id_str in user_view_history_resent_100):
                    user_view_history_resent_100.remove(content_id_str)
                    user_view_history_resent_100.append(content_id_str)
                    query="UPDATE user_view_history SET view_history_resent_100='{}'WHERE user_id = {};".format(",".join(user_view_history_resent_100),user_id_str)
                else:
                    if(len(user_view_history_resent_100)>=100):#閲覧履歴が埋まってたら先頭を削除 elseはない
                        query="UPDATE user_view_history SET view_history_resent_100='{}' WHERE user_id = {}".format(
                            result[2][len(user_view_history_resent_100[0])+1:]+","+content_id_str,user_id_str)#+1は,の分
                    else:
                        query="UPDATE user_view_history SET view_history_resent_100='{}' WHERE user_id = {}".format(result[2]+","+content_id_str,user_id_str)
            cono.cursor.execute(query)
            cono.cnx.commit()
        cono.terminate_connection()
    return HttpResponse("")


def review_post(request:HttpRequest):
    try:
        request_data = json.loads(request.body)
    except (ValueError, UnicodeDecodeError):
        request_data = {}
    response_data={}
    if("session_id_1" in request_data and
       "session_id_2" in request_data and
       "content_id" in request_data and
       "change" in request_data):
        content_id_str=request_data["content_id"]
        cono=connection_to_user_db(request_json_data=request_data)
        change=request_data["change"]
        query="SELECT content_id FROM post_data_table WHERE content_id=%s;"
        data=(content_id_str,)
        cono.cursor.execute(query,data)
        result02=cono.cursor.fetchone()
        if(cono.session.user_id>=1 and result02 is not None):
            post_review=""#対象のpostへの対象のユーザーの評価
            query="select like_history,dislike_history from user_review_history where user_id={}".format(cono.session.user_id)
            cono.cursor.execute(query)
            result=cono.cursor.fetchone()
            liked_list = result[0].split(",")#全て文字列
            disliked_list = result[1].split(",")
            
            if("" in liked_list):
                liked_list.remove("")#これで空のcontent_idが入らないようにする
            if("" in disliked_list):
                disliked_list.remove("")
            
            if(content_id_str in liked_list):
                post_review="liked"
            elif(content_id_str in disliked_list):#liked xor disliked
                post_review="disliked"
            
            if(change=="add_like"):
                response_data["dislike"]="none"#場合によっては変わる
                if(post_review=="liked"):#likeを消す
                    liked_list.remove(content_id_str)
                    new_liked_list_joind=",".join(liked_list)
                    query="UPDATE user_review_history SET like_history='{}' WHERE user_id = {};".format(new_liked_list_joind,cono.session.user_id)
                    cono.cursor.execute(query)
                    query="""UPDATE post_review_table SET like_count=like_count-1,
                    like_count_hour=like_count_hour-1,
                    like_count_day=like_count_day-1,
                    like_count_week=like_count_week-1,
                    like_count_month_30=like_count_month_30-1 WHERE content_id = {};""".format(content_id_str)
                    cono.cursor.execute(query)
                    response_data["like"]="removed"
                else:#likeを足す
                    if(post_review=="disliked"):#dislikeを消す
                        disliked_list.remove(content_id_str)
                        new_disliked_list_joind=",".join(disliked_list)
                        query="UPDATE user_review_history SET dislike_history='{}' WHERE user_id = {};".format(new_disliked_list_joind,cono.session.user_id)
                        cono.cursor.execute(query)
                        query="""UPDATE post_review_table SET dislike_count=dislike_count-1,
                        dislike_count_hour=dislike_count_hour-1,
                        dislike_count_day=dislike_count_day-1,
                        dislike_count_week=dislike_count_week-1,
                        dislike_count_month_30=dislike_count_month_30-1 WHERE content_id = {};""".format(content_id_str)
                        cono.cursor.execute(query)
                        response_data["dislike"]="removed"
                    liked_list.append(content_id_str)
                    new_liked_list_joind=",".join(liked_list)
                    query="UPDATE user_review_history SET like_history='{}' WHERE user_id = {};".format(new_liked_list_joind,cono.session.user_id)
                    cono.cursor.execute(query)
                    query="""UPDATE post_review_table SET like_count=like_count+1,
                    like_count_hour=like_count_hour+1,
                    like_count_day=like_count_day+1,
                    like_count_week=like_count_week+1,
                    like_count_month_30=like_count_month_30+1 WHERE content_id = {};""".format(content_id_str)
                    cono.cursor.execute(query)
                    response_data["like"]="added"
            elif(change=="add_dislike"):#add_likeの反対
                response_data["like"]="none"#場合によっては変わる
                if(post_review=="disliked"):#すでにdislikeされているならdislikeを取り消す
                    disliked_list.remove(content_id_str)
                    new_disliked_list_joind=",".join(disliked_list)
                    query="UPDATE user_review_history SET dislike_history='{}' WHERE user_id = {};".format(new_disliked_list_joind,cono.session.user_id)
                    cono.cursor.execute(query)
                    query="""UPDATE post_review_table SET dislike_count=dislike_count-1,
                    dislike_count_hour=dislike_count_hour-1,
                    dislike_count_day=dislike_count_day-1,
                    dislike_count_week=dislike_count_week-1,
                    dislike_count_month_30=dislike_count_month_30-1 WHERE content_id = {};""".format(content_id_str)
                    cono.cursor.execute(query)
                    response_data["dislike"]="removed"
                else:
                    if(post_review=="liked"):#likeを取り消す
                        liked_list.remove(content_id_str)
                        new_liked_list_joind=",".join(liked_list)
                        query="UPDATE user_review_history SET like_history='{}' WHERE user_id = {};".format(new_liked_list_joind,cono.session.user_id)
                        cono.cursor.execute(query)
                        query="""UPDATE post_review_table SET like_count=like_count-1,
                        like_count_hour=like_count_hour-1,
                        like_count_day=like_count_day-1,
                        like_count_week=like_count_week-1,
                        like_count_month_30=like_count_month_30-1 WHERE content_id = {};""".format(content_id_str)
                        cono.cursor.execute(query)
                        response_data["like"]="removed"
                    disliked_list.append(content_id_str)
                    new_disliked_list_joind=",".join(disliked_list)
                    query="UPDATE user_review_history SET dislike_history='{}' WHERE user_id = {};".format(new_disliked_list_joind,cono.session.user_id)
                    cono.cursor.execute(query)
                    query="""UPDATE post_review_table SET dislike_count=dislike_count+1,
                    dislike_count_hour=dislike_count_hour+1,
                    dislike_count_day=dislike_count_day+1,
                    dislike_count_week=dislike_count_week+1,
                    dislike_count_month_30=dislike_count_month_30+1 WHERE content_id = {};""".format(content_id_str)
                    cono.cursor.execute(query)
                    response_data["dislike"]="added"
            query="select like_count,dislike_count from post_review_table where content_id=%s;"
            cono.cursor.execute(query,(content_id_str,))
            result=cono.cursor.fetchone()
            query="UPDATE post_review_table SET like_dislike_ratio=%s where content_id=%s;"
            cono.cursor.execute(query,((result[0] if result[0]!=0 else 1)/(result[1] if result[1]!=0 else 1),content_id_str))
            
            response_data["result"]="success"
        else:
            response_data["result"]="failed_error"
        cono.cnx.commit()
        cono.terminate_connection()
    else:
        response_data["result"]="failed_error"
    
    return JsonResponse(response_data)


@csrf_exempt
def review_post_app(request:HttpRequest):
    try:
        request_data = json.loads(request.body)
    except (ValueError, UnicodeDecodeError):
        request_data = {}
    response_data={}
    if("content_id" in request_data and
       "change" in request_data):
        content_id_str=request_data["content_id"]
        cono=connection_to_user_db(request_json_data=request_data,from_app_flag=True)
        change=request_data["change"]
        query="SELECT content_id FROM post_data_table WHERE content_id=%s;"
        data=(content_id_str,)
        cono.cursor.execute(query,data)
        result=cono.cursor.fetchone()
        if(cono.session.user_id>=1 and result is not None):
            post_review=""#対象のpostへの対象のユーザーの評価
            query="select like_history,dislike_history from user_review_history where user_id={}".format(cono.session.user_id)
            cono.cursor.execute(query)
            result=cono.cursor.fetchone()
            liked_list = result[0].split(",")#全て文字列
            disliked_list = result[1].split(",")
            
            if("" in liked_list):
                liked_list.remove("")#これで空のcontent_idが入らないようにする
            if("" in disliked_list):
                disliked_list.remove("")
            
            if(content_id_str in liked_list):
                post_review="liked"
            elif(content_id_str in disliked_list):#liked xor disliked
                post_review="disliked"
            
            if(change=="add_like"):
                response_data["dislike"]="none"#場合によっては変わる
                if(post_review=="liked"):#likeを消す
                    liked_list.remove(content_id_str)
                    new_liked_list_joind=",".join(liked_list)
                    query="UPDATE user_review_history SET like_history='{}' WHERE user_id = {};".format(new_liked_list_joind,cono.session.user_id)
                    cono.cursor.execute(query)
                    query="""UPDATE post_review_table SET like_count=like_count-1,
                    like_count_hour=like_count_hour-1,
                    like_count_day=like_count_day-1,
                    like_count_week=like_count_week-1,
                    like_count_month_30=like_count_month_30-1 WHERE content_id = {};""".format(content_id_str)
                    cono.cursor.execute(query)
                    response_data["like"]="removed"
                else:#likeを足す
                    if(post_review=="disliked"):#dislikeを消す
                        disliked_list.remove(content_id_str)
                        new_disliked_list_joind=",".join(disliked_list)
                        query="UPDATE user_review_history SET dislike_history='{}' WHERE user_id = {};".format(new_disliked_list_joind,cono.session.user_id)
                        cono.cursor.execute(query)
                        query="""UPDATE post_review_table SET dislike_count=dislike_count-1,
                        dislike_count_hour=dislike_count_hour-1,
                        dislike_count_day=dislike_count_day-1,
                        dislike_count_week=dislike_count_week-1,
                        dislike_count_month_30=dislike_count_month_30-1 WHERE content_id = {};""".format(content_id_str)
                        cono.cursor.execute(query)
                        response_data["dislike"]="removed"
                    liked_list.append(content_id_str)
                    new_liked_list_joind=",".join(liked_list)
                    query="UPDATE user_review_history SET like_history='{}' WHERE user_id = {};".format(new_liked_list_joind,cono.session.user_id)
                    cono.cursor.execute(query)
                    query="""UPDATE post_review_table SET like_count=like_count+1,
                    like_count_hour=like_count_hour+1,
                    like_count_day=like_count_day+1,
                    like_count_week=like_count_week+1,
                    like_count_month_30=like_count_month_30+1 WHERE content_id = {};""".format(content_id_str)
                    cono.cursor.execute(query)
                    response_data["like"]="added"
            elif(change=="add_dislike"):#add_likeの反対
                response_data["like"]="none"#場合によっては変わる
                if(post_review=="disliked"):#すでにdislikeされているならdislikeを取り消す
                    disliked_list.remove(content_id_str)
                    new_disliked_list_joind=",".join(disliked_list)
                    query="UPDATE user_review_history SET dislike_history='{}' WHERE user_id = {};".format(new_disliked_list_joind,cono.session.user_id)
                    cono.cursor.execute(query)
                    query="""UPDATE post_review_table SET dislike_count=dislike_count-1,
                    dislike_count_hour=dislike_count_hour-1,
                    dislike_count_day=dislike_count_day-1,
                    dislike_count_week=dislike_count_week-1,
                    dislike_count_month_30=dislike_count_month_30-1 WHERE content_id = {};""".format(content_id_str)
                    cono.cursor.execute(query)
                    response_data["dislike"]="removed"
                else:
                    if(post_review=="liked"):#likeを取り消す
                        liked_list.remove(content_id_str)
                        new_liked_list_joind=",".join(liked_list)
                        query="UPDATE user_review_history SET like_history='{}' WHERE user_id = {};".format(new_liked_list_joind,cono.session.user_id)
                        cono.cursor.execute(query)
                        query="""UPDATE post_review_table SET like_count=like_count-1,
                        like_count_hour=like_count_hour-1,
                        like_count_day=like_count_day-1,
                        like_count_week=like_count_week-1,
                        like_count_month_30=like_count_month_30-1 WHERE content_id = {};""".format(content_id_str)
                        cono.cursor.execute(query)
                        response_data["like"]="removed"
                    disliked_list.append(content_id_str)
                    new_disliked_list_joind=",".join(disliked_list)
                    query="UPDATE user_review_history SET dislike_history='{}' WHERE user_id = {};".format(new_disliked_list_joind,cono.session.user_id)
                    cono.cursor.execute(query)
                    query="""UPDATE post_review_table SET dislike_count=dislike_count+1,
                    dislike_count_hour=dislike_count_hour+1,
                    dislike_count_day=dislike_count_day+1,
                    dislike_count_week=dislike_count_week+1,
                    dislike_count_month_30=dislike_count_month_30+1 WHERE content_id = {};""".format(content_id_str)
                    cono.cursor.execute(query)
                    response_data["dislike"]="added"
            query="select like_count,dislike_count from post_review_table where content_id=%s;"
            cono.cursor.execute(query,(content_id_str,))
            result=cono.cursor.fetchone()
            query="UPDATE post_review_table SET like_dislike_ratio=%s where content_id=%s;"
            cono.cursor.execute(query,((result[0] if result[0]!=0 else 1)/(result[1] if result[1]!=0 else 1),content_id_str))
            response_data["result"]="success"
        else:
            response_data["result"]="failed_error"
        cono.cnx.commit()
        cono.terminate_connection()
    else:
        response_data["result"]="failed_error"
    print(response_data)
    return JsonResponse(response_data)


@csrf_exempt
def get_my_post(request:HttpRequest):
    try:
        request_data = json.loads(request.body)
    except (ValueError, UnicodeDecodeError):
        request_data = {}
    response_data={}
    cono=connection_to_user_db(request=request,request_json_data=request_data,from_app_flag=True)
    if(cono.session.user_id>=1):
        user_id=cono.session.user_id
        query="select * from user_data_table where user_id={}".format(user_id)
        cono.cursor.execute(query)
        user_data=cono.cursor.fetchone()
        username=user_data[1]
        user_posted_list = list(dict.fromkeys(my_search.search_post_index(include_text=str(user_id),search_conditions=["user_id"])))#何故か重複するので重複排除
        posted_post_=my_functions.create_content_dict(
            cursor=cono.cursor,
            content_id_list=user_posted_list,
            amount_of_displayed_post=1000,
            start_number=1,
            page_number=1,
            order="new_post",
            user_id=cono.session.user_id
            )
        response_data={**response_data,**posted_post_}
        response_data["result"]="success"
                
    else:
        response_data["result"]="incrrect_session_error"
        my_functions.error_log("3242342342")
    
    cono.terminate_connection()
    return JsonResponse(response_data)


@csrf_exempt
def search_process_app(request: HttpRequest):
    response_data={}
    try:
        request_data = json.loads(request.body)
    except (ValueError, UnicodeDecodeError):
        request_data = {}
        response_data["result"]="request_broken_error"
        my_functions.error_log("374263876786")
        return JsonResponse(response_data)
    max_display_number=10
    if(my_functions.check_existence(multi=request_data,keys=["post_order"],allow_empty=False)):
        order=request_data["post_order"]#不正な文字列の判定はcreate_content_dictでやる
    else:
        my_functions.error_log("293287897")
        order="new_post"

    if(my_functions.check_existence(multi=request_data,keys=["page_number"],allow_empty=False)):
        if my_functions.check_str_is_int(request_data["page_number"]):  # 整数以外を送られたら
            page_number=int(request_data["page_number"])
        else:
            my_functions.error_log("297989878973")
            page_number=-1
    else:
        my_functions.error_log("297989878297")
        page_number=1
    
    if my_functions.check_existence(multi=request_data, keys=["user_id"],allow_empty=False):
        if my_functions.check_str_is_int(request_data["user_id"]):
            user_id=int(request_data["user_id"])
        else:
            user_id=-1
            my_functions.error_log("9798987897")
    else:
        my_functions.error_log("29798987897")
        user_id=-1
    
    cnx=my_functions.connect_to_database()
    cursor=cnx.cursor(buffered=True)
    
    if(user_id>=1):
        if my_functions.check_existence(multi=request_data, keys=["user_id","session_id_1","session_id_2","device_unique_id"],allow_empty=False):
            query="SELECT user_id FROM user_session_table WHERE user_id=%s and session_id_1=%s and session_id_2=%s and uniqueid=%s;"
            cursor.execute(query,(str(user_id),request_data["session_id_1"],request_data["session_id_2"],request_data["device_unique_id"]))
            result=cursor.fetchone()
            if(result is None):
                cursor.close()
                cnx.close()
                response_data["result"]="disable_session_error"
                my_functions.error_log("789273497")
                return JsonResponse(response_data)
        else:
            cursor.close()
            cnx.close()
            response_data["result"]="request_broken_error"
            my_functions.error_log("7289273497")
            return JsonResponse(response_data)
    
    search_conditions=["title","content","overview","tags"]
    search_word_dict={}
    if(my_functions.check_existence(multi=request_data,keys=["search_words"],allow_empty=False)):
        search_words = request_data["search_words"]
        search_word_dict["search_words"]=search_words
    else:
        search_words="inculde_all"
        search_conditions.append("for_all")
        search_word_dict["search_words"]=""
    if(my_functions.check_existence(multi=request_data,keys=["search_words_exclude"],allow_empty=False)):
        exclude_words=request_data["search_words_exclude"]
        search_word_dict["search_words_exclude"]=exclude_words
    else:
        exclude_words=""
        search_word_dict["search_words_exclude"]=""
    matched_post_list = my_search.search_post_index(include_text=search_words,exclude_text=exclude_words,search_conditions=search_conditions)
    displayed_post=my_functions.create_content_dict(
        cursor=cursor,
        content_id_list=matched_post_list,
        amount_of_displayed_post=max_display_number,
        start_number=(page_number-1)*10+1,
        page_number=page_number,
        order=order,
        user_id=user_id
        )
    response_data={**response_data,**displayed_post}
    response_data["result"]="success"
    cursor.close()
    cnx.close()
    return JsonResponse(response_data)


@csrf_exempt
def get_discussion_data(request:HttpRequest):#アプリでも使える
    try:
        request_data = json.loads(request.body)
    except (ValueError, UnicodeDecodeError):
        request_data = {}
    response_data={}
    if("content_id" in request_data):
        content_id_str=request_data["content_id"]
        cnx=my_functions.connect_to_database()
        cursor=cnx.cursor(buffered=True)
        query="SELECT content_id FROM post_data_table WHERE content_id=%s;"
        data=(content_id_str,)
        cursor.execute(query,data)
        result=cursor.fetchone()
        if(result is not None):
            content_id_str=str(result[0])#念のため
            query="SELECT comment_ids FROM post_discussion_table WHERE content_id={};".format(content_id_str)
            cursor.execute(query)          
            result=cursor.fetchone()
            if(result[0]!=""):
                comment_id_list=result[0].split(",")
                query="SELECT content,parent_comment_id,user_id,post_date FROM discussion_data_table where comment_id in("
                for i in comment_id_list:
                    query+=i+","#comment_id_listの要素はstr
                query=query[:-1]+");"#[:-1]は最後の,を消すため
                cursor.execute(query)
                results=cursor.fetchall()
                comment_id_combined="<".join(comment_id_list)
                comment_content_combined=""
                parent_comment_id_combined=""
                comment_user_id_combined=""
                comment_username_combined=""
                comment_date_combined=""
                for i in results:
                    comment_content_combined+=i[0]+"<"
                    parent_comment_id_combined+=str(i[1])+"<"
                    comment_user_id_combined+=str(i[2])+"<"
                    query="select username from user_data_table where user_id={}".format(i[2])
                    cursor.execute(query)
                    result=cursor.fetchone()
                    comment_username_combined+=result[0]+"<"
                    comment_date_combined+=i[3].strftime("%Y,%m,%d,%H,%M,%S")+"<"
                response_data["amount_of_displayd_comment"]=str(len(comment_id_list))
                response_data["comment_id_combined"]=comment_id_combined#ここだけ[:-1]いらない
                response_data["comment_content_combined"]=comment_content_combined[:-1]
                response_data["parent_comment_id_combined"]=parent_comment_id_combined[:-1]
                response_data["comment_user_id_combined"]=comment_user_id_combined[:-1]
                response_data["comment_username_combined"]=comment_username_combined[:-1]
                response_data["comment_date_combined"]=comment_date_combined[:-1]
            else:
                response_data["amount_of_displayd_comment"]="0"
            response_data["result"]="success"
        else:
            response_data["result"]="failed_error"
        cnx.commit()
        cursor.close()
        cnx.close()
    else:
        response_data["result"]="failed_error"
    return JsonResponse(response_data)


def add_comment(request:HttpRequest):
    try:
        request_data = json.loads(request.body)
    except (ValueError, UnicodeDecodeError):
        request_data = {}
    response_data={}
    if("session_id_1" in request_data and
       "session_id_2" in request_data and
       "content_id" in request_data and
       "comment_content" in request_data and
       "parent_comment_id" in request_data):
        content_id_str=request_data["content_id"]
        comment_content=request_data["comment_content"]
        parent_comment_id_str=request_data["parent_comment_id"]
        cono=connection_to_user_db(request=request,request_json_data=request_data,get_user_setting=True,from_app_flag=False)
        query="SELECT content_id,comment_ids FROM post_discussion_table WHERE content_id=%s;"
        data=(content_id_str,)
        cono.cursor.execute(query,data)
        result02=cono.cursor.fetchone()
        if(cono.session.user_id>=1 and result02 is not None and
           my_functions.check_content(text=comment_content,max_character_count=1000)):
            result02=list(result02)
            user_id_str=str(cono.session.user_id)
            content_id_str=str(result02[0])
            if(result02[1]==""):
                result02[1]="0"
            else:
                result02[1]+=",0"
            posted_comment_list=result02[1].split(",")
            if(parent_comment_id_str in  posted_comment_list):
                query="SELECT comment_id FROM discussion_data_table ORDER BY comment_id DESC LIMIT 1 ;"
                cono.cursor.execute(query)
                result = cono.cursor.fetchone()
                if(result is not None):
                    comment_id=result[0]+1
                else:
                    comment_id=1
                query="""
                INSERT INTO discussion_data_table (comment_id,content,parent_content_id,parent_comment_id,user_id,post_date)
                VALUES
                (%s,%s,%s,%s,%s,%s) ;"""
                now = datetime.datetime.now(JST)
                data=[str(comment_id),comment_content,content_id_str,parent_comment_id_str,user_id_str,now.strftime("%Y-%m-%d %H:%M:%S")]
                cono.cursor.execute(query,data)
                query="SELECT comment_ids FROM post_discussion_table WHERE content_id = {};".format(content_id_str)
                cono.cursor.execute(query)
                result=cono.cursor.fetchone()
                if(result[0]==""):
                    new_comment_ids=str(comment_id)
                else:
                    new_comment_ids=result[0]+","+str(comment_id)
                query="UPDATE post_discussion_table SET comment_ids=%s WHERE content_id = %s;"
                data=[new_comment_ids,content_id_str]
                cono.cursor.execute(query,data)
                response_data["result"]="success"
                response_data["comment_id"]=str(comment_id)
                response_data["comment_content"]=comment_content
                query="select username from user_data_table where user_id={};".format(cono.session.user_id)
                cono.cursor.execute(query)
                result=cono.cursor.fetchone()
                response_data["comment_username"]=result[0]
            else:
                response_data["result"]="parent_comment_deleted"
        else:
            response_data["result"]="failed_error"
        cono.cnx.commit()
        cono.terminate_connection()
    else:
        response_data["result"]="failed_error"
    return JsonResponse(response_data)


@csrf_exempt
def add_comment_app(request:HttpRequest):
    try:
        request_data = json.loads(request.body)
    except (ValueError, UnicodeDecodeError):
        request_data = {}
    response_data={}
    if("session_id_1" in request_data and
       "session_id_2" in request_data and
       "content_id" in request_data and
       "comment_content" in request_data and
       "parent_comment_id" in request_data):
        content_id_str=request_data["content_id"]
        comment_content=request_data["comment_content"]
        parent_comment_id_str=request_data["parent_comment_id"]
        cono=connection_to_user_db(request=request,request_json_data=request_data,get_user_setting=True,from_app_flag=True)
        query="SELECT content_id,comment_ids FROM post_discussion_table WHERE content_id=%s;"
        data=(content_id_str,)
        cono.cursor.execute(query,data)
        result02=cono.cursor.fetchone()
        if(cono.session.user_id<=0 ):
            response_data["result"]="incorrect_session_error"
            cono.terminate_connection()
            return JsonResponse(response_data)
            
        if(result02 is not None and
           my_functions.check_content(text=comment_content,max_character_count=1000)):
            result02=list(result02)
            user_id_str=str(cono.session.user_id)
            content_id_str=str(result02[0])
            if(result02[1]==""):
                result02[1]="0"
            else:
                result02[1]+=",0"
            posted_comment_list=result02[1].split(",")
            if(parent_comment_id_str in  posted_comment_list):
                query="SELECT comment_id FROM discussion_data_table ORDER BY comment_id DESC LIMIT 1 ;"
                cono.cursor.execute(query)
                result = cono.cursor.fetchone()
                if(result is not None):
                    comment_id=result[0]+1
                else:
                    comment_id=1
                query="""
                INSERT INTO discussion_data_table (comment_id,content,parent_content_id,parent_comment_id,user_id,post_date)
                VALUES
                (%s,%s,%s,%s,%s,%s) ;"""
                now = datetime.datetime.now(JST)
                data=[str(comment_id),comment_content,content_id_str,parent_comment_id_str,user_id_str,now.strftime("%Y-%m-%d %H:%M:%S")]
                cono.cursor.execute(query,data)
                query="SELECT comment_ids FROM post_discussion_table WHERE content_id = {};".format(content_id_str)
                cono.cursor.execute(query)
                result=cono.cursor.fetchone()
                if(result[0]==""):
                    new_comment_ids=str(comment_id)
                else:
                    new_comment_ids=result[0]+","+str(comment_id)
                query="UPDATE post_discussion_table SET comment_ids=%s WHERE content_id = %s;"
                data=[new_comment_ids,content_id_str]
                cono.cursor.execute(query,data)
                response_data["result"]="success"
                response_data["comment_id"]=str(comment_id)
                response_data["comment_content"]=comment_content
                query="select username from user_data_table where user_id={};".format(cono.session.user_id)
                cono.cursor.execute(query)
                result=cono.cursor.fetchone()
                response_data["comment_username"]=result[0]
            else:
                response_data["result"]="parent_comment_deleted"
        else:
            response_data["result"]="failed_error"
        cono.cnx.commit()
        cono.terminate_connection()
    else:
        response_data["result"]="failed_error"
    return JsonResponse(response_data)


def change_user_info_process(request:HttpRequest):
    response_data={}
    if("json" in request.FILES):
        json_binary=request.FILES['json'].read()
        if(my_functions.is_valid_json(json_binary)):
            request_data = json.loads(json_binary.decode('utf-8'))
        else:
            response_data["result"]="request_broken_error"
            my_functions.error_log("57267567")
            return JsonResponse(response_data)
    else:
        response_data["result"]="request_broken_error"
        my_functions.error_log("714565")
        return JsonResponse(response_data)
    
    if(my_functions.check_existence(multi=request_data,keys=["new_profile"],allow_empty=True) and
       my_functions.check_existence(multi=request_data,keys=["new_username","icon_inputed_flag","session_id_1","session_id_2"],allow_empty=False)):
        new_username = request_data["new_username"]
        new_profile = request_data["new_profile"]
    else:
        response_data["result"]="request_broken_error"
        my_functions.error_log("1722319283")
        return JsonResponse(response_data)
    
    if(my_functions.check_username(text=new_username)==False or
       my_functions.check_content(text=new_profile,max_character_count=150,min_character_count=0,allow_new_line=True,max_new_line_count=3)==False
       ):
        my_functions.error_log("66234658")
        response_data["result"]="failed_error"
        return JsonResponse(response_data)
    
    cono=connection_to_user_db(request=request,request_json_data=request_data,from_app_flag=False)
    if(cono.session.user_id>=1):
        user_id=cono.session.user_id
        if(request_data["icon_inputed_flag"]=="y"):
            if(not 'image_file' in request.FILES):
                my_functions.error_log("8279182379")
                response_data["result"]="failed_error"
                return JsonResponse(response_data)
            
            image_binary=request.FILES['image_file'].read()
            if(my_functions.is_valid_image(image_binary)):
                my_functions.delete_file_if_exists(os.path.join(my_functions.media_path+"\\user_icons","user_icon_{}.png".format(user_id)))
                uploaded_image =my_functions.image_resize_and_crop_square(image=Image.open(io.BytesIO(image_binary)),size=400)
                uploaded_image.save(os.path.join(my_functions.media_path+"\\user_icons","user_icon_{}.png".format(user_id)))
                my_functions.delete_file_if_exists(os.path.join(my_functions.media_path+"\\user_icons","user_icon_mini_{}.png".format(user_id)))
                uploaded_image =my_functions.image_resize_and_crop_square(image=Image.open(io.BytesIO(image_binary)),size=200)
                uploaded_image.save(os.path.join(my_functions.media_path+"\\user_icons","user_icon_mini_{}.png".format(user_id)))
            else:
                cono.terminate_connection()
                my_functions.error_log("127317928")
                response_data["result"]="failed_error"
                return JsonResponse(response_data)
            
        if(my_functions.check_username_overlap(cursor=cono.cursor,username=new_username,allow_user_id_list=[user_id])==False):
            cono.terminate_connection()
            response_data["result"]="user_overlap_error"
            return JsonResponse(response_data)
        
        query="UPDATE user_data_table SET username=%s,user_profile=%s WHERE user_id = %s;".format(new_username,user_id)
        data=(new_username,new_profile,str(user_id))
        cono.cursor.execute(query,data)
        cono.cnx.commit()
        cono.terminate_connection()
        response_data={"result":"success"}
        return JsonResponse(response_data)
    else:
        cono.terminate_connection()
        my_functions.error_log("7879989789")
        response_data["result"]="failed_error"
        return JsonResponse(response_data)


@csrf_exempt
def change_user_info_process_app(request:HttpRequest):
    response_data={}
    try:
        request_data = json.loads(request.body)
    except (ValueError, UnicodeDecodeError):
        request_data = {}

    if(my_functions.check_existence(multi=request_data,keys=["new_profile"],allow_empty=True) and
       my_functions.check_existence(multi=request_data,keys=["new_username","icon_inputed_flag","session_id_1","session_id_2"],allow_empty=False)):
        new_username = request_data["new_username"]
        new_profile = request_data["new_profile"]
    else:
        response_data["result"]="request_broken_error"
        my_functions.error_log("172319283")
        return JsonResponse(response_data)
    
    if(my_functions.check_username(text=new_username)==False or
       my_functions.check_content(text=new_profile,max_character_count=150,min_character_count=0,allow_new_line=True,max_new_line_count=3)==False
       ):
        my_functions.error_log("662258")
        response_data["result"]="failed_error"
        return JsonResponse(response_data)
    
    cono=connection_to_user_db(request=request,request_json_data=request_data,from_app_flag=True)
    if(cono.session.user_id>=1):
        user_id=cono.session.user_id
        if(request_data["icon_inputed_flag"]=="y"):
            if(not 'image_base64' in request_data):
                my_functions.error_log("82712182379")
                response_data["result"]="failed_error"
                return JsonResponse(response_data)
            
            image_binary=base64.b64decode(request_data["image_base64"])
            if(my_functions.is_valid_image(image_binary)):
                my_functions.delete_file_if_exists(os.path.join(my_functions.media_path+"\\user_icons","user_icon_{}.png".format(user_id)))
                uploaded_image =my_functions.image_resize_and_crop_square(image=Image.open(io.BytesIO(image_binary)),size=400)
                uploaded_image.save(os.path.join(my_functions.media_path+"\\user_icons","user_icon_{}.png".format(user_id)))
                my_functions.delete_file_if_exists(os.path.join(my_functions.media_path+"\\user_icons","user_icon_mini_{}.png".format(user_id)))
                uploaded_image =my_functions.image_resize_and_crop_square(image=Image.open(io.BytesIO(image_binary)),size=200)
                uploaded_image.save(os.path.join(my_functions.media_path+"\\user_icons","user_icon_mini_{}.png".format(user_id)))
            else:
                cono.terminate_connection()
                my_functions.error_log("3123")
                response_data["result"]="failed_error"
                return JsonResponse(response_data)
            
        if(my_functions.check_username_overlap(cursor=cono.cursor,username=new_username,allow_user_id_list=[user_id])==False):
            cono.terminate_connection()
            response_data["result"]="user_overlap_error"
            return JsonResponse(response_data)
        
        query="UPDATE user_data_table SET username=%s,user_profile=%s WHERE user_id = %s;".format(new_username,user_id)
        data=(new_username,new_profile,str(user_id))
        cono.cursor.execute(query,data)
        cono.cnx.commit()
        cono.terminate_connection()
        response_data={"result":"success"}
        return JsonResponse(response_data)
    else:
        cono.terminate_connection()
        my_functions.error_log("783897987")
        response_data["result"]="failed_error"
        return JsonResponse(response_data)


def change_password_process(request:HttpRequest):
    try:
        request_data = json.loads(request.body)
    except (ValueError, UnicodeDecodeError):
        request_data = {}
        response_data={"result":"failed_error"}
        return JsonResponse(response_data)
    if("user_id" in request_data and
       "session_id_1" in request_data and
       "session_id_2" in request_data and
       "password_old" in request_data and
       "password_new" in request_data
       ):
        password_old=request_data["password_old"]
        password_new=request_data["password_new"]
        session_id_1_str=request_data["session_id_1"]
        session_id_2_str=request_data["session_id_2"]
        cnx=my_functions.connect_to_database()
        cursor=cnx.cursor(buffered=True)
        query="SELECT user_id FROM user_session_table WHERE session_id_1=%s AND session_id_2=%s and is_app='n'"
        data=(session_id_1_str,session_id_2_str)
        cursor.execute(query,data)
        result = cursor.fetchone()
        if(result[0]==int(request_data["user_id"]) and my_functions.check_password(password_new)):
            user_id=result[0]
            query="SELECT password FROM user_data_table WHERE user_id={};".format(user_id)
            cursor.execute(query)
            result = cursor.fetchone()
            if(argon2.verify(password_old + secret_values.password_salt, result[0])):
                password_new=argon2.hash(password_new + secret_values.password_salt)
                query="UPDATE user_data_table SET password=%s WHERE user_id = %s;"
                data=(password_new,user_id)
                cursor.execute(query,data)
                query="DELETE FROM user_session_table WHERE user_id = %s"
                data=(user_id,)
                cursor.execute(query,data)
                cnx.commit()
                cursor.close()
                cnx.close()
                response_data={"result":"success"}
            else:
                response_data={"result":"failed_password"}
        else:
            response_data={"result":"failed_error"}
    else:
        response_data={"result":"failed_error"}
    return JsonResponse(response_data)


@csrf_exempt
def get_user_data_process(request:HttpRequest):
    response_data={}
    try:
        request_data = json.loads(request.body)
    except (ValueError, UnicodeDecodeError):
        request_data = {}
        response_data["result"]="request_broken_error"
        my_functions.error_log("374263876786")
        return JsonResponse(response_data)
    if not my_functions.check_existence(multi=request_data, keys=["user_id"],allow_empty=False):
        my_functions.error_log("9808098908234")
        response_data["result"]="failed_error"
        return JsonResponse(response_data)
    
    if my_functions.check_existence(multi=request_data, keys=["get_f_f"],allow_empty=False):
        get_f_f_flag=True if request_data["get_f_f"]=="y" else False
    else:
        get_f_f_flag=False
        
    if get_f_f_flag and my_functions.check_existence(multi=request_data, keys=["get_followed_user_name"],allow_empty=False):#get_f_fがyでなきゃいけない
        get_followed_user_name_flag=True if request_data["get_followed_user_name"]=="y" else False
    else:
        get_followed_user_name_flag=False
    
    if my_functions.check_existence(multi=request_data, keys=["get_posts"],allow_empty=False):
        get_posts_title_flag=True if request_data["get_posts"]=="y" else False
    else:
        get_posts_title_flag=False
    
    if(my_functions.check_str_is_int(request_data["user_id"])):
        user_id=int(request_data["user_id"])
    else:
        response_data["result"]="request_broken_error"
        return JsonResponse(response_data)
    
    cnx=my_functions.connect_to_database()
    cursor=cnx.cursor(buffered=True)
    query="SELECT user_id FROM user_data_table WHERE user_id=%s;"
    cursor.execute(query,(str(user_id),))
    result = cursor.fetchone()
    if(result is None):
        cursor.close()
        cnx.close()
        response_data["result"]="request_broken_error"
        my_functions.error_log("92348789734892")
        return JsonResponse(response_data)

    else:
        query="select username,user_profile from user_data_table where user_id={};".format(user_id)
        cursor.execute(query)
        result=cursor.fetchone()
        response_data["username"]=result[0]
        response_data["user_profile"]=result[1]
        
        if(get_f_f_flag):
            query="select followers,followed_users from user_relation_table where user_id={};".format(user_id)
            cursor.execute(query)
            result=cursor.fetchone()
            response_data["followers"]=result[0]
            response_data["followed_users"]=result[1]
            
            if(get_followed_user_name_flag):
                followed_user_id_list=response_data["followed_users"].split(",")
                followed_username_combined=""
                if(response_data["followed_users"]!=""):
                    query="select username from user_data_table where user_id in("
                    for i in followed_user_id_list:
                        query+=str(i)+","#i[0]=content_id
                    query=query[:-1]+");"#末尾の,を削除
                    cursor.execute(query)
                    results=cursor.fetchall()

                    if(results is not None):

                        for i in results:
                            followed_username_combined+=i[0]+"<"

                        followed_username_combined=followed_username_combined[:-1]
                
                response_data["followed_username_combined"]=followed_username_combined
                
        if(get_posts_title_flag):
            user_posted_list = list(dict.fromkeys(my_search.search_post_index(include_text=str(user_id),search_conditions=["user_id"])))#何故か重複するので重複排除
            displayed_post=my_functions.create_content_dict(
                cursor=cursor,
                content_id_list=user_posted_list,
                amount_of_displayed_post=1000,
                start_number=1,
                page_number=1,
                order="new_post",
                user_id=user_id
                )
            response_data={**displayed_post,**response_data}

        cursor.close()
        cnx.close()
        response_data["result"]="success"
        
    return JsonResponse(response_data)


def user_follow(request:HttpRequest):
    response_data={}
    try:
        request_data = json.loads(request.body)
    except (ValueError, UnicodeDecodeError):
        response_data["result"]="request_broken_error"
        my_functions.error_log("234298479823789798")
        return JsonResponse(response_data)
    if(my_functions.check_existence(multi=request_data,keys=["session_id_1","session_id_2","followed_user_id"],allow_empty=False)):
        if(my_functions.check_str_is_int(request_data["followed_user_id"])):
            followed_user_id=int(request_data["followed_user_id"])
        else:
            response_data["result"]="request_broken_error"
            return JsonResponse(response_data)
    else:
        my_functions.error_log("79728638236762")
        response_data["result"]="request_broken_error"
        return JsonResponse(response_data)
    cono=connection_to_user_db(request=request,request_json_data=request_data,from_app_flag=False)
    query="SELECT user_id FROM user_data_table WHERE user_id=%s;"
    cono.cursor.execute(query,(str(followed_user_id),))
    result01 = cono.cursor.fetchone()
    if(result01 is None):
        cono.terminate_connection()
        response_data["result"]="request_broken_error"
        my_functions.error_log("72298374987497")
        return JsonResponse(response_data)
    
    
    if  cono.session.user_id<=0:
        cono.terminate_connection()
        response_data["result"]="failed_error"
        my_functions.error_log("22379789789797")
        return JsonResponse(response_data)
    elif(followed_user_id==cono.session.user_id):
        response_data["result"]="myself_follow_error"
        my_functions.error_log("3249878979")
    elif(followed_user_id!=cono.session.user_id):
        user_id=cono.session.user_id
        query="select followed_users from user_relation_table where user_id={};".format(user_id)
        cono.cursor.execute(query)
        result=cono.cursor.fetchone()
        followed_users_list=result[0].split(",")
        if("" in followed_users_list):
            followed_users_list.remove("")
                
        query="select followers from user_relation_table where user_id={};".format(followed_user_id)
        cono.cursor.execute(query)
        result=cono.cursor.fetchone()
        followed_user_followers_list=result[0].split(",")
        if("" in followed_user_followers_list):
            followed_user_followers_list.remove("")
    
        if((not str(followed_user_id) in followed_users_list) and (not str(user_id) in followed_user_followers_list)):
            followed_users_list.append(str(followed_user_id)) 
            followed_user_followers_list.append(str(user_id))
            query="UPDATE user_relation_table SET followed_user_count=followed_user_count+1 where user_id={}".format(user_id)
            cono.cursor.execute(query)
            query="UPDATE user_relation_table SET followers_count=followers_count+1 where user_id={}".format(followed_user_id)
            cono.cursor.execute(query)
            
        elif(str(followed_user_id) in followed_users_list and str(user_id) in followed_user_followers_list):
            followed_users_list.remove(str(followed_user_id)) 
            followed_user_followers_list.remove(str(user_id))
            query="UPDATE user_relation_table SET followed_user_count=followed_user_count-1 where user_id={}".format(user_id)
            cono.cursor.execute(query)
            query="UPDATE user_relation_table SET followers_count=followers_count-1 where user_id={}".format(followed_user_id)
            cono.cursor.execute(query)
            
        elif((not str(followed_user_id) in followed_users_list) and str(user_id) in followed_user_followers_list):#ここからはエラー
            followed_user_followers_list.remove(str(user_id))
            query="UPDATE user_relation_table SET followers_count=followers_count-1 where user_id={}".format(followed_user_id)
            cono.cursor.execute(query)
            
        else:
            followed_users_list.remove(str(followed_user_id))
            query="UPDATE user_relation_table SET followed_user_count=followed_user_count-1 where user_id={}".format(user_id)
            cono.cursor.execute(query)
            
        new_followed_users=",".join(followed_users_list)
        new_followed_user_followers=",".join(followed_user_followers_list)
        query="UPDATE user_relation_table SET followed_users=%s where user_id=%s"
        data=(new_followed_users,str(user_id))
        cono.cursor.execute(query,data)
        query="UPDATE user_relation_table SET followers=%s where user_id=%s"
        data=(new_followed_user_followers,str(followed_user_id))
        cono.cursor.execute(query,data)
        cono.cnx.commit()
        response_data["result"]="success"
    else:
        response_data["result"]="failed_error"
        my_functions.error_log("039024898398298")
    cono.terminate_connection()
    return JsonResponse(response_data)


@csrf_exempt
def user_follow_app(request:HttpRequest):
    response_data={}
    try:
        request_data = json.loads(request.body)
    except (ValueError, UnicodeDecodeError):
        response_data["result"]="request_broken_error"
        my_functions.error_log("234223789798")
        return JsonResponse(response_data)
    if(my_functions.check_existence(multi=request_data,keys=["followed_user_id"],allow_empty=False)):
        if(my_functions.check_str_is_int(request_data["followed_user_id"])):
            followed_user_id=int(request_data["followed_user_id"])
        else:
            response_data["result"]="request_broken_error"
            return JsonResponse(response_data)
    else:
        my_functions.error_log("79728636762")
        response_data["result"]="request_broken_error"
        return JsonResponse(response_data)
    cono=connection_to_user_db(request=request,request_json_data=request_data,from_app_flag=True)
    query="SELECT user_id FROM user_data_table WHERE user_id=%s;"
    cono.cursor.execute(query,(str(followed_user_id),))
    result01 = cono.cursor.fetchone()
    if(result01 is None):
        cono.terminate_connection()
        response_data["result"]="request_broken_error"
        my_functions.error_log("72298374987497")
        return JsonResponse(response_data)
    
    
    if  cono.session.user_id<=0:
        cono.terminate_connection()
        response_data["result"]="failed_error"
        my_functions.error_log("22379789789797")
        return JsonResponse(response_data)
    elif(followed_user_id==cono.session.user_id):
        response_data["result"]="myself_follow_error"
        my_functions.error_log("3249878979")
    elif(followed_user_id!=cono.session.user_id):
        user_id=cono.session.user_id
        query="select followed_users from user_relation_table where user_id={};".format(user_id)
        cono.cursor.execute(query)
        result=cono.cursor.fetchone()
        followed_users_list=result[0].split(",")
        if("" in followed_users_list):
            followed_users_list.remove("")
                
        query="select followers from user_relation_table where user_id={};".format(followed_user_id)
        cono.cursor.execute(query)
        result=cono.cursor.fetchone()
        followed_user_followers_list=result[0].split(",")
        if("" in followed_user_followers_list):
            followed_user_followers_list.remove("")
    
        if((not str(followed_user_id) in followed_users_list) and (not str(user_id) in followed_user_followers_list)):#フォロー
            followed_users_list.append(str(followed_user_id)) 
            followed_user_followers_list.append(str(user_id))
            query="UPDATE user_relation_table SET followed_user_count=followed_user_count+1 where user_id={}".format(user_id)
            cono.cursor.execute(query)
            query="UPDATE user_relation_table SET followers_count=followers_count+1 where user_id={}".format(followed_user_id)
            cono.cursor.execute(query)
            response_data["change"]="followed"
            
        elif(str(followed_user_id) in followed_users_list and str(user_id) in followed_user_followers_list):#フォロー解除
            followed_users_list.remove(str(followed_user_id)) 
            followed_user_followers_list.remove(str(user_id))
            query="UPDATE user_relation_table SET followed_user_count=followed_user_count-1 where user_id={}".format(user_id)
            cono.cursor.execute(query)
            query="UPDATE user_relation_table SET followers_count=followers_count-1 where user_id={}".format(followed_user_id)
            cono.cursor.execute(query)
            response_data["change"]="unfollowed"
            
        elif((not str(followed_user_id) in followed_users_list) and str(user_id) in followed_user_followers_list):#ここからはエラー
            followed_user_followers_list.remove(str(user_id))
            query="UPDATE user_relation_table SET followers_count=followers_count-1 where user_id={}".format(followed_user_id)
            cono.cursor.execute(query)
            response_data["change"]="error"
            
        else:
            followed_users_list.remove(str(followed_user_id))
            query="UPDATE user_relation_table SET followed_user_count=followed_user_count-1 where user_id={}".format(user_id)
            cono.cursor.execute(query)
            response_data["change"]="error"
            
        new_followed_users=",".join(followed_users_list)
        new_followed_user_followers=",".join(followed_user_followers_list)
        query="UPDATE user_relation_table SET followed_users=%s where user_id=%s"
        data=(new_followed_users,str(user_id))
        cono.cursor.execute(query,data)
        query="UPDATE user_relation_table SET followers=%s where user_id=%s"
        data=(new_followed_user_followers,str(followed_user_id))
        cono.cursor.execute(query,data)
        cono.cnx.commit()
        response_data["result"]="success"
    else:
        response_data["result"]="failed_error"
        my_functions.error_log("039024898398298")
    cono.terminate_connection()
    return JsonResponse(response_data)


@csrf_exempt
def get_view_history_app(request: HttpRequest):
    response_data={}
    try:
        request_data = json.loads(request.body)
    except (ValueError, UnicodeDecodeError):
        response_data["result"]="request_broken_error"
        my_functions.error_log("2119798")
        return JsonResponse(response_data)
    cono=connection_to_user_db(request=request,request_json_data=request_data,from_app_flag=True)
    if(cono.session.user_id>=1):
        user_id=cono.session.user_id
        query="select view_history_resent_100 from user_view_history where user_id={};".format(user_id)
        cono.cursor.execute(query)
        result=cono.cursor.fetchone()
        content_id_list=result[0].split(",")
        if(result[0]!=""):
            content_id_list.reverse()
            for i in content_id_list:
                query="select content_id from post_data_table where content_id={};".format(i)
                cono.cursor.execute(query)
                result=cono.cursor.fetchone()
                if(result is None):
                    content_id_list.remove(i)
        view_history_content_dict=my_functions.create_content_dict(
            cursor=cono.cursor,content_id_list=content_id_list,amount_of_displayed_post=50,start_number=1,page_number=1,order="no_sort_str",user_id=user_id
            )
        response_data["result"]="success"
        response_data={**response_data,**view_history_content_dict}
    else:
        response_data["result"]="incorrect_session_error"
    cono.terminate_connection()
    return JsonResponse(response_data)



def report_process(request:HttpRequest):
    try:
        request_data = json.loads(request.body)
    except (ValueError, UnicodeDecodeError):
        response_data={"result":"failed_error"}
        return JsonResponse(response_data)
    if(not ("session_id_1" in request_data and
       "session_id_2" in request_data and
       "subject_category" in request_data and
       "subject_id" in request_data and
       "report_category" in request_data and
       "report_comment" in request_data)):
        response_data={"result":"failed_error"}
        return JsonResponse(response_data)
    report_item_list=["malicious_misinformation","extremely_violent_content","extremely_sexual_content","behavior_soliciting_personal_information",
                      "behavior_soliciting_real-life_encounters","other_violations_of_terms","other_legal_violations",
                      "other_ethically_problematic_behaviors","behaviors_that_do_not_fit_the_above_items_but_are_problematic"]
    if(not request_data["report_category"] in report_item_list):
        response_data={"result":"failed_error"}
        return JsonResponse(response_data)
    report_comment=request_data["report_comment"]
    report_category=request_data["report_category"]
    subject_category=request_data["subject_category"]
    subject_id=request_data["subject_id"]
    cono=connection_to_user_db(request=request,request_json_data=request_data,from_app_flag=False)
    if(cono.session.user_id==-1):
        user_id=0
    else:
        user_id=cono.session.user_id
    query="select report_id from report_table ORDER BY report_id DESC LIMIT 1;"
    cono.cursor.execute(query)
    result=cono.cursor.fetchone()
    if(result is None):
        report_id=1
    else:
        report_id=result[0]+1
    query="INSERT INTO report_table (report_id,report_user_id,report_category,report_comment) VALUES(%s,%s,%s,%s) ;"
    data=(str(report_id),str(user_id),report_category,subject_category+":id="+subject_id+"\n"+report_comment)
    cono.cursor.execute(query,data)
    cono.cnx.commit()
    cono.terminate_connection()
    response_data={"result":"success"}
    return JsonResponse(response_data)


@csrf_exempt
def report_process_app(request:HttpRequest):
    try:
        request_data = json.loads(request.body)
    except (ValueError, UnicodeDecodeError):
        response_data={"result":"failed_error"}
        return JsonResponse(response_data)
    if(not ("session_id_1" in request_data and
       "session_id_2" in request_data and
       "subject_category" in request_data and
       "subject_id" in request_data and
       "report_category" in request_data and
       "report_comment" in request_data)):
        response_data={"result":"failed_error"}
        return JsonResponse(response_data)
    report_item_list=["malicious_misinformation","extremely_violent_content","extremely_sexual_content","behavior_soliciting_personal_information",
                      "behavior_soliciting_real-life_encounters","other_violations_of_terms","other_legal_violations",
                      "other_ethically_problematic_behaviors","behaviors_that_do_not_fit_the_above_items_but_are_problematic"]
    if(not request_data["report_category"] in report_item_list):
        response_data={"result":"failed_error"}
        return JsonResponse(response_data)
    report_comment=request_data["report_comment"]
    report_category=request_data["report_category"]
    subject_category=request_data["subject_category"]
    subject_id=request_data["subject_id"]
    cono=connection_to_user_db(request=request,request_json_data=request_data,from_app_flag=True)
    if(cono.session.user_id==-1):
        user_id=0
    else:
        user_id=cono.session.user_id
    query="select report_id from report_table ORDER BY report_id DESC LIMIT 1;"
    cono.cursor.execute(query)
    result=cono.cursor.fetchone()
    if(result is None):
        report_id=1
    else:
        report_id=result[0]+1
    query="INSERT INTO report_table (report_id,report_user_id,report_category,report_comment) VALUES(%s,%s,%s,%s) ;"
    data=(str(report_id),str(user_id),report_category,subject_category+":id="+subject_id+"\n"+report_comment)
    cono.cursor.execute(query,data)
    cono.cnx.commit()
    cono.terminate_connection()
    response_data={"result":"success"}
    return JsonResponse(response_data)


def delete_user_process(request:HttpRequest):
    response_data={}
    try:
        request_data = json.loads(request.body)
    except (ValueError, UnicodeDecodeError):
        response_data={"result":"request_broken_error"}
        my_functions.error_log("2343424234491")
        return JsonResponse(response_data)
    if not "password" in request_data:
        response_data={"result":"request_broken_error"}
        my_functions.error_log("2245354423")
        return JsonResponse(response_data)
    cono=connection_to_user_db(request=request,request_json_data=request_data)
    if(cono.session.user_id>=1):
        user_id=cono.session.user_id
        password=request_data["password"]
        query="SELECT password FROM user_data_table WHERE user_id={};".format(user_id)
        cono.cursor.execute(query)
        result = cono.cursor.fetchone()
        if(argon2.verify(password + secret_values.password_salt, result[0])):
            query="UPDATE user_data_table SET username='退会したユーザー',mailaddress='deleted_user_{}',user_profile='退会したユーザーです' where user_id={}".format(user_id,user_id)
            cono.cursor.execute(query)
            query="DELETE FROM user_session_table WHERE user_id={};".format(user_id)
            cono.cursor.execute(query)
            cono.cnx.commit()
            response_data["result"]="success"
        else:
            response_data["result"]="incorrect_password"
    else:
        response_data["result"]="incorrect_session"
    cono.terminate_connection()
    return JsonResponse(response_data)