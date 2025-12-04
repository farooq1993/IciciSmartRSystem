from flask import Blueprint, request, jsonify, render_template, Response, redirect, url_for
from models.channel import CreateChannel, DataStructureField,DataStructureTemplate
from utils.database import SessionLocal
from utils.extension import db
from datetime import datetime


channel = Blueprint("channel", __name__)
# db = SessionLocal()


@channel.route("/", methods=["GET"])
def get_channel_list():
    return jsonify({'msg':'all channels list'})


# @channel.route('/create_channel', methods=['GET', 'POST'])
# def create_channel():
#     if request.method == "POST":
#         channel_name = request.form.get("channel_name")
#         channel_type = request.form.get("channel_type")
#         channel_source_path = request.form.get("channel_source_path")
#         channel_file_type = request.form.get("channel_file_type")
#         channel_username = request.form.get("channel_username")
#         channel_polling_freq = request.form.get("channel_polling_freq")

#         new_channel = CreateChannel(
#             channel_name=channel_name,
#             channel_type=channel_type,
#             channel_source_path=channel_source_path,
#             channel_file_type=channel_file_type,
#             channel_username=channel_username,
#             channel_polling_freq=channel_polling_freq,
#             created_at=datetime.utcnow()
#         )

#         db.add(new_channel)
#         db.commit()

#         return redirect(url_for("channel.create_channel"))
    
#     # Handle GET → fetch channel list
#     try:
#         # channels = db.session.query(CreateChannel).all()
#         channels = CreateChannel.query.all()
#         templates = DataStructureTemplate.query.all()
#         print("temp:", templates)
#     except Exception as e:
#         db.session.rollback()
#         raise e
#     finally:
#         db.session.close()
#     return render_template("create_channel.html", channels=channels, template=templates)

@channel.route('/create_channel', methods=['GET', 'POST'])
def create_channel():
    if request.method == "POST":
        new_channel = CreateChannel(
            channel_name=request.form.get("channel_name"),
            channel_type=request.form.get("channel_type"),
            channel_source_path=request.form.get("channel_source_path"),
            channel_file_type=request.form.get("channel_file_type"),
            channel_username=request.form.get("channel_username"),
            channel_polling_freq=request.form.get("channel_polling_freq"),
            created_at=datetime.utcnow()
        )
        db.session.add(new_channel)
        db.session.commit()

        return redirect(url_for("channel.create_channel"))

    return render_template(
        "create_channel.html",
        channels=CreateChannel.query.all(),
        templates=DataStructureTemplate.query.all(),
        template=None
    )


@channel.route("/structure/template/add", methods=["POST"])
def add_template():
    tpl = DataStructureTemplate(
        name=request.form.get("name"),
        description=request.form.get("description")
    )
    db.session.add(tpl)
    db.session.commit()

    return redirect(url_for("channel.create_channel"))


# Add Field (AJAX)
@channel.route("/structure/template/<int:template_id>/field/add", methods=["POST"])
def add_field(template_id):
    max_sort = db.session.query(
        db.func.max(DataStructureField.sort_order)
    ).filter_by(template_id=template_id).scalar() or 0

    field = DataStructureField(
        template_id=template_id,
        field_name=request.form.get("field_name"),
        data_type=request.form.get("data_type"),
        format=request.form.get("format"),
        min_length=int(request.form.get("min_length")),
        max_length=int(request.form.get("max_length")),
        mandatory=("mandatory" in request.form),
        primary_key=("primary_key" in request.form),
        regex=request.form.get("regex"),
        sort_order=max_sort + 1,
    )

    db.session.add(field)
    db.session.commit()

    return {
        "id": field.id,
        "field_name": field.field_name,
        "data_type": field.data_type,
        "mandatory": field.mandatory,
        "primary_key": field.primary_key,
    }




# Select template
@channel.route("/structure/template/select")
def select_template():
    template_id = request.args.get("template_id")
    print("temi id", template_id)
    if not template_id:
        return redirect(url_for("channel.create_channel"))

    return redirect(url_for("channel.edit_template", template_id=template_id))

@channel.route("/structure/template/<int:template_id>")
def edit_template(template_id):
    # Load selected template
    template = DataStructureTemplate.query.get_or_404(template_id)

    # Load channel list (for Channel Tab)
    channels = CreateChannel.query.all()

    # Load all templates (for dropdown)
    templates = DataStructureTemplate.query.all()

    # Render main page with complete context
    return render_template(
        "create_channel.html",
        channels=channels,
        templates=templates,
        template=template
    )


@channel.route("/structure/field/<int:field_id>/edit", methods=["POST"])
def update_field(field_id):

    field = DataStructureField.query.get_or_404(field_id)
    form = request.form

    field.field_name = form.get("field_name")
    field.data_type = form.get("data_type")
    field.format = form.get("format")
    field.min_length = int(form.get("min_length"))
    field.max_length = int(form.get("max_length"))
    field.mandatory = ('mandatory' in form)
    field.primary_key = ('primary_key' in form)
    field.regex = form.get("regex")

    db.session.commit()

    return redirect(url_for("channel.edit_template", template_id=field.template_id))


@channel.route("/structure/field/<int:field_id>/delete", methods=["DELETE"])
def delete_field(field_id):
    f = DataStructureField.query.get_or_404(field_id)
    db.session.delete(f)
    db.session.commit()

    return {"success": True, "id": field_id}


