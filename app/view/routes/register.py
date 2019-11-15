from app import db
from app.view.routes import app_view
from app.view.forms.RegistrationForm import RegistrationForm
from flask import render_template
from flask import flash
from flask import redirect
from app.view.models.user import User


@app_view.route('/register', methods=['GET', 'POST'])
def register():
    """
    Here the registration is handled.
    The username and password are validated and checked if they don't already exist
    If the registration is successful the success message is shown and the data is included in the database.
    """
    form = RegistrationForm()
    if form.validate_on_submit():
        user = User(username=form.username.data)
        user.set_password(form.password.data)
        db.session.add(user)
        db.session.commit()
        flash('Congratulations, you are now a registered user!')
        return redirect('/home')
    return render_template('register.html', title='Register', form=form)

