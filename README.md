# PROJECT TITLE: Food Protect
### Video Demo:  https://youtu.be/ifGv5qSbKII
### Description:
#### About
このアプリケーションでは、グループを作成し、そのグループ内で画像付きの投稿を共有することができます。
これにより例えば、自分が買ってきたお菓子の写真を撮り、家族が参加するグループに画像と共に「食べないで」とコメントをつけて投稿することで自分のお菓子を家族に勝手に食べられずに済みます。
(The application allows you to create groups and share posts with images within those groups.
 This allows, for example, to take a picture of the sweets you bought and post them to the group in which your family participates with a comment "Don't eat" along with the image so that your family cannot eat your sweets without permission. It will be done.)

#### Contents and functions of each file
##### static/image
ユーザーからアップロードされた画像を保存しておくためのファイルです。
(This is a file for saving images uploaded by users.)

##### static/logo
このアプリケーションのドーナッツのロゴマークを保存しているファイルです。
(This is the file that stores the donut logo mark of this application.)

##### static/style.css
HTMLファイルを装飾するためのファイルです。
(A file for decorating HTML files.)

##### templates/auth
会員登録、ログインなどの承認機能を使用する際に表示されるHTMLファイルを保存しておくためのファイルです。
login.htmlは、ログイン画面に使用されます。
register.htmlは、会員登録画面に使用されます。
(This file is for saving the HTML file that is displayed when using approval functions such as membership registration and login.
 login.html is used for the login screen.
 register.html is used for the member registration screen.)

##### templates/BulletinBoard
ログイン後に使用できる機能を操作する際に表示されるHTMLファイルを保存しておくためのファイルです。
index.htmlは、ホーム（グループ一覧表示）画面に使用されます。
makeGroup.htmlは、グループ作成画面に使用されます。
makePost.htmlは、投稿作成画面に使用されます。
postsList.htmlは、グループまたは個人の投稿一覧の表示画面に使用される。
searchGroup.htmlは、グループ検索画面に使用されます。
(This file is for saving the HTML file that is displayed when operating the functions that can be used after login.
 index.html is used for the home (group list display) screen.
 makeGroup.html is used for the group creation screen.
 makePost.html is used for the post creation screen.
 postsList.html is used to display the list of posts for groups or individuals.
 searchGroup.html is used for the group search screen.)

##### templates/layout.html
今回のアプリケーションで使用する全てのHTMLファイルのベースとなるHTMLファイルです。
(This is the HTML file that is the base of all the HTML files used in this application.)

##### application.py
今回のアプリケーションのバックエンドの処理を行うファイルです。
※セキュリティー対策はできていません。
(This file is used to process the back end of this application.
 * No security measures have been taken.)

##### helpers.py
application.pyで利用されます。
def login_required(f)は、ログインされていない場合に、ログインを要求する関数です。
def allowed_file(filename)は、アップロードされたファイルの拡張子がこのアプリで許可されているものかチェックする関数です。
(Used in application.py.
 def login_required (f) is a function that requires you to log in if you are not logged in.
 def allowed_file (filename) is a function that checks if the extension of the uploaded file is allowed by this app.)

### Technology used
CS50 IDE, HTML, CSS, Bootstrap, flask, SQLite
