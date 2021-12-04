import os

from cs50 import SQL
from flask import Flask, redirect, render_template, request, session, flash
from flask_session import Session
from tempfile import mkdtemp
from helpers import login_required, allowed_file
from werkzeug.security import check_password_hash, generate_password_hash
from werkzeug.utils import secure_filename
from pykakasi import kakasi

#アプリケーションを構成する
app = Flask(__name__)

# アップロードするフォルダを指定
UPLOAD_FOLDER = './static/images'

# アップロードされたファイルが格納される場所を指定
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

# テンプレートが自動再読み込みされることを確認します
app.config["TEMPLATES_AUTO_RELOAD"] = True

app.config["SESSION_FILE_DIR"] = mkdtemp()
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

db = SQL("sqlite:///foodProtect.db")


# ホーム画面（グループ一覧）
@app.route("/")
@login_required
def index():
    groups = db.execute(
        'SELECT g.id AS id, g.maker_id AS creator_id, u1.username AS creator, g.group_name AS group_name , g.made_at AS made_at'
        ' FROM groups AS g JOIN users AS u1 ON g.maker_id = u1.id'
        ' JOIN group_joins AS gj ON g.id = gj.group_id'
        ' JOIN users AS u2 ON gj.user_id = u2.id'
        ' WHERE gj.user_id = ?'
        , session["user_id"])

    return render_template("BulletinBoard/index.html", groups=groups)


# ログインについて
@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        # ユーザー名とパスワードが入力されたかどうかチェック
        username = request.form.get("username")
        if not username:
            flash("ユーザーIDを入力してください", category="error")
            return redirect("/login")
            
        password = request.form.get("password")
        if not password:
            flash("パスワードを入力してください", category="error")
            return redirect("login")
        
        # 入力されたユーザー名とパスワードが一致するかチェック
        rows = db.execute("SELECT * FROM users WHERE username = ?", username)
        if len(rows) != 1 or not check_password_hash(rows[0]["password_hash"], password):
            flash('ユーザー名またはパスワードが間違っています', category="error")
            return redirect("login")

        # どのユーザーがログインしたか記憶する
        session["user_id"] = rows[0]["id"]

        flash('ログイン成功!')
        # もし、ログインした情報と一致した場合
        return redirect("/")

    else:
        return render_template("auth/login.html")


# ユーザー登録について
@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        # 入力条件を確認
        username = request.form.get("username")
        if not username:
            flash("ユーザー名を入力してください", category="error")
            return redirect("/register")

        password = request.form.get("password")
        if not password:
            flash("パスワードを入力してください", category="error")
            return redirect("/register")

        if not (5 <= len(password) <= 20):
            flash("パスワードは5字以上20字以下で入力してください", category="error")
            return redirect("/register")

        confirmation = request.form.get("confirmation")
        if not confirmation:
            flash("パスワード（確認）を入力してください", category="error")
            return redirect("/register")

        if password != confirmation:
            flash("入力されたパスワードが一致しません", category="error")
            return redirect("/register")
        
        # ハッシュしたパスワードを保存
        password_hash = generate_password_hash(password)
        db.execute(
            'INSERT INTO users (username, password_hash)'
            ' VALUES(?, ?)'
            , username, password_hash)
            
        # どのユーザーがログインしたか記憶する
        rows = db.execute("SELECT * FROM users WHERE username = ?", username)    
        session["user_id"] = rows[0]["id"]
        
        flash("会員登録完了！")    
        return redirect("/")
        
    if request.method == "GET":
        return render_template("auth/register.html")


# 投稿作成機能
@app.route("/post",methods=["GET", "POST"])
@login_required
def post():
    if request.method == "POST":
        groupName = request.form.get("groupName")
        if not groupName:
            flash("投稿するグループを選択してください", category="error")
            return redirect("/post")

        # ユーザーが所属しているグループかどうか確認する
        groups = db.execute(
            'SELECT group_name FROM groups AS g'
            ' JOIN group_joins AS gj ON g.id = gj.group_id'
            ' WHERE g.group_name = ?'
            ' AND gj.user_id = ?'
            , groupName, session["user_id"])
        
        if not groups:
            flash("不正な入力です", category="error")
            return redirect("/register")

        productName = request.form.get("productName")
        if not productName:
            flash("商品名を入力してください", category="error")
            return redirect("/register")

        comment = request.form.get("comment")
        if not comment:
            flash("コメントを入力してください", category="error")
            return redirect("/register")

        #ファイルが選択された場合の処理
        file = request.files.get("image")
        if file:
            # ファイル名のない空のファイルの場合
            if file.filename == '':
                flash('ファイルが存在しません', category="error")
                return redirect("/register")

            # 有効なファイルである場合
            if file and allowed_file(file.filename):
                # ファイル名に日本語が含まれている場合の処理
                Kakasi = kakasi()
                # H:ひらがな K:カタカナ J:漢字をローマ字に変更する設定
                Kakasi.setMode('H', 'a')
                Kakasi.setMode('K', 'a')
                Kakasi.setMode('J', 'a')
                conv = Kakasi.getConverter()
                tempfileName = conv.do(file.filename)
                filename = secure_filename(tempfileName)

            file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))

            # データベースに保存するファイルパス
            filepath = '/static/images/' + filename
            # 投稿に関するデータ
            db.execute(
                'INSERT INTO posts (food_name, food_image, comment, poster_id, group_id)'
                ' VALUES(?, ?, ?, ?, (SELECT id FROM groups WHERE group_name = ?))'
                , productName, filepath, comment, session["user_id"], groupName)

        # ファイルが選択されなかった場合の処理
        else:
            db.execute(
                'INSERT INTO posts (food_name, comment, poster_id, group_id)'
                ' VALUES(?, ?, ?, (SELECT id FROM groups WHERE group_name = ?))'
                , productName, comment, session["user_id"], groupName)

        flash("投稿作成完了！")

        return redirect("/")
    else:
        groups = db.execute(
            'SELECT group_name FROM groups' 
            ' WHERE id IN (SELECT group_id FROM group_joins WHERE user_id = ?)'
            , session["user_id"])
        return render_template("BulletinBoard/makePost.html", groups=groups)


# 自分の投稿一覧
@app.route("/myPosts")
@login_required
def myPosts():
    posts = db.execute(
        'SELECT posts.id AS id, poster_id, username, food_name, food_image, comment, posts.created_at AS posted_at'
        ' FROM posts JOIN users ON posts.poster_id = users.id'
        ' WHERE posts.poster_id = ?'
        , session["user_id"])
    return render_template("BulletinBoard/postsList.html", posts=posts)


# 自分の投稿削除
@app.route("/<int:id>/postDelete", methods=["POST"])
@login_required
def postDelete(id):
    if request.method == "POST":
        posts = db.execute("SELECT poster_id FROM posts WHERE id = ?", id)
        if session["user_id"] == posts[0]["poster_id"]:
            db.execute("DELETE FROM posts WHERE id = ?", id)
            flash("投稿が削除されました", category="error")
            return redirect("/myPosts")
        return "不正アクセス検知"


# グループ作成機能
@app.route("/group", methods=["GET", "POST"])
@login_required
def group():
    if request.method == "POST":
        groupName = request.form.get("groupName")
        if not groupName:
            flash("グループ名を入力してください", category="error")
            return redirect("/group")

        try:
            # グループ情報を追加する
            db.execute(
                'INSERT INTO groups (group_name, maker_id) VALUES(?, ?)'
                , groupName, session["user_id"])
                       
            # ユーザーの所属グループ情報を追加する
            db.execute(
                'INSERT INTO group_joins (group_id, user_id)'
                ' VALUES((SELECT id FROM groups WHERE group_name = ?), ?)'
                , groupName, session["user_id"])
            
            flash("グループ作成完了！")
            return redirect("/")

        except ValueError:
            flash("そのグループ名は利用できません", category="error")
            return redirect("/group")
    else:
        return render_template("BulletinBoard/makeGroup.html")


# グループ名検索
@app.route("/search", methods=["GET", "POST"])
@login_required
def search():
    if request.method == "POST":
        groupName = request.form.get("groupName")
        # グループ名が入力されたかどうか確認する
        if not groupName:
            flash("検索したいグループ名を入力してください", category="error")
            return redirect("/search")

        # 入力されたグループが存在するか確かめる
        datas = db.execute("SELECT COUNT(id) FROM groups WHERE group_name = ?", groupName)
        if datas[0]["COUNT(id)"] == 0:
            flash("検索されたグループは見つかりませんでした", category="error")
            return redirect("/search")

        try:
            # データベースにユーザーがどのグループに参加したかを保存する
            db.execute(
                'INSERT INTO group_joins (group_id, user_id)'
                ' VALUES((SELECT id FROM groups WHERE group_name = ?), ?)'
                , groupName, session["user_id"])

        except ValueError:
            flash("既に参加しているグループです", category="error")
            return redirect("/search")

        flash("グループ参加完了！")
        return redirect("/")

    if request.method == "GET":
        return render_template("BulletinBoard/searchGroup.html")


# グループの投稿一覧表示
@app.route("/<int:id>/groupPosts", methods=["POST"])
@login_required
def groupPosts(id):
    if request.method == "POST":
        
        # グループに参加しているメンバーを取得する
        groupMembers = db.execute("SELECT user_id FROM group_joins WHERE group_id = ?", id)
        for groupMember in groupMembers:
            # ログインしているユーザーがグループのメンバーだった場合、そのグループの投稿とグループ名を取得する
            if session["user_id"] == groupMember["user_id"]:
                posts = db.execute(
                    'SELECT posts.id AS id, poster_id, username, food_name, food_image, comment, posts.created_at AS posted_at FROM posts'
                    ' JOIN users ON posts.poster_id = users.id'
                    ' WHERE posts.group_id = ?'
                    , id)
                groups = db.execute(
                    'SELECT group_name FROM groups'
                    ' WHERE id = ?'
                    , id)
                groupName = groups[0]["group_name"]
                
                return render_template("BulletinBoard/postsList.html", posts=posts, groupName=groupName)
        
        flash("不正なアクセスが検知されました", category="error")       
        return redirect("/logout")


# グループ削除
@app.route("/<int:id>/groupDelete", methods=["POST"])
@login_required
def groupDelete(id):
    if request.method == "POST":
        
        # ログインしているユーザーがグループの作成者であった場合、そのグループに関するデータを全削除する
        groups = db.execute("SELECT maker_id FROM groups WHERE id = ?", id)
        if session["user_id"] == groups[0]["maker_id"]:
            db.execute("DELETE FROM group_joins WHERE group_id = ?", id)
            db.execute("DELETE FROM posts WHERE group_id = ?", id)
            db.execute("DELETE FROM groups WHERE id = ?", id)
            flash("グループ削除完了！")
            return redirect("/")
        
        flash("不正なアクセスが検知されました", category="error")   
        return redirect("/logout")


@app.route("/logout")
def logout():
    # user_idを忘れる
    session.clear()
    # ユーザーをログインフォームにリダイレクトする
    return redirect("/")