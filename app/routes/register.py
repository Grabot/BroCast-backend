from app.routes import app_home
from app.forms.RegistrationForm import RegistrationForm
from flask import render_template
from app.models.user import User


@app_home.route('/register', methods=['GET', 'POST'])
def register():
    """
    Here the registration is handled.
    The username and password are validated and checked if they don't already exist
    If the registration is successful the success message is shown and the data is included in the database.
    """
    form = RegistrationForm()
    if form.validate_on_submit():
        user = User(username=form.username.data, email=form.email.data)
        user.set_password(form.password.data)
        db.session.add(user)
        db.session.commit()
        flash('Congratulations, you are now a registered user!')
        return redirect(url_for('login'))
    return render_template('register.html', title='Register', form=form)

