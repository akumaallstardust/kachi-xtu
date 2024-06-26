from datetime import datetime, date
from apscheduler.schedulers.background import BackgroundScheduler
from . import my_functions
from . import my_search
import datetime
t_delta = datetime.timedelta(hours=9)
JST = datetime.timezone(t_delta, "JST")
def update_hour(cnx,cursor):
   all_post_list=my_search.search_post_index(include_text="inculde_all",exclude_text="",search_conditions=["for_all"])
   
   for i in all_post_list:
      query="select content_id,hour,hour_joined_23,day from post_view_count_table where content_id={}".format(i)
      cursor.execute(query)
      result=cursor.fetchone()
      new_hour_joined_23_list=result[2].split(",")
      new_view_count_day=result[3]-int(new_hour_joined_23_list[0])
      new_hour_joined_23_list.pop(0)
      new_hour_joined_23_list.append(str(result[1]))
      data=(
          "0",
          ",".join(new_hour_joined_23_list),
          str(new_view_count_day),
          str(i)
         )
      query="UPDATE post_view_count_table SET hour=%s,hour_joined_23=%s,day=%s WHERE content_id = %s;"
      cursor.execute(query,data)
      cnx.commit()
   
   for i in all_post_list:
      query="""
      select content_id,like_count_hour,like_count_hour_joined_23,like_count_day,
      dislike_count_hour,dislike_count_hour_joined_23,dislike_count_day
      from post_review_table where content_id={}""".format(i)#3#6
      cursor.execute(query)
      result=cursor.fetchone()
      new_like_count_hour_joined_23_list=result[2].split(",")
      new_like_count_day=result[3]-int(new_like_count_hour_joined_23_list[0])
      new_like_count_hour_joined_23_list.pop(0)
      new_like_count_hour_joined_23_list.append(str(result[1]))

      new_dislike_count_hour_joined_23_list=result[5].split(",")
      new_dislike_count_day=result[6]-int(new_dislike_count_hour_joined_23_list[0])
      new_dislike_count_hour_joined_23_list.pop(0)
      new_dislike_count_hour_joined_23_list.append(str(result[4]))
      query="""UPDATE post_review_table SET like_count_hour=%s,like_count_hour_joined_23=%s,like_count_day=%s,dislike_count_hour=%s,dislike_count_hour_joined_23=%s,dislike_count_day=%s WHERE content_id = %s;"""
      data=(
          "0",
          ",".join(new_like_count_hour_joined_23_list),
          str(new_like_count_day),
          "0",
          ",".join(new_dislike_count_hour_joined_23_list),
          str(new_dislike_count_day),
          str(i)
         )
      cursor.execute(query,data)
      cnx.commit()


def update_day(cnx,cursor):
   all_post_list=my_search.search_post_index(include_text="inculde_all",exclude_text="",search_conditions=["for_all"])
   for i in all_post_list:
      query="select content_id,hour,hour_joined_23,day,day_joined_29,week,month_30 from post_view_count_table where content_id={}".format(i)
      cursor.execute(query)
      result=cursor.fetchone()
      new_hour_joined_23_list=result[2].split(",")
      new_view_count_day=result[3]-int(new_hour_joined_23_list[0])
      new_hour_joined_23_list.pop(0)
      new_hour_joined_23_list.append(str(result[1]))
      new_day_joined_29_list=result[4].split(",")
      new_view_count_week=result[5]-int(new_day_joined_29_list[0])
      new_view_count_month_30=result[6]-int(new_day_joined_29_list[0])
      new_day_joined_29_list.pop(0)
      new_day_joined_29_list.append(str(new_view_count_day))
      data=(
         "0",
         ",".join(new_hour_joined_23_list),
         str(new_view_count_day),
         ",".join(new_day_joined_29_list),
         str(new_view_count_week),
         str(new_view_count_month_30),
         str(i)
         )
      query="UPDATE post_view_count_table SET hour=%s,hour_joined_23=%s,day=%s,day_joined_29=%s,week=%s,month_30=%s WHERE content_id = %s;"
      cursor.execute(query,data)
      cnx.commit()
   
   for i in all_post_list:
      query="""
      select content_id,like_count_hour,like_count_hour_joined_23,like_count_day,like_count_day_joined_29,like_count_week,like_count_month_30,
      dislike_count_hour,dislike_count_hour_joined_23,dislike_count_day,dislike_count_day_joined_29,dislike_count_week,dislike_count_month_30
      from post_review_table where content_id={}""".format(i)#6#12
      cursor.execute(query)
      result=cursor.fetchone()
      new_like_count_hour_joined_23_list=result[2].split(",")
      new_like_count_day=result[3]-int(new_like_count_hour_joined_23_list[0])
      new_like_count_hour_joined_23_list.pop(0)
      new_like_count_hour_joined_23_list.append(str(result[1]))
      new_like_count_day_joined_29_list=result[4].split(",")
      new_like_count_week=result[5]-int(new_like_count_day_joined_29_list[0])
      new_like_count_month_30=result[6]-int(new_like_count_day_joined_29_list[0])
      new_like_count_day_joined_29_list.pop(0)
      new_like_count_day_joined_29_list.append(str(new_like_count_day))
      new_dislike_count_hour_joined_23_list=result[8].split(",")
      new_dislike_count_day=result[9]-int(new_dislike_count_hour_joined_23_list[0])
      new_dislike_count_hour_joined_23_list.pop(0)
      new_dislike_count_hour_joined_23_list.append(str(result[7]))
      new_dislike_count_day_joined_29_list=result[10].split(",")
      new_dislike_count_week=result[11]-int(new_dislike_count_day_joined_29_list[0])
      new_dislike_count_month_30=result[12]-int(new_dislike_count_day_joined_29_list[0])
      new_dislike_count_day_joined_29_list.pop(0)
      new_dislike_count_day_joined_29_list.append(str(new_like_count_day))
      query="""UPDATE post_review_table SET like_count_hour=%s,like_count_hour_joined_23=%s,like_count_day=%s,like_count_day_joined_29=%s,like_count_week=%s,like_count_month_30=%s,
      dislike_count_hour=%s,dislike_count_hour_joined_23=%s,dislike_count_day=%s,dislike_count_day_joined_29=%s,dislike_count_week=%s,dislike_count_month_30=%s WHERE content_id = %s;"""
      data=(
          "0",
             ",".join(new_like_count_hour_joined_23_list),
             str(new_like_count_day),
             ",".join(new_day_joined_29_list),
             str(new_like_count_week),
             str(new_like_count_month_30),
             "0",
             ",".join(new_dislike_count_hour_joined_23_list),
             str(new_dislike_count_day),
             ",".join(new_day_joined_29_list),
             str(new_dislike_count_week),
             str(new_dislike_count_month_30),
          str(i)
         )
      cursor.execute(query,data)
      cnx.commit()
   
   query="UPDATE user_view_history SET view_history_today=''"
   cursor.execute(query)
   cnx.commit()
   query="DELETE FROM user_session_table WHERE last_access_time <= NOW() - INTERVAL 1 MONTH;"
   cursor.execute(query)
   cnx.commit()

def update_periodically():
   cnx=my_functions.connect_to_database()
   cursor=cnx.cursor(buffered=True)
   query="select update_hour_count from other_values_table where id=1"
   cursor.execute(query)
   result=cursor.fetchone()
   if(result[0]%24==0):
      update_day(cnx=cnx,cursor=cursor)
      query="update other_values_table set update_hour_count=update_hour_count+1 where id=1"
      cursor.execute(query)
   else:
      update_hour(cnx=cnx,cursor=cursor)
      if(result[0]%24==23):
         query="update other_values_table set update_hour_count=0 where id=1"
      else:
         query="update other_values_table set update_hour_count=update_hour_count+1 where id=1"
      cursor.execute(query)
   cnx.commit()
   cursor.close()
   cnx.close()
      

# new=>
def start():
   scheduler = BackgroundScheduler()
   scheduler.add_job(update_periodically, 'interval', seconds=60*60)
   """   scheduler.add_job(update_day, 'cron', hour=0, minute=0)
   scheduler.add_job(update_hour, 'cron', hour=1, minute=0)
   scheduler.add_job(update_hour, 'cron', hour=2, minute=0)
   scheduler.add_job(update_hour, 'cron', hour=3, minute=0)
   scheduler.add_job(update_hour, 'cron', hour=4, minute=0)
   scheduler.add_job(update_hour, 'cron', hour=5, minute=0)
   scheduler.add_job(update_hour, 'cron', hour=6, minute=0)
   scheduler.add_job(update_hour, 'cron', hour=7, minute=0)
   scheduler.add_job(update_hour, 'cron', hour=8, minute=0)
   scheduler.add_job(update_hour, 'cron', hour=9, minute=0)
   scheduler.add_job(update_hour, 'cron', hour=10, minute=0)
   scheduler.add_job(update_hour, 'cron', hour=11, minute=0)
   scheduler.add_job(update_hour, 'cron', hour=12, minute=0)
   scheduler.add_job(update_hour, 'cron', hour=13, minute=0)
   scheduler.add_job(update_hour, 'cron', hour=14, minute=0)
   scheduler.add_job(update_hour, 'cron', hour=15, minute=0)
   scheduler.add_job(update_hour, 'cron', hour=16, minute=0)
   scheduler.add_job(update_hour, 'cron', hour=17, minute=0)
   scheduler.add_job(update_hour, 'cron', hour=18, minute=0)
   scheduler.add_job(update_hour, 'cron', hour=19, minute=0)
   scheduler.add_job(update_hour, 'cron', hour=20, minute=0)
   scheduler.add_job(update_hour, 'cron', hour=21, minute=0)
   scheduler.add_job(update_hour, 'cron', hour=22, minute=0)
   scheduler.add_job(update_hour, 'cron', hour=23, minute=0)"""
   scheduler.start()