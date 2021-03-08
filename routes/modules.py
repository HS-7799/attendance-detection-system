from services.forms import ModuleForm
from flask import Flask, url_for, render_template, request, redirect, session, Blueprint
from services.models import Module, db
from flask_login import (
    current_user,
    login_required,
)
m = Blueprint('m', __name__, template_folder='templates')
# modules


@m.route('/admin/modules', methods=["GET", "POST"])
@m.route('/admin/modules/<isUpdated>', methods=["GET", "POST"])
@login_required
def modules(isUpdated=True):
    if (current_user.roles[0].id == 1):
        modules = Module.query.all()
        add = ModuleForm()
        if (add.validate_on_submit()):
            errors = []
            success = False
            if not add.name.data:
                errors.append("Name field is required")
            else:
                for module in modules:
                    if module.name == add.name.data.casefold():
                        errors.append("Module already exist")
                        break

            if (not errors):
                module_name = add.name.data.casefold()
                module_label = add.name.data.capitalize()
                module = Module(name=module_name,label = module_label)
                db.session.add(module)
                db.session.commit()
                success = True
                modules.append(module)
            return render_template("/admin/modules.html", current_user=current_user, modules=modules, form=add,
                                   errors=errors, success=success, isUpdated=isUpdated)

        return render_template("/admin/modules.html", current_user=current_user, modules=modules, form=add, isUpdated=isUpdated)
    else:
        return render_template("error.html", name='ADMIN', error=401)


@m.route('/admin/modules/delete/<moduleId>', methods=['POST'])
@login_required
def delete_module(moduleId):
    """Delete a module."""
    if (current_user.roles[0].id == 1):
        module1 = Module.query.filter_by(id=moduleId).first()
        if module1:
            # for e in module1.examens:
            #     db.session.delete(e)
            db.session.delete(module1)
            db.session.commit()
        return redirect(url_for("m.modules"))
    else:
        return render_template("error.html", name='ADMIN', error=401)


@m.route('/admin/modules/update/<moduleId>', methods=['POST'])
@login_required
def update_module(moduleId):
    """update a module."""
    if (current_user.roles[0].id == 1):
        update = ModuleForm()
        module = Module.query.filter_by(id=moduleId).first()
        if module and update.name.data:
            isUpdated = True
            isExist = Module.query.filter_by(
                name=update.name.data.casefold()).one_or_none()
            if not isExist:
                module.name = update.name.data.casefold()
                module.label = update.name.data.capitalize()
            else:
                isUpdated = False
            db.session.commit()
            return redirect(url_for("m.modules", isUpdated=isUpdated))
    else:
        return render_template("error.html", name='ADMIN', error=401)


# fin modules
