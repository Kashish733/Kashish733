from datetime import datetime

from flask import (
    Blueprint,
    render_template,
    request,
    redirect,
    url_for,
    flash,
    session,
    send_from_directory,
)
from auth import login_required
from models import get_db
from steg import embed_payload, extract_payload
from utils import (
    ensure_upload_dirs,
    unique_filename,
    save_bytes,
    OUTPUT_DIR,
    CARRIER_DIR,
    PAYLOAD_DIR,
    guess_is_image,
)

main_bp = Blueprint("main", __name__)

ensure_upload_dirs()


@main_bp.route("/")
def index():
    conn = get_db()
    posts = conn.execute(
        "SELECT * FROM posts ORDER BY id DESC"
    ).fetchall()
    conn.close()

    return render_template("index.html", posts=posts)


@main_bp.route("/submit", methods=["GET", "POST"])
@login_required
def submit():
    if request.method == "POST":
        title = request.form.get("title", "").strip()
        start_bit = request.form.get("start_bit", "").strip()
        period_bits = request.form.get("period_bits", "").strip()
        mode = request.form.get("mode", "fixed").strip()

        carrier_file = request.files.get("carrier")
        payload_file = request.files.get("payload")

        if not title:
            flash("Title is required.")
            return redirect(url_for("main.submit"))

        if not carrier_file or not payload_file:
            flash("Both carrier file and payload file are required.")
            return redirect(url_for("main.submit"))

        try:
            start_bit = int(start_bit)
            period_bits = int(period_bits)
        except ValueError:
            flash("Start bit and period must be integers.")
            return redirect(url_for("main.submit"))

        if start_bit < 0 or period_bits <= 0:
            flash("Start bit must be >= 0 and period must be > 0.")
            return redirect(url_for("main.submit"))

        carrier_bytes = carrier_file.read()
        payload_bytes = payload_file.read()

        if not carrier_bytes or not payload_bytes:
            flash("Uploaded files cannot be empty.")
            return redirect(url_for("main.submit"))

        try:
            stego_bytes = embed_payload(
                carrier_bytes=carrier_bytes,
                payload_bytes=payload_bytes,
                start_bit=start_bit,
                period_bits=period_bits,
                mode=mode,
            )
        except Exception as e:
            flash(f"Embedding failed: {e}")
            return redirect(url_for("main.submit"))

        carrier_name = unique_filename(carrier_file.filename, "carrier")
        payload_name = unique_filename(payload_file.filename, "payload")
        stego_name = unique_filename("stego_output.bin", "stego")

        save_bytes(carrier_bytes, CARRIER_DIR, carrier_name)
        save_bytes(payload_bytes, PAYLOAD_DIR, payload_name)
        save_bytes(stego_bytes, OUTPUT_DIR, stego_name)

        conn = get_db()
        conn.execute(
            """
            INSERT INTO posts (
                title,
                username,
                carrier_filename,
                stego_filename,
                payload_name,
                payload_size,
                start_bit,
                period_bits,
                mode,
                created_at
            )
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                title,
                session["user"],
                carrier_name,
                stego_name,
                payload_file.filename,
                len(payload_bytes),
                start_bit,
                period_bits,
                mode,
                datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S UTC"),
            ),
        )
        conn.commit()
        conn.close()

        flash("Stego file created and posted successfully.")
        return redirect(url_for("main.index"))

    return render_template("submit.html")


@main_bp.route("/extract", methods=["GET", "POST"])
@login_required
def extract():
    extracted_filename = None

    if request.method == "POST":
        stego_file = request.files.get("stego")
        start_bit = request.form.get("start_bit", "").strip()
        period_bits = request.form.get("period_bits", "").strip()
        mode = request.form.get("mode", "fixed").strip()

        if not stego_file:
            flash("Please upload a stego file.")
            return redirect(url_for("main.extract"))

        try:
            start_bit = int(start_bit)
            period_bits = int(period_bits)
        except ValueError:
            flash("Start bit and period must be integers.")
            return redirect(url_for("main.extract"))

        if start_bit < 0 or period_bits <= 0:
            flash("Start bit must be >= 0 and period must be > 0.")
            return redirect(url_for("main.extract"))

        stego_bytes = stego_file.read()
        if not stego_bytes:
            flash("Uploaded stego file cannot be empty.")
            return redirect(url_for("main.extract"))

        try:
            payload_bytes = extract_payload(
                stego_bytes=stego_bytes,
                start_bit=start_bit,
                period_bits=period_bits,
                mode=mode,
            )
        except Exception as e:
            flash(f"Extraction failed: {e}")
            return redirect(url_for("main.extract"))

        extracted_filename = unique_filename("recovered_payload.bin", "extracted")
        save_bytes(payload_bytes, OUTPUT_DIR, extracted_filename)

        flash("Payload extracted successfully.")
        return render_template(
            "extract.html",
            extracted_filename=extracted_filename
        )

    return render_template("extract.html", extracted_filename=extracted_filename)


@main_bp.route("/preview/carrier/<path:filename>")
def preview_carrier(filename):
    return send_from_directory(CARRIER_DIR, filename, as_attachment=False)


@main_bp.route("/files/<path:filename>")
def files(filename):
    return send_from_directory(OUTPUT_DIR, filename, as_attachment=True)


@main_bp.app_template_filter("is_image_file")
def is_image_file_filter(filename):
    return guess_is_image(filename)