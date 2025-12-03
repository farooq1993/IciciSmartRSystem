from flask import Blueprint, request, jsonify, render_template, Response, redirect
from models.channel import CreateChannel, DataStructureTemplate,DataStructureField
from utils.database import SessionLocal
from datetime import datetime


channel = Blueprint("channel", __name__)
db = SessionLocal()


@channel.route("/", methods=["GET"])
def get_channel_list():
    return jsonify({'msg':'all channels list'})


@channel.route('/create_channel', methods=['GET', 'POST'])
def create_channel():
    if request.method == "POST":
        channel_name = request.form.get("channel_name")
        channel_type = request.form.get("channel_type")
        channel_source_path = request.form.get("channel_source_path")
        channel_file_type = request.form.get("channel_file_type")
        channel_username = request.form.get("channel_username")
        channel_polling_freq = request.form.get("channel_polling_freq")

        new_channel = CreateChannel(
            channel_name=channel_name,
            channel_type=channel_type,
            channel_source_path=channel_source_path,
            channel_file_type=channel_file_type,
            channel_username=channel_username,
            channel_polling_freq=channel_polling_freq,
            created_at=datetime.utcnow()
        )

        db.add(new_channel)
        db.commit()

        return redirect(url_for("channel.create_channel"))

    # Handle GET → fetch channel list
    try:
        channels = db.query(CreateChannel).all()
    except Exception as e:
        db.rollback()
        raise e
    finally:
        db.close()
    return render_template("create_channel.html", channels=channels)


@channel.route("/structure")
def structure_home():
    templates = DataStructureTemplate.query.order_by(DataStructureTemplate.id.asc()).all()

    selected_template_id = request.args.get("template_id", type=int)
    selected_template = None
    fields = []

    if selected_template_id:
        selected_template = DataStructureTemplate.query.get(selected_template_id)
        if selected_template:
            fields = selected_template.fields

    return render_template(
        "structure.html",
        templates=templates,
        selected_template=selected_template,
        fields=fields
    )

@channel.route("/structure/template/add", methods=["POST"])
def add_template():
    name = request.form.get("name")
    description = request.form.get("description")

    template = DataStructureTemplate(name=name, description=description)
    db.session.add(template)
    db.session.commit()

    return redirect(url_for("structure.structure_home", template_id=template.id))

@channel.route("/structure/template/<int:template_id>/field/add", methods=["POST"])
def add_field(template_id):
    template = DataStructureTemplate.query.get_or_404(template_id)

    form = request.form

    max_sort = db.session.query(db.func.max(DataStructureField.sort_order))\
        .filter_by(template_id=template.id).scalar() or 0

    field = DataStructureField(
        template_id=template.id,
        field_name=form.get("field_name"),
        data_type=form.get("data_type"),
        format=form.get("format") or None,
        min_length=int(form.get("min_length", 0)),
        max_length=int(form.get("max_length", 255)),
        mandatory=("mandatory" in form),
        primary_key=("primary_key" in form),
        regex=form.get("regex") or None,
        sort_order=max_sort + 1
    )

    db.session.add(field)
    db.session.commit()

    return redirect(url_for("structure.structure_home", template_id=template.id))


@channel.route("/structure/field/<int:field_id>/delete", methods=["DELETE"])
def delete_field(field_id):
    field = DataStructureField.query.get_or_404(field_id)
    template_id = field.template_id

    db.session.delete(field)
    db.session.commit()

    return redirect(url_for("structure.structure_home", template_id=template_id))

