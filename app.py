from flask import Flask, render_template, request, redirect, session
import sqlite3, os
from werkzeug.utils import secure_filename

app = Flask(__name__)
app.secret_key = "vivid"

UPLOAD_FOLDER = "static/uploads"
app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER

# ================= DATABASE =================
def db():
    conn = sqlite3.connect("database.db")
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    return conn


# ================= USER UNLOCK =================
@app.route("/", methods=["GET", "POST"])
def unlock():
    error = False
    if request.method == "POST":
        if request.form["password"] == "vivid":
            session["unlock"] = True
            return redirect("/courses")
        else:
            error = True
    return render_template("unlock.html", error=error)


# ================= USER SIDE =================
@app.route("/courses")
def courses():
    if not session.get("unlock"):
        return redirect("/")
    conn = db()
    data = conn.execute("SELECT * FROM courses").fetchall()
    conn.close()
    return render_template("courses.html", courses=data)


@app.route("/course/<int:id>")
def subjects(id):
    conn = db()
    data = conn.execute("SELECT * FROM subjects WHERE course_id=?", (id,)).fetchall()
    conn.close()
    return render_template("subjects.html", subjects=data)


@app.route("/subject/<int:id>")
def chapters(id):
    conn = db()
    chapters = conn.execute("SELECT * FROM chapters WHERE subject_id=?", (id,)).fetchall()
    tests = conn.execute("SELECT * FROM weekly_tests WHERE subject_id=?", (id,)).fetchall()
    conn.close()
    return render_template("chapters.html", chapters=chapters, tests=tests)


@app.route("/chapter/<int:id>")
def contents(id):
    conn = db()
    data = conn.execute("SELECT * FROM contents WHERE chapter_id=?", (id,)).fetchall()
    conn.close()
    return render_template("contents.html", contents=data)


@app.route("/weekly_test/<int:id>")
def weekly_test(id):
    conn = db()
    files = conn.execute("SELECT * FROM weekly_test_files WHERE test_id=?", (id,)).fetchall()
    conn.close()
    return render_template("weekly_test.html", files=files)


# ================= ADMIN LOGIN =================
@app.route("/login", methods=["GET", "POST"])
def login():
    error = False
    if request.method == "POST":
        if request.form["username"] == "vivid" and request.form["password"] == "vividxdlellorvii":
            session["admin"] = True
            return redirect("/admin")
        else:
            error = True
    return render_template("login.html", error=error)


@app.route("/logout")
def logout():
    session.clear()
    return redirect("/login")


# ================= ADMIN PANEL =================
@app.route("/admin")
def admin():
    if not session.get("admin"):
        return redirect("/login")

    conn = db()
    data = render_template(
        "admin.html",
        courses=conn.execute("SELECT * FROM courses").fetchall(),
        subjects=conn.execute("SELECT * FROM subjects").fetchall(),
        chapters=conn.execute("SELECT * FROM chapters").fetchall(),
        tests=conn.execute("SELECT * FROM weekly_tests").fetchall(),
    )
    conn.close()
    return data


# ================= ADD =================
@app.route("/add_course", methods=["POST"])
def add_course():
    if not session.get("admin"):
        return redirect("/login")
    conn = db()
    conn.execute("INSERT INTO courses(name) VALUES(?)", (request.form["name"],))
    conn.commit()
    conn.close()
    return redirect("/admin")


@app.route("/add_subject", methods=["POST"])
def add_subject():
    conn = db()
    conn.execute("INSERT INTO subjects(course_id,name) VALUES(?,?)",
                 (request.form["course_id"], request.form["name"]))
    conn.commit()
    conn.close()
    return redirect("/admin")


@app.route("/add_chapter", methods=["POST"])
def add_chapter():
    conn = db()
    conn.execute("INSERT INTO chapters(subject_id,name) VALUES(?,?)",
                 (request.form["subject_id"], request.form["name"]))
    conn.commit()
    conn.close()
    return redirect("/admin")


@app.route("/add_test", methods=["POST"])
def add_test():
    conn = db()
    conn.execute("INSERT INTO weekly_tests(subject_id,name) VALUES(?,?)",
                 (request.form["subject_id"], request.form["name"]))
    conn.commit()
    conn.close()
    return redirect("/admin")


@app.route("/add_content", methods=["POST"])
def add_content():
    conn = db()
    file = request.files["file"]
    path = ""

    if file and file.filename != "":
        filename = secure_filename(file.filename)
        path = os.path.join(app.config["UPLOAD_FOLDER"], filename)
        file.save(path)

    conn.execute("INSERT INTO contents(chapter_id,type,link,file_path) VALUES(?,?,?,?)",
                 (request.form["chapter_id"],
                  request.form["type"],
                  request.form["link"],
                  path))
    conn.commit()
    conn.close()
    return redirect("/admin")


@app.route("/add_test_file", methods=["POST"])
def add_test_file():
    conn = db()
    file = request.files["file"]
    path = ""

    if file and file.filename != "":
        filename = secure_filename(file.filename)
        path = os.path.join(app.config["UPLOAD_FOLDER"], filename)
        file.save(path)

    conn.execute("INSERT INTO weekly_test_files(test_id,title,file_path) VALUES(?,?,?)",
                 (request.form["test_id"],
                  request.form["title"],
                  path))
    conn.commit()
    conn.close()
    return redirect("/admin")


# ================= DELETE =================
@app.route("/delete_course/<int:id>")
def delete_course(id):
    conn = db()
    conn.execute("DELETE FROM courses WHERE id=?", (id,))
    conn.commit()
    conn.close()
    return redirect("/admin")


@app.route("/delete_subject/<int:id>")
def delete_subject(id):
    conn = db()
    conn.execute("DELETE FROM subjects WHERE id=?", (id,))
    conn.commit()
    conn.close()
    return redirect("/admin")


@app.route("/delete_chapter/<int:id>")
def delete_chapter(id):
    conn = db()
    conn.execute("DELETE FROM chapters WHERE id=?", (id,))
    conn.commit()
    conn.close()
    return redirect("/admin")


@app.route("/delete_test/<int:id>")
def delete_test(id):
    conn = db()
    conn.execute("DELETE FROM weekly_tests WHERE id=?", (id,))
    conn.commit()
    conn.close()
    return redirect("/admin")


# ================= EDIT =================
@app.route("/edit_course/<int:id>", methods=["GET", "POST"])
def edit_course(id):
    conn = db()
    if request.method == "POST":
        conn.execute("UPDATE courses SET name=? WHERE id=?",
                     (request.form["name"], id))
        conn.commit()
        conn.close()
        return redirect("/admin")

    data = conn.execute("SELECT * FROM courses WHERE id=?", (id,)).fetchone()
    conn.close()
    return render_template("edit.html", data=data, type="Course")


@app.route("/edit_subject/<int:id>", methods=["GET", "POST"])
def edit_subject(id):
    conn = db()
    if request.method == "POST":
        conn.execute("UPDATE subjects SET name=? WHERE id=?",
                     (request.form["name"], id))
        conn.commit()
        conn.close()
        return redirect("/admin")

    data = conn.execute("SELECT * FROM subjects WHERE id=?", (id,)).fetchone()
    conn.close()
    return render_template("edit.html", data=data, type="Subject")


@app.route("/edit_chapter/<int:id>", methods=["GET", "POST"])
def edit_chapter(id):
    conn = db()
    if request.method == "POST":
        conn.execute("UPDATE chapters SET name=? WHERE id=?",
                     (request.form["name"], id))
        conn.commit()
        conn.close()
        return redirect("/admin")

    data = conn.execute("SELECT * FROM chapters WHERE id=?", (id,)).fetchone()
    conn.close()
    return render_template("edit.html", data=data, type="Chapter")


@app.route("/edit_test/<int:id>", methods=["GET", "POST"])
def edit_test(id):
    conn = db()
    if request.method == "POST":
        conn.execute("UPDATE weekly_tests SET name=? WHERE id=?",
                     (request.form["name"], id))
        conn.commit()
        conn.close()
        return redirect("/admin")

    data = conn.execute("SELECT * FROM weekly_tests WHERE id=?", (id,)).fetchone()
    conn.close()
    return render_template("edit.html", data=data, type="Weekly Test")


# ================= RUN =================
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
