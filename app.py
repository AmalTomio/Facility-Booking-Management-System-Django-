from flask import (
    Flask, render_template, redirect,
    url_for, flash, abort, request
)
from flask_login import (
    LoginManager, login_user, logout_user,
    login_required, current_user
)
from config import get_config
from database import check_database_connection, init_database
from models import User, Facility, Booking
from forms import LoginForm, RegisterForm, FacilityForm, BookingForm
from time import time
from datetime import date
from flask import session
import logging
import os

# APP SETUP

app = Flask(__name__)
app.config.from_object(get_config())

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

UPLOAD_FOLDER = "static/uploads/facilities"
app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

# LOGIN MANAGER

login_manager = LoginManager(app)
login_manager.login_view = "login"


@login_manager.user_loader
def load_user(user_id):
    return User.get_by_id(int(user_id))


# AUTH

@app.route("/")
def index():
    if current_user.is_authenticated:
        return redirect(
            url_for("admin_dashboard")
            if current_user.is_admin()
            else url_for("staff_dashboard")
        )
    return redirect(url_for("login"))

@app.route("/register", methods=["POST"])
def register():
    form = RegisterForm()
    login_form = LoginForm()

    if form.validate_on_submit():
        if User.get_by_email(form.email.data):
            flash("Email already registered", "auth-danger")
        else:
            User.create(
                name=form.name.data,
                email=form.email.data,
                password=form.password.data,
                role=form.role.data
            )
            flash("Account created. Please login.", "auth-success")

    return render_template(
        "auth.html",
        login_form=login_form,
        register_form=form
    )


@app.route("/login", methods=["GET", "POST"])
def login():
    login_form = LoginForm()
    register_form = RegisterForm()

    if login_form.validate_on_submit():
        user = User.get_by_email(login_form.email.data)
        if user and user.verify_password(login_form.password.data):
            login_user(user)
            return redirect(
                url_for("admin_dashboard")
                if user.is_admin()
                else url_for("staff_dashboard")
            )
        flash("Invalid email or password", "auth-danger")

    return render_template(
        "auth.html",
        login_form=login_form,
        register_form=register_form
    )


@app.route("/logout")
@login_required
def logout():
    logout_user()
    session.pop("_flash", None)
    flash("Logged out successfully", "auth-success")
    return redirect(url_for("login"))


@app.route("/staff/dashboard")
@login_required
def staff_dashboard():
    if not current_user.is_staff():
        abort(403)

    stats = Booking.get_user_stats(current_user.user_id)

    # ✅ UPCOMING BOOKINGS
    bookings = Booking.get_upcoming_by_user(
        current_user.user_id,
        limit=5
    )

    return render_template(
        "dashboard_staff.html",
        stats=stats,
        bookings=bookings,
        active_page="dashboard"
    )


@app.route("/staff/facilities")
@login_required
def staff_facilities():
    if not current_user.is_staff():
        abort(403)

    booking_form = BookingForm()
    stats = Booking.get_user_stats(current_user.user_id)

    return render_template(
        "staff/facilities.html",
        facilities=Facility.get_all(),
        booking_form=booking_form,
        stats=stats,
        active_page="facilities"
    )


@app.route("/booking/my-bookings")
@login_required
def my_bookings():
    if not current_user.is_staff():
        abort(403)

    raw_bookings = Booking.get_by_user(current_user.user_id)
    stats = Booking.get_user_stats(current_user.user_id)

    bookings = []
    for b in raw_bookings:
        def format_time(t):
            if hasattr(t, "strftime"):
                return t.strftime("%H:%M")
            if hasattr(t, "total_seconds"):
                h = int(t.total_seconds() // 3600)
                m = int((t.total_seconds() % 3600) // 60)
                return f"{h:02d}:{m:02d}"
            return str(t)

        bookings.append({
            "booking_id": b.booking_id,
            "facility_name": b.facility_name,
            "booking_date": b.booking_date.strftime("%d %b %Y"),
            "time": f"{format_time(b.start_time)} – {format_time(b.end_time)}",
            "status": b.status,
        })

    return render_template(
        "booking_history.html",
        bookings=bookings,
        stats=stats,
        is_admin=False,
        active_page="bookings",
    )

@app.route("/booking/create", methods=["POST"])
@login_required
def create_booking():
    if not current_user.is_staff():
        abort(403)

    form = BookingForm()

    if not form.validate_on_submit():
        flash("Invalid booking data.", "dashboard-danger")
        return redirect(url_for("staff_dashboard"))

    Booking.create(
        user_id=current_user.user_id,
        facility_id=form.facility_id.data,
        booking_date=form.booking_date.data,
        start_time=form.start_time.data,
        end_time=form.end_time.data,
        purpose=form.purpose.data,
    )

    flash("Booking request submitted.", "dashboard-success")
    return redirect(url_for("staff_dashboard"))

@app.route("/booking/cancel/<int:booking_id>", methods=["POST"])
@login_required
def cancel_booking(booking_id):
    if not current_user.is_staff():
        abort(403)

    Booking.cancel(
        booking_id=booking_id,
        user_id=current_user.user_id
    )

    flash("Booking cancelled successfully.", "dashboard-success")
    return redirect(url_for("my_bookings"))


# ADMIN DASHBOARD

@app.route("/admin/dashboard")
@login_required
def admin_dashboard():
    if not current_user.is_admin():
        abort(403)

    stats = {
        "total": Booking.get_total_count(),
        "pending": Booking.get_pending_count(),
        "approved": Booking.get_approved_count(),
        "rejected": Booking.get_rejected_count(),
        "facilities": Facility.get_active_count(),
    }

    return render_template(
        "dashboard_admin.html",
        stats=stats,
        recent_bookings=Booking.get_recent(limit=10),
        active_page="dashboard",
    )

# ADMIN – BOOKINGS

@app.route("/admin/bookings/pending")
@login_required
def pending_bookings():
    if not current_user.is_admin():
        abort(403)

    return render_template(
        "pending_bookings.html",
        bookings=Booking.get_all(status="pending"),
        active_page="bookings"
    )

@app.route("/admin/bookings/approve/<int:booking_id>", methods=["POST"])
@login_required
def approve_booking(booking_id):
    if not current_user.is_admin():
        abort(403)

    Booking.update_status(booking_id, "approved")
    flash("Booking approved.", "dashboard-success")
    return redirect(url_for("pending_bookings"))


@app.route("/admin/bookings/reject/<int:booking_id>", methods=["POST"])
@login_required
def reject_booking(booking_id):
    if not current_user.is_admin():
        abort(403)

    Booking.update_status(booking_id, "rejected")
    flash("Booking rejected.", "dashboard-success")
    return redirect(url_for("pending_bookings"))


# ADMIN – FACILITIES

@app.route("/admin/facilities")
@login_required
def facilities_list():
    if not current_user.is_admin():
        abort(403)

    return render_template(
        "facilities.html",
        facilities=Facility.get_all(include_inactive=True),
        add_form=FacilityForm(),
        edit_form=FacilityForm(),
        active_page="facilities"
    )

@app.route("/admin/facilities/create", methods=["POST"])
@login_required
def create_facility():
    if not current_user.is_admin():
        abort(403)

    form = FacilityForm()
    if not form.validate_on_submit():
        flash("Invalid inputs.", "dashboard-danger")
        return redirect(url_for("facilities_list"))

    image_name = None
    image = request.files.get("image")
    if image and image.filename:
        image_name = f"{int(time())}_{image.filename}"
        image.save(os.path.join(app.config["UPLOAD_FOLDER"], image_name))

    Facility.create(
        form.name.data,
        form.capacity.data,
        None,
        form.status.data,
        image_name
    )

    flash("Facility added successfully.", "dashboard-success")
    return redirect(url_for("facilities_list"))

@app.route("/admin/facilities/update", methods=["POST"])
@login_required
def update_facility():
    if not current_user.is_admin():
        abort(403)

    form = FacilityForm()

    if not form.validate_on_submit():
        flash("Invalid inputs. Please check the form.", "dashboard-danger")
        return redirect(url_for("facilities_list"))  # ✅ FIXED

    facility_id = form.facility_id.data
    if not facility_id:
        flash("Missing facility ID.", "dashboard-danger")
        return redirect(url_for("facilities_list"))  # ✅ FIXED

    facility = Facility.get_by_id(int(facility_id))
    if not facility:
        flash("Facility not found.", "dashboard-danger")
        return redirect(url_for("facilities_list"))  # ✅ FIXED

    image_name = facility.image
    image = request.files.get("image")
    if image and image.filename:
        image_name = f"{int(time())}_{image.filename}"
        image.save(os.path.join(app.config["UPLOAD_FOLDER"], image_name))

    Facility.update(
        facility.facility_id,
        form.name.data,
        form.capacity.data,
        None,
        form.status.data,
        image_name
    )

    flash("Facility updated successfully.", "dashboard-success")
    return redirect(url_for("facilities_list"))  



@app.route("/admin/facilities/delete/<int:facility_id>", methods=["POST"])
@login_required
def delete_facility(facility_id):
    if not current_user.is_admin():
        abort(403)

    facility = Facility.get_by_id(facility_id)
    if not facility:
        flash("Facility not found.", "dashboard-danger")
        return redirect(url_for("facilities_list"))

    if Facility.has_active_bookings(facility_id):
        flash(
            "Cannot delete facility with active or pending bookings.",
            "dashboard-danger"
        )
        return redirect(url_for("facilities_list"))

    Facility.delete(facility_id)
    flash("Facility deleted successfully.", "dashboard-success")
    return redirect(url_for("facilities_list"))


@app.route("/api/stats")
@login_required
def api_stats():
    if current_user.is_admin():
        return {
            "total": Booking.get_total_count(),
            "pending": Booking.get_pending_count(),
            "approved": Booking.get_approved_count(),
        }

    return Booking.get_user_stats(current_user.user_id)


# =============================================================================
# MAIN
# =============================================================================

if __name__ == "__main__":
    if not check_database_connection():
        logger.error("Database connection failed")
        exit(1)

    init_database()
    app.run(debug=True)
