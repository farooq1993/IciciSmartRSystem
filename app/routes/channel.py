from flask import Blueprint, request, jsonify, render_template, Response, redirect
from models.channel import CreateChannel, DataStructureField
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


@channel.route("/structure/field/add", methods=["GET", "POST"])
def add_field():
    form = request.form

    max_sort = db.session.query(db.func.max(DataStructureField.sort_order)).scalar() or 0

    field = DataStructureField(
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

    return redirect(url_for("channel.add_field"))



@channel.route("/structure/field/<int:field_id>/delete", methods=["DELETE"])
def delete_field(field_id):
    field = DataStructureField.query.get_or_404(field_id)
    template_id = field.template_id

    db.session.delete(field)
    db.session.commit()

    return redirect(url_for("structure.structure_home", template_id=template_id))

