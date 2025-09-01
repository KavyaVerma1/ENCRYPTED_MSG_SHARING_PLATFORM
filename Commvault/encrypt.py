from flask import Flask, request, render_template_string
import pymysql
import uuid
from datetime import datetime, timedelta
from cryptography.fernet import Fernet

app = Flask(__name__)
key = Fernet.generate_key()
cipher = Fernet(key)

db = pymysql.connect(
    host="encrypted-messages-db.crg2gkwqm2zd.eu-north-1.rds.amazonaws.com",
    user="admin",
    password="kavya123",
    port=3306,
    database="encrypted-messages-db"
)

cur = db.cursor()
cur.execute("""
CREATE TABLE IF NOT EXISTS messages (
    id INT AUTO_INCREMENT PRIMARY KEY,
    link_id VARCHAR(255) UNIQUE,
    message TEXT,
    created_at DATETIME,
    expire_at DATETIME,
    one_time BOOLEAN,
    used BOOLEAN DEFAULT FALSE
)
""")
db.commit()

form_html = """
<!DOCTYPE html>
<html>
<head>
<title>Encrypt Message</title>
</head>
<body>
<form method="POST">
<textarea name="message" rows="10" cols="50" required></textarea><br><br>
<input type="checkbox" id="time_expiry" name="time_expiry" value="1" onclick="toggleExpiry()">
<label for="time_expiry">Time Based Expiry</label>
<div id="expiry_options" style="display:none;">
<input type="number" name="expiry_value" min="1">
<select name="expiry_unit">
<option value="seconds">Seconds</option>
<option value="minutes">Minutes</option>
</select>
</div><br>
<input type="checkbox" id="one_time" name="one_time" value="1">
<label for="one_time">One Time Click</label><br><br>
<input type="submit" value="Encrypt Text">
</form>
<script>
function toggleExpiry() {
  var box = document.getElementById("time_expiry");
  var opts = document.getElementById("expiry_options");
  opts.style.display = box.checked ? "block" : "none";
}
</script>
</body>
</html>
"""

link_html = """
<!DOCTYPE html>
<html>
<head>
<title>Decryption Link</title>
</head>
<body>
<p>Your decryption link:</p>
<input type="text" id="link" value="{{ link }}" readonly size="80">
<button onclick="navigator.clipboard.writeText(document.getElementById('link').value)">Copy</button>
</body>
</html>
"""

@app.route("/", methods=["GET","POST"])
def index():
    if request.method == "POST":
        message = request.form["message"]
        one_time = "one_time" in request.form
        time_expiry = "time_expiry" in request.form

        if not one_time and not time_expiry:
            return "Error: Please select at least Time Expiry or One-Time option."

        encrypted = cipher.encrypt(message.encode()).decode()
        link_id = str(uuid.uuid4())
        created_at = datetime.utcnow()
        expire_at = None
        if time_expiry:
            val = int(request.form.get("expiry_value", 0))
            unit = request.form.get("expiry_unit", "seconds")
            delta = timedelta(seconds=val) if unit=="seconds" else timedelta(minutes=val)
            expire_at = created_at + delta

        cur.execute("INSERT INTO messages (link_id,message,created_at,expire_at,one_time,used) VALUES (%s,%s,%s,%s,%s,%s)",
                    (link_id, encrypted, created_at, expire_at, one_time, False))
        db.commit()
        return render_template_string(link_html, link=request.host_url+"decrypt/"+link_id)
    return form_html

@app.route("/decrypt/<link_id>")
def decrypt(link_id):
    cur.execute("SELECT message,created_at,expire_at,one_time,used FROM messages WHERE link_id=%s", (link_id,))
    row = cur.fetchone()
    if not row:
        return "Invalid link."
    message, created_at, expire_at, one_time, used = row
    now = datetime.utcnow()

    if expire_at and now > expire_at:
        return "Link expired."

    if one_time and used:
        return "This one-time link has already been used."

    decrypted = cipher.decrypt(message.encode()).decode()

    if one_time:
        cur.execute("UPDATE messages SET used=TRUE WHERE link_id=%s", (link_id,))
        db.commit()

    return f"Decrypted Message: {decrypted}"

if __name__ == "__main__":
    app.run(debug=True)
