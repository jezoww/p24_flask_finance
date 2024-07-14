from flask import render_template, session, redirect, url_for, request, flash
from app import app, bcrypt, db
from app.forms import *
from app.models import *
from random import randint


@app.route("/")
def home():
    return render_template("home.html")


@app.route("/home_menu")
def home_menu():
    if session.get("user_id"):
        return render_template("home_menu.html")
    else:
        return redirect(url_for("login"))


@app.route("/login", methods=["GET", "POST"])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        user = Users.query.filter_by(username=form.username.data).first()
        if user and bcrypt.check_password_hash(user.password, form.password.data):
            session["user_id"] = user.id
            flash(f"Welcome {user.username}", "success")
            return redirect(url_for("home_menu"))
        else:
            flash("Username or password is wrong", "danger")

    return render_template("login.html", form=form)


@app.route("/register", methods=["GET", "POST"])
def register():
    if session.get("users_id"):
        return redirect(url_for("home"))
    form = RegistrationForm()
    checkbox = request.form.get("terms")
    message = None
    if form.validate_on_submit():
        if checkbox == 'agree':
            hashed_password = bcrypt.generate_password_hash(form.password.data).decode("utf-8")
            hashed_secret_code = bcrypt.generate_password_hash(form.secret_code.data).decode("utf-8")
            ids = Used_wallets.query.all()
            list_ids = []
            for i in range(len(ids)):
                list_ids.append(ids[i].wallet_id)
            wallet_id = 100000000
            while wallet_id in list_ids:
                wallet_id = randint(100000000, 999999999)
            user = Users(username=form.username.data,
                         first_name=form.first_name.data,
                         last_name=form.last_name.data,
                         passport=form.passport.data,
                         password=hashed_password,
                         email=form.email.data,
                         phone=form.phone.data,
                         secret_code=hashed_secret_code)
            db.session.add(user)
            db.session.commit()
            wallet = E_wallets(id=wallet_id,
                               user_id=user.id,
                               balance=0)
            used_wallet = Used_wallets(wallet_id=wallet_id)
            db.session.add(wallet)
            db.session.commit()
            db.session.add(used_wallet)
            db.session.commit()
            flash("User  successfully registered", "success")
            return redirect(url_for("login"))
        else:
            message = "You have to be agree with our terms"

    return render_template("register.html", form=form, message=message)


@app.route("/terms")
def terms():
    return render_template("terms.html")


@app.route("/info")
def info():
    user = Users.query.filter_by(id=session.get("user_id")).first()
    wallet = E_wallets.query.filter_by(user_id=user.id).first()
    return render_template("info.html",
                           first_name=user.first_name,
                           last_name=user.last_name,
                           username=user.username,
                           phone=user.phone,
                           email=user.email,
                           balance=wallet.balance,
                           wallet_id=wallet.id)


@app.route("/change_info", methods=["GET", "POST"])
def change_info():
    if not session.get("user_id"):
        return redirect(url_for("login"))
    user = Users.query.filter_by(id=session.get("user_id")).first()
    form = ChangeInfo()
    if form.validate_on_submit():
        user.first_name = form.first_name.data
        user.last_name = form.last_name.data
        user.username = form.username.data
        user.phone = form.phone.data
        user.email = form.email.data
        db.session.commit()
        flash("Information successfully updated", "success")
        return redirect(url_for("home_menu"))
    return render_template("change_info.html", form=form)


@app.route("/show_balance")
def show_balance():
    user = Users.query.filter_by(id=session.get("user_id")).first()
    wallet = E_wallets.query.filter_by(user_id=user.id).first()
    balance = wallet.balance
    return render_template("show_balance.html", balance=balance)


@app.route("/add_balance", methods=["GET", "POST"])
def add_balance():
    if not session.get("user_id"):
        return redirect(url_for("login"))
    form = AddBalance()
    user = Users.query.filter_by(id=session.get("user_id")).first()
    wallet = E_wallets.query.filter_by(user_id=user.id).first()
    if form.validate_on_submit():
        wallet.balance += form.balance.data
        db.session.commit()
        flash("Balance successfully added", "success")
        return redirect(url_for("home_menu"))
    return render_template("add_balance.html", form=form)


@app.route("/transfer_money", methods=["GET", "POST"])
def transfer_money():
    if not session.get("user_id"):
        return redirect(url_for("login"))
    form = TransferMoney()
    sender_wallet = E_wallets.query.filter_by(user_id=session.get("user_id")).first()
    receiver_wallet = E_wallets.query.filter_by(id=form.receiver.data).first()
    if form.validate_on_submit():
        sender_wallet.balance -= form.amount.data
        receiver_wallet.balance += form.amount.data
        history = History(sender=sender_wallet.id,
                          receiver=receiver_wallet.id,
                          amount=form.amount.data,
                          description=form.description.data,
                          time=datetime.now())
        db.session.add(history)
        db.session.commit()
        flash("Money successfully transferred", "success")
        return redirect(url_for("home_menu"))
    return render_template("transfer_money.html", form=form)


@app.route('/history', methods=["GET", "POST"])
def history():
    if not session.get("user_id"):
        return redirect(url_for("login"))
    form = HistoryForm()
    sent = 0
    received = 0
    wallet = E_wallets.query.filter_by(user_id=session.get("user_id")).first()
    transfers1 = History.query.filter_by(sender=wallet.id).all()
    transfers2 = History.query.filter_by(receiver=wallet.id).all()
    transfers = []
    if form.validate_on_submit():
        for transfer in transfers1:
            if form.to_date.data >= transfer.time.date() >= form.from_date.data and form.to_time.data >= transfer.time.time() >= form.from_time.data:
                transfers.append(transfer)
                sent += transfer.amount
        for transfer in transfers2:
            if form.to_date.data >= transfer.time.date() >= form.from_date.data and form.to_time.data >= transfer.time.time() >= form.from_time.data:
                transfers.append(transfer)
                received += transfer.amount
        return render_template("history.html", transfers=transfers, form=form, sent=sent, received=received)
    for transfer in transfers1:
        transfers.append(transfer)
        sent += transfer.amount
    for transfer in transfers2:
        transfers.append(transfer)
        received += transfer.amount

    return render_template("history.html", transfers=transfers, form=form, sent=sent, received=received)


@app.route('/settings')
def settings():
    if not session.get("user_id"):
        return redirect(url_for("login"))
    return render_template('settings.html')


@app.route('/delete', methods=['GET', 'POST'])
def delete():
    if not session.get("user_id"):
        return redirect(url_for("login"))
    form = DeleteForm()
    if form.validate_on_submit():
        Users.query.filter_by(id=session.get("user_id")).delete()
        db.session.commit()
        E_wallets.query.filter_by(user_id=session.get("user_id")).delete()
        db.session.commit()
        flash("Account successfully deleted", "success")
        return redirect(url_for("home"))
    return render_template("delete.html", form=form)


@app.route('/change_password', methods=['POST', 'GET'])
def change_password():
    if not session.get("user_id"):
        return redirect(url_for("login"))
    form = ChangePassword()
    if form.validate_on_submit():
        user = Users.query.filter_by(id=session.get("user_id")).first()
        hashed_password = bcrypt.generate_password_hash(form.new_password.data).decode('utf-8')
        user.password = hashed_password
        db.session.commit()
        flash("Password successfully updated", "success")
        return redirect(url_for("login"))
    return render_template("change_password.html", form=form)


@app.route('/forgot_password', methods=['POST', 'GET'])
def forgot_password():
    if not session.get("user_id"):
        return redirect(url_for("login"))
    form = ForgotPassword()
    if form.validate_on_submit():
        user = Users.query.filter_by(username=form.username.data).first()
        hashed_password = bcrypt.generate_password_hash(form.new_password.data).decode('utf-8')
        user.password = hashed_password
        db.session.commit()
        flash("Password successfully updated", "success")
        return redirect(url_for("login"))
    return render_template('forgot_password.html', form=form)
