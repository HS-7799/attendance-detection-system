from services.forms import BranchForm
from flask import Flask, url_for, render_template, request, redirect, session, Blueprint
from services.models import Branch, db
from flask_login import (
    current_user,
    login_required,
)
b = Blueprint('b', __name__, template_folder="templates")


@b.route('/admin/branches', methods=["GET", "POST"])
@b.route('/admin/branches/<isUpdated>', methods=["GET", "POST"])
@login_required
def branches(isUpdated=True):
    add = BranchForm()
    branches = db.session.query(Branch).all()
    if (current_user.roles[0].id == 1):
        if (add.validate_on_submit()):
            errors = []
            success = False
            if not add.name.data:
                errors.append("Name field is required")
            else:
                for branch in branches:
                    if branch.name == add.name.data.casefold():
                        errors.append("Branch already exists")
                        break
            if not errors:
                branch = Branch(name=add.name.data.casefold(),label=add.name.data.capitalize())
                db.session.add(branch)
                db.session.commit()
                branches.append(branch)
                success = True
            return render_template("/admin/branches.html", current_user=current_user, form=add, errors=errors,
                                   success=success, branches=branches, isUpdated=isUpdated)
        return render_template("/admin/branches.html", current_user=current_user, form=add,
                               branches=branches, isUpdated=isUpdated)
    else:
        return render_template("error.html", name='ADMIN', error=401)


@b.route('/admin/branches/delete/<branchId>', methods=['POST'])
@login_required
def delete_branch(branchId):
    if (current_user.roles[0].id == 1):
        branch = Branch.query.filter_by(id=branchId).first()
        if branch:
            db.session.delete(branch)
            db.session.commit()
        return redirect(url_for('b.branches'))
    else:
        return render_template("error.html", name='ADMIN', error=401)


@b.route('/admin/branches/update/<branchId>', methods=['POST'])
@login_required
def update_branch(branchId):
    """update a branch."""
    if (current_user.roles[0].id == 1):
        update = BranchForm()
        branch = Branch.query.filter_by(id=branchId).first()
        if branch and update.name.data:
            isUpdated = True
            isExist = Branch.query.filter_by(
                name=update.name.data.casefold()).one_or_none()
            if not isExist:
                branch.name = update.name.data.casefold()
                branch.label = update.name.data.capitalize()
            else:
                isUpdated = False
            db.session.commit()
            return redirect(url_for("b.branches", isUpdated=isUpdated))
    else:
        return render_template("error.html", name='ADMIN', error=401)
