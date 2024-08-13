var username_exclusion_pattern = />|<| |　|\u200b|&gt;|&lt;|,|\n|\r|\t/g;
var mailaddress_pattern =
  /^[a-zA-Z0-9_+-]+(.[a-zA-Z0-9_+-]+)*@([a-zA-Z0-9][a-zA-Z0-9-]*[a-zA-Z0-9]*\.)+[a-zA-Z]{2,}/;
var password_pattern =
  /^(([a-zA-Z0-9]|\!|\@|\#|\$|\%|\^|\&|\*|\(|\)|\_|\+|\-|\=|\[|\]|\{|\}|\||\;|\:|\'|\,|\.|\<|\>|\?|\/|\~|\`)+)$/;
var content_exclusion_pattern = /(<|>|\u200b|\t|\&lt|\&gt|`)+/g;
function censor_content(text) {
  let censored_text = text.replace(/</g, "＜");
  censored_text = censored_text.replace(/>/g, "＞");
  censored_text = censored_text.replace(/`/g, "‘");
  censored_text = censored_text.replace(/\&lt/g, "＆lt");
  censored_text = censored_text.replace(/\&gt/g, "＆gt");
  censored_text = censored_text.replace(content_exclusion_pattern, "");
  censored_text = censored_text.replace(/\n\r/g, "\n");
  censored_text = censored_text.replace(/\r/g, "\n");
  return censored_text;
}
function set_text_with_newline(text) {
  let split_text = text.split(/\r\n|\n/);
  let return_text = "";
  for (let i = 0; i < split_text.length; i++) {
    return_text += split_text[i] + "<br>";
  }
  return return_text;
}
function convertStringsToNumbers(array) {
  return array.map((item) => {
    const number = parseFloat(item);
    return isNaN(number) ? item : number;
  });
}
function split_less_than(text) {
  return text == "" ? [] : text.split("<");
}
var username_exclusion_pattern = />|<| |　|\u200b|&gt;|&lt;|,|\n|\r|\t/g;
var mailaddress_pattern =
  /^[a-zA-Z0-9_+-]+(.[a-zA-Z0-9_+-]+)*@([a-zA-Z0-9][a-zA-Z0-9-]*[a-zA-Z0-9]*\.)+[a-zA-Z]{2,}/;
var password_pattern =
  /^(([a-zA-Z0-9]|\!|\@|\#|\$|\%|\^|\&|\*|\(|\)|\_|\+|\-|\=|\[|\]|\{|\}|\||\;|\:|\'|\,|\.|\<|\>|\?|\/|\~|\`)+)$/;

class post_component {
  constructor(
    {
      display_delete_post_button = false,
      out_of_main_box = document.getElementById("out_of_main_box"),
      uni_post = false,
      option_category = "",
      subject_id = 0,
    } = {},
    parent_element,
    post_dict
  ) {
    this.uni_post = uni_post;
    this.content_id = Number(post_dict["content_id"]);
    this.title = post_dict["title"];
    this.content_split = post_dict["content"].split(">");
    this.image_count = Math.floor((this.content_split.length - 1) / 2);
    this.overview = post_dict["overview"];
    this.post_date = post_dict["post_date"].split(",");
    this.tags = post_dict["tags"];
    this.user_id = Number(post_dict["user_id"]);
    this.username = post_dict["username"];
    this.my_review = post_dict["my_review"];
    this.like_count = Number(post_dict["like_count"]);
    this.dislike_count = Number(post_dict["dislike_count"]);
    this.comment_count = Number(post_dict["comment_count"]);
    this.already_viewed_flag = false;
    this.content_open_flag = false;
    this.discussion_box_open_flag = false;
    this.out_of_main_box = out_of_main_box;

    this.post_box = document.createElement("div");
    this.post_box.id = `listed_post_${this.content_id}`;
    this.post_box.className = "post_display_box";
    parent_element.appendChild(this.post_box);

    this.post_box_left = document.createElement("div");
    this.post_box_left.id = `listed_post_box_left${this.content_id}`;
    this.post_box_left.className = "post_box_left";
    this.post_box.appendChild(this.post_box_left);
    this.post_box_right = document.createElement("div");
    this.post_box_right.id = `listed_post_box_right${this.content_id}`;
    this.post_box_right.className = "post_box_right";
    this.post_box.appendChild(this.post_box_right);

    this.listed_post_icon_box = document.createElement("div");
    this.listed_post_icon_box.id = `listed_post_icon_box_${this.content_id}`;
    this.listed_post_icon_box.classList.add("listed_post_icon_box");
    this.post_box_left.appendChild(this.listed_post_icon_box);
    this.listed_post_icon = document.createElement("a");
    this.listed_post_icon.id = `listed_post_icon_${this.content_id}`;
    this.listed_post_icon.classList.add("listed_post_icon");
    this.listed_post_icon.href = site_url + `user/${this.user_id}/`;
    this.listed_post_icon.innerHTML = `<img class="listed_post_icon" src="/media/user_icons/user_icon_mini_${this.user_id}.png" alt="icon">`;
    this.listed_post_icon_box.appendChild(this.listed_post_icon);

    this.listed_post_username = document.createElement("a");
    this.listed_post_username.id = `listed_post_username_${this.content_id}`;
    this.listed_post_username.classList.add("listed_post_username");
    this.listed_post_username.href = site_url + `user/${this.user_id}/`;
    this.listed_post_username.textContent = `${this.username}`;
    this.post_box_right.appendChild(this.listed_post_username);

    this.post_title = document.createElement("a");
    this.post_title.href = site_url + `post/${this.content_id}/`;
    this.post_title.id = `listed_post_title_${this.content_id}`;
    this.post_title.className = "post_title";
    this.post_title.textContent = this.title;
    this.post_box_right.appendChild(this.post_title);

    this.post_date_text = document.createElement("div");
    this.post_date_text.id = `listed_post_date${this.content_id}`;
    this.post_date_text.classList.add("listed_post_date");
    this.post_date_text.textContent = `投稿日 ${this.post_date[0]}年${this.post_date[1]}月${this.post_date[2]}日${this.post_date[3]}時${this.post_date[4]}分`;
    this.post_box_right.appendChild(this.post_date_text);

    if (this.overview != "") {
      this.post_overview_box = document.createElement("div");
      this.post_overview_box.id = `listed_post_overview_box_${this.content_id}`;
      this.post_overview_box.classList.add("post_overview_box");
      this.post_box_right.appendChild(this.post_overview_box);
      this.post_overview = document.createElement("div");
      this.post_overview.id = `listed_post_overview_${this.content_id}`;
      this.post_overview.classList.add("post_title_overview");
      this.post_overview.innerHTML = set_text_with_newline(this.overview);
      this.post_overview_box.appendChild(this.post_overview);
    }

    this.open_content_button_box = document.createElement("div");
    this.open_content_button_box.classList.add("open_content_button_box");
    this.post_box.appendChild(this.open_content_button_box);

    this.open_content_button = document.createElement("button");
    this.open_content_button.id = `open_content_button_${this.content_id}`;
    this.open_content_button.classList.add("open_content_button");
    this.open_content_button.textContent = "読む";
    this.open_content_button_box.appendChild(this.open_content_button);
    this.open_content_button.addEventListener("click", () => {
      this.open_content();
    });

    this.ai_supplement_button = document.createElement("button");
    this.ai_supplement_button.classList.add("ai_supplement_button");
    this.ai_supplement_button.textContent = "AI";
    this.ai_supplement_button.addEventListener("click", () => {
      this.open_ai_supplement();
    });
    this.open_content_button_box.appendChild(this.ai_supplement_button);

    this.post_content_box = document.createElement("div");
    this.post_content_box.id = `listed_post_content_box_${this.content_id}`;
    this.post_content_box.className = "post_content_box";
    this.post_content_box.style.display = "none";
    this.post_box.appendChild(this.post_content_box);

    this.post_content = document.createElement("div");
    this.post_content.id = `listed_post_content_${this.content_id}`;
    this.post_content.classList.add(`listed_post_content`);
    this.post_content_box.appendChild(this.post_content);

    this.content_button_box = document.createElement("div");
    this.content_button_box.id = `content_button_box${this.content_id}`;
    this.content_button_box.classList.add("content_button_box");
    if (this.uni_post) {
      this.post_box.insertBefore(
        this.content_button_box,
        this.post_content_box
      );
    } else {
      this.post_box.appendChild(this.content_button_box);
    }

    this.like_button_box = document.createElement("button");
    this.like_button_box.id = `like_button_box_${this.content_id}`;
    this.like_button_box.classList.add("like_button_box");
    this.content_button_box.appendChild(this.like_button_box);
    this.like_button_box.addEventListener("click", () => {
      this.add_review("add_like");
    });

    this.like_button = document.createElement("div");
    this.like_button.id = `like_button_${this.content_id}`;
    this.like_button.classList.add("like_button");
    this.like_button_box.appendChild(this.like_button);
    this.like_button.type = "button";
    this.like_button.title = "高評価";

    this.like_button_img = document.createElement("img");
    this.like_button_img.id = `like_button_img_${this.content_id}`;
    this.like_button_img.alt = "icon";
    this.like_button_img.classList.add("like_button");
    this.like_button.appendChild(this.like_button_img);
    if (this.my_review == "liked") {
      this.like_button_img.src = "/media/like_button_liked.svg";
    } else {
      this.like_button_img.src = "/media/like_button_normal.svg";
    }

    this.like_count_text = document.createElement("div");
    this.like_count_text.id = `like_count_${this.content_id}`;
    this.like_count_text.classList.add("review_count");
    this.like_count_text.textContent = String(this.like_count);
    this.like_button_box.appendChild(this.like_count_text);

    this.dislike_button_box = document.createElement("button");
    this.dislike_button_box.id = `dislike_button_box_${this.content_id}`;
    this.dislike_button_box.classList.add("dislike_button_box");
    this.content_button_box.appendChild(this.dislike_button_box);
    this.dislike_button_box.addEventListener("click", () => {
      this.add_review("add_dislike");
    });

    this.dislike_button = document.createElement("div");
    this.dislike_button.id = `dislike_button_${this.content_id}`;
    this.dislike_button.classList.add("dislike_button");
    this.dislike_button_box.appendChild(this.dislike_button);
    this.dislike_button.type = "button";
    this.dislike_button.title = "低評価";

    this.dislike_button_img = document.createElement("img");
    this.dislike_button_img.id = `dislike_button_img_${this.content_id}`;
    this.dislike_button_img.alt = "icon";
    this.dislike_button_img.classList.add("dislike_button");
    this.dislike_button.appendChild(this.dislike_button_img);
    if (this.my_review == "disliked") {
      this.dislike_button_img.src = "/media/dislike_button_disliked.svg";
    } else {
      this.dislike_button_img.src = "/media/dislike_button_normal.svg";
    }

    this.dislike_count_text = document.createElement("div");
    this.dislike_count_text.id = `dislike_count_${this.content_id}`;
    this.dislike_count_text.classList.add("review_count");
    this.dislike_count_text.textContent = String(this.dislike_count);
    this.dislike_button_box.appendChild(this.dislike_count_text);

    this.open_comment_button = document.createElement("button");
    this.open_comment_button.id = `open_comment_button_${this.content_id}`;
    this.open_comment_button.classList.add("open_comment_button");
    this.open_comment_button.textContent = `コメント${
      this.comment_count == 0 ? "" : `(${this.comment_count})`
    }`;
    this.open_comment_button.type = "button";
    this.open_comment_button.title = "コメントを開く";
    this.open_comment_button.addEventListener("click", () => {
      this.open_comment();
    });
    this.content_button_box.appendChild(this.open_comment_button);

    if (display_delete_post_button) {
      this.delete_button = document.createElement("button");
      this.delete_button.id = `delete_button_${this.content_id}`;
      this.delete_button.classList.add("delete_post_button");
      this.delete_button.textContent = "削除";
      this.delete_button.title = "削除";
      this.delete_count = 0;
      this.delete_button.addEventListener("click", () => {
        if (this.delete_count <= 4) {
          alert(`後${5 - this.delete_count}回押したら削除されます`);
          this.delete_count++;
        } else {
          let request_json_data = {
            content_id: String(this.content_id),
            session_id_1: session_id_1,
            session_id_2: session_id_2,
          };
          fetch(site_url + "delete_post_process/", {
            method: "post",
            headers: {
              "Content-Type": "application/json", //JSON形式のデータのヘッダー
              "X-CSRFToken": csrftoken,
            },
            body: JSON.stringify(request_json_data),
          })
            .then((response) => response.json())
            .then((data) => {
              if (data["result"] == "success") {
                alert("削除に成功しました");
                window.location.reload(true);
              }
            });
        }
      });
      this.content_button_box.appendChild(this.delete_button);
    } else {
      this.report_button = document.createElement("button");
      this.report_button.id = `report_button_${this.content_id}`;
      this.report_button.classList.add("report_button");
      this.report_button.textContent = "通報";
      this.report_button.title = "通報";
      this.report_button.addEventListener("click", () => {
        document.getElementById("report_subject_category_base").value = "post";
        document.getElementById("report_subject_id_base").value = String(
          this.content_id
        );
        document.getElementById("report_form_base").submit();
      });
      this.content_button_box.appendChild(this.report_button);
    }
    if (this.tags != "") {
      this.post_tags_box = document.createElement("div");
      this.post_tags_box.id = `listed_post_tags_box_${this.content_id}`;
      this.post_tags_box.classList.add("post_tags_box");
      this.post_tags_box.textContent = "";
      if (uni_post) {
        this.post_box.insertBefore(this.post_tags_box, this.post_content_box);
      } else {
        this.post_box.appendChild(this.post_tags_box);
      }
      this.displayed_tag = this.tags.split(",");
      this.post_tag_box_list = [];
      this.post_tag_list = [];
      for (let j = 0; j < this.displayed_tag.length; j++) {
        this.post_tag_box_list[j] = document.createElement("div");
        this.post_tag_box_list[j].id = `post_tag_box_${this.content_id}_${
          j + 1
        }`;
        this.post_tag_box_list[j].classList.add("post_tag_box");
        this.post_tags_box.appendChild(this.post_tag_box_list[j]);
        this.post_tag_list[j] = document.createElement("a");
        this.post_tag_list[j].href =
          site_url +
          `search/?page_number=1&search_subjects_joined=tags&search_words=${this.displayed_tag[j]}&search_words_exclude=&post_order=new_post`;
        this.post_tag_list[j].id = `post_tag_${this.content_id}_${j + 1}`;
        this.post_tag_list[j].classList.add("post_tag");
        this.post_tag_list[j].textContent = "# " + this.displayed_tag[j];
        this.post_tag_box_list[j].appendChild(this.post_tag_list[j]);
      }
    }
    if (this.uni_post) {
      this.post_box.style.marginTop = "15px";
      this.open_content_button.style.display = "none";
      this.ai_supplement_button.style.width = "100%";
      this.post_content.style.borderTopWidth = "0px";
      this.open_content();
      if(option_category == "open_ai_supplement_assist"){

      }
      else if(option_category == "open_ai_supplement_antonym"){

      }
      else if (option_category != "") {
        if(this,this.comment_count==0){
          this.open_ai_supplement("antonym")
        }
        else{
          this.open_comment().then(() => {
            let open_comment_id = 0;
            if (option_category == "latest_parent_comment") {
              open_comment_id =
                this.parent_comment_list[this.parent_comment_list.length - 1]
                  .comment_id;
            } else if (option_category == "latest_child_comment") {
              for (let i = 0; i < this.parent_comment_list.length; i++) {
                if (
                  this.parent_comment_list[i].comment_id == Number(subject_id)
                ) {
                  open_comment_id =
                    this.parent_comment_list[i].child_comment_list[
                      this.parent_comment_list[i].child_comment_list.length - 1
                    ].comment_id;
                  i = this.parent_comment_list.length;
                }
              }
            } else if ("just_open_comment") {
            }
            this.move_to_comment(open_comment_id);
          });
        }
      }
    }
  }
  post_comment(parent_comment_id = 0, comment_content) {
    if (my_user_id <= 0) {
      location.href = site_url + `signup/`;
    }
    if (comment_content != "") {
      let request_json_data = {
        session_id_1: session_id_1,
        session_id_2: session_id_2,
        content_id: String(this.content_id),
        comment_content: comment_content,
        parent_comment_id: String(parent_comment_id),
      };
      return fetch(site_url + "add_comment/", {
        method: "post",
        headers: {
          "Content-Type": "application/json", //JSON形式のデータのヘッダー
          "X-CSRFToken": csrftoken,
        },
        body: JSON.stringify(request_json_data),
      })
        .then((response) => response.json())
        .then((data) => {
          return new Promise((resolve, reject) => {
            // 非同期処理が成功した場合
            resolve({
              result: data["result"],
              comment_id: Number(data["comment_id"]),
            });
            // 非同期処理が失敗した場合
            // reject('失敗した理由');
          });
        });
    } else {
      alert("内容がないよう");
    }
  }
  async delete_comment(comment_id) {
    let request_json_data = {
      session_id_1: session_id_1,
      session_id_2: session_id_2,
      comment_id: comment_id,
    };
    return fetch(site_url + "delete_comment/", {
      method: "post",
      headers: {
        "Content-Type": "application/json", //JSON形式のデータのヘッダー
        "X-CSRFToken": csrftoken,
      },
      body: JSON.stringify(request_json_data),
    })
      .then((response) => response.json())
      .then((data) => {
        return new Promise((resolve, reject) => {
          // 非同期処理が成功した場合
          resolve({
            result: data["result"],
          });
          // 非同期処理が失敗した場合
          // reject('失敗した理由');
        });
      });
  }
  static parent_comment = class {
    static child_comment = class {
      constructor(parent_post, parent_comment_box, comment_datas) {
        const comment_user_id = Number(comment_datas["user_id"]);
        const comment_username = comment_datas["username"];
        const comment_content = comment_datas["content"];
        this.parent_post = parent_post;
        this.comment_id = Number(comment_datas["comment_id"]);
        this.comment_box = document.createElement("div");
        this.comment_box.classList.add("comment_box");
        parent_comment_box.appendChild(this.comment_box);

        let comment_user_box = document.createElement("div");
        comment_user_box.classList.add("comment_user_box");
        this.comment_box.appendChild(comment_user_box);

        let comment_user_icon = document.createElement("a");
        comment_user_icon.classList.add("comment_user_icon");
        comment_user_icon.innerHTML = `<img class="comment_user_icon" src="/media/user_icons/user_icon_mini_${comment_user_id}.png" alt="icon">`;
        comment_user_box.appendChild(comment_user_icon);

        let comment_username_text_link = document.createElement("a");
        comment_username_text_link.classList.add("comment_username");
        comment_username_text_link.href = site_url + `user/${comment_user_id}/`;
        comment_username_text_link.textContent = comment_username;
        comment_user_box.appendChild(comment_username_text_link);

        let report_comment_button_box = document.createElement("div");
        report_comment_button_box.id = `report_comment_button_box_${this.comment_id}`;
        report_comment_button_box.classList.add("report_comment_button_box");
        comment_user_box.appendChild(report_comment_button_box);

        if (comment_user_id == my_user_id) {
          let delete_comment_button = document.createElement("button");
          delete_comment_button.id = `delete_comment_button_${this.comment_id}`;
          delete_comment_button.classList.add("delete_comment_button");
          delete_comment_button.textContent = "削除";
          this.delete_count = 0;
          const max_delete_count = 3;
          delete_comment_button.addEventListener("click", () => {
            if (this.delete_count == 3) {
              this.parent_post.delete_comment(this.comment_id).then((data) => {
                if (data["result"] == "success") {
                  this.comment_box.style.display = "none";
                }
              });
            } else {
              alert(
                `後${
                  max_delete_count - this.delete_count
                }回押したら削除されます`
              );
              this.delete_count++;
            }
          });
          report_comment_button_box.appendChild(delete_comment_button);
        } else {
          let report_comment_button = document.createElement("button");
          report_comment_button.id = `report_comment_button_${this.comment_id}`;
          report_comment_button.classList.add("report_comment_button");
          report_comment_button.textContent = "通報";
          report_comment_button.addEventListener("click", () => {
            document.getElementById("report_subject_category_base").value =
              "comment";
            document.getElementById("report_subject_id_base").value = String(
              this.comment_id
            );
            document.getElementById("report_form_base").submit();
          });
          report_comment_button_box.appendChild(report_comment_button);
        }

        let comment_content_div = document.createElement("div");
        comment_content_div.classList.add("comment_content");
        comment_content_div.innerHTML = set_text_with_newline(comment_content);
        this.comment_box.appendChild(comment_content_div);
      }
    };
    constructor(content_id, comment_datas, parent_post) {
      this.content_id = Number(content_id);
      this.comment_id = Number(comment_datas["comment_id"]);
      this.child_comment_open_flag = false;
      this.child_comment_list = [];
      this.parent_post = parent_post;
      const comment_user_id = Number(comment_datas["user_id"]);
      const comment_username = comment_datas["username"];
      this.child_comment_data_list = comment_datas["child_comment_data_list"];
      const comment_content = comment_datas["content"];
      this.comment_box = document.createElement("div");
      this.comment_box.classList.add("comment_box");
      this.comment_box.id = `comment_box_${this.comment_id}`;
      this.parent_post.discussion_box.appendChild(this.comment_box);
      let comment_user_box = document.createElement("div");
      comment_user_box.id = `comment_user_box_${this.comment_id}`;
      comment_user_box.classList.add("comment_user_box");
      this.comment_box.appendChild(comment_user_box);

      let comment_user_icon = document.createElement("a");
      comment_user_icon.id = `comment_user_icon_${this.comment_id}`;
      comment_user_icon.classList.add("comment_user_icon");
      comment_user_icon.innerHTML = `<img class="comment_user_icon" src="/media/user_icons/user_icon_mini_${comment_user_id}.png" alt="icon">`;
      comment_user_box.appendChild(comment_user_icon);

      let comment_username_text_link = document.createElement("a");
      comment_username_text_link.id = `comment_username_${this.comment_id}`;
      comment_username_text_link.classList.add("comment_username");
      comment_username_text_link.href = site_url + `user/${comment_user_id}/`;
      comment_username_text_link.textContent = comment_username;
      comment_user_box.appendChild(comment_username_text_link);

      if (comment_user_id == my_user_id) {
        let delete_comment_button = document.createElement("button");
        delete_comment_button.id = `delete_comment_button_${this.comment_id}`;
        delete_comment_button.classList.add("delete_comment_button");
        delete_comment_button.textContent = "削除";
        this.delete_count = 0;
        const max_delete_count = 3;
        delete_comment_button.addEventListener("click", () => {
          if (this.delete_count == 3) {
            this.parent_post.delete_comment(this.comment_id).then((data) => {
              if (data["result"] == "success") {
                this.comment_box.style.display = "none";
              }
            });
          } else {
            alert(
              `後${max_delete_count - this.delete_count}回押したら削除されます`
            );
            this.delete_count++;
          }
        });
        comment_user_box.appendChild(delete_comment_button);
      } else {
        let report_comment_button = document.createElement("button");
        report_comment_button.id = `report_comment_button_${this.comment_id}`;
        report_comment_button.classList.add("report_comment_button");
        report_comment_button.textContent = "通報";
        report_comment_button.addEventListener("click", () => {
          document.getElementById("report_subject_category_base").value =
            "comment";
          document.getElementById("report_subject_id_base").value = String(
            this.comment_id
          );
          document.getElementById("report_form_base").submit();
        });
        comment_user_box.appendChild(report_comment_button);
      }

      let comment_content_div = document.createElement("div");
      comment_content_div.id = `comment_content_${this.comment_id}`;
      comment_content_div.classList.add("comment_content");
      comment_content_div.innerHTML = set_text_with_newline(comment_content);
      this.comment_box.appendChild(comment_content_div);

      this.open_child_comment_button = document.createElement("button");
      this.open_child_comment_button.type = "button";
      this.open_child_comment_button.textContent = "返信を見る";
      this.open_child_comment_button.id = `open_child_comment_button_${this.comment_id}`;
      this.open_child_comment_button.classList.add("open_child_comment_button");
      this.open_child_comment_button.addEventListener("click", () => {
        this.open_child_comment();
      });
      this.comment_box.appendChild(this.open_child_comment_button);

      this.child_comment_box = document.createElement("div");
      this.child_comment_box.id = `child_comment_box_${this.comment_id}`;
      this.child_comment_box.classList.add("child_comment_box");
      this.child_comment_box.classList.add("hidden");
      this.comment_box.appendChild(this.child_comment_box);
      let add_child_comment_box = document.createElement("div");
      this.child_comment_box.appendChild(add_child_comment_box);
      add_child_comment_box.id = `add_child_comment_box_${this.comment_id}`;
      add_child_comment_box.classList.add("add_child_comment_box");

      let add_child_comment_textarea_box = document.createElement("div");
      add_child_comment_textarea_box.id = `add_child_comment_textarea_box_${this.comment_id}`;
      add_child_comment_textarea_box.classList.add(
        "add_child_comment_textarea_box"
      );
      add_child_comment_box.appendChild(add_child_comment_textarea_box);

      let add_child_comment_textarea_dummy = document.createElement("div");
      add_child_comment_textarea_dummy.id = `add_child_comment_textarea_dummy_${this.comment_id}`;
      add_child_comment_textarea_dummy.classList.add(
        "add_child_comment_textarea_dummy"
      );
      add_child_comment_textarea_box.appendChild(
        add_child_comment_textarea_dummy
      );
      add_child_comment_textarea_dummy.style.minHeight = "65px";

      let add_child_comment_textarea = document.createElement("textarea");
      add_child_comment_textarea.id = `add_child_comment_textarea_${this.comment_id}`;
      add_child_comment_textarea.classList.add("add_child_comment_textarea");
      add_child_comment_textarea_box.appendChild(add_child_comment_textarea);
      add_child_comment_textarea.placeholder = "返信を入力";
      add_child_comment_textarea.addEventListener("input", () => {
        add_child_comment_textarea.value = censor_content(
          add_child_comment_textarea.value
        );
        if (add_child_comment_textarea.value.length >= 501) {
          add_child_comment_textarea.value.slice(0, 500);
        }
        add_child_comment_textarea_dummy.textContent =
          add_child_comment_textarea.value + "\u200b";
      });

      let add_child_comment_button = document.createElement("button");
      add_child_comment_button.id = `add_child_comment_button_${this.comment_id}`;
      add_child_comment_button.classList.add("add_child_comment_button");
      add_child_comment_button.textContent = "投稿";
      add_child_comment_button.addEventListener("click", () => {
        this.parent_post
          .post_comment(this.comment_id, add_child_comment_textarea.value)
          .then((data) => {
            if (data["result"] == "success") {
              this.child_comment_data_list[
                this.child_comment_data_list.length
              ] = {
                comment_id: Number(data["comment_id"]),
                content: add_child_comment_textarea.value,
                user_id: my_user_id,
                username: username,
              };
              this.child_comment_list[this.child_comment_list.length] =
                new post_component.parent_comment.child_comment(
                  this.parent_post,
                  this.child_comment_box,
                  {
                    comment_id: Number(data["comment_id"]),
                    user_id: my_user_id,
                    username: username,
                    content: add_child_comment_textarea.value,
                  }
                );
              add_child_comment_textarea.value = "";
              this.parent_post.move_to_comment(Number(data["comment_id"]));
            }
          });
      });
      add_child_comment_box.appendChild(add_child_comment_button);
      if (this.child_comment_data_list.length >= 1) {
        for (let i = 0; i < this.child_comment_data_list.length; i++) {
          this.child_comment_list[i] =
            new post_component.parent_comment.child_comment(
              this.parent_post,
              this.child_comment_box,
              this.child_comment_data_list[i]
            );
        }
      }
    }

    open_child_comment() {
      if (this.child_comment_open_flag == false) {
        this.child_comment_box.classList.remove("hidden");
        this.open_child_comment_button.textContent = "返信を閉じる";
        this.child_comment_open_flag = true;
      } else if (this.child_comment_open_flag == true) {
        this.child_comment_box.classList.add("hidden");
        this.open_child_comment_button.textContent = "返信を見る";
        this.child_comment_open_flag = false;
      }
    }
  };
  close_comment() {
    this.out_of_main_box.style.display = "none";
    this.discussion_box_open_flag = false;
  }
  open_comment() {
    return new Promise((resolve, reject) => {
      if (this.discussion_box_open_flag == false) {
        this.out_of_main_box.innerHTML = ""; ///一度リセット
        this.gray_out = document.createElement("div");
        this.gray_out.classList.add("gray_out_out_of_main");
        this.out_of_main_box.appendChild(this.gray_out);
        this.gray_out.addEventListener("click", () => {
          this.close_comment();
        });
        let request_json_data = {
          content_id: String(this.content_id),
        };
        fetch(site_url + "get_discussion_data/", {
          method: "post",
          headers: {
            "Content-Type": "application/json", //JSON形式のデータのヘッダー
            "X-CSRFToken": csrftoken,
          },
          body: JSON.stringify(request_json_data),
        })
          .then((response) => response.json())
          .then((data) => {
            if (data["result"] == "success") {
              this.out_of_main_box.style.display = "block";

              this.discussion_box_box = document.createElement("div");
              this.discussion_box_box.className = "discussion_box_box";
              this.out_of_main_box.appendChild(this.discussion_box_box);
              this.discussion_box = document.createElement("div");
              this.discussion_box.style.display = "block";
              this.discussion_box.id = "discussion_box";
              this.discussion_box.classList.add("discussion_box");
              this.discussion_box_opened = true;
              this.discussion_box_box.appendChild(this.discussion_box);
              this.add_comment_box = document.createElement("div");
              this.add_comment_box.id = "add_comment_box";
              this.add_comment_box.classList.add("add_comment_box");
              this.discussion_box.appendChild(this.add_comment_box);

              this.add_comment_textarea_box = document.createElement("div");
              this.add_comment_textarea_box.id = "add_comment_textarea_box";
              this.add_comment_textarea_box.classList.add(
                "add_comment_textarea_box"
              );
              this.add_comment_box.appendChild(this.add_comment_textarea_box);

              this.add_comment_textarea_dummy = document.createElement("div");
              this.add_comment_textarea_dummy.id = "add_comment_textarea_dummy";
              this.add_comment_textarea_dummy.classList.add(
                "add_child_comment_textarea_dummy"
              );
              this.add_comment_textarea_dummy.ariaHidden = "true";
              this.add_comment_textarea_dummy.style.minHeight = "100px";
              this.add_comment_textarea_box.appendChild(
                this.add_comment_textarea_dummy
              );

              this.add_comment_textarea = document.createElement("textarea");
              this.add_comment_textarea.id = "add_comment_textarea";
              this.add_comment_textarea.classList.add("add_comment_textarea");
              this.add_comment_textarea.title = "abc";
              this.add_comment_textarea.placeholder = "コメントを書く";
              this.add_comment_textarea.addEventListener("input", () => {
                this.add_comment_textarea.value = censor_content(
                  this.add_comment_textarea.value
                );
                if (this.add_comment_textarea.value.length >= 501) {
                  this.add_comment_textarea.value.slice(0, 500);
                }
                this.add_comment_textarea_dummy.textContent =
                  this.add_comment_textarea.value + "\u200b";
              });
              this.add_comment_textarea_box.appendChild(
                this.add_comment_textarea
              );
              this.post_comment_button = document.createElement("button");
              this.post_comment_button.id = "post_comment_button";
              this.post_comment_button.classList.add("post_comment_button");
              this.post_comment_button.textContent = "投稿";

              this.post_comment_button.addEventListener("click", () => {
                this.post_comment(0, this.add_comment_textarea.value).then(
                  (data) => {
                    if (data["result"] == "success") {
                      if (this.amount_of_displayd_comment == 0) {
                        this.comment_id_list = [];
                        this.parent_comment_list = [];
                        this.child_comment_open_flag_list = [];
                      }
                      this.comment_id_list[this.comment_id_list.length] =
                        String(data["comment_id"]);
                      this.amount_of_displayd_comment += 1;
                      this.child_comment_open_flag_list[
                        this.child_comment_open_flag_list.length
                      ] = false;
                      this.parent_comment_list.push(
                        new post_component.parent_comment(
                          this.content_id,
                          {
                            comment_id: Number(data["comment_id"]),
                            content: this.add_comment_textarea.value,
                            user_id: Number(my_user_id),
                            username: username,
                            child_comment_data_list: [],
                          },
                          this
                        )
                      );
                      this.add_comment_textarea.value = "";
                      this.parent_comment_list[
                        this.parent_comment_list.length - 1
                      ].comment_box.scrollIntoView({
                        behavior: "smooth",
                        block: "center",
                      });
                    }
                  }
                );
              });

              this.add_comment_box.appendChild(this.post_comment_button);
              this.parent_comment_list = [];
              this.amount_of_displayd_comment = Number(
                data["amount_of_displayd_comment"]
              );
              if (this.amount_of_displayd_comment >= 1) {
                this.comment_id_list = convertStringsToNumbers(
                  split_less_than(data["comment_id_combined"])
                );
                this.comment_content_list = split_less_than(
                  data["comment_content_combined"]
                );
                this.parent_comment_id_list = convertStringsToNumbers(
                  split_less_than(data["parent_comment_id_combined"])
                );
                this.comment_user_id_list = convertStringsToNumbers(
                  split_less_than(data["comment_user_id_combined"])
                );
                this.comment_username_list = split_less_than(
                  data["comment_username_combined"]
                );
                this.comment_date_list = split_less_than(
                  data["comment_date_combined"]
                );
                this.child_comment_open_flag_list = Array(
                  this.comment_id_list.length
                ).fill(false);
                this.parent_comment_data_list = [];
                this.comment_id_to_index_dict = {};
                for (let i = 0; i < this.amount_of_displayd_comment; i++) {
                  if (Number(this.parent_comment_id_list[i]) == 0) {
                    this.comment_id_to_index_dict[
                      String(this.comment_id_list[i])
                    ] = this.parent_comment_data_list.length;
                    this.parent_comment_data_list[
                      this.parent_comment_data_list.length
                    ] = {
                      comment_id: Number(this.comment_id_list[i]),
                      content: this.comment_content_list[i],
                      user_id: Number(this.comment_user_id_list[i]),
                      username: this.comment_username_list[i],
                      child_comment_data_list: [],
                    };
                  } else {
                    this.parent_comment_data_list[
                      this.comment_id_to_index_dict[
                        String(this.parent_comment_id_list[i])
                      ]
                    ]["child_comment_data_list"].push({
                      comment_id: Number(this.comment_id_list[i]),
                      content: this.comment_content_list[i],
                      user_id: Number(this.comment_user_id_list[i]),
                      username: this.comment_username_list[i],
                    });
                  }
                }
                for (let i = 0; i < this.parent_comment_data_list.length; i++) {
                  this.parent_comment_list[i] =
                    new post_component.parent_comment(
                      this.content_id,
                      this.parent_comment_data_list[i],
                      this
                    );
                }
              } else {
                let nocomment_text_div = document.createElement("div");
                nocomment_text_div.textContent = "まだコメントがありません";
                nocomment_text_div.classList.add("no_comment_text");
                this.discussion_box.appendChild(nocomment_text_div);
              }
              resolve({});
            } else {
              alert("エラー");
            }

            this.close_discussion_box_button = document.createElement("button");
            this.close_discussion_box_button.classList.add(
              "Close_out_of_main_button"
            );
            this.close_discussion_box_button.textContent = "閉じる";
            this.close_discussion_box_button.addEventListener("click", () => {
              this.close_comment();
            });
            this.discussion_box_box.appendChild(
              this.close_discussion_box_button
            );
          });
      } else {
        this.close_comment();
      }
    });
  }
  open_ai_supplement(option = "antonym") {
    return new Promise((resolve, reject) => {
      if (this.discussion_box_open_flag == false) {
        this.supplement_option = option;
        this.out_of_main_box.innerHTML = ""; ///一度リセット
        this.gray_out = document.createElement("div");
        this.gray_out.classList.add("gray_out_out_of_main");
        this.out_of_main_box.appendChild(this.gray_out);
        this.gray_out.addEventListener("click", () => {
          this.close_comment();
        });
        this.out_of_main_box.style.display = "block";

        this.discussion_box_box = document.createElement("div");
        this.discussion_box_box.className = "discussion_box_box";
        this.out_of_main_box.appendChild(this.discussion_box_box);
        this.discussion_box = document.createElement("div");
        this.discussion_box.style.display = "block";
        this.discussion_box.id = "discussion_box";
        this.discussion_box.classList.add("discussion_box");
        this.discussion_box_opened = true;
        this.discussion_box_box.appendChild(this.discussion_box);
        this.ai_option_select_button_box = document.createElement("div");
        this.ai_option_select_button_box.classList.add(
          "ai_option_select_button_box"
        );
        this.discussion_box.appendChild(this.ai_option_select_button_box);
        this.ai_option_select_button_assist = document.createElement("button");
        this.ai_option_select_button_assist.className =
          option == "assist"
            ? "ai_option_select_button_selected"
            : "ai_option_select_button";
        this.ai_option_select_button_assist.textContent = "アドバイス";
        this.ai_option_select_button_assist.addEventListener("click", () => {
          this.open_ai_supplement("assist");
        });
        this.ai_option_select_button_box.appendChild(
          this.ai_option_select_button_assist
        );

        this.ai_option_select_button_antonym = document.createElement("button");
        this.ai_option_select_button_antonym.className =
          option == "antonym"
            ? "ai_option_select_button_selected"
            : "ai_option_select_button";
        this.ai_option_select_button_antonym.textContent = "対義語";
        this.ai_option_select_button_antonym.addEventListener("click", () => {
          this.open_ai_supplement("antonym");
        });
        this.ai_option_select_button_box.appendChild(
          this.ai_option_select_button_antonym
        );
        this.close_discussion_box_button = document.createElement("button");
        this.close_discussion_box_button.classList.add(
          "Close_out_of_main_button"
        );
        this.close_discussion_box_button.textContent = "閉じる";
        this.close_discussion_box_button.addEventListener("click", () => {
          this.close_comment();
        });
        this.discussion_box_box.appendChild(this.close_discussion_box_button);
        
        let loading_window = document.createElement("div");
        loading_window.className = "ai_supplement_loading_box";
        loading_window.textContent = "読み込み中";
        this.discussion_box.appendChild(loading_window);
        let dotCount = 0;
        const maxDots = 3; // 最大のドットの数
        const interval = 300; // 更新間隔（ミリ秒）
        let loadingInterval
        setTimeout(function () {
          if (loading_window) {
            loadingInterval= setInterval(() => {
              // ドットの数を増やし、最大数に達したら0に戻す
              dotCount = (dotCount + 1) % (maxDots + 1);
              if (loading_window) {
                loading_window.innerText =
                  "作成中" + "・".repeat(dotCount);
              }
              // 表示を更新
            }, interval);
          }
        }, 500); // 500ミリ秒（0.5秒）
        let request_json_data = {
          content_id: String(this.content_id),
          option: option,
        };
        fetch(site_url + "get_ai_supplement/", {
          method: "post",
          headers: {
            "Content-Type": "application/json", //JSON形式のデータのヘッダー
            "X-CSRFToken": csrftoken,
          },
          body: JSON.stringify(request_json_data),
        })
          .then((response) => response.json())
          .then((data) => {
            if (data["result"] == "success") {
              if (this.supplement_option == option) {
                loading_window.remove();
                loading_window = null;
                clearInterval(loadingInterval);
                let ai_supplement_text = document.createElement("div");
                ai_supplement_text.classList.add("ai_supplement_text");
                ai_supplement_text.textContent = data["supplement"];
                this.discussion_box.appendChild(ai_supplement_text);
              }
            } else {
              alert("エラー");
            }
          });
      } else {
        this.close_comment();
      }
    });
  }

  move_to_comment(comment_id) {
    if (this.discussion_box_open_flag == false) {
      for (let i = 0; i < this.parent_comment_list.length; i++) {
        if (this.parent_comment_list[i].comment_id == Number(comment_id)) {
          this.parent_comment_list[i].comment_box.scrollIntoView({
            behavior: "smooth",
            block: "center",
          });
          i = this.parent_comment_list.length; //後にする
        } else {
          for (
            let j = 0;
            j < this.parent_comment_list[i].child_comment_list.length;
            j++
          ) {
            if (
              this.parent_comment_list[i].child_comment_list[j].comment_id ==
              comment_id
            ) {
              if (
                this.parent_comment_list[i].child_comment_open_flag == false
              ) {
                this.parent_comment_list[i].open_child_comment();
              }

              this.parent_comment_list[i].child_comment_list[
                j
              ].comment_box.scrollIntoView({
                behavior: "smooth",
                block: "center",
              });
              j = this.parent_comment_list[i].child_comment_list.length; //後にする
            }
          }
          i = this.parent_comment_list.length;
        }
      }
    }
  }

  open_content() {
    if (this.content_open_flag == false) {
      this.post_content_box.style.display = "block";
      this.open_content_button.textContent = "閉じる";
      this.content_open_flag = true;
      if (this.already_viewed_flag == false) {
        this.already_viewed_flag = true;
        this.post_content.innerHTML = "";
        for (let i = 0; i < this.image_count; i++) {
          this.post_content.innerHTML += set_text_with_newline(
            this.content_split[2 * i]
          );
          let listed_post_image = document.createElement("img");
          listed_post_image.classList.add("listed_post_image");
          listed_post_image.src = `/media/content_image/${this.content_id}/${
            this.content_split[2 * i + 1]
          }`;
          listed_post_image.alt = `画像${i + 1}`;
          if (this.content_id == this.image_count) {
            listed_post_image.addEventListener("load", () => {
              if (
                this.post_content_box.offsetHeight >=
                document.documentElement.clientHeight / 2
              ) {
                if (this.uni_post == false) {
                  this.top_content_close_button_box =
                    document.createElement("div");
                  this.top_content_close_button_box.classList.add(
                    "open_content_button_box"
                  );
                  this.top_content_close_button_box.style.width = "100%";

                  this.top_content_close_button =
                    document.createElement("button");
                  this.top_content_close_button.id = `top_content_close_button_${this.content_id}`;
                  this.top_content_close_button.classList.add(
                    "open_content_button"
                  );
                  this.top_content_close_button.textContent = "閉じる";
                  this.top_content_close_button.addEventListener(
                    "click",
                    () => {
                      this.open_content();
                    }
                  );
                  this.top_content_close_button_box.appendChild(
                    this.top_content_close_button
                  );
                  this.post_content_box.insertBefore(
                    this.top_content_close_button_box,
                    this.post_content
                  );
                }
              }
            });
          }
          this.post_content.appendChild(listed_post_image);
        }
        this.post_content.innerHTML += set_text_with_newline(
          this.content_split[2 * this.image_count]
        );
        if (my_user_id >= 1) {
          let call_by_view_request = new XMLHttpRequest();
          call_by_view_request.open(
            "POST",
            site_url + "view_count_doubleplus/",
            true
          );
          call_by_view_request.setRequestHeader(
            "Content-Type",
            "application/json"
          );
          call_by_view_request.setRequestHeader("X-CSRFToken", csrftoken);
          let request_json_data = {
            content_id: String(this.content_id),
            user_id: String(my_user_id),
            session_id_1: session_id_1,
            session_id_2: session_id_2,
          };
          call_by_view_request.send(JSON.stringify(request_json_data));
        }
      }
    } else {
      this.post_content_box.style.display = "none";
      this.open_content_button.textContent = "読む";
      this.content_open_flag = false;
    }
  }

  add_review(change____) {
    if (my_user_id >= 1) {
      let data = {
        change: change____,
        user_id: String(my_user_id),
        content_id: String(this.content_id),
        session_id_1: session_id_1,
        session_id_2: session_id_2,
      };
      fetch(site_url + "review_post/", {
        method: "post",
        headers: {
          "Content-Type": "application/json", //JSON形式のデータのヘッダー
          "X-CSRFToken": csrftoken,
        },
        body: JSON.stringify(data),
      })
        .then((response) => response.json())
        .then((data) => {
          if (data["result"] == "success") {
            if (data["like"] == "added") {
              this.like_button_img.src = "/media/like_button_liked.svg";
              this.like_count++;
              this.like_count_text.textContent = String(this.like_count);
            } else if (data["like"] == "removed") {
              this.like_button_img.src = "/media/like_button_normal.svg";
              this.like_count--;
              this.like_count_text.textContent = String(this.like_count);
            }
            if (data["dislike"] == "added") {
              this.dislike_button_img.src =
                "/media/dislike_button_disliked.svg";
              this.dislike_count++;
              this.dislike_count_text.textContent = String(this.dislike_count);
            } else if (data["dislike"] == "removed") {
              this.dislike_button_img.src = "/media/dislike_button_normal.svg";
              this.dislike_count--;
              this.dislike_count_text.textContent = String(this.dislike_count);
            }
          } else if (data["result"] == "failed_error") {
            alert(
              "エラー\n\nエラーコード:旅行は絶対平日にするべき\n\nページを読み込み直してもこのメッセージが出る場合はエラーコードと共に運営に問い合わせてください"
            );
          }
        })
        .catch((error) => {
          console.log(error);
          alert(
            "通信エラー\n\nエラーコード:スマホは小型化よりも高耐久化して欲しい\n\nページを読み込み直してもこのメッセージが出る場合はエラーコードと共に運営に問い合わせてください"
          );
        });
    } else {
      location.href = site_url + `signup/`;
    }
  }

  relocation_page_box() {
    main_middle.style.height = `100%`;
    main_middle.style.height = `${document.documentElement.scrollHeight}px`;
  }
}
let post_data_loading_flag = false;
const fetch_post = ({
  url,
  box = document.getElementById("main_middle"),
  display_delete_post_button = false,
  out_of_main_box = document.getElementById("out_of_main_box"),
  uni_post = false,
  option_category = "",
  subject_id = 0,
  extra_request_data = {},
}) => {
  let request_json_data = {
    session_id_1: session_id_1,
    session_id_2: session_id_2,
  };
  request_json_data = Object.assign(request_json_data, extra_request_data);
  if (post_data_loading_flag == false) {
    //post_data_loading_flag=trueサーバーに余裕があるうちは無効
    fetch(url, {
      method: "post",
      headers: {
        "Content-Type": "application/json", //JSON形式のデータのヘッダー
        "X-CSRFToken": csrftoken,
      },
      body: JSON.stringify(request_json_data),
    })
      .then((response) => response.json())
      .then((data) => {
        post_data_loading_flag = false;
        var displayed_post_number = Number(data["amount_of_displayed_post"]);
        if (displayed_post_number <= 0) {
          box.innerHTML = "";
        } else if (displayed_post_number >= 1) {
          let page_number = Number(data[`page_number`]);
          let total_page_number = Number(data[`total_page_number`]);
          let content_id_list = data[`content_id_combined`].split("<");
          let title_list = data[`title_combined`].split("<");
          let content_list = data[`content_combined`].split("<");
          let user_id_list = data[`user_id_combined`].split("<");
          let user_name_list = data[`user_name_combined`].split("<");
          let overview_list = data[`overview_combined`].split("<");
          let word_counts_list = data[`word_counts_combined`].split("<");
          let tags_list = data[`tags_combined`].split("<");
          let my_review_list = data[`my_review_combined`].split("<");
          let like_counts_list = data[`like_counts_combined`].split("<");
          let dislike_counts_list = data[`dislike_counts_combined`].split("<");
          let post_date_list = data[`post_date_combined`].split("<");
          let comment_count_list = data[`comment_count_combined`].split("<");
          let post_dict_list = [];
          for (let i = 0; i < displayed_post_number; i++) {
            post_dict_list[i] = {
              content_id: Number(content_id_list[i]),
              title: title_list[i],
              content: content_list[i],
              overview: overview_list[i],
              tags: tags_list[i],
              post_date: post_date_list[i],
              user_id: Number(user_id_list[i]),
              username: user_name_list[i],
              my_review: my_review_list[i],
              like_count: Number(like_counts_list[i]),
              dislike_count: Number(dislike_counts_list[i]),
              comment_count: Number(comment_count_list[i]),
            };
          }
          let post_box_list = [];
          box.innerHTML = "";
          for (let i = 0; i < displayed_post_number; i++) {
            post_box_list[i] = new post_component(
              {
                display_delete_post_button: display_delete_post_button,
                out_of_main_box: out_of_main_box,
                uni_post: uni_post,
                option_category: option_category,
                subject_id: subject_id,
              },
              box,
              post_dict_list[i]
            );
          }
        }
      });
  }
};
